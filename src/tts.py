"""
Text-to-Speech Module for JSAIBOT.

Provides text-to-speech capability for voice responses to queries.
Uses pyttsx3 for offline text-to-speech conversion with optimized voices.
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
    
    Provides methods to convert text responses to spoken English with
    optimized voice selection for better quality output.
    """
    
    # Voice preference order (best quality first)
    PREFERRED_VOICE_KEYWORDS = [
        'david', 'zira', 'google', 'apple', 'samantha',
        'victoria', 'alex', 'fred', 'good voice', 'premium'
    ]
    
    def __init__(
        self,
        rate: int = 160,           # Slightly faster for natural conversation
        volume: float = 0.9,       # Slightly below max to avoid distortion
        voice_id: Optional[str] = None,
        optimize_for_conversation: bool = True
    ):
        """
        Initialize the TTS engine.
        
        Args:
            rate: Speech rate in words per minute (default: 160)
            volume: Volume level (0.0 to 1.0, default: 0.9)
            voice_id: Optional specific voice ID. Uses best available if not specified.
            optimize_for_conversation: Enable conversation-optimized settings
        """
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        self.optimize_for_conversation = optimize_for_conversation
        self.engine = None
        self._initialized = False
        self.selected_voice = None
        
    def _initialize_engine(self):
        """Initialize the pyttsx3 engine with optimized voice selection."""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            # Set base properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', max(0.0, min(1.0, self.volume)))
            
            # Get all available voices
            voices = self.engine.getProperty('voices')
            
            if not voices:
                logger.warning("No voices found on this system")
                self.selected_voice = None
            elif self.voice_id:
                # Use specified voice if provided
                for voice in voices:
                    if voice.id == self.voice_id:
                        self.engine.setProperty('voice', self.voice_id)
                        self.selected_voice = voice
                        break
                if not self.selected_voice:
                    logger.warning(f"Voice '{self.voice_id}' not found, using default")
            else:
                # Select best available voice for conversation
                self._select_best_voice(voices)
            
            self._initialized = True
            
        except ImportError:
            logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    def _select_best_voice(self, voices: List) -> None:
        """
        Select the best available voice for conversation.
        
        Prioritizes voices with keywords that indicate better quality.
        Falls back to first available voice if no match found.
        """
        # Try to find a preferred voice
        for keyword in self.PREFERRED_VOICE_KEYWORDS:
            for voice in voices:
                voice_name = voice.name.lower() if voice.name else ''
                if keyword in voice_name or (voice.languages and any(keyword in str(lang).lower() for lang in voice.languages)):
                    self.engine.setProperty('voice', voice.id)
                    self.selected_voice = voice
                    logger.info(f"Selected voice: {voice.name}")
                    return
        
        # Fallback to first available voice
        if voices:
            self.engine.setProperty('voice', voices[0].id)
            self.selected_voice = voices[0]
            logger.info(f"Using default voice: {voices[0].name}")
    
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
            # Remove any markdown formatting that might interfere with TTS
            clean_text = text.replace('*', '').replace('#', '').replace('_', '')
            
            self.engine.say(clean_text)
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
            engine.setProperty('volume', max(0.0, min(1.0, self.volume)))
            
            voices = engine.getProperty('voices')
            if voices:
                # Select best voice for conversation
                for keyword in self.PREFERRED_VOICE_KEYWORDS:
                    for voice in voices:
                        voice_name = voice.name.lower() if voice.name else ''
                        if keyword in voice_name:
                            engine.setProperty('voice', voice.id)
                            break
            
            def speak_sync():
                clean_text = text.replace('*', '').replace('#', '').replace('_', '')
                engine.say(clean_text)
                engine.runAndWait()
            
            try:
                await loop.run_in_executor(None, speak_sync)
                return True
            except Exception as e:
                logger.error(f"TTS async error: {e}")
                return False
        
        # Use existing engine if already initialized
        def speak_sync():
            clean_text = text.replace('*', '').replace('#', '').replace('_', '')
            self.engine.say(clean_text)
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
                    'name': voice.name or 'Unknown',
                    'languages': voice.languages,
                    'gender': voice.gender or 'Unknown'
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def set_rate(self, rate: int) -> None:
        """Set speech rate."""
        self.rate = max(50, min(400, rate))  # Clamp to reasonable range
        if self._initialized and self.engine:
            self.engine.setProperty('rate', self.rate)
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self._initialized and self.engine:
            self.engine.setProperty('volume', self.volume)
    
    def select_voice_by_name(self, name: str) -> bool:
        """
        Select a voice by name.
        
        Args:
            name: Partial or full name of the voice to select
            
        Returns:
            True if voice was selected successfully
        """
        if not self._initialized:
            self._initialize_engine()
        
        try:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if name.lower() in (voice.name or '').lower():
                    self.engine.setProperty('voice', voice.id)
                    self.selected_voice = voice
                    logger.info(f"Selected voice: {voice.name}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error selecting voice: {e}")
            return False


# Convenience function for quick usage
def speak_text(text: str, **kwargs) -> bool:
    """
    Quick text-to-speech without managing engine state.
    
    Args:
        text: Text to speak
        **kwargs: TTS constructor arguments
        
    Returns:
        True if successful
    """
    tts = TextToSpeech(**kwargs)
    return tts.speak(text)


if __name__ == "__main__":
    async def main():
        """Example usage."""
        print("JSAIBOT Text-to-Speech")
        print("=" * 40)
        
        try:
            tts = TextToSpeech(rate=165, volume=0.9)
            
            # List available voices
            voices = tts.get_available_voices()
            if voices:
                print(f"\nAvailable voices ({len(voices)}):")
                for i, voice in enumerate(voices):
                    print(f"  {i+1}. {voice['name']} (ID: {voice['id']})")
                
                # Try to select a premium-sounding voice
                print("\nTrying optimized voice selection...")
                selected = tts.get_available_voices()
                if selected:
                    print(f"Using voice: {selected[0]['name']}")
            
            # Speak some text
            test_text = "Hello! I am JSAIBOT, an AI chat system with local WebLLM integration and optimized TTS voices."
            print(f"\nSpeaking with optimized settings...")
            success = await tts.speak_async(test_text)
            
            if success:
                print("Speech completed successfully!")
            else:
                print("Failed to speak text.")
                
        except ImportError as e:
            print(f"Error: {e}")
            print("Install pyttsx3: pip install pyttsx3")
    
    asyncio.run(main())