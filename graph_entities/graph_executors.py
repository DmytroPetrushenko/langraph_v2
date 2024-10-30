import random
import traceback

from typing import Optional, Dict
from langgraph.graph.state import CompiledStateGraph, StateGraph
from utils.common_utils import generate_unique_id, save_and_open_graph


def execute_graph(
        graph: StateGraph,
        full_task_message: Dict,
        thread_id: int = random.randint(0, 100000)
):
    config = {"configurable": {"thread_id": thread_id}}

    try:
        compiled_graph: CompiledStateGraph = graph.compile()
        save_and_open_graph(compiled_graph)
    except Exception as compile_error:
        print(f"{compile_error} during graph compilation!")
        print(traceback.format_exc())
        return None

    event: Optional[Dict] = None

    try:
        # Set to store the IDs of already processed messages
        processed_message_ids = set()

        for event in compiled_graph.stream(full_task_message, config, stream_mode='values'):
            # Loop through all the messages in the event
            for message in event['messages']:
                # Try to get the message ID
                message_id = getattr(message, 'id', None)

                # If there's no ID, generate a unique one
                if message_id is None:
                    message_id = generate_unique_id(message.content)
                    message.id = message_id

                # Check if the message has already been processed
                if message_id not in processed_message_ids:
                    # Print the message
                    message.pretty_print()
                    # Add the message ID to the set of processed ones
                    processed_message_ids.add(message_id)
    except Exception as execution_error:
        print(f"{execution_error} during graph execution!")
        print(traceback.format_exc())
        return None

    return event
