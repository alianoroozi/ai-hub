import operator

from langchain_core.messages import AnyMessage
from typing_extensions import Annotated, TypedDict


class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    topic: str
    research_brief: str
    article: str
    tool_call_count: int
