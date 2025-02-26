"""Node implementations for structured data extraction."""

import json
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.types import interrupt

from src.schemas import StructuredData
from src.state import State


def generate_structured_data(state: State) -> Dict[str, Any]:
    """Extract structured data from user input using LLM with structured output.

    This node uses LangChain's structured output method to extract data from
    user input according to the StructuredData schema.

    Args:
        state: Current application state

    Returns:
        Dict[str, Any]: Updated state with structured data
    """
    # Create OpenAI model
    model = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    # Get the latest user message or use original text if we're regenerating
    if state.get("is_satisfied") is False and state.get("original_text"):
        # We're regenerating after feedback
        original_text = state["original_text"]

        # Find feedback messages (the most recent human message)
        feedback = ""
        for message in reversed(state["messages"]):
            if isinstance(message, HumanMessage):
                feedback = message.content
                break

        system_prompt = f"""Extract structured information from this text: "{original_text}".
            Identify the type of request, the main entity, and relevant attributes.
            If dates are mentioned, include them in ISO format (YYYY-MM-DD).
            Add appropriate tags for categorization.
            Make sure to include relevant key-value pairs in the attributes field.
            
            IMPORTANT: The previous extraction needs improvement.
            User feedback: {feedback}
            Please update the extraction based on this feedback.
            """
    else:
        # First-time extraction
        last_message = state["messages"][-1]
        original_text = last_message.content

        system_prompt = f"""Extract structured information from this text: "{original_text}".
            Identify the type of request, the main entity, and relevant attributes.
            If dates are mentioned, include them in ISO format (YYYY-MM-DD).
            Add appropriate tags for categorization.
            Make sure to include relevant key-value pairs in the attributes field.
            """

    # Use structured output to guarantee schema compliance
    model_with_structure = model.with_structured_output(
        StructuredData,
        method="function_calling"
    )

    # Call model with the user input
    structured_data = model_with_structure.invoke(system_prompt)

    # Create response message
    ai_message = AIMessage(
        content=f"I've extracted the following structured data:\n```json\n{json.dumps(structured_data.model_dump(), indent=2)}\n```"
    )

    # Update state
    return {
        "messages": [ai_message],
        "structured_data": structured_data,
        "is_satisfied": None,  # Will be set by human feedback
        "original_text": original_text,
    }


def get_human_feedback(state: State) -> Dict[str, Any]:
    """Get human feedback on the extracted structured data.

    This node interrupts execution to request feedback from the user
    on the quality of the extracted structured data.

    Args:
        state: Current application state

    Returns:
        Dict[str, Any]: Updated state with user satisfaction
    """
    # If there's no structured data, skip this step
    if not state.get("structured_data"):
        return {"is_satisfied": False}

    # Prepare data to show to the user
    structured_data = state["structured_data"]

    human_interrupt_data = {
        "question": "Are you satisfied with this structured data?",
        "structured_data": structured_data.model_dump(),
        "original_text": state.get("original_text", "")
    }

    # Interrupt execution to get user feedback
    human_response = interrupt(human_interrupt_data)

    # Check if user is satisfied
    is_satisfied = human_response.get("satisfied", False)

    # If user provided modified data, use it
    modified_data = human_response.get("modified_data")
    if is_satisfied and modified_data:
        try:
            # Use modified data if provided
            updated_data = StructuredData.model_validate(modified_data)

            ai_message = AIMessage(
                content="Thank you for the corrections! The structured data has been updated."
            )

            return {
                "messages": [ai_message],
                "structured_data": updated_data,
                "is_satisfied": True
            }
        except Exception as e:
            # If there's an error processing the modified data
            ai_message = AIMessage(
                content=f"Error processing modified data: {str(e)}"
            )
            return {
                "messages": [ai_message],
                "is_satisfied": False
            }

    # Create message based on satisfaction
    if is_satisfied:
        message = AIMessage(
            content="Thank you! The structured data has been approved.")
    else:
        # Create a more helpful message requesting specific feedback
        message = AIMessage(
            content="I understand you're not satisfied with the structured data. " +
                    "Please provide feedback on what should be improved or corrected."
        )

    # Return updated state
    return {
        "messages": [message],
        "is_satisfied": is_satisfied
    }


def process_structured_data(state: State) -> Dict[str, Any]:
    """Process the final approved structured data.

    This node handles the final approved structured data and creates
    a summary message to complete the process.

    Args:
        state: Current application state

    Returns:
        Dict[str, Any]: Updated state with final confirmation
    """
    structured_data = state.get("structured_data")

    if not structured_data:
        ai_message = AIMessage(
            content="Error: No structured data found."
        )
        return {"messages": [ai_message]}

    # Create a summary based on the data type
    data_type = structured_data.data_type
    entity = structured_data.primary_entity

    summary = f"Successfully processed {data_type} data for '{entity}'."

    if structured_data.datetime:
        summary += f" Relevant date/time: {structured_data.datetime}."

    if structured_data.tags:
        tags_str = ", ".join(structured_data.tags)
        summary += f" Tags: {tags_str}."

    # Create final message
    ai_message = AIMessage(
        content=f"{summary}\n\nFull structured data:\n```json\n{json.dumps(structured_data.model_dump(), indent=2)}\n```"
    )

    # Return updated state
    return {"messages": [ai_message]}
