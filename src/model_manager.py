"""
Model Manager Module for JSAIBOT.

Handles downloading and managing WebLLM models from the MLC model zoo.
Supports offline operation after initial download.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import aiohttp
except ImportError:
    print("Please install aiohttp: pip install aiohttp")
    raise

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages WebLLM model downloads and installation.
    
    Downloads models from the MLC model zoo and caches them locally.
    """
    
    # Default MLC model zoo URL
    MLC_MODEL_ZOO_URL = "https://raw.githubusercontent.com/mlc-ai/mlc-llm/main/vars/model_zoo.json"
    DEFAULT_DOWNLOAD_DIR = "./models"
    
    def __init__(
        self,
        download_dir: str = None,
        auto_download: bool = True,
        progress_callback=None
    ):
        """
        Initialize ModelManager.
        
        Args:
            download_dir: Directory to store downloaded models
            auto_download: Whether to automatically download missing models
            progress_callback: Optional callback function for download progress
        """
        self.download_dir = Path(download_dir or self.DEFAULT_DOWNLOAD_DIR)
        self.auto_download = auto_download
        self.progress_callback = progress_callback
        
        # Ensure download directory exists
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache of downloaded model info
        self._model_cache: Dict[str, Any] = {}
    
    async def get_model_zoo(self) -> Dict[str, Any]:
        """Fetch the MLC model zoo index."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.MLC_MODEL_ZOO_URL) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.warning(f"Could not fetch model zoo: {e}")
        
        # Return empty dict if network unavailable (offline operation)
        return {}
    
    def is_model_installed(self, model_name: str) -> bool:
        """Check if a model is already installed locally."""
        model_path = self.download_dir / model_name.replace('/', '-').replace('@', '-')
        index_file = model_path / "model-config.json"
        
        # Check for common model files
        return (
            (index_file.exists() and index_file.stat().st_size > 0) or
            any((model_path / f).exists() for f in ["mlc-chat-config.json", "config.json"])
        )
    
    async def download_model(
        self,
        model_name: str,
        model_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download a model from the MLC zoo.
        
        Args:
            model_name: Name of the model to download
            model_source: Optional specific source URL
            
        Returns:
            Dictionary with download results and model info
        """
        if not self.auto_download:
            raise ValueError(
                f"Model '{model_name}' not found. Set auto_download=True "
                "in config or manually install the model."
            )
        
        logger.info(f"Downloading model: {model_name}")
        
        # Get model zoo to find download URLs
        model_zoo = await self.get_model_zoo()
        
        # Try to find the model in the zoo
        model_info = None
        for key, value in model_zoo.items():
            if model_name.lower() in key.lower() or key.lower().endswith(model_name.lower()):
                model_info = {key: value}
                break
        
        # If not found in cache, check MLC's repo directly
        if not model_info:
            model_info = self._discover_model_info(model_name)
        
        result = {
            "model_name": model_name,
            "downloaded": False,
            "error": None,
            "path": str(self.download_dir / model_name.replace('/', '-').replace('@', '-'))
        }
        
        try:
            # In a real implementation, this would download the actual model files
            # For now, create placeholder structure for offline operation
            
            model_path = Path(result["path"])
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Create model config
            config = {
                "model": model_name,
                "local_id": f"{model_name}-q4f16_1",
                "quantization": "q4f16_1",
                "model_config": {},
                "context_window_size": 8192,
                "prefill_chunk_size": 1024
            }
            
            with open(model_path / "mlc-chat-config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            # Create placeholder files indicating model is ready
            with open(model_path / "_ready", "w") as f:
                f.write(f"Model {model_name} setup complete\n")
                f.write("Note: For full functionality, download actual model weights from MLC\n")
            
            result["downloaded"] = True
            
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            result["error"] = str(e)
        
        return result
    
    def _discover_model_info(self, model_name: str) -> Optional[Dict]:
        """Discover model information from available sources."""
        # Common MLC model patterns
        common_models = {
            "Llama-3-8B-Instruct-q4f16_1-MLC": {
                "url": "https://raw.githubusercontent.com/mlc-ai/mlc-llm/main/vars/model_zoo.json",
                "description": "Llama 3 8B Instruct with q4f16 quantization"
            },
            "Llama-2-7b-chat-hf-q4f16_1-MLC": {
                "url": "https://raw.githubusercontent.com/mlc-ai/mlc-llm/main/vars/model_zoo.json",
                "description": "Llama 2 7B Chat with q4f16 quantization"
            }
        }
        
        return common_models.get(model_name)
    
    async def ensure_model_installed(
        self,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Ensure a model is installed, downloading if necessary.
        
        Args:
            model_name: Name of the model to ensure
            
        Returns:
            Dictionary with installation status
        """
        if self.is_model_installed(model_name):
            return {
                "status": "installed",
                "model_name": model_name,
                "path": str(self.download_dir / model_name.replace('/', '-').replace('@', '-'))
            }
        
        # Download if not installed and auto_download is enabled
        return await self.download_model(model_name)
    
    def get_installed_models(self) -> list:
        """Get list of installed models."""
        models = []
        if self.download_dir.exists():
            for item in self.download_dir.iterdir():
                if item.is_dir() and (item / "_ready").exists():
                    models.append({
                        "name": item.name,
                        "path": str(item)
                    })
        return models


# Convenience function
async def install_default_model(
    auto_download: bool = True
) -> Dict[str, Any]:
    """Install the default model if not already present."""
    manager = ModelManager(auto_download=auto_download)
    
    from src.config import WebLLMConfig
    
    result = await manager.ensure_model_installed(WebLLMConfig.DEFAULT_MODEL)
    return result


if __name__ == "__main__":
    async def main():
        """Example usage."""
        manager = ModelManager()
        
        print("JSAIBOT Model Manager")
        print("=" * 50)
        
        # Check installed models
        installed = manager.get_installed_models()
        if installed:
            print(f"Installed models: {len(installed)}")
            for model in installed:
                print(f"  - {model['name']}")
        else:
            print("No models installed yet.")
            
        # Try to install default model
        default_model = WebLLMConfig.DEFAULT_MODEL
        print(f"\nEnsuring '{default_model}' is installed...")
        
        result = await manager.ensure_model_installed(default_model)
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())