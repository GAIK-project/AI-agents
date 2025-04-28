from __future__ import annotations

from dataclasses import dataclass, field

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from pydantic_ai import Agent


# State containing conversation history
@dataclass
class ConversationState:
    topic: str
    messages: list[str] = field(default_factory=list)

# AI agent for generating questions
question_agent = Agent(
    'openai:gpt-4o',
    system_prompt='Generate engaging questions about the given topic.'
)

# First node - generates a question
@dataclass
class AskQuestion(BaseNode[ConversationState]):
    async def run(self, ctx: GraphRunContext[ConversationState]) -> ReceiveAnswer:
        result = await question_agent.run(f"Ask a question about {ctx.state.topic}")
        question = result.data
        ctx.state.messages.append(f"Q: {question}")
        print(f"Question: {question}")
        return ReceiveAnswer()

# Second node - simulates receiving an answer
@dataclass
class ReceiveAnswer(BaseNode[ConversationState, None, str]):
    async def run(self, ctx: GraphRunContext[ConversationState]) -> EvaluateAnswer | End[str]:
        # In a real app, you'd get this from user input
        answer = input("Your answer: ")
        ctx.state.messages.append(f"A: {answer}")
        
        if answer.lower() == "exit":
            return End("Conversation ended by user")
        return EvaluateAnswer(answer)

# Third node - evaluates the answer
@dataclass
class EvaluateAnswer(BaseNode[ConversationState, None, str]):
    answer: str
    
    async def run(self, ctx: GraphRunContext[ConversationState]) -> AskQuestion | End[str]:
        if len(ctx.state.messages) >= 6:  # 3 questions and answers
            return End("Conversation complete!")
        return AskQuestion()

# Create and run the conversation graph
async def main():
    state = ConversationState(topic="artificial intelligence")
    conversation_graph = Graph(nodes=[AskQuestion, ReceiveAnswer, EvaluateAnswer])
    result = await conversation_graph.run(AskQuestion(), state=state)
    
    print("\nConversation summary:")
    for message in state.messages:
        print(message)
    print(f"\nResult: {result.output}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())