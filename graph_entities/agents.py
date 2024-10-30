from typing import Any, Callable

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.agents import create_structured_chat_agent

from utils.orm_util import *
from graph_entities.statets import *


def assistant_agent_with_tools(
        model_llm: ChatOpenAI | ChatAnthropic,
        all_tools: List,
        system_message: str):
    """
    Create an agent with specified tools and a system message.

    Args:
        model_llm: The agent model to bind tools with.
        all_tools: A list of tools to integrate into the agent.
        system_message: A specialized system message to customize the agent's behavior.

    Returns:
        A configured prompt bound with the model and tools.
    """
    # Load the default template message for the system
    default_msg = create_message_from_file('default_without_tools.txt')

    # Define the prompt template using the system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_msg),
            ("system", system_message),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Bind the tools to the model and return the configured prompt
    return prompt | model_llm.bind_tools(all_tools)


def assistant_agent_without_tools(
        model_llm: ChatOpenAI | ChatAnthropic,
        system_message: str,
        all_tools: Optional[List[StructuredTool]] = None
) -> Callable:
    """
    Create an agent without tools, customized with a system message.

    Args:
        model_llm: The agent model to configure.
        system_message: A system message that adds specific instructions or context to the agent.
        all_tools: An optional list of tool descriptions that will be passed to the agent.

    Returns:
        A prompt configured with the model and system message.
    """
    # Load the default template message for the system
    default_msg = create_message_from_file('default_without_tools.txt')

    # Validate system_message input
    if not system_message or not isinstance(system_message, str):
        raise ValueError("Invalid system message. It must be a non-empty string.")

    # Prepare tools descriptions if tools are provided
    tools_descriptions = []
    if all_tools:
        for num in range(len(all_tools)):
            tools_descriptions.append(f'{num + 1}) Name: {all_tools[num].name}, '
                                      f'Description: {all_tools[num].description.replace("/n", " ")};')
    else:
        tools_descriptions = "No tools available."

    # Define the prompt template with system message and tools description
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_msg),
            ("system", system_message),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    prompt = prompt.partial(tools_descriptions=tools_descriptions)

    # Bind the prompt to the model and return it
    return prompt | model_llm


def assistant_agent_with_constructed_output(
        model_llm: ChatOpenAI | ChatAnthropic,
        system_message: str,
        oai_schema
):
    """
        Creates an agent with a specified system message and binds the model to handle structured output.

        This function takes a language model (ChatOpenAI or ChatAnthropic) and a system message to create
        an agent capable of handling structured output based on the provided OpenAI schema. It constructs
        a prompt with dynamic messages and a system message for the agent's configuration.

        Args:
            model_llm (ChatOpenAI | ChatAnthropic): The language model (LLM) to bind the prompt with.
                                                    It must be either ChatOpenAI or ChatAnthropic.
            system_message (str): A customized system message that defines the agent's behavior and context.
                                  It must be a non-empty string.
            oai_schema: The OpenAI schema to define the structured output format, typically used for
                        validating the agent's response structure.

        Returns:
            Callable: A configured prompt that is bound to the model and is capable of returning structured
                      output based on the provided schema. The output is processed using the `json_schema` method.

        Raises:
            ValueError: If the `system_message` is not provided or is not a valid string.
    """

    # Load the default template message for agents without tools
    default_without_tools = create_message_from_file('default_without_tools.txt')

    # Validate system_message input
    if not system_message or not isinstance(system_message, str):
        raise ValueError("Invalid system message. It must be a non-empty string.")

    # Define the prompt template using the system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_without_tools),
            ("system", system_message),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Bind the structured output (TeamState) and return the configured prompt
    return prompt | model_llm.with_structured_output(
        schema=oai_schema,
        method="json_schema"
    )


def assistant_agent_with_constructed_output_bind_tools(
        model_llm: ChatOpenAI | ChatAnthropic,
        system_message: str,
        teams: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None
):
    """
    Create an agent with a specified system message, bind it with the model,
    configure it to handle structured output, and integrate tools for the agent to use.

    Args:
        model_llm: The agent model (ChatOpenAI or ChatAnthropic) to bind the prompt with.
        system_message: A specialized system message to customize the agent's behavior.
        teams: An optional list of team names that will be passed to the agent.
        tools: An optional list of tools that the agent can use.

    Returns:
        An agent configured to produce structured outputs and capable of using tools.
    """

    # Load the default template message for agents without tools
    default_msg = create_message_from_file('default_without_tools.txt')

    # Validate system_message input
    if not system_message or not isinstance(system_message, str):
        raise ValueError("Invalid system message. It must be a non-empty string.")

    # Define the prompt template using the system message and placeholder for dynamic messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", default_msg),
            (MessagesPlaceholder(variable_name="messages"))
        ]
    )

    # Add specialization to the current agent using the system message and teams (if provided)
    prompt = prompt.partial(system_message=system_message, teams=teams)

    # Create the LLM chain with the prompt and model, including structured output
    llm_chain = prompt | model_llm.with_structured_output(TeamState)

    # If tools are provided, initialize an agent that can use them
    if tools:
        agent = create_structured_chat_agent(
            llm=llm_chain,
            tools=tools,
            prompt=prompt
        )
        return agent
    else:
        # Return the chain without tools
        return llm_chain
