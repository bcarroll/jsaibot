"""
WebLLM Client Module

Provides API communication with a locally downloaded WebLLM instance.
Supports WebSocket-based real-time chat and HTTP REST endpoints.
"""

import asyncio
import json
from typing import Optional, Dict, List, Callable, AsyncIterator
from urllib.parse import urljoin

try:
    import aiohttp
except ImportError:
    print("Please install aiohttp: pip install aiohttp")
    raise


class WebLLMClient:
    """
    Client for communicating with a locally running WebLLM instance.
    
    WebLLM typically runs on http://localhost:3000 or a configurable port.
    It provides both WebSocket and HTTP REST APIs for chat interactions.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        model_name: Optional[str] = None,
        max_new_tokens: int = 256,
        temperature: float = 0.7
    ):
        """
        Initialize the WebLLM client.
        
        Args:
            host: Host address of the WebLLM instance (default: localhost)
            port: Port number of the WebLLM instance (default: 3000)
            model_name: Optional specific model name to use
            max_new_tokens: Maximum tokens for generation
            temperature: Sampling temperature for response generation
        """
        self.base_url = f"http://{host}:{port}"
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        
        # Chat history tracking
        self.conversation_history: List[Dict[str, str]] = []
        
    def _build_payload(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """Build the API request payload."""
        return {
            "message": message,
            "history": history or self.conversation_history,
            "max_new_tokens": max_new_tokens or self.max_new_tokens,
            "temperature": temperature or self.temperature,
            "model_name": self.model_name
        }

    async def generate_response(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """
        Generate a response from the WebLLM instance using HTTP REST API.
        
        Args:
            message: User's input message
            history: Optional conversation history override
            max_new_tokens: Optional token limit override
            temperature: Optional temperature override
            
        Returns:
            Dictionary containing the model's response and metadata
        """
        payload = self._build_payload(message, history, max_new_tokens, temperature)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                urljoin(self.base_url, "/api/generate"),
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": message})
                    if "response" in result:
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": result["response"]
                        })
                    
                    return result
                else:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"WebLLM API error: {response.status} - {error_text}"
                    )

    async def stream_response(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncIterator[str]:
        """
        Stream response tokens from WebLLM as they are generated.
        
        Args:
            message: User's input message
            history: Optional conversation history override
            max_new_tokens: Optional token limit override
            temperature: Optional temperature override
            
        Yields:
            Individual tokens or text chunks from the model
        """
        payload = self._build_payload(message, history, max_new_tokens, temperature)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                urljoin(self.base_url, "/api/stream"),
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            # Handle different response formats
                            try:
                                chunk = json.loads(line.decode('utf-8'))
                                if "token" in chunk:
                                    yield chunk["token"]
                                elif "text" in chunk:
                                    yield chunk["text"]
                                else:
                                    yield str(chunk)
                            except json.JSONDecodeError:
                                yield line.decode('utf-8')
                else:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"WebLLM streaming error: {response.status} - {error_text}"
                    )

    async def get_model_info(self) -> Dict:
        """
        Retrieve information about the currently loaded model.
        
        Returns:
            Dictionary containing model metadata
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(urljoin(self.base_url, "/api/model")) as response:
                if response.status == 200:
                    return await response.json()
                raise RuntimeError(f"Failed to get model info: {response.status}")

    async def health_check(self) -> bool:
        """
        Check if the WebLLM instance is running and accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(urljoin(self.base_url, "/health")) as response:
                    return response.status == 200
        except Exception:
            return False

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []

    def set_model_config(
        self,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        model_name: Optional[str] = None
    ) -> None:
        """
        Update model configuration parameters.
        
        Args:
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 - 1.0)
            model_name: Name of the model to switch to
        """
        if max_new_tokens is not None:
            self.max_new_tokens = max_new_tokens
        if temperature is not None:
            self.temperature = temperature
        if model_name is not None:
            self.model_name = model_name


# Convenience function for quick usage
async def chat_with_webllm(
    message: str,
    host: str = "localhost",
    port: int = 3000,
    history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Quick chat with WebLLM without manually managing client state.
    
    Args:
        message: User's input message
        host: WebLLM instance host
        port: WebLLM instance port
        history: Optional conversation history
        
    Returns:
        Model's response text
    """
    client = WebLLMClient(host=host, port=port)
    result = await client.generate_response(message, history)
    return result.get("response", "")


if __name__ == "__main__":
    async def main():
        """Example usage."""
        client = WebLLMClient()
        
        # Check health
        if not await client.health_check():
            print("WebLLM instance is not running. Please start it first.")
            return
            
        print("Connected to WebLLM!")
        
        # Get model info
        try:
            model_info = await client.get_model_info()
            print(f"Model: {model_info.get('model_name', 'Unknown')}")
        except Exception as e:
            print(f"Could not retrieve model info: {e}")
        
        # Chat example
        response = await client.generate_response("Hello, how are you?")
        print(f"Response: {response}")

    asyncio.run(main())