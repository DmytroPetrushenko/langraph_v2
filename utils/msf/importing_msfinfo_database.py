import logging
import re
from typing import List, Dict

import constants

from pymetasploit3.msfrpc import MsfRpcClient

from utils.msf.classes import CustomMsfRpcClient


def work_with_msf_console(console_commands: List[str]) -> str:
    """
    Executes a list of commands in the Metasploit console and returns the combined output.

    :param console_commands: A list of commands to execute in the Metasploit console.
    :return: The combined output from the console as a string.
    """
    try:
        # Create Metasploit RPC client
        client: MsfRpcClient = CustomMsfRpcClient().get_client()

        # Create a new console
        current_console = client.consoles.console()

        # Execute the provided commands in the console
        for command in console_commands:
            current_console.write(command)

        united_outputs = []

        while True:
            console_output = current_console.read()
            united_outputs.append(console_output['data'])

            if not console_output['busy']:
                break

        # Join all the console outputs into a single string
        united_outputs_str = ''.join(united_outputs).strip()

        # Log the successful execution of commands
        logging.info(f'Successfully executed console commands: {console_commands}')

        return united_outputs_str

    except Exception as e:
        logging.error(f'Error while executing console commands: {console_commands}, Error: {str(e)}')
        raise


def format_columns_name(column_name: str) -> str:
    column_name = column_name.lower().replace(' ', '_')
    return column_name if column_name != 'check' else 'status_check'


def _parse_modules_data(data: str) -> List[Dict[str, str]]:
    """
    Parses module data from a string and returns it as a list of dictionaries.

    :param data: The string containing module data
    :return: A list of modules, represented as dictionaries {field name: field value}
    """
    # Filter out empty lines
    lines = [line for line in data.splitlines() if line]
    parsed_data = []

    # Extract column headers from the first line
    columns_name = re.split(r'\s{2,}', lines[0].strip())

    for line in lines[1:]:
        # Skip lines that contain only dashes or spaces (e.g., separators)
        if re.search(r'^[- ]+$', line):
            continue

        # Split the line by multiple spaces
        values = re.split(r'\s{2,}', line.strip())

        # Create a record by mapping values to columns
        record = {
            'group': _extract_group(values[1]),
            'sub_group': _extract_sub_group(values[1]),
            format_columns_name(columns_name[1]): values[1],
            format_columns_name(columns_name[2]): values[2],
            format_columns_name(columns_name[3]): values[3],
            format_columns_name(columns_name[4]): values[4],
            format_columns_name(columns_name[5]): values[5] if len(values) > 5 else ''
        }

        # Add the record to the final list
        parsed_data.append(record)

    return parsed_data


def _extract_sub_group(module_path: str) -> str:
    """
    Extracts the word between the first and second slash in a module path.

    :param module_path: The module path string (e.g., 'auxiliary/scanner/dcerpc/management')
    :return: The word between the first and second slash (e.g., 'scanner')
    """
    parts = module_path.split('/')
    if len(parts) >= 3:
        return parts[1]
    return ''


def _extract_group(module_path: str) -> str:
    """
    Extracts the word between the first and second slash in a module path.

    :param module_path: The module path string (e.g., 'auxiliary/scanner/dcerpc/management')
    :return: The word between the first and second slash (e.g., 'scanner')
    """
    parts = module_path.split('/')
    if len(parts) >= 3:
        return parts[0]
    return ''


def load_modules_list(module_category: str = 'auxiliary'):
    """
    Loads the list of Metasploit modules for a given category and returns the result as a string.
    :param module_category: The category of modules to show (e.g., 'auxiliary', 'exploit'). Default is 'auxiliary'.
    :return: The list of modules as a string.
    """
    try:
        command = f'show {module_category}'
        output = work_with_msf_console([command])

        # Join all the console outputs into a single string
        united_outputs_str = ''.join(output)

        # Find the start of the module list and clean up the output
        index = united_outputs_str.find(constants.DELETE_UNTIL)
        if index != -1:
            united_outputs_str = united_outputs_str[index:].rstrip()

        parsed_data: List[Dict[str, str]] = _parse_modules_data(united_outputs_str)

        return parsed_data

    except Exception as e:
        logging.error(f'Error while loading module list for category {module_category}: {str(e)}')
        raise


def get_required_options_msf_modules(module_category: str, module_name: str) -> List[str]:
    # Create Metasploit RPC client
    client: MsfRpcClient = CustomMsfRpcClient().get_client()
    module = client.modules.use(module_category, module_name)

    # Filter strings that are fully uppercase
    main_options = [string for string in module.required if string.isupper()]
    return main_options
