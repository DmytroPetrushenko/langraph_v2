import datetime
import json
from typing import Any, Dict, List

from langchain_core.load.load import loads
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.pregel import StateSnapshot


def save_snapshot_in_json(list_snapshots: List[StateSnapshot], team_name: str):
    """
    Save a list of StateSnapshot objects in a JSON file.

    Args:
        list_snapshots: List of StateSnapshot objects to save.

    The file will be saved in the 'resources/states/' directory with a
    timestamp-based filename.
    """
    list_json = []
    for snapshot in list_snapshots:
        list_json.append(_state_to_json(snapshot))

    # Generate a unique file name with the current date and time
    with open(f'resources/states/{team_name.replace(" ", "_")}_snapshots_{datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")}', 'x') as file_writer:
        for snapshot_json in list_json:
            file_writer.write(snapshot_json)
            file_writer.write('\n\n')


def load_snapshot_from_json(file_path: str, position: int = 0) -> StateSnapshot:
    """
    Load a StateSnapshot object from a JSON file.

    Args:
        file_path: Path to the file where the snapshots are stored.
        position: The position in the file to read from (default is 0).

    Returns:
        A StateSnapshot object restored from the JSON data.
    """
    with open(file_path, 'r') as f:
        text_json = f.read().split('\n\n')
    return _json_to_state_snapshot(text_json[position])


# All the following functions are now private by adding a leading underscore

def _state_snapshot_to_dict(snapshot: StateSnapshot) -> Dict[str, Any]:
    """
    Convert a StateSnapshot object into a dictionary format.

    Args:
        snapshot: The StateSnapshot object to convert.

    Returns:
        A dictionary representation of the snapshot with keys like 'values', 'next', 'config', etc.
    """
    return {
        'values': snapshot.values,
        'next': snapshot.next,
        'config': snapshot.config,
        'metadata': snapshot.metadata,
        'created_at': snapshot.created_at,
        'parent_config': snapshot.parent_config,
        'tasks': snapshot.tasks
    }


def _state_to_json(graph_state: StateSnapshot) -> str:
    """
    Convert a StateSnapshot object into a JSON string.

    Args:
        graph_state: The StateSnapshot object to convert.

    Returns:
        A JSON string representation of the graph state.
    """
    fields: Dict[str, Any] = _state_snapshot_to_dict(graph_state)
    raw_json = _dict_to_json(fields)
    return json.dumps(raw_json)


def _dict_to_json(fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively process a dictionary and convert its values to JSON-serializable format.

    Args:
        fields: A dictionary to process.

    Returns:
        A dictionary with values converted into JSON-serializable formats.
    """
    for key, value in fields.items():
        if isinstance(value, (HumanMessage, AIMessage, ToolMessage)):
            fields[key] = value.to_json()  # Calls to_json for HumanMessage or AIMessage
        elif isinstance(value, dict):
            fields[key] = _dict_to_json(value)  # Recursive call for nested dictionaries
        elif isinstance(value, list):
            fields[key] = _list_to_json(value)  # Recursive call for nested lists
    return fields


def _list_to_json(fields: List[Any]) -> List[Any]:
    """
    Recursively process a list and convert its values to JSON-serializable format.

    Args:
        fields: A list to process.

    Returns:
        A list with values converted into JSON-serializable formats.
    """
    result_list = []
    for value in fields:
        if isinstance(value, (HumanMessage, AIMessage, ToolMessage)):
            result_list.append(value.to_json())  # Calls to_json for HumanMessage or AIMessage
        elif isinstance(value, dict):
            result_list.append(_dict_to_json(value))  # Recursive call for dictionaries in lists
        elif isinstance(value, list):
            result_list.append(_list_to_json(value))  # Recursive call for nested lists
        else:
            result_list.append(value)  # Append simple values
    return result_list


def _json_to_state_snapshot(text: str) -> StateSnapshot:
    """
    Convert JSON data back into a StateSnapshot object.

    Args:
        text: A JSON string representing the state snapshot.

    Returns:
        A StateSnapshot object reconstructed from the JSON data.
    """
    json_snapshot = loads(text)

    # Return the StateSnapshot object
    state = StateSnapshot(
        values=json_snapshot.get('values', {}),
        next=tuple(json_snapshot.get('next', '')),
        config=json_snapshot.get('config', {}),
        metadata=json_snapshot.get('metadata', {}),
        created_at=json_snapshot.get('created_at', None),
        parent_config=json_snapshot.get('parent_config', None),
        tasks=json_snapshot.get('tasks', ())
    )

    return state


def _json_to_message(json_values: Dict[str, Any]):
    """
    Convert JSON data back into a message object (e.g., HumanMessage, AIMessage).

    Args:
        json_values: A dictionary representing the JSON data of the message.

    Returns:
        A message object, such as HumanMessage or AIMessage, based on the data.
    """
    messages_list: List[Dict[str, Any]] = json_values['messages']

    for message in messages_list:
        # Determine the message type by the 'type' field
        message_type = message.get('type')

        if message_type == 'constructor':
            human_message = loads(str(json_values).replace("\'", "\""))
            return HumanMessage(
                content=message.get('content'),
                additional_kwargs=message.get('additional_kwargs', {}),
                response_metadata=message.get('response_metadata', {})
            )

        elif message_type == 'ai':
            human_message = loads(str(json_values))
            return AIMessage(
                content=message.get('content'),
                response_metadata=message.get('response_metadata', {}),
                id=message.get('id'),
                usage_metadata=message.get('usage_metadata', {}),
                tool_calls=message.get('tool_calls', []),
                invalid_tool_calls=message.get('invalid_tool_calls', [])
            )

        else:
            raise ValueError(f"Unknown message type: {message_type}")
