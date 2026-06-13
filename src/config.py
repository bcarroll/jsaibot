"""
Configuration module for JSAIBOT.
Provides settings and defaults for WebLLM client configuration.
"""

from typing import Optional


class WebLLMConfig:
    """Configuration class for WebLLM client."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        model_path: Optional[str] = None,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        history_size: int = 10
    ):
        """
        Initialize configuration.
        
        Args:
            host: WebLLM instance host address
            port: WebLLM instance port number
            model_path: Path to the local WebLLM model (if loaded externally)
            max_new_tokens: Maximum tokens for generation
            temperature: Sampling temperature (0.0 - 1.0)
            history_size: Number of conversation turns to retain
        """
        self.host = host
        self.port = port
        self.model_path = model_path
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.history_size = history_size
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "WebLLMConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "model_path": self.model_path,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "history_size": self.history_size
        }


# Default configuration instance
default_config = WebLLMConfig()