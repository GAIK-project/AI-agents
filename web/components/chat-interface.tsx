"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Single chat message type
 * @property role - Message role: "user", "assistant" or "system" (system message)
 * @property content - Message content
 * @property sender - Name of the message sender (agent name)
 */
interface Message {
  role: string;
  content: string;
  sender?: string;
}

/**
 * API request to Swarm service
 * @property messages - All conversation history messages
 * @property context_variables - Context variables (user information)
 */
interface SwarmRequest {
  messages: Message[];
  context_variables: {
    user_name: string;
    location?: string;
  };
}

/**
 * Response from Swarm service
 */
interface SwarmResponse {
  messages: Message[];
  agent_name: string;
  context_variables?: {
    user_name?: string;
    location?: string;
  };
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [userName, setUserName] = useState("Vieras");
  const [location, setLocation] = useState<string | undefined>("Helsinki");
  const [currentAgent, setCurrentAgent] = useState("Assistant");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /**
   * Handles message submission
   * 1. Adds user message to chat history
   * 2. Sends the entire history to the API
   * 3. Processes the response and adds new messages to history
   */
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const requestData: SwarmRequest = {
        messages: [...messages, userMessage],
        context_variables: {
          user_name: userName,
          location,
        },
      };

      console.log("Sending request with messages:", requestData.messages);

      const response = await fetch("http://localhost:8000/api/swarm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const swarmResponse: SwarmResponse = await response.json();
      console.log("Received response:", swarmResponse);

      setCurrentAgent(swarmResponse.agent_name);

      // Process new assistant messages from response
      const newMessages = swarmResponse.messages
        .filter((msg) => msg.role === "assistant" && msg.content?.trim() !== "")
        .map((msg) => ({
          role: msg.role,
          content: msg.content,
          sender: swarmResponse.agent_name,
        }));

      console.log("New messages to add:", newMessages);

      if (newMessages.length > 0) {
        // Add the last assistant message from response
        const lastAssistantMessage = newMessages[newMessages.length - 1];
        setMessages((prev) => [...prev, lastAssistantMessage]);
      } else {
        console.log("No new messages found in response");
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Sorry, I didn't catch that. Could you try again?",
            sender: swarmResponse.agent_name,
          },
        ]);
      }

      // Update user information if needed
      updateUserInfoFromResponse(swarmResponse);
      
    } catch (error) {
      console.error("Error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, an error occurred during the conversation. Please try again.",
          sender: currentAgent,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update user information from response
   */
  const updateUserInfoFromResponse = (response: SwarmResponse): void => {
    if (
      response.context_variables?.user_name &&
      response.context_variables.user_name !== userName
    ) {
      setUserName(response.context_variables.user_name);
    }

    if (
      response.context_variables?.location &&
      response.context_variables.location !== location
    ) {
      setLocation(response.context_variables.location);
    }
  };

  /**
   * Handles Enter key press
   * Sends message when Enter is pressed without Shift key
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Updates user information (name and location)
   * Shows prompt dialogs for entering information
   */
  const updateUserInfo = () => {
    const newName = prompt("Enter your name:", userName);
    if (newName) setUserName(newName);

    const newLocation = prompt("Enter your location:", location || "");
    if (newLocation) setLocation(newLocation);

    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        content: `User information updated: ${newName || userName} from ${
          newLocation || location || "unknown"
        }`,
      },
    ]);
  };

  /**
   * Returns emoji icon corresponding to the agent
   */
  const getAgentIcon = (agentName: string) => {
    switch (agentName) {
      case "Finnish Agent":
        return "🇫🇮";
      case "Weather Expert":
        return "🌤️";
      default:
        return "🤖";
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold">Swarm Agent Chat</h1>
          <div className="flex items-center space-x-2">
            <span className="text-sm">
              {getAgentIcon(currentAgent)}{" "}
              <span className="font-bold">{currentAgent}</span>
            </span>
            <button
              onClick={updateUserInfo}
              className="bg-white text-blue-600 px-3 py-1 rounded-md text-sm font-medium hover:bg-blue-100"
            >
              Update info
            </button>
          </div>
        </div>
        <div className="text-sm mt-1">
          User: {userName}
          {location && ` from ${location}`}
        </div>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>Welcome to chat with Swarm agents!</p>
            <p className="mt-2">Try these:</p>
            <ul className="mt-2 list-disc list-inside">
              <li>General questions (Assistant)</li>
              <li>
                Say "Hello" or "Hi", or say "Let's speak Finnish" (Finnish Agent)
              </li>
              <li>Ask "What is the weather like?" (Weather Expert)</li>
              <li>
                You can request "Go back" to return to the main agent
              </li>
            </ul>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.role === "user" ? "text-right" : "text-left"
              }`}
            >
              <div
                className={`inline-block px-4 py-2 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : message.role === "system"
                    ? "bg-gray-300 text-gray-800"
                    : "bg-white text-gray-800 border border-gray-300"
                }`}
              >
                {message.content}
              </div>
              {message.role === "assistant" && (
                <div className="text-xs text-gray-500 mt-1">
                  {getAgentIcon(message.sender || currentAgent)}{" "}
                  {message.sender || currentAgent}
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input */}
      <div className="p-4 border-t border-gray-300 bg-white rounded-b-lg">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
