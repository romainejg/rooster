"""
Webhook handler for Twilio SMS replies
Run this as a separate Flask app or integrate with your deployment
"""
from flask import Flask, request, Response
from twilio_service import TwilioService
from openai_service import OpenAIService
from conversation_store import ConversationStore
import os

app = Flask(__name__)

# Initialize services
try:
    twilio_service = TwilioService()
    openai_service = OpenAIService()
    conversation_store = ConversationStore()
except Exception as e:
    print(f"Error initializing services: {e}")
    twilio_service = None
    openai_service = None
    conversation_store = None

@app.route('/webhook/sms', methods=['POST'])
def handle_sms_webhook():
    """
    Handle incoming SMS messages from Twilio
    """
    if not all([twilio_service, openai_service, conversation_store]):
        return Response("Service not configured", status=500)
    
    try:
        # Parse incoming message
        message_data = twilio_service.parse_incoming_message(request.form)
        from_number = message_data['from_number']
        message_body = message_data['message_body']
        message_sid = message_data['message_sid']
        
        # Store incoming message
        conversation_store.add_message(
            phone_number=from_number,
            direction='incoming',
            message_text=message_body,
            message_sid=message_sid
        )
        
        # Get conversation history for context
        conversation_history = conversation_store.get_conversation_for_openai(from_number)
        
        # Generate response using OpenAI
        response_text = openai_service.answer_question(
            question=message_body,
            conversation_history=conversation_history
        )
        
        # Store outgoing message
        conversation_store.add_message(
            phone_number=from_number,
            direction='outgoing',
            message_text=response_text
        )
        
        # Return TwiML response
        twiml = twilio_service.create_webhook_response(response_text)
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error handling webhook: {e}")
        # Return a generic error response
        error_response = twilio_service.create_webhook_response(
            "I'm sorry, I encountered an error. Please try again later."
        )
        return Response(error_response, mimetype='text/xml')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
