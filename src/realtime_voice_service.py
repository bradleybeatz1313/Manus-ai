import os
import json
import base64
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class RealtimeVoiceService:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.openai_ws = None
        self.session_id = None
        self.is_connected = False
        
        # Configuration
        self.voice = 'alloy'  # Options: alloy, echo, shimmer
        self.system_message = (
            "You are a helpful AI voice receptionist for a business. "
            "You can help customers with appointments, business hours, services, "
            "and general inquiries. Be professional, friendly, and concise. "
            "If you need to book an appointment, ask for the customer's name, "
            "preferred date and time, and contact information."
        )
        
        # Event handlers
        self.on_audio_response: Optional[Callable] = None
        self.on_text_response: Optional[Callable] = None
        self.on_session_update: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Log specific event types
        self.log_event_types = [
            'response.content.done',
            'rate_limits.updated', 
            'response.done',
            'input_audio_buffer.committed',
            'input_audio_buffer.speech_stopped',
            'input_audio_buffer.speech_started',
            'session.created',
            'session.updated',
            'error'
        ]
    
    async def connect_to_openai(self):
        """Connect to OpenAI Realtime API"""
        try:
            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.openai_ws = await websockets.connect(url, extra_headers=headers)
            self.is_connected = True
            logger.info("Connected to OpenAI Realtime API")
            
            # Send session configuration
            await self.configure_session()
            
            # Start listening for messages
            asyncio.create_task(self.listen_to_openai())
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI: {e}")
            self.is_connected = False
            if self.on_error:
                await self.on_error(f"OpenAI connection failed: {e}")
    
    async def configure_session(self):
        """Configure the OpenAI session with system message and voice settings"""
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self.system_message,
                "voice": self.voice,
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_ulaw",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": [],
                "tool_choice": "auto",
                "temperature": 0.8,
                "max_response_output_tokens": 4096
            }
        }
        
        await self.send_to_openai(session_update)
        logger.info("Session configured with OpenAI")
    
    async def send_to_openai(self, message: Dict[str, Any]):
        """Send message to OpenAI Realtime API"""
        if self.openai_ws and self.is_connected:
            try:
                await self.openai_ws.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to OpenAI: {e}")
                if self.on_error:
                    await self.on_error(f"Failed to send to OpenAI: {e}")
    
    async def listen_to_openai(self):
        """Listen for messages from OpenAI Realtime API"""
        try:
            async for message in self.openai_ws:
                await self.handle_openai_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error listening to OpenAI: {e}")
            self.is_connected = False
            if self.on_error:
                await self.on_error(f"OpenAI listening error: {e}")
    
    async def handle_openai_message(self, message: Dict[str, Any]):
        """Handle incoming messages from OpenAI"""
        event_type = message.get('type')
        
        # Log specific events
        if event_type in self.log_event_types:
            logger.info(f"OpenAI Event: {event_type}")
        
        # Handle different event types
        if event_type == 'session.created':
            self.session_id = message.get('session', {}).get('id')
            logger.info(f"Session created: {self.session_id}")
            if self.on_session_update:
                await self.on_session_update(message)
        
        elif event_type == 'session.updated':
            logger.info("Session updated")
            if self.on_session_update:
                await self.on_session_update(message)
        
        elif event_type == 'response.audio.delta':
            # Stream audio response back to caller
            audio_data = message.get('delta')
            if audio_data and self.on_audio_response:
                await self.on_audio_response(audio_data)
        
        elif event_type == 'response.text.delta':
            # Handle text response (for logging/debugging)
            text_data = message.get('delta')
            if text_data and self.on_text_response:
                await self.on_text_response(text_data)
        
        elif event_type == 'response.done':
            logger.info("Response completed")
        
        elif event_type == 'input_audio_buffer.speech_started':
            logger.info("User started speaking")
        
        elif event_type == 'input_audio_buffer.speech_stopped':
            logger.info("User stopped speaking")
        
        elif event_type == 'error':
            error_msg = message.get('error', {}).get('message', 'Unknown error')
            logger.error(f"OpenAI error: {error_msg}")
            if self.on_error:
                await self.on_error(f"OpenAI error: {error_msg}")
    
    async def send_audio(self, audio_data: str):
        """Send audio data to OpenAI for processing"""
        if not self.is_connected:
            logger.warning("Not connected to OpenAI, cannot send audio")
            return
        
        audio_message = {
            "type": "input_audio_buffer.append",
            "audio": audio_data
        }
        
        await self.send_to_openai(audio_message)
    
    async def commit_audio_buffer(self):
        """Commit the audio buffer to trigger processing"""
        if not self.is_connected:
            return
        
        commit_message = {
            "type": "input_audio_buffer.commit"
        }
        
        await self.send_to_openai(commit_message)
    
    async def create_response(self):
        """Trigger AI response generation"""
        if not self.is_connected:
            return
        
        response_message = {
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "Please respond to the user's input."
            }
        }
        
        await self.send_to_openai(response_message)
    
    async def send_text_message(self, text: str):
        """Send a text message to the AI (for testing purposes)"""
        if not self.is_connected:
            logger.warning("Not connected to OpenAI, cannot send text")
            return
        
        # Add user message
        user_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        
        await self.send_to_openai(user_message)
        
        # Trigger response
        await self.create_response()
    
    async def interrupt_response(self):
        """Interrupt the current AI response"""
        if not self.is_connected:
            return
        
        interrupt_message = {
            "type": "response.cancel"
        }
        
        await self.send_to_openai(interrupt_message)
    
    async def clear_audio_buffer(self):
        """Clear the input audio buffer"""
        if not self.is_connected:
            return
        
        clear_message = {
            "type": "input_audio_buffer.clear"
        }
        
        await self.send_to_openai(clear_message)
    
    async def update_session(self, instructions: str = None, voice: str = None):
        """Update session configuration"""
        if not self.is_connected:
            return
        
        session_data = {}
        
        if instructions:
            session_data["instructions"] = instructions
        
        if voice:
            session_data["voice"] = voice
        
        if session_data:
            update_message = {
                "type": "session.update",
                "session": session_data
            }
            
            await self.send_to_openai(update_message)
    
    async def disconnect(self):
        """Disconnect from OpenAI Realtime API"""
        if self.openai_ws:
            await self.openai_ws.close()
            self.is_connected = False
            logger.info("Disconnected from OpenAI Realtime API")
    
    def set_system_message(self, message: str):
        """Update the system message"""
        self.system_message = message
    
    def set_voice(self, voice: str):
        """Update the AI voice (alloy, echo, shimmer)"""
        if voice in ['alloy', 'echo', 'shimmer']:
            self.voice = voice
        else:
            logger.warning(f"Invalid voice: {voice}. Using default: alloy")
    
    def set_audio_response_handler(self, handler: Callable):
        """Set handler for audio responses"""
        self.on_audio_response = handler
    
    def set_text_response_handler(self, handler: Callable):
        """Set handler for text responses"""
        self.on_text_response = handler
    
    def set_session_update_handler(self, handler: Callable):
        """Set handler for session updates"""
        self.on_session_update = handler
    
    def set_error_handler(self, handler: Callable):
        """Set handler for errors"""
        self.on_error = handler

