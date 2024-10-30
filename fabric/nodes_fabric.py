from functools import partial
from typing import Callable, Union, Optional, Dict, List
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic

from utils.orm_util import create_message_from_file


class NodesFabric:
    def __init__(self, model_llm: Optional[Union[ChatOpenAI, ChatAnthropic, Callable]]):
        """
        Initialize NodesFabric with the given model.

        Args:
            model_llm (Union[ChatOpenAI, ChatAnthropic, Callable]): A callable representing the language model
                to be used by agents, or an instance of ChatOpenAI or ChatAnthropic.
        """

        self.model_llm = model_llm

    def create_graph_node(
            self,
            agent_func: Callable,
            sys_msg_path: str,
            node_func: Callable,
            node_name: str,
            model_llm: Union[ChatOpenAI, ChatAnthropic, Callable] = None,
            oai_schema: Optional[Dict] = None,
            tools: Optional[List[Callable]] = None,
            chooser_options: Optional[List[Callable]] = None

    ) -> Callable:
        """
            Fields examples:
                agent_func=,
                sys_msg_path=,
                node_func=,
                node_name=,
                oai_schema=,
                tools=,
                chooser_options=
        """
        sys_msg = create_message_from_file(sys_msg_path)


        # Create an agent
        if not model_llm:
            model_llm = self.model_llm

        if agent_func.__name__ == 'assistant_agent_with_constructed_output':
            agent = agent_func(model_llm=model_llm, system_message=sys_msg, oai_schema=oai_schema)
        elif tools:
            agent = agent_func(model_llm=model_llm, system_message=sys_msg, all_tools=tools)
        else:
            agent = agent_func(model_llm=model_llm, system_message=sys_msg)


        # Create a node
        if node_func.__name__ is 'create_chooser_node':
            node = partial(node_func, agent=agent, name=node_name, chooser_options=chooser_options)
        else:
            node = partial(node_func, agent=agent, name=node_name)

        return node

    def create_team_node(
            self,
            graph_func: Callable,
            node_func: Callable,
            name: str,
            conditional_func: Optional[Callable] = None,
            tools: Optional[List[Callable]] = None,
            **msg_path
    ) -> Callable:
        """
            Create a single team node by combining a node function, a graph, and a name.
            This method requires node_func with a graph.
        """

        if msg_path is None:
            msg_path = {}

        # Create the graph
        if tools:
            graph = graph_func(self.model_llm, tools, **msg_path)
        else:
            graph = graph_func(self.model_llm, **msg_path)

        # Create a team node, partially applying graph and name
        if node_func.__name__ == 'create_connector_sub_graph':
            team_node = partial(node_func, graph=graph, name=name, conditional_func=conditional_func)
        else:
            team_node = partial(node_func, graph=graph, name=name)

        return team_node
