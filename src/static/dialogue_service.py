"""
Dialogue Management Service
Manages conversation flow, context, and determines appropriate responses
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from openai import OpenAI
from src.services.nlu_service import NLUService

class DialogueState:
    """Represents the current state of a conversation"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_intent = None
        self.context = {}
        self.conversation_history = []
        self.user_info = {}
        self.appointment_details = {}
        self.last_activity = datetime.now()
        self.state = 'initial'  # initial, collecting_info, confirming, completed
    
    def add_turn(self, user_input: str, bot_response: str, intent: str = None):
        """Add a conversation turn to history"""
        turn = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'bot_response': bot_response,
            'intent': intent
        }
        self.conversation_history.append(turn)
        self.last_activity = datetime.now()
    
    def update_context(self, key: str, value: Any):
        """Update conversation context"""
        self.context[key] = value
    
    def get_context(self, key: str, default=None):
        """Get value from conversation context"""
        return self.context.get(key, default)

class DialogueService:
    def __init__(self):
        """Initialize the Dialogue Service"""
        self.client = OpenAI()
        self.nlu_service = NLUService()
        self.active_sessions = {}  # Store active conversation sessions
        
        # Business configuration (should be configurable per client)
        self.business_config = {
            'name': 'Your Business Name',
            'hours': 'Monday-Friday 9AM-6PM, Saturday 9AM-3PM',
            'address': '123 Main Street, City, State 12345',
            'phone': '(555) 123-4567',
            'email': 'info@yourbusiness.com',
            'services': ['Consultation', 'Treatment', 'Follow-up'],
            'booking_slots': self._generate_available_slots()
        }
    
    def process_message(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user message and generate appropriate response
        
        Args:
            user_input: User's message
            session_id: Optional session ID for conversation continuity
        
        Returns:
            Dictionary containing response and session information
        """
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = DialogueState(session_id)
        
        session = self.active_sessions[session_id]
        
        # Analyze user input
        nlu_result = self.nlu_service.analyze_intent(user_input)
        intent = nlu_result['intent']
        entities = nlu_result['entities']
        
        # Update session with current intent
        session.current_intent = intent
        
        # Generate response based on intent and current state
        response = self._generate_response(session, intent, entities, user_input)
        
        # Add turn to conversation history
        session.add_turn(user_input, response['message'], intent)
        
        return {
            'session_id': session_id,
            'response': response['message'],
            'intent': intent,
            'entities': entities,
            'state': session.state,
            'requires_action': response.get('requires_action', False),
            'action_type': response.get('action_type', None),
            'action_data': response.get('action_data', {})
        }
    
    def _generate_response(self, session: DialogueState, intent: str, entities: Dict, user_input: str) -> Dict[str, Any]:
        """
        Generate appropriate response based on intent and session state
        
        Args:
            session: Current dialogue session
            intent: Detected intent
            entities: Extracted entities
            user_input: Original user input
        
        Returns:
            Dictionary containing response message and any required actions
        """
        response = {
            'message': '',
            'requires_action': False,
            'action_type': None,
            'action_data': {}
        }
        
        if intent == 'greeting':
            response['message'] = f"Hello! Thank you for calling {self.business_config['name']}. How can I help you today?"
            session.state = 'initial'
        
        elif intent == 'appointment_booking':
            response = self._handle_appointment_booking(session, entities, user_input)
        
        elif intent == 'appointment_cancel':
            response = self._handle_appointment_cancellation(session, entities, user_input)
        
        elif intent == 'business_hours':
            response['message'] = f"Our business hours are {self.business_config['hours']}. Is there anything else I can help you with?"
        
        elif intent == 'location':
            response['message'] = f"We're located at {self.business_config['address']}. Would you like me to provide directions or any other information?"
        
        elif intent == 'services':
            services_list = ', '.join(self.business_config['services'])
            response['message'] = f"We offer the following services: {services_list}. Would you like more information about any specific service or would you like to schedule an appointment?"
        
        elif intent == 'pricing':
            response['message'] = "Our pricing varies depending on the specific service you're interested in. Could you tell me which service you'd like to know about, and I'll provide you with detailed pricing information?"
        
        elif intent == 'contact':
            response['message'] = f"You can reach us at {self.business_config['phone']} or email us at {self.business_config['email']}. Is there anything specific you'd like to know or discuss?"
        
        elif intent == 'goodbye':
            response['message'] = f"Thank you for calling {self.business_config['name']}! Have a wonderful day, and we look forward to serving you soon."
            session.state = 'completed'
        
        else:
            # Handle unknown intent or use AI for complex responses
            response = self._handle_complex_query(session, user_input)
        
        return response
    
    def _handle_appointment_booking(self, session: DialogueState, entities: Dict, user_input: str) -> Dict[str, Any]:
        """Handle appointment booking conversation flow"""
        response = {
            'message': '',
            'requires_action': False,
            'action_type': 'appointment_booking',
            'action_data': {}
        }
        
        # Extract appointment details from entities
        appointment_details = self.nlu_service.extract_appointment_details(user_input)
        
        # Update session with any new information
        for key, value in appointment_details.items():
            if value:
                session.appointment_details[key] = value
        
        # Extract user information from entities
        if 'name' in entities:
            session.user_info['name'] = entities['name'][0]
        if 'phone' in entities:
            session.user_info['phone'] = entities['phone'][0]
        if 'email' in entities:
            session.user_info['email'] = entities['email'][0]
        
        # Determine what information we still need
        missing_info = []
        if not session.user_info.get('name'):
            missing_info.append('name')
        if not session.user_info.get('phone'):
            missing_info.append('phone number')
        if not session.appointment_details.get('service_type'):
            missing_info.append('service type')
        if not session.appointment_details.get('preferred_date'):
            missing_info.append('preferred date')
        if not session.appointment_details.get('preferred_time'):
            missing_info.append('preferred time')
        
        if missing_info:
            # Ask for missing information
            if 'name' in missing_info:
                response['message'] = "I'd be happy to help you schedule an appointment. May I have your name please?"
            elif 'phone number' in missing_info:
                response['message'] = f"Thank you, {session.user_info.get('name', '')}. Could you please provide your phone number?"
            elif 'service type' in missing_info:
                services_list = ', '.join(self.business_config['services'])
                response['message'] = f"What type of service would you like to schedule? We offer: {services_list}."
            elif 'preferred date' in missing_info:
                response['message'] = "What date would you prefer for your appointment? I can check our availability."
            elif 'preferred time' in missing_info:
                response['message'] = "What time would work best for you? We have morning, afternoon, and early evening slots available."
            
            session.state = 'collecting_info'
        else:
            # All information collected, confirm appointment
            response = self._confirm_appointment(session)
        
        return response
    
    def _handle_appointment_cancellation(self, session: DialogueState, entities: Dict, user_input: str) -> Dict[str, Any]:
        """Handle appointment cancellation"""
        response = {
            'message': '',
            'requires_action': True,
            'action_type': 'appointment_cancel',
            'action_data': {}
        }
        
        # Extract user information
        if 'name' in entities:
            session.user_info['name'] = entities['name'][0]
        
        if not session.user_info.get('name'):
            response['message'] = "I can help you cancel your appointment. May I have your name please?"
            response['requires_action'] = False
        else:
            response['message'] = f"I'll help you cancel your appointment, {session.user_info['name']}. Let me look up your booking and process the cancellation."
            response['action_data'] = {'name': session.user_info['name']}
        
        return response
    
    def _confirm_appointment(self, session: DialogueState) -> Dict[str, Any]:
        """Confirm appointment details with user"""
        name = session.user_info.get('name', '')
        phone = session.user_info.get('phone', '')
        service = session.appointment_details.get('service_type', '')
        date = session.appointment_details.get('preferred_date', '')
        time = session.appointment_details.get('preferred_time', '')
        
        confirmation_message = f"""
        Perfect! Let me confirm your appointment details:
        
        Name: {name}
        Phone: {phone}
        Service: {service}
        Date: {date}
        Time: {time}
        
        Is this information correct? If yes, I'll book this appointment for you.
        """
        
        session.state = 'confirming'
        
        return {
            'message': confirmation_message.strip(),
            'requires_action': True,
            'action_type': 'appointment_confirm',
            'action_data': {
                'name': name,
                'phone': phone,
                'service': service,
                'date': date,
                'time': time
            }
        }
    
    def _handle_complex_query(self, session: DialogueState, user_input: str) -> Dict[str, Any]:
        """Handle complex queries using AI"""
        try:
            # Create context from business config and conversation history
            context = f"""
            You are an AI receptionist for {self.business_config['name']}.
            Business hours: {self.business_config['hours']}
            Location: {self.business_config['address']}
            Phone: {self.business_config['phone']}
            Email: {self.business_config['email']}
            Services: {', '.join(self.business_config['services'])}
            
            Recent conversation:
            {self._get_recent_conversation(session)}
            
            Customer query: {user_input}
            
            Provide a helpful, professional response as a receptionist would.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": context}],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                'message': response.choices[0].message.content.strip(),
                'requires_action': False
            }
        
        except Exception as e:
            print(f"Error in complex query handling: {str(e)}")
            return {
                'message': "I apologize, but I'm having trouble understanding your request. Could you please rephrase it or let me know how I can help you?",
                'requires_action': False
            }
    
    def _get_recent_conversation(self, session: DialogueState, num_turns: int = 3) -> str:
        """Get recent conversation history as string"""
        recent_turns = session.conversation_history[-num_turns:]
        conversation_text = ""
        for turn in recent_turns:
            conversation_text += f"User: {turn['user_input']}\nBot: {turn['bot_response']}\n"
        return conversation_text
    
    def _generate_available_slots(self) -> List[str]:
        """Generate available appointment slots (mock implementation)"""
        slots = []
        base_date = datetime.now() + timedelta(days=1)
        
        for day in range(7):  # Next 7 days
            current_date = base_date + timedelta(days=day)
            if current_date.weekday() < 6:  # Monday to Saturday
                for hour in [9, 10, 11, 14, 15, 16]:  # 9AM-11AM, 2PM-4PM
                    slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slots.append(slot_time.strftime("%Y-%m-%d %H:%M"))
        
        return slots
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a specific session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                'session_id': session_id,
                'state': session.state,
                'current_intent': session.current_intent,
                'user_info': session.user_info,
                'appointment_details': session.appointment_details,
                'conversation_length': len(session.conversation_history),
                'last_activity': session.last_activity.isoformat()
            }
        return None
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove old inactive sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.active_sessions.items():
            if session.last_activity < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

