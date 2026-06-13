"""Tests for server module."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestWebLLMProxy:
    """Test cases for WebLLMProxy class."""
    
    def test_proxy_creation_with_defaults(self):
        """Test creating proxy with default URL."""
        # Mock config since we don't want to import full modules
        class MockConfig:
            model_name = "Llama-3-8B-Instruct"
            download_dir = "./models"
        
        from server import WebLLMProxy
        
        proxy = WebLLMProxy(webllm_url="http://localhost:3000", config=MockConfig())
        
        assert proxy.webllm_url == "http://localhost:3000"
        assert len(proxy.conversation_history) == 0
    
    def test_proxy_creation_with_custom_url(self):
        """Test creating proxy with custom URL."""
        class MockConfig:
            model_name = "test-model"
            download_dir = "./models"
        
        from server import WebLLMProxy
        
        proxy = WebLLMProxy(
            webllm_url="http://127.0.0.1:3001",
            config=MockConfig()
        )
        
        assert proxy.webllm_url == "http://127.0.0.1:3001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])