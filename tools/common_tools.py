import datetime
import json
import os
import yaml

from typing import Any, Dict


def write_to_file(data: Any, filename: str = f'result.md') -> str:
    """
    Goals: Writes given data to a file, converting non-string data to strings as necessary.

    Parameters:
    - data: The data to write to the file. Can be of any type (str, int, float, list, dict, bool).
    - filename: The base name of the file to which data will be written. A timestamp will be
                      appended to this base name. Defaults to 'result.txt'.

    Returns:
    - bool: True if the file was written successfully, False otherwise.

    Raises:
    - Exception: Propagates any exceptions that occur during file writing or data serialization.
    """
    try:
        # Convert non-string data to a string format
        if not isinstance(data, str):
            # For dictionaries and lists, use JSON serialization
            if isinstance(data, (dict, list)):
                data = json.dumps(data, indent=4)
            else:
                # For other data types, use the str() function
                data = str(data)

        current_time = datetime.datetime.now()

        # Build the full path to the result's directory.
        result_folder_path = f"{os.getcwd()}/resources/scan_results/{current_time.strftime('%Y_%m_%d')}"

        # Create the directory if it does not exist.
        if not os.path.exists(result_folder_path):
            os.makedirs(result_folder_path)

        # Modify the filename to include a timestamp
        basename, extension = os.path.splitext(filename)
        if not extension:
            extension = '.md'
        timestamped_filename = (f"{result_folder_path}/{basename}_"
                                f"{current_time.strftime('%H-%M-%S')}{extension}")

        # Saving the data to a file
        with open(timestamped_filename, 'w') as file:
            file.write(data)

        print(f"Results saved to {timestamped_filename}")
        return "written in file"
    except Exception as e:
        raise IOError(f"Writing to file failed: {e}")


def read_from_file(filename: str = None) -> list[str]:
    """
    Reads a file from the specified path and returns a list of strings,
    with each string representing a line from the file. The newline characters
    are removed from each line.

    Args:
        filename: The name of the file to read. The file should be located
                        in the "resources" directory within the current working directory.

    Returns:
        list[str]: A list of strings, each representing a line from the file with
                   newline characters removed.
    """
    file_path = f"{os.getcwd()}/resources/{filename}"
    with open(file_path, 'r') as filereader:
        output: list = filereader.readlines()
        filtered_output: list[str] = [f'auxiliary/{module.replace('\n', '')}' for module in output]

    return filtered_output


def read_json_and_convert_to_yaml(path_file: str) -> str:
    """
    Reads JSON data from a file, removes empty elements, and converts it to a YAML string.

    Parameters:
    path_file: The path to the file containing JSON data. The string must not be empty.

    Returns:
    str: A YAML formatted string of the JSON data, with empty fields omitted.

    Raises:
    ValueError: If the provided file path is empty.
    FileNotFoundError: If the file does not exist.
    IOError: If an I/O error occurs while reading from or processing the file.
    """
    if not path_file:
        raise ValueError("File path must not be empty.")

    try:
        # Open the file and load the JSON data
        with open(path_file, "r") as read_file:
            json_data = json.load(read_file)

        # Remove empty elements from the JSON data
        cleaned_data = remove_empty_elements(json_data)

        # Convert cleaned data to YAML string
        yaml_string = json_to_yaml(cleaned_data)
        return yaml_string

    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {path_file} was not found.")
    except IOError as e:
        raise IOError(f"An I/O error occurred: {e}")


def remove_empty_elements(data: Dict):
    """
    Recursively remove empty lists, dictionaries, or None elements from a dictionary.

    Args:
        data: The dictionary from which to remove empty elements.

    Returns:
        dict: The dictionary with empty elements removed.
    """
    if isinstance(data, dict):
        return {k: remove_empty_elements(v) for k, v in data.items() if v or v == 0}
    elif isinstance(data, list):
        return [remove_empty_elements(v) for v in data if v or v == 0]
    else:
        return data


def json_to_yaml(data: Dict):
    """
    Converts a Python dictionary to a YAML string, omitting empty fields.

    Args:
        data: A Python dictionary, typically one cleaned of empty fields.

    Returns:
        str: A YAML formatted string.
    """
    # Convert Python object to YAML string
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False)
    return yaml_str
