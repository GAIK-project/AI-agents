import json
import os
import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.types import Command

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the graph
from src.graph import graph


def main():
    """Run a test interaction with the structured data agent."""
    # Thread configuration
    thread_id = "test-thread-1"
    config = {"configurable": {"thread_id": thread_id}}

    print("\n==================================")
    print("STRUCTURED DATA AGENT - TEST")
    print("==================================\n")

    # Get user input
    print("Enter text you want to convert to structured data.")
    print("Examples:")
    print("- \"I want to book a trip to New York on December 25, 2024\"")
    print("- \"Tell me about Spain, especially its food culture\"")
    print("- \"My contact info: John Doe, phone 555-1234, address 123 Main St\"")

    user_input = input("\nUser: ")
    if not user_input:
        user_input = "I want to book a trip to New York on December 25, 2024"
        print(f"Using example input: {user_input}")

    # Call the graph with user input
    print("\nExtracting structured data...")
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config
    )

    # Print the latest message from the graph
    if result["messages"]:
        print(f"\nAgent: {result['messages'][-1].content}")

    # Continue conversation until completed
    try:
        while True:
            # Get current graph state
            state = graph.get_state(config)

            # Check for interrupts
            if state.tasks:
                task = state.tasks[0]
                if hasattr(task, 'interrupts') and task.interrupts:
                    interrupt = task.interrupts[0]

                    # Show interrupt details
                    print(f"\nAgent asks: {interrupt.value['question']}")
                    print(f"Original text: \"{interrupt.value['original_text']}\"")
                    print(f"Structured data: {json.dumps(interrupt.value['structured_data'], indent=2)}")

                    # Simplified feedback options
                    print("\nFeedback options:")
                    print("1. Type 'accept' if you're satisfied")
                    print("2. Type your feedback if you want changes (e.g., 'add datetime 12.12.2025')")

                    # Get user feedback
                    user_response = input("\nYour feedback: ")

                    # Process the feedback
                    if user_response.lower() == 'accept':
                        # User is satisfied
                        feedback_data = {"satisfied": True}
                    else:
                        # User provided feedback
                        feedback_data = {
                            "satisfied": False,
                            "feedback": user_response
                        }

                    try:
                        # If user is not satisfied and provides feedback
                        if not feedback_data.get("satisfied", True) and "feedback" in feedback_data:
                            # Add the feedback as a human message
                            graph.update_state(
                                config, 
                                {"messages": [HumanMessage(content=feedback_data["feedback"])]}
                            )
                        
                        # Continue graph with simplified feedback
                        print("\nProcessing based on feedback...")
                        resume_data = {"satisfied": feedback_data.get("satisfied", False)}
                        result = graph.invoke(Command(resume=resume_data), config)

                        # Print the latest message from the graph
                        if result["messages"]:
                            print(f"\nAgent: {result['messages'][-1].content}")

                        # If process is complete, break the loop
                        if "is_satisfied" in result and result["is_satisfied"]:
                            break

                    except Exception as e:
                        print(f"\nError processing feedback: {e}")
                else:
                    print("No interrupts, process is complete.")
                    break
            else:
                print("No active tasks, process is complete.")
                break

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nTest completed. Thank you!")


if __name__ == "__main__":
    main()
