import hashlib
import re
import time
from typing import Dict

from langchain_core.messages import AIMessage, ToolMessage


def extract_tool_content_and_sender(data):
    for sender, messages in data.items():
        for message in messages:  # Directly iterating over the list of ToolMessage objects
            # Check if the message is an instance of ToolMessage
            if isinstance(message, ToolMessage):
                # Extract and print the tool name (if relevant) and content
                tool_call_id = message.tool_call_id
                tool_content = message.content
                tool_status = message.status  # Optional: Include the status of the tool execution
                print('\n************************************************************\n')
                print(f"\nTool Call ID: {tool_call_id}\nStatus: {tool_status}\n"
                      f"Content:\n{formate_content_by_width(tool_content)}\n")
            else:
                print(f"Unknown message format: {message}")


# Example call with your data
# extract_tool_content_and_sender(data)


def extract_content_and_sender(data):
    for sender, info in data.items():
        for message in info['messages']:
            sender_name = info.get('sender', sender)

            # Check if the message is an instance of AIMessage
            if isinstance(message, AIMessage):
                # Check if content is a list
                if isinstance(message.content, list):
                    for item in message.content:
                        if isinstance(item, dict) and 'text' in item:
                            # Display the text spoken by the agent
                            print(f"Sender: {sender_name}\nContent:\n{formate_content_by_width(item['text'])}\n")
                        elif isinstance(item, dict) and 'name' in item and 'input' in item:
                            # Display information about the tool
                            tool_name = item['name']
                            tool_input = item['input']
                            print(f"Tool: {tool_name}\nInput: {formate_content_by_width(str(tool_input))}\n")
                        elif isinstance(item, str):
                            # If it is a plain string
                            print(f"Sender: {sender_name}\nContent:\n{formate_content_by_width(item)}\n")
                else:
                    # If content is a string, display it directly
                    print(f"Sender: {sender_name}\nContent:\n{formate_content_by_width(message.content)}\n")
            else:
                print(f"Unknown message format: {formate_content_by_width(message)}")


def common_extract_content(data: Dict):
    if 'call_tool' in data:
        extract_tool_content_and_sender(data['call_tool'])
    else:
        extract_content_and_sender(data)


def formate_content_by_width(content: str, width: int = 120) -> str:
    """
    Format the given content string to fit within the specified width.

    Args:
        content (str): The input string to be formatted.
        width (int, optional): The maximum width for each line. Defaults to 80.

    Returns:
        str: The formatted string with line breaks inserted to fit the specified width.

    Raises:
        ValueError: If the content is not a string or if the width is less than 1.
    """
    if not isinstance(content, str):
        raise ValueError("Content must be a string.")
    if not isinstance(width, int) or width < 1:
        raise ValueError("Width must be a positive integer.")

    words = content.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + (1 if current_line else 0) <= width:
            current_line.append(word)
            current_length += len(word) + (1 if current_length > 0 else 0)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


import os
import subprocess
import tempfile
import sys


def save_and_open_graph(graph):
    try:
        # get PNG data
        png_data = graph.get_graph(xray=True).draw_mermaid_png()

        # create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_filename = tmp_file.name
            tmp_file.write(png_data)

        print(f"Graph image saved as: {tmp_filename}")

        # Open an image by a standard viewer
        if os.name == 'nt':  # for Windows
            os.startfile(tmp_filename)
        elif os.name == 'posix':  # for macOS and Linux
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, tmp_filename])
        else:
            print(f"Unable to open the image automatically. Please open {tmp_filename} manually.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure you have Graphviz installed and accessible in your system PATH.")



def generate_unique_id(message_content: str) -> str:
    """
    Generates a unique ID based on the message content and current time.
    """
    # Combine content and current time to ensure uniqueness
    content_hash = hashlib.md5(message_content.encode()).hexdigest()
    timestamp = str(time.time())  # Current timestamp
    return f"{content_hash}_{timestamp}"


def compare_messages_by_groups(previous_message: str, current_message:str):
    """
    This function compares two messages by automatically splitting them into groups
    using regular expressions and counts how many groups match between the two.

    Parameters:
        previous_message (str): The second-to-last message.
        current_message (str): The most recent message.

    Returns:
        tuple: (number of matching groups, total number of groups in the previous message)
    """
    # Create a regex pattern to capture words (\w+), digits (\d+), and punctuation like colons (:) and periods (.)
    pattern = re.compile(r'(\w+|\d+|[:.])')

    # Apply the regex pattern to both messages to find all matching groups (words, numbers, etc.)
    previous_match = pattern.findall(previous_message)
    current_match = pattern.findall(current_message)

    # If both messages contain matches, compare the groups
    if previous_match and current_match:
        # Count how many groups match between the two messages
        group_matches = sum([1 for prev, curr in zip(previous_match, current_match) if prev == curr])
        return group_matches, len(previous_match)
    else:
        # Return 0 matches if no groups were found or compared
        return 0, len(previous_match)

