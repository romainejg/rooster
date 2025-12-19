"""
Twilio SMS service for sending and receiving messages
"""
import os
from typing import Optional, Dict
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

class TwilioService:
    def __init__(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not account_sid or not auth_token:
            raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment variables")
        
        self.client = Client(account_sid, auth_token)
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.default_recipient = os.getenv('RECIPIENT_PHONE_NUMBER')
        
        if not self.from_number:
            raise ValueError("TWILIO_PHONE_NUMBER must be set in environment variables")
    
    def send_sms(self, message: str, to_number: Optional[str] = None) -> Dict[str, str]:
        """
        Send an SMS message via Twilio
        
        Args:
            message: The message text to send
            to_number: Recipient phone number (uses default if not provided)
        
        Returns:
            Dict with status and message_sid or error
        """
        recipient = to_number or self.default_recipient
        
        if not recipient:
            return {
                'status': 'error',
                'error': 'No recipient phone number provided'
            }
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient
            )
            
            return {
                'status': 'success',
                'message_sid': message_obj.sid,
                'to': recipient
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def create_webhook_response(self, response_text: str) -> str:
        """
        Create a TwiML response for Twilio webhook
        
        Args:
            response_text: The text to send back to the user
        
        Returns:
            TwiML XML string
        """
        response = MessagingResponse()
        response.message(response_text)
        return str(response)
    
    def parse_incoming_message(self, request_data: Dict) -> Dict[str, str]:
        """
        Parse incoming webhook request from Twilio
        
        Args:
            request_data: The request form data from Twilio
        
        Returns:
            Dict with from_number, to_number, and message_body
        """
        return {
            'from_number': request_data.get('From', ''),
            'to_number': request_data.get('To', ''),
            'message_body': request_data.get('Body', ''),
            'message_sid': request_data.get('MessageSid', '')
        }
