"""
Background scheduler for sending scheduled Bible verses
Run this separately or integrate with your deployment
"""
import time
import schedule
from datetime import datetime
from bible_service import BibleVerseService
from openai_service import OpenAIService
from twilio_service import TwilioService
from conversation_store import ConversationStore

def send_scheduled_verses():
    """Check and send any scheduled verses"""
    print(f"[{datetime.now()}] Checking for scheduled verses...")
    
    try:
        # Initialize services
        bible_service = BibleVerseService()
        openai_service = OpenAIService()
        twilio_service = TwilioService()
        conversation_store = ConversationStore()
        
        # Get current time
        current_time = datetime.now().strftime('%H:%M')
        
        # Get all pending scheduled messages
        scheduled_messages = conversation_store.get_pending_scheduled_messages()
        
        for msg in scheduled_messages:
            # Check if it's time to send this message
            if msg['schedule_time'] == current_time:
                print(f"Sending scheduled verse: {msg['book']} {msg['chapter']}:{msg['start_verse']}")
                
                # Fetch verse
                verse_text = bible_service.get_verse(
                    msg['book'], 
                    msg['chapter'], 
                    msg['start_verse'], 
                    msg['end_verse']
                )
                
                if verse_text:
                    # Create reference
                    verse_ref = f"{msg['book']} {msg['chapter']}:{msg['start_verse']}"
                    if msg['end_verse'] != msg['start_verse']:
                        verse_ref += f"-{msg['end_verse']}"
                    
                    # Format with OpenAI
                    formatted_message = openai_service.format_verse_with_reflection(
                        verse_text, 
                        verse_ref, 
                        msg['include_reflection']
                    )
                    
                    # Send SMS
                    result = twilio_service.send_sms(
                        formatted_message,
                        msg['recipient_number']
                    )
                    
                    if result['status'] == 'success':
                        print(f"✅ SMS sent successfully: {result['message_sid']}")
                        
                        # Store in conversation history
                        conversation_store.add_message(
                            phone_number=msg['recipient_number'],
                            direction='outgoing',
                            message_text=formatted_message,
                            message_sid=result['message_sid']
                        )
                        
                        # Mark as sent
                        conversation_store.mark_scheduled_message_sent(msg['id'])
                    else:
                        print(f"❌ Failed to send SMS: {result.get('error')}")
                else:
                    print(f"❌ Could not fetch verse")
                    
    except Exception as e:
        print(f"Error in send_scheduled_verses: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main scheduler loop"""
    print("📅 Bible Verse Scheduler started")
    print("Checking for scheduled verses every minute...")
    print("⚠️  For production, consider using a cron job that runs at specific times instead of continuous polling")
    
    # Schedule the check to run every minute
    schedule.every(1).minutes.do(send_scheduled_verses)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    main()
