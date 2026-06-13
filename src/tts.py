"""
Text-to-Speech Module for JSAIBOT.

Provides text-to-speech capability for voice responses to queries.
Uses pyttsx3 for offline text-to-speech conversion.
"""

import asyncio
import logging
import os
import sys
from typing import Optional, List

logger = logging.getLogger(__name__)


class TextToSpeech:
    """
    Text-to-Speech engine using pyttsx3 for offline speech synthesis.
    
    Provides methods to convert text responses to spoken English.
    """
    
    def __init__(
        self,
        rate: int = 150,
        volume: float = 1.0,
        voice_id: Optional[str] = None
    ):
        """
        Initialize the TTS engine.
        
        Args:
            rate: Speech rate in words per minute (default: 150)
            volume: Volume level (0.0 to 1.0, default: 1.0)
            voice_id: Optional specific voice ID. Uses default if not specified.
        """
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        self.engine = None
        self._initialized = False
        
    def _initialize_engine(self):
        """Initialize the pyttsx3 engine."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice_id:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice.id == self.voice_id:
                        self.engine.setProperty('voice', self.voice_id)
                        break
            
            self._initialized = True
        except ImportError:
            logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            raise
    
    def speak(self, text: str) -> bool:
        """
        Speak the given text.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if speech was initiated successfully
        """
        if not self._initialized:
            self._initialize_engine()
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    async def speak_async(self, text: str) -> bool:
        """
        Speak the given text asynchronously.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if speech was initiated successfully
        """
        loop = asyncio.get_event_loop()
        
        if not self._initialized:
            # Create a new engine instance for async operation
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)
            
            if self.voice_id:
                voices = engine.getProperty('voices')
                for voice in voices:
                    if voice.id == self.voice_id:
                        engine.setProperty('voice', self.voice_id)
                        break
            
            def speak_sync():
                engine.say(text)
                engine.runAndWait()
            
            try:
                await loop.run_in_executor(None, speak_sync)
                return True
            except Exception as e:
                logger.error(f"TTS async error: {e}")
                return False
        
        # Use existing engine if already initialized
        def speak_sync():
            self.engine.say(text)
            self.engine.runAndWait()
        
        try:
            await loop.run_in_executor(None, speak_sync)
            return True
        except Exception as e:
            logger.error(f"TTS async error: {e}")
            return False
    
    def get_available_voices(self) -> List[dict]:
        """
        Get list of available voices on the system.
        
        Returns:
            List of dictionaries with voice information
        """
        if not self._initialized:
            self._initialize_engine()
        
        try:
            voices = self.engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def set_rate(self, rate: int) -> None:
        """Set speech rate."""
        self.rate = rate
        if self._initialized and self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self._initialized and self.engine:
            self.engine.setProperty('volume', self.volume)


# Convenience function for quick usage
def speak_text(text: str) -> bool:
    """
    Quick text-to-speech without managing engine state.
    
    Args:
        text: Text to speak
        
    Returns:
        True if successful
    """
    tts = TextToSpeech()
    return tts.speak(text)


if __name__ == "__main__":
    async def main():
        """Example usage."""
        print("JSAIBOT Text-to-Speech")
        print("=" * 40)
        
        try:
            tts = TextToSpeech(rate=160, volume=0.8)
            
            # List available voices
            voices = tts.get_available_voices()
            if voices:
                print(f"\nAvailable voices ({len(voices)}):")
                for voice in voices:
                    print(f"  - {voice['name']} (ID: {voice['id']})")
            
            # Speak some text
            test_text = "Hello! I am JSAIBOT, an AI chat system with local WebLLM integration."
            print(f"\nSpeaking: {test_text}")
            success = await tts.speak_async(test_text)
            
            if success:
                print("Speech completed successfully!")
            else:
                print("Failed to speak text.")
                
        except ImportError as e:
            print(f"Error: {e}")
            print("Install pyttsx3: pip install pyttsx3")
    
    asyncio.run(main())