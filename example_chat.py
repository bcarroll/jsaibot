"""
Example script demonstrating how to use the WebLLM client.

This script shows various ways to interact with a locally running WebLLM instance.
"""

import asyncio
from src.webllm_client import WebLLMClient, chat_with_webllm


async def example_basic_chat():
    """Basic chat example."""
    print("=== Basic Chat Example ===")
    
    client = WebLLMClient()
    
    # Check if WebLLM is running
    if not await client.health_check():
        print("Error: WebLLM instance is not running.")
        print("Please start WebLLM on http://localhost:3000 first.")
        return
    
    print("Connected to WebLLM!")
    
    # Send a message
    response = await client.generate_response("Hello, how are you?")
    print(f"Response: {response.get('response', '')}")
    print()


async def example_streaming():
    """Streaming response example."""
    print("=== Streaming Response Example ===")
    
    client = WebLLMClient()
    
    if not await client.health_check():
        print("Error: WebLLM instance is not running.")
        return
    
    print("Asking WebLLM to explain Python async...")
    print("Response:")
    
    # Stream response token by token
    full_response = ""
    async for token in client.stream_response("Explain Python async/await in simple terms:"):
        full_response += token
        print(token, end="", flush=True)
    
    print()  # New line after streaming
    print(f"Full response: {full_response}")
    print()


async def example_conversation_history():
    """Conversation with history tracking."""
    print("=== Conversation History Example ===")
    
    client = WebLLMClient()
    
    if not await client.health_check():
        print("Error: WebLLM instance is not running.")
        return
    
    # First message
    response1 = await client.generate_response("What is the capital of France?")
    print(f"User: What is the capital of France?")
    print(f"WebLLM: {response1.get('response', '')}")
    
    # Second message (references first conversation)
    response2 = await client.generate_response("And what is the population of that city?")
    print(f"User: And what is the population of that city?")
    print(f"WebLLM: {response2.get('response', '')}")
    print()
    
    # Clear history for a new conversation
    client.clear_history()
    print("Conversation history cleared.")
    print()


async def example_custom_config():
    """Example with custom configuration."""
    print("=== Custom Configuration Example ===")
    
    client = WebLLMClient(
        host="localhost",
        port=3000,
        max_new_tokens=512,  # Generate more tokens
        temperature=0.8,     # Higher creativity
        model_name=None      # Use default model
    )
    
    if not await client.health_check():
        print("Error: WebLLM instance is not running.")
        return
    
    response = await client.generate_response(
        "Write a short poem about coding."
    )
    print(f"Response (custom config): {response.get('response', '')}")
    print()


async def main():
    """Run all examples."""
    print("JSAIBOT - WebLLM Client Examples")
    print("=" * 40)
    print()
    
    # Only run examples if WebLLM is available
    client = WebLLMClient()
    if await client.health_check():
        await example_basic_chat()
        await example_streaming()
        await example_conversation_history()
        await example_custom_config()
    else:
        print("WebLLM instance not found at http://localhost:3000")
        print("Please start WebLLM to run the examples.")
        print()
        print("To install and start WebLLM, visit:")
        print("https://github.com/mlc-ai/web-llm")


if __name__ == "__main__":
    asyncio.run(main())