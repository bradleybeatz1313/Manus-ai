"""
Speech Service Module
Handles Speech-to-Text and Text-to-Speech functionality using OpenAI APIs
"""

import os
import io
import tempfile
from openai import OpenAI
from typing import Optional, Union

class SpeechService:
    def __init__(self):
        """Initialize the Speech Service with OpenAI client"""
        self.client = OpenAI()
    
    def speech_to_text(self, audio_file: Union[str, io.BytesIO], language: Optional[str] = None) -> str:
        """
        Convert speech audio to text using OpenAI Whisper API
        
        Args:
            audio_file: Path to audio file or BytesIO object containing audio data
            language: Optional language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            Transcribed text from the audio
        """
        try:
            # Handle different input types
            if isinstance(audio_file, str):
                # File path provided
                with open(audio_file, 'rb') as f:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        language=language
                    )
            elif isinstance(audio_file, io.BytesIO):
                # BytesIO object provided
                audio_file.seek(0)  # Reset to beginning
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            else:
                raise ValueError("audio_file must be a file path string or BytesIO object")
            
            return transcript.text
        
        except Exception as e:
            print(f"Error in speech-to-text conversion: {str(e)}")
            raise
    
    def text_to_speech(self, text: str, voice: str = "alloy", output_path: Optional[str] = None) -> Union[str, bytes]:
        """
        Convert text to speech using OpenAI TTS API
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            output_path: Optional path to save the audio file
        
        Returns:
            If output_path is provided, returns the path to the saved file
            Otherwise, returns the audio data as bytes
        """
        try:
            # Available voices: alloy, echo, fable, onyx, nova, shimmer
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if voice not in valid_voices:
                voice = "alloy"  # Default fallback
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            if output_path:
                # Save to file
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                # Return audio data as bytes
                return response.content
        
        except Exception as e:
            print(f"Error in text-to-speech conversion: {str(e)}")
            raise
    
    def get_available_voices(self) -> list:
        """
        Get list of available TTS voices
        
        Returns:
            List of available voice names
        """
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def validate_audio_format(self, file_path: str) -> bool:
        """
        Validate if the audio file format is supported
        
        Args:
            file_path: Path to the audio file
        
        Returns:
            True if format is supported, False otherwise
        """
        supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in supported_formats

