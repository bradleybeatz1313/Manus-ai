"""
CRM Service
Handles CRM integration for lead management and customer data
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.models.call import BusinessConfig

class CRMService:
    def __init__(self):
        """Initialize the CRM Service"""
        self.salesforce_access_token = None
        self.salesforce_instance_url = None
        self.hubspot_api_key = None
        self.zoho_access_token = None
        
        # Load configuration from database
        self._load_config()
    
    def _load_config(self):
        """Load CRM configuration from database"""
        self.salesforce_access_token = BusinessConfig.get_config('salesforce_access_token')
        self.salesforce_instance_url = BusinessConfig.get_config('salesforce_instance_url')
        self.hubspot_api_key = BusinessConfig.get_config('hubspot_api_key')
        self.zoho_access_token = BusinessConfig.get_config('zoho_access_token')
    
    def create_lead(self, lead_data: Dict) -> Dict[str, Any]:
        """
        Create a new lead in the configured CRM system
        
        Args:
            lead_data: Dictionary containing lead information
        
        Returns:
            Dictionary with creation result
        """
        try:
            # Try different CRM systems based on configuration
            if self.hubspot_api_key:
                return self._create_hubspot_contact(lead_data)
            elif self.salesforce_access_token:
                return self._create_salesforce_lead(lead_data)
            elif self.zoho_access_token:
                return self._create_zoho_lead(lead_data)
            else:
                # No CRM configured, just return success
                return {
                    'success': True,
                    'message': 'Lead data captured (no CRM integration configured)',
                    'lead_id': None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating lead: {str(e)}',
                'lead_id': None
            }
    
    def _create_hubspot_contact(self, lead_data: Dict) -> Dict[str, Any]:
        """
        Create a contact in HubSpot
        
        Args:
            lead_data: Lead information
        
        Returns:
            Dictionary with creation result
        """
        try:
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            
            # Map lead data to HubSpot properties
            properties = {
                'firstname': lead_data.get('first_name', ''),
                'lastname': lead_data.get('last_name', ''),
                'email': lead_data.get('email', ''),
                'phone': lead_data.get('phone', ''),
                'company': lead_data.get('company', ''),
                'lifecyclestage': 'lead',
                'lead_source': 'AI Voice Receptionist',
                'hs_lead_status': 'NEW'
            }
            
            # Add custom properties
            if lead_data.get('service_interest'):
                properties['service_interest'] = lead_data['service_interest']
            if lead_data.get('notes'):
                properties['notes_last_contacted'] = lead_data['notes']
            
            headers = {
                'Authorization': f'Bearer {self.hubspot_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'properties': properties
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 201:
                contact = response.json()
                return {
                    'success': True,
                    'message': 'Contact created in HubSpot',
                    'lead_id': contact.get('id')
                }
            else:
                return {
                    'success': False,
                    'message': f'HubSpot API error: {response.status_code}',
                    'lead_id': None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating HubSpot contact: {str(e)}',
                'lead_id': None
            }
    
    def _create_salesforce_lead(self, lead_data: Dict) -> Dict[str, Any]:
        """
        Create a lead in Salesforce
        
        Args:
            lead_data: Lead information
        
        Returns:
            Dictionary with creation result
        """
        try:
            url = f"{self.salesforce_instance_url}/services/data/v52.0/sobjects/Lead/"
            
            # Map lead data to Salesforce fields
            lead_record = {
                'FirstName': lead_data.get('first_name', ''),
                'LastName': lead_data.get('last_name', 'Unknown'),
                'Email': lead_data.get('email', ''),
                'Phone': lead_data.get('phone', ''),
                'Company': lead_data.get('company', 'Unknown'),
                'LeadSource': 'AI Voice Receptionist',
                'Status': 'Open - Not Contacted'
            }
            
            # Add custom fields
            if lead_data.get('service_interest'):
                lead_record['Service_Interest__c'] = lead_data['service_interest']
            if lead_data.get('notes'):
                lead_record['Description'] = lead_data['notes']
            
            headers = {
                'Authorization': f'Bearer {self.salesforce_access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json=lead_record)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'message': 'Lead created in Salesforce',
                    'lead_id': result.get('id')
                }
            else:
                return {
                    'success': False,
                    'message': f'Salesforce API error: {response.status_code}',
                    'lead_id': None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating Salesforce lead: {str(e)}',
                'lead_id': None
            }
    
    def _create_zoho_lead(self, lead_data: Dict) -> Dict[str, Any]:
        """
        Create a lead in Zoho CRM
        
        Args:
            lead_data: Lead information
        
        Returns:
            Dictionary with creation result
        """
        try:
            url = "https://www.zohoapis.com/crm/v2/Leads"
            
            # Map lead data to Zoho fields
            lead_record = {
                'First_Name': lead_data.get('first_name', ''),
                'Last_Name': lead_data.get('last_name', 'Unknown'),
                'Email': lead_data.get('email', ''),
                'Phone': lead_data.get('phone', ''),
                'Company': lead_data.get('company', 'Unknown'),
                'Lead_Source': 'AI Voice Receptionist',
                'Lead_Status': 'Not Contacted'
            }
            
            # Add custom fields
            if lead_data.get('service_interest'):
                lead_record['Service_Interest'] = lead_data['service_interest']
            if lead_data.get('notes'):
                lead_record['Description'] = lead_data['notes']
            
            headers = {
                'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'data': [lead_record]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 201:
                result = response.json()
                if result.get('data') and len(result['data']) > 0:
                    return {
                        'success': True,
                        'message': 'Lead created in Zoho CRM',
                        'lead_id': result['data'][0].get('details', {}).get('id')
                    }
            
            return {
                'success': False,
                'message': f'Zoho CRM API error: {response.status_code}',
                'lead_id': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating Zoho lead: {str(e)}',
                'lead_id': None
            }
    
    def update_lead(self, lead_id: str, update_data: Dict) -> Dict[str, Any]:
        """
        Update an existing lead in the CRM system
        
        Args:
            lead_id: CRM lead/contact ID
            update_data: Data to update
        
        Returns:
            Dictionary with update result
        """
        try:
            if self.hubspot_api_key:
                return self._update_hubspot_contact(lead_id, update_data)
            elif self.salesforce_access_token:
                return self._update_salesforce_lead(lead_id, update_data)
            elif self.zoho_access_token:
                return self._update_zoho_lead(lead_id, update_data)
            else:
                return {
                    'success': True,
                    'message': 'No CRM integration configured'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating lead: {str(e)}'
            }
    
    def _update_hubspot_contact(self, contact_id: str, update_data: Dict) -> Dict[str, Any]:
        """Update HubSpot contact"""
        try:
            url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
            
            properties = {}
            if update_data.get('status'):
                properties['hs_lead_status'] = update_data['status']
            if update_data.get('notes'):
                properties['notes_last_contacted'] = update_data['notes']
            if update_data.get('appointment_booked'):
                properties['lifecyclestage'] = 'opportunity'
            
            headers = {
                'Authorization': f'Bearer {self.hubspot_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'properties': properties
            }
            
            response = requests.patch(url, headers=headers, json=payload)
            
            return {
                'success': response.status_code == 200,
                'message': 'HubSpot contact updated' if response.status_code == 200 else f'Update failed: {response.status_code}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating HubSpot contact: {str(e)}'
            }
    
    def _update_salesforce_lead(self, lead_id: str, update_data: Dict) -> Dict[str, Any]:
        """Update Salesforce lead"""
        try:
            url = f"{self.salesforce_instance_url}/services/data/v52.0/sobjects/Lead/{lead_id}"
            
            update_record = {}
            if update_data.get('status'):
                update_record['Status'] = update_data['status']
            if update_data.get('notes'):
                update_record['Description'] = update_data['notes']
            
            headers = {
                'Authorization': f'Bearer {self.salesforce_access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(url, headers=headers, json=update_record)
            
            return {
                'success': response.status_code == 204,
                'message': 'Salesforce lead updated' if response.status_code == 204 else f'Update failed: {response.status_code}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating Salesforce lead: {str(e)}'
            }
    
    def _update_zoho_lead(self, lead_id: str, update_data: Dict) -> Dict[str, Any]:
        """Update Zoho CRM lead"""
        try:
            url = f"https://www.zohoapis.com/crm/v2/Leads/{lead_id}"
            
            update_record = {}
            if update_data.get('status'):
                update_record['Lead_Status'] = update_data['status']
            if update_data.get('notes'):
                update_record['Description'] = update_data['notes']
            
            headers = {
                'Authorization': f'Zoho-oauthtoken {self.zoho_access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'data': [update_record]
            }
            
            response = requests.put(url, headers=headers, json=payload)
            
            return {
                'success': response.status_code == 200,
                'message': 'Zoho lead updated' if response.status_code == 200 else f'Update failed: {response.status_code}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating Zoho lead: {str(e)}'
            }
    
    def search_contact(self, email: str = None, phone: str = None) -> Dict[str, Any]:
        """
        Search for existing contact in CRM
        
        Args:
            email: Email address to search
            phone: Phone number to search
        
        Returns:
            Dictionary with search result
        """
        try:
            if self.hubspot_api_key:
                return self._search_hubspot_contact(email, phone)
            elif self.salesforce_access_token:
                return self._search_salesforce_contact(email, phone)
            elif self.zoho_access_token:
                return self._search_zoho_contact(email, phone)
            else:
                return {
                    'found': False,
                    'contact': None,
                    'message': 'No CRM integration configured'
                }
        
        except Exception as e:
            return {
                'found': False,
                'contact': None,
                'message': f'Error searching contact: {str(e)}'
            }
    
    def _search_hubspot_contact(self, email: str = None, phone: str = None) -> Dict[str, Any]:
        """Search HubSpot contact"""
        try:
            if email:
                url = f"https://api.hubapi.com/crm/v3/objects/contacts/{email}?idProperty=email"
            elif phone:
                url = f"https://api.hubapi.com/crm/v3/objects/contacts/search"
                # HubSpot search by phone is more complex, simplified here
                return {'found': False, 'contact': None, 'message': 'Phone search not implemented for HubSpot'}
            else:
                return {'found': False, 'contact': None, 'message': 'No search criteria provided'}
            
            headers = {
                'Authorization': f'Bearer {self.hubspot_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                contact = response.json()
                return {
                    'found': True,
                    'contact': contact,
                    'message': 'Contact found in HubSpot'
                }
            else:
                return {
                    'found': False,
                    'contact': None,
                    'message': 'Contact not found in HubSpot'
                }
        
        except Exception as e:
            return {
                'found': False,
                'contact': None,
                'message': f'Error searching HubSpot: {str(e)}'
            }
    
    def _search_salesforce_contact(self, email: str = None, phone: str = None) -> Dict[str, Any]:
        """Search Salesforce contact"""
        # Simplified implementation - would need proper SOQL queries
        return {
            'found': False,
            'contact': None,
            'message': 'Salesforce search not implemented in this demo'
        }
    
    def _search_zoho_contact(self, email: str = None, phone: str = None) -> Dict[str, Any]:
        """Search Zoho CRM contact"""
        # Simplified implementation - would need proper search API calls
        return {
            'found': False,
            'contact': None,
            'message': 'Zoho search not implemented in this demo'
        }
    
    def get_crm_status(self) -> Dict[str, Any]:
        """
        Get the status of CRM integrations
        
        Returns:
            Dictionary with CRM integration status
        """
        status = {
            'hubspot': {
                'configured': bool(self.hubspot_api_key),
                'status': 'Connected' if self.hubspot_api_key else 'Not configured'
            },
            'salesforce': {
                'configured': bool(self.salesforce_access_token and self.salesforce_instance_url),
                'status': 'Connected' if (self.salesforce_access_token and self.salesforce_instance_url) else 'Not configured'
            },
            'zoho': {
                'configured': bool(self.zoho_access_token),
                'status': 'Connected' if self.zoho_access_token else 'Not configured'
            }
        }
        
        return status

