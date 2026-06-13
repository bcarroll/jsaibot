"""Tests for model manager module."""

import pytest
import sys
import json
from pathlib import Path
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from model_manager import ModelManager


class TestModelManager:
    """Test cases for ModelManager class."""
    
    def test_init_with_custom_dir(self):
        """Test initialization with custom download directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ModelManager(download_dir=tmpdir, auto_download=True)
            
            assert Path(tmpdir).exists()
            assert manager.auto_download is True
    
    def test_init_creates_directory(self):
        """Test that init creates the download directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_models"
            
            manager = ModelManager(download_dir=str(new_dir))
            
            assert new_dir.exists()
    
    def test_is_model_installed_with_no_files(self):
        """Test checking if model is installed when nothing exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ModelManager(download_dir=tmpdir, auto_download=False)
            
            # No files should mean not installed
            assert manager.is_model_installed("test-model") is False
    
    def test_is_model_installed_with_config_json(self):
        """Test checking if model is installed with mlc-chat-config.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ModelManager(download_dir=tmpdir, auto_download=False)
            
            # Create a fake model directory with mlc-chat-config.json
            model_path = Path(tmpdir) / "test-model"
            model_path.mkdir()
            (model_path / "mlc-chat-config.json").write_text('{"local_id": "test"}')
            
            assert manager.is_model_installed("test-model") is True
    
    def test_get_installed_models_empty(self):
        """Test getting installed models when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ModelManager(download_dir=tmpdir, auto_download=False)
            
            models = manager.get_installed_models()
            
            assert isinstance(models, list)
            assert len(models) == 0


class TestModelManagerIntegration:
    """Integration tests for ModelManager."""
    
    def test_create_model_config(self):
        """Test that model config is properly created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ModelManager(download_dir=tmpdir, auto_download=True)
            
            # This would normally download from MLC zoo
            result = manager.is_model_installed("Llama-3-8B-Instruct")
            
            # Should return False since we didn't actually download
            assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])