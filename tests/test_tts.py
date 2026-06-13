"""Tests for text-to-speech module."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestTextToSpeech:
    """Test cases for TextToSpeech class."""
    
    def test_init_with_defaults(self):
        """Test initializing TTS with default parameters."""
        # Skip if pyttsx3 not available (will fail in headless CI)
        try:
            import pyttsx3
            from tts import TextToSpeech
            
            tts = TextToSpeech()
            
            assert tts.rate == 160
            assert tts.volume == 0.9
        except ImportError:
            pytest.skip("pyttsx3 not installed")
    
    def test_init_with_custom_rate(self):
        """Test initializing TTS with custom rate."""
        try:
            import pyttsx3
            from tts import TextToSpeech
            
            tts = TextToSpeech(rate=200)
            
            assert tts.rate == 200
        except ImportError:
            pytest.skip("pyttsx3 not installed")
    
    def test_init_with_custom_volume(self):
        """Test initializing TTS with custom volume."""
        try:
            import pyttsx3
            from tts import TextToSpeech
            
            tts = TextToSpeech(volume=0.8)
            
            assert tts.volume == 0.8
        except ImportError:
            pytest.skip("pyttsx3 not installed")
    
    def test_set_rate(self):
        """Test setting rate after initialization."""
        try:
            import pyttsx3
            from tts import TextToSpeech
            
            tts = TextToSpeech()
            tts.set_rate(180)
            
            assert tts.rate == 180
        except ImportError:
            pytest.skip("pyttsx3 not installed")
    
    def test_set_volume(self):
        """Test setting volume after initialization."""
        try:
            import pyttsx3
            from tts import TextToSpeech
            
            tts = TextToSpeech()
            tts.set_volume(0.95)
            
            assert tts.volume == 0.95
        except ImportError:
            pytest.skip("pyttsx3 not installed")
    
    def test_set_rate_clamps_values(self):
        """Test that rate values are clamped to valid range."""
        try:
            import pyttsx3
            from tts import TextToSpeech
            
            tts = TextToSpeech()
            
            # Test lower bound
            tts.set_rate(10)
            assert tts.rate >= 50  # Should clamp to min
            
            # Test upper bound
            tts.set_rate(500)
            assert tts.rate <= 400  # Should clamp to max
        except ImportError:
            pytest.skip("pyttsx3 not installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])