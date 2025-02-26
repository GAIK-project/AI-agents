"""State definition for the LangGraph agent."""

from typing import Annotated, List, Optional

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from src.schemas import StructuredData


class State(TypedDict):
    """State for the LangGraph agent.

    Attributes:
        messages: Chat history between user and agent
        structured_data: Extracted structured data from user input
        is_satisfied: Whether the user is satisfied with the extracted data
        original_text: Original user input text
    """
    messages: Annotated[List[BaseMessage], add_messages]
    structured_data: Optional[StructuredData]
    is_satisfied: Optional[bool]
    original_text: Optional[str]
