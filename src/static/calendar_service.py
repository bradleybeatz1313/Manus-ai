"""
Calendar Service
Handles calendar integration for appointment scheduling
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.models.call import BusinessConfig

class CalendarService:
    def __init__(self):
        """Initialize the Calendar Service"""
        self.google_calendar_api_key = None
        self.google_calendar_id = None
        self.outlook_access_token = None
        
        # Load configuration from database
        self._load_config()
    
    def _load_config(self):
        """Load calendar configuration from database"""
        self.google_calendar_api_key = BusinessConfig.get_config('google_calendar_api_key')
        self.google_calendar_id = BusinessConfig.get_config('google_calendar_id')
        self.outlook_access_token = BusinessConfig.get_config('outlook_access_token')
    
    def get_available_slots(self, date_start: str, date_end: str, duration_minutes: int = 60) -> List[Dict]:
        """
        Get available appointment slots for a date range
        
        Args:
            date_start: Start date in YYYY-MM-DD format
            date_end: End date in YYYY-MM-DD format
            duration_minutes: Duration of appointment in minutes
        
        Returns:
            List of available time slots
        """
        try:
            # Get business hours configuration
            business_hours = BusinessConfig.get_config('business_hours', 'Monday-Friday 9AM-6PM')
            
            # Parse business hours (simplified implementation)
            available_slots = []
            
            # Generate time slots based on business hours
            start_date = datetime.strptime(date_start, '%Y-%m-%d')
            end_date = datetime.strptime(date_end, '%Y-%m-%d')
            
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends (simplified - should be configurable)
                if current_date.weekday() < 6:  # Monday = 0, Sunday = 6
                    # Generate hourly slots from 9 AM to 5 PM
                    for hour in range(9, 17):
                        slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                        
                        # Check if slot is available (not booked)
                        if self._is_slot_available(slot_time, duration_minutes):
                            available_slots.append({
                                'datetime': slot_time.isoformat(),
                                'date': slot_time.strftime('%Y-%m-%d'),
                                'time': slot_time.strftime('%H:%M'),
                                'duration_minutes': duration_minutes,
                                'available': True
                            })
                
                current_date += timedelta(days=1)
            
            return available_slots
        
        except Exception as e:
            print(f"Error getting available slots: {str(e)}")
            return []
    
    def _is_slot_available(self, slot_time: datetime, duration_minutes: int) -> bool:
        """
        Check if a time slot is available (not conflicting with existing appointments)
        
        Args:
            slot_time: The datetime of the slot to check
            duration_minutes: Duration of the appointment
        
        Returns:
            True if slot is available, False otherwise
        """
        try:
            # Check against existing appointments in database
            from src.models.call import Appointment
            
            slot_end = slot_time + timedelta(minutes=duration_minutes)
            
            # Query for conflicting appointments
            conflicting_appointments = Appointment.query.filter(
                Appointment.appointment_date == slot_time.date(),
                Appointment.status.in_(['scheduled', 'confirmed'])
            ).all()
            
            for appointment in conflicting_appointments:
                # Combine date and time for comparison
                appointment_datetime = datetime.combine(
                    appointment.appointment_date,
                    appointment.appointment_time
                )
                appointment_end = appointment_datetime + timedelta(minutes=appointment.duration_minutes)
                
                # Check for overlap
                if (slot_time < appointment_end and slot_end > appointment_datetime):
                    return False
            
            # If using external calendar, check against it too
            if self.google_calendar_api_key and self.google_calendar_id:
                return self._check_google_calendar_availability(slot_time, duration_minutes)
            
            return True
        
        except Exception as e:
            print(f"Error checking slot availability: {str(e)}")
            return False
    
    def _check_google_calendar_availability(self, slot_time: datetime, duration_minutes: int) -> bool:
        """
        Check availability against Google Calendar
        
        Args:
            slot_time: The datetime of the slot to check
            duration_minutes: Duration of the appointment
        
        Returns:
            True if slot is available, False otherwise
        """
        try:
            if not self.google_calendar_api_key or not self.google_calendar_id:
                return True  # If not configured, assume available
            
            # Google Calendar API endpoint
            url = f"https://www.googleapis.com/calendar/v3/calendars/{self.google_calendar_id}/events"
            
            # Time range for checking conflicts
            time_min = slot_time.isoformat() + 'Z'
            time_max = (slot_time + timedelta(minutes=duration_minutes)).isoformat() + 'Z'
            
            params = {
                'key': self.google_calendar_api_key,
                'timeMin': time_min,
                'timeMax': time_max,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                events = response.json().get('items', [])
                return len(events) == 0  # Available if no events found
            else:
                print(f"Google Calendar API error: {response.status_code}")
                return True  # Assume available if API fails
        
        except Exception as e:
            print(f"Error checking Google Calendar: {str(e)}")
            return True
    
    def book_appointment(self, appointment_data: Dict) -> Dict[str, Any]:
        """
        Book an appointment in the calendar system
        
        Args:
            appointment_data: Dictionary containing appointment details
        
        Returns:
            Dictionary with booking result
        """
        try:
            # Create appointment in database (already handled in voice_api.py)
            
            # If Google Calendar is configured, create event there too
            if self.google_calendar_api_key and self.google_calendar_id:
                google_result = self._create_google_calendar_event(appointment_data)
                if google_result.get('success'):
                    return {
                        'success': True,
                        'message': 'Appointment booked successfully',
                        'calendar_event_id': google_result.get('event_id')
                    }
            
            return {
                'success': True,
                'message': 'Appointment booked successfully (local only)'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error booking appointment: {str(e)}'
            }
    
    def _create_google_calendar_event(self, appointment_data: Dict) -> Dict[str, Any]:
        """
        Create an event in Google Calendar
        
        Args:
            appointment_data: Appointment details
        
        Returns:
            Dictionary with creation result
        """
        try:
            url = f"https://www.googleapis.com/calendar/v3/calendars/{self.google_calendar_id}/events"
            
            # Prepare event data
            start_datetime = datetime.combine(
                datetime.strptime(appointment_data['date'], '%Y-%m-%d').date(),
                datetime.strptime(appointment_data['time'], '%H:%M').time()
            )
            end_datetime = start_datetime + timedelta(minutes=appointment_data.get('duration', 60))
            
            event_data = {
                'summary': f"Appointment - {appointment_data.get('service', 'Service')}",
                'description': f"Customer: {appointment_data.get('name')}\nPhone: {appointment_data.get('phone')}\nService: {appointment_data.get('service')}",
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York'  # Should be configurable
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York'
                },
                'attendees': [
                    {
                        'email': appointment_data.get('email', ''),
                        'displayName': appointment_data.get('name', '')
                    }
                ]
            }
            
            headers = {
                'Authorization': f'Bearer {self.google_calendar_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json=event_data)
            
            if response.status_code == 200:
                event = response.json()
                return {
                    'success': True,
                    'event_id': event.get('id')
                }
            else:
                print(f"Google Calendar event creation failed: {response.status_code}")
                return {'success': False}
        
        except Exception as e:
            print(f"Error creating Google Calendar event: {str(e)}")
            return {'success': False}
    
    def cancel_appointment(self, appointment_id: int, calendar_event_id: str = None) -> Dict[str, Any]:
        """
        Cancel an appointment
        
        Args:
            appointment_id: Database appointment ID
            calendar_event_id: External calendar event ID
        
        Returns:
            Dictionary with cancellation result
        """
        try:
            # Update appointment status in database
            from src.models.call import Appointment, db
            
            appointment = Appointment.query.get(appointment_id)
            if appointment:
                appointment.status = 'cancelled'
                appointment.updated_at = datetime.utcnow()
                db.session.commit()
            
            # Cancel in Google Calendar if event ID provided
            if calendar_event_id and self.google_calendar_api_key and self.google_calendar_id:
                self._cancel_google_calendar_event(calendar_event_id)
            
            return {
                'success': True,
                'message': 'Appointment cancelled successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error cancelling appointment: {str(e)}'
            }
    
    def _cancel_google_calendar_event(self, event_id: str) -> bool:
        """
        Cancel an event in Google Calendar
        
        Args:
            event_id: Google Calendar event ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"https://www.googleapis.com/calendar/v3/calendars/{self.google_calendar_id}/events/{event_id}"
            
            headers = {
                'Authorization': f'Bearer {self.google_calendar_api_key}'
            }
            
            response = requests.delete(url, headers=headers)
            return response.status_code == 204
        
        except Exception as e:
            print(f"Error cancelling Google Calendar event: {str(e)}")
            return False

