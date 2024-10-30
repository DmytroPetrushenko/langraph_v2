import getpass
import os


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


def launch_environment() -> None:
    _set_env("OPENAI_API_KEY")
    _set_env("TAVILY_API_KEY")
    _set_env("LANGCHAIN_API_KEY")
