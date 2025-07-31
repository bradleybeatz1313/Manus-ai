"""
Natural Language Understanding Service
Handles intent recognition, entity extraction, and conversation understanding
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from datetime import datetime, timedelta

class NLUService:
    def __init__(self):
        """Initialize the NLU Service with OpenAI client"""
        self.client = OpenAI()
        
        # Define common intents and their patterns
        self.intent_patterns = {
            'greeting': [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\bhow are you\b',
                r'\bgreetings\b'
            ],
            'appointment_booking': [
                r'\b(book|schedule|make|set up|arrange)\b.*\b(appointment|meeting|consultation)\b',
                r'\bi (want|need|would like) to (book|schedule|make)\b',
                r'\bcan i (book|schedule|make)\b',
                r'\bavailable (times|slots|appointments)\b'
            ],
            'appointment_cancel': [
                r'\b(cancel|reschedule|change|move)\b.*\b(appointment|meeting)\b',
                r'\bi need to (cancel|reschedule|change)\b',
                r'\bcancel my (appointment|meeting)\b'
            ],
            'business_hours': [
                r'\b(hours|open|close|operating hours|business hours)\b',
                r'\bwhen (are you|do you) (open|close)\b',
                r'\bwhat time (do you|are you) (open|close)\b'
            ],
            'location': [
                r'\b(where|location|address|directions)\b',
                r'\bhow do i get to\b',
                r'\bwhere are you located\b'
            ],
            'services': [
                r'\b(services|what do you do|what do you offer)\b',
                r'\bwhat (services|treatments|procedures)\b',
                r'\btell me about your (services|offerings)\b'
            ],
            'pricing': [
                r'\b(price|cost|fee|charge|rate|pricing)\b',
                r'\bhow much (does|do|is|are)\b',
                r'\bwhat (does|do) (it|this|that) cost\b'
            ],
            'contact': [
                r'\b(phone|email|contact|reach)\b',
                r'\bhow can i (contact|reach)\b',
                r'\bcontact (information|details)\b'
            ],
            'goodbye': [
                r'\b(goodbye|bye|see you|talk to you later|have a good day)\b',
                r'\bthanks?\s*(bye|goodbye)?\b',
                r'\bi have to go\b'
            ]
        }
        
        # Common entities patterns
        self.entity_patterns = {
            'time': [
                r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b',
                r'\b(\d{1,2})\s*(am|pm)\b',
                r'\b(morning|afternoon|evening|noon)\b'
            ],
            'date': [
                r'\b(today|tomorrow|yesterday)\b',
                r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
                r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\b'
            ],
            'name': [
                r'\bmy name is\s+([A-Za-z\s]+)\b',
                r'\bi\'m\s+([A-Za-z\s]+)\b',
                r'\bthis is\s+([A-Za-z\s]+)\b'
            ],
            'phone': [
                r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',
                r'\b(\(\d{3}\)\s*\d{3}[-.\s]?\d{4})\b'
            ],
            'email': [
                r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
            ]
        }
    
    def analyze_intent(self, text: str) -> Dict[str, any]:
        """
        Analyze the intent of the user's message using pattern matching and AI
        
        Args:
            text: User's input text
        
        Returns:
            Dictionary containing intent, confidence, and extracted entities
        """
        text_lower = text.lower()
        
        # First try pattern matching for quick common intents
        pattern_intent = self._pattern_based_intent(text_lower)
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Use AI for more complex intent analysis if pattern matching is uncertain
        if pattern_intent['confidence'] < 0.7:
            ai_intent = self._ai_based_intent(text)
            if ai_intent['confidence'] > pattern_intent['confidence']:
                pattern_intent = ai_intent
        
        return {
            'intent': pattern_intent['intent'],
            'confidence': pattern_intent['confidence'],
            'entities': entities,
            'original_text': text
        }
    
    def _pattern_based_intent(self, text: str) -> Dict[str, any]:
        """
        Use pattern matching to determine intent
        
        Args:
            text: Lowercase user input text
        
        Returns:
            Dictionary with intent and confidence score
        """
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = 0.8  # High confidence for pattern matches
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
        
        return {
            'intent': best_intent,
            'confidence': best_confidence
        }
    
    def _ai_based_intent(self, text: str) -> Dict[str, any]:
        """
        Use OpenAI to analyze intent for complex cases
        
        Args:
            text: User input text
        
        Returns:
            Dictionary with intent and confidence score
        """
        try:
            prompt = f"""
            Analyze the following customer message and determine the intent. 
            Choose from these intents: greeting, appointment_booking, appointment_cancel, 
            business_hours, location, services, pricing, contact, goodbye, unknown.
            
            Customer message: "{text}"
            
            Respond with only the intent name and confidence (0.0-1.0) in this format:
            intent: <intent_name>
            confidence: <confidence_score>
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the response
            intent_match = re.search(r'intent:\s*(\w+)', result)
            confidence_match = re.search(r'confidence:\s*([\d.]+)', result)
            
            intent = intent_match.group(1) if intent_match else 'unknown'
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            
            return {
                'intent': intent,
                'confidence': confidence
            }
        
        except Exception as e:
            print(f"Error in AI-based intent analysis: {str(e)}")
            return {
                'intent': 'unknown',
                'confidence': 0.0
            }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from the text using pattern matching
        
        Args:
            text: User input text
        
        Returns:
            Dictionary of entity types and their values
        """
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    if entity_type == 'name':
                        # For names, extract the captured group
                        matches.extend([match for match in found if isinstance(match, str)])
                    else:
                        matches.extend(found)
            
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def get_response_template(self, intent: str, entities: Dict = None) -> str:
        """
        Get appropriate response template based on intent
        
        Args:
            intent: Detected intent
            entities: Extracted entities
        
        Returns:
            Response template string
        """
        templates = {
            'greeting': "Hello! Thank you for calling. How can I help you today?",
            'appointment_booking': "I'd be happy to help you schedule an appointment. What type of service are you looking for, and when would you prefer to come in?",
            'appointment_cancel': "I can help you with that. Can you please provide your name and the date of your current appointment?",
            'business_hours': "Our business hours are Monday through Friday, 9 AM to 6 PM, and Saturday 9 AM to 3 PM. We're closed on Sundays.",
            'location': "We're located at [BUSINESS_ADDRESS]. Would you like me to provide directions or send you our location details?",
            'services': "We offer a variety of services including [LIST_SERVICES]. Would you like more information about any specific service?",
            'pricing': "Our pricing varies depending on the service. Could you tell me which specific service you're interested in so I can provide accurate pricing information?",
            'contact': "You can reach us at [PHONE_NUMBER] or email us at [EMAIL_ADDRESS]. Is there anything specific you'd like to know?",
            'goodbye': "Thank you for calling! Have a wonderful day, and we look forward to serving you soon.",
            'unknown': "I'm sorry, I didn't quite understand that. Could you please rephrase your question or let me know how I can help you?"
        }
        
        return templates.get(intent, templates['unknown'])
    
    def extract_appointment_details(self, text: str) -> Dict[str, any]:
        """
        Extract specific appointment-related details from text
        
        Args:
            text: User input text
        
        Returns:
            Dictionary with appointment details
        """
        details = {
            'service_type': None,
            'preferred_date': None,
            'preferred_time': None,
            'duration': None,
            'special_requests': None
        }
        
        # Extract service type
        service_keywords = ['consultation', 'checkup', 'cleaning', 'treatment', 'therapy', 'massage', 'haircut']
        for service in service_keywords:
            if service in text.lower():
                details['service_type'] = service
                break
        
        # Extract date and time from entities
        entities = self._extract_entities(text)
        if 'date' in entities:
            details['preferred_date'] = entities['date'][0]
        if 'time' in entities:
            details['preferred_time'] = entities['time'][0]
        
        return details

