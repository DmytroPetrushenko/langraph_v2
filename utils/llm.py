from typing import Optional

from utils.literals import MODEL
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def get_correct_anthropic_name(model_name: str) -> Optional[str]:
    if model_name == 'Claude 3.5 Sonnet':
        return 'claude-3-5-sonnet-20240620'
    if model_name == 'Claude 3 Sonnet':
        return 'claude-3-sonnet-20240229'
    if model_name == 'Claude 3 Opus':
        return 'claude-3-opus-20240229'
    return None


def create_llm(model_name: MODEL, temperature: float = 0) -> ChatOpenAI:
    if 'gpt' in model_name:
        llm = ChatOpenAI(model=model_name, temperature=temperature)
    elif 'claude' in model_name.lower():
        correct_anthropic_name = get_correct_anthropic_name(model_name)
        llm = ChatAnthropic(model_name=correct_anthropic_name, temperature=temperature)
    else:
        raise ValueError('model_name doesn\'t exist as a key in the following list: \'gpt\', \'claude\'')
    return llm
