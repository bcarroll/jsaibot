"""
Configuration module for JSAIBOT.
Provides settings and defaults for WebLLM client configuration.
"""

from typing import Optional


class WebLLMConfig:
    """Configuration class for WebLLM client."""
    
    # Default model configuration
    DEFAULT_MODEL = "Llama-3-8B-Instruct"
    DEFAULT_MODEL_SOURCE = "mlc-ai/Llama-3-8B-Instruct-q4f16_1-MLC"
    DEFAULT_DOWNLOAD_DIR = "./models"
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        model_path: Optional[str] = None,
        model_name: Optional[str] = None,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        history_size: int = 10,
        auto_download: bool = True
    ):
        """
        Initialize configuration.
        
        Args:
            host: WebLLM instance host address
            port: WebLLM instance port number
            model_path: Path to the local WebLLM model (if loaded externally)
            model_name: Name of the model to download/use
            max_new_tokens: Maximum tokens for generation
            temperature: Sampling temperature (0.0 - 1.0)
            history_size: Number of conversation turns to retain
            auto_download: Whether to automatically download missing models
        """
        self.host = host
        self.port = port
        self.model_path = model_path
        self.model_name = model_name or self.DEFAULT_MODEL
        self.download_dir = self.DEFAULT_DOWNLOAD_DIR
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.history_size = history_size
        self.auto_download = auto_download
    
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
            "model_name": self.model_name,
            "download_dir": self.download_dir,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "history_size": self.history_size,
            "auto_download": self.auto_download
        }
    
    def get_model_full_path(self) -> str:
        """Get the full path to the model directory."""
        return f"{self.download_dir}/{self.model_name.replace('/', '-').replace('@', '-')}"


# Default configuration instance
default_config = WebLLMConfig()