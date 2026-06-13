"""Tests for configuration module."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import WebLLMConfig, default_config


class TestWebLLMConfig:
    """Test cases for WebLLMConfig class."""
    
    def test_default_config_creation(self):
        """Test creating a config with defaults."""
        config = WebLLMConfig()
        
        assert config.host == "localhost"
        assert config.port == 3000
        assert config.model_name == "Llama-3-8B-Instruct"
        assert config.download_dir == "./models"
        assert config.auto_download is True
    
    def test_custom_config_creation(self):
        """Test creating a config with custom values."""
        config = WebLLMConfig(
            host="0.0.0.0",
            port=8080,
            model_name="Llama-2-7b-chat-hf"
        )
        
        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.model_name == "Llama-2-7b-chat-hf"
        # download_dir uses default since it's not a constructor parameter
        assert config.download_dir == WebLLMConfig.DEFAULT_DOWNLOAD_DIR
    
    def test_default_config_exists(self):
        """Test that default_config is properly created."""
        assert isinstance(default_config, WebLLMConfig)
        assert default_config.host == "localhost"
        assert default_config.port == 3000


class TestDefaultConfig:
    """Test cases for default configuration."""
    
    def test_default_values_are_reasonable(self):
        """Verify default values are sensible for local development."""
        config = default_config
        
        # Host should be localhost
        assert config.host in ["localhost", "127.0.0.1"]
        
        # Port should be a valid port number
        assert 1 <= config.port <= 65535
        
        # Model name should be set
        assert len(config.model_name) > 0
    
    def test_port_is_valid(self):
        """Test that default port is within valid range."""
        assert 1 <= default_config.port <= 65535


if __name__ == "__main__":
    pytest.main([__file__, "-v"])