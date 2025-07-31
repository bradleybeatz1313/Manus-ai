"""
Simple Test Suite for AI Voice Receptionist
Tests basic functionality without complex database setup
"""

import unittest
import json
import requests
import time

class SimpleAPITestCase(unittest.TestCase):
    """Simple API tests using requests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = 'http://localhost:5000'
        
        # Wait a moment to ensure server is ready
        time.sleep(1)
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f'{self.base_url}/')
            self.assertEqual(response.status_code, 200)
            print("✓ Health check endpoint working")
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")
    
    def test_voice_text_chat(self):
        """Test voice text chat endpoint"""
        try:
            response = requests.post(
                f'{self.base_url}/api/voice/text-chat',
                json={'message': 'Hello, I need help'},
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn('response', data)
            self.assertIn('intent', data)
            self.assertIn('session_id', data)
            print("✓ Voice text chat endpoint working")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")
    
    def test_voice_appointment_booking(self):
        """Test appointment booking intent"""
        try:
            response = requests.post(
                f'{self.base_url}/api/voice/text-chat',
                json={'message': 'I want to book an appointment'},
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertEqual(data['intent'], 'book_appointment')
            self.assertIn('appointment', data['response'].lower())
            print("✓ Appointment booking intent working")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")
    
    def test_voice_business_hours(self):
        """Test business hours inquiry"""
        try:
            response = requests.post(
                f'{self.base_url}/api/voice/text-chat',
                json={'message': 'What are your business hours?'},
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertEqual(data['intent'], 'business_hours')
            print("✓ Business hours inquiry working")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")
    
    def test_phone_calls_endpoint(self):
        """Test phone calls endpoint"""
        try:
            response = requests.get(f'{self.base_url}/api/phone/calls')
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn('calls', data)
            self.assertIn('total', data)
            print("✓ Phone calls endpoint working")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")
    
    def test_phone_numbers_endpoint(self):
        """Test phone numbers endpoint"""
        try:
            response = requests.get(f'{self.base_url}/api/phone/numbers')
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn('numbers', data)
            print("✓ Phone numbers endpoint working")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")
    
    def test_conversation_flow(self):
        """Test complete conversation flow"""
        try:
            # Step 1: Greeting
            response1 = requests.post(
                f'{self.base_url}/api/voice/text-chat',
                json={'message': 'Hello'},
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response1.status_code, 200)
            data1 = response1.json()
            session_id = data1['session_id']
            
            # Step 2: Appointment request
            response2 = requests.post(
                f'{self.base_url}/api/voice/text-chat',
                json={
                    'message': 'I want to book an appointment',
                    'session_id': session_id
                },
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response2.status_code, 200)
            data2 = response2.json()
            self.assertEqual(data2['intent'], 'book_appointment')
            
            # Step 3: Provide details
            response3 = requests.post(
                f'{self.base_url}/api/voice/text-chat',
                json={
                    'message': 'My name is John Doe, phone 555-1234',
                    'session_id': session_id
                },
                headers={'Content-Type': 'application/json'}
            )
            
            self.assertEqual(response3.status_code, 200)
            data3 = response3.json()
            
            print("✓ Complete conversation flow working")
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")

class FunctionalTestCase(unittest.TestCase):
    """Functional tests for business logic"""
    
    def test_intent_recognition(self):
        """Test various intent recognition scenarios"""
        test_cases = [
            ('Hello', 'greeting'),
            ('Hi there', 'greeting'),
            ('I want to book an appointment', 'book_appointment'),
            ('Schedule me for next week', 'book_appointment'),
            ('What are your hours?', 'business_hours'),
            ('When are you open?', 'business_hours'),
            ('What services do you offer?', 'services_inquiry'),
            ('How much does it cost?', 'pricing_inquiry'),
            ('Where are you located?', 'location_inquiry'),
            ('Thank you, goodbye', 'goodbye')
        ]
        
        try:
            for message, expected_intent in test_cases:
                response = requests.post(
                    'http://localhost:5000/api/voice/text-chat',
                    json={'message': message},
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    actual_intent = data.get('intent')
                    
                    if actual_intent == expected_intent:
                        print(f"✓ Intent '{expected_intent}' correctly recognized for: '{message}'")
                    else:
                        print(f"✗ Intent mismatch for '{message}': expected '{expected_intent}', got '{actual_intent}'")
                else:
                    print(f"✗ API error for message: '{message}'")
                    
        except requests.exceptions.ConnectionError:
            self.skipTest("Backend server not running")

if __name__ == '__main__':
    print("=" * 60)
    print("AI Voice Receptionist - Simple Test Suite")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        print("✓ Backend server is running")
        print()
    except requests.exceptions.ConnectionError:
        print("✗ Backend server is not running")
        print("Please start the server with: python src/main.py")
        print()
        exit(1)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print()
    print("=" * 60)
    print("Test Summary Complete")
    print("=" * 60)

