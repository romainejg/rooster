"""
Streamlit Bible Verse SMS Application
Daily Bible verse scheduler with SMS delivery and Q&A via OpenAI + Twilio
"""
import streamlit as st
import os
from datetime import datetime, time
from dotenv import load_dotenv

# Import our services
from bible_service import BibleVerseService
from openai_service import OpenAIService
from twilio_service import TwilioService
from conversation_store import ConversationStore

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Daily Bible Verse SMS",
    page_icon="📖",
    layout="wide"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services (cached)"""
    try:
        bible_service = BibleVerseService()
        openai_service = OpenAIService()
        twilio_service = TwilioService()
        conversation_store = ConversationStore()
        return bible_service, openai_service, twilio_service, conversation_store
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        st.info("Please ensure all required environment variables are set. See .env.example for reference.")
        return None, None, None, None

bible_service, openai_service, twilio_service, conversation_store = init_services()

# Title and description
st.title("📖 Daily Bible Verse SMS")
st.markdown("Send formatted Bible verses via SMS with OpenAI-generated reflections. Reply to SMS for Q&A in your church's doctrinal perspective.")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Display current settings (masked)
    if os.getenv('OPENAI_API_KEY'):
        st.success("✅ OpenAI API configured")
    else:
        st.error("❌ OpenAI API not configured")
    
    if os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'):
        st.success("✅ Twilio configured")
    else:
        st.error("❌ Twilio not configured")
    
    recipient_number = st.text_input(
        "Recipient Phone Number",
        value=os.getenv('RECIPIENT_PHONE_NUMBER', ''),
        placeholder="+1234567890",
        help="Phone number to send Bible verses to"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app allows you to:
    - Select Bible verses
    - Format with AI reflections
    - Send via Twilio SMS
    - Answer questions via SMS
    """)

# Check if services are initialized
if not all([bible_service, openai_service, twilio_service, conversation_store]):
    st.stop()

# Main interface tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Send Verse", "📅 Schedule", "💬 Conversations", "ℹ️ Setup"])

# Tab 1: Send Verse Immediately
with tab1:
    st.header("Send Bible Verse Now")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Book selection
        books = bible_service.get_book_list()
        selected_book = st.selectbox("Select Book", books, index=books.index("John") if "John" in books else 0)
        
        # Chapter and verse selection
        col_ch, col_v1, col_v2 = st.columns(3)
        with col_ch:
            chapter = st.number_input("Chapter", min_value=1, max_value=150, value=3)
        with col_v1:
            start_verse = st.number_input("Start Verse", min_value=1, max_value=176, value=16)
        with col_v2:
            end_verse = st.number_input("End Verse", min_value=1, max_value=176, value=16)
        
        # Options
        include_reflection = st.checkbox("Include AI-generated reflection", value=True)
    
    with col2:
        st.info(f"**Selected:**\n\n{selected_book} {chapter}:{start_verse}" + 
                (f"-{end_verse}" if end_verse != start_verse else ""))
    
    # Preview section
    if st.button("📖 Preview Message", type="secondary", use_container_width=True):
        with st.spinner("Fetching and formatting verse..."):
            # Fetch verse
            verse_text = bible_service.get_verse(selected_book, chapter, start_verse, end_verse)
            
            if verse_text:
                verse_ref = f"{selected_book} {chapter}:{start_verse}"
                if end_verse != start_verse:
                    verse_ref += f"-{end_verse}"
                
                # Format with OpenAI
                formatted_message = openai_service.format_verse_with_reflection(
                    verse_text, verse_ref, include_reflection
                )
                
                st.session_state.preview_message = formatted_message
                st.session_state.current_verse_ref = verse_ref
            else:
                st.error("Could not fetch verse. Please check the reference.")
    
    # Display preview
    if 'preview_message' in st.session_state:
        st.markdown("### 📱 Message Preview")
        st.info(st.session_state.preview_message)
        
        # Character count
        char_count = len(st.session_state.preview_message)
        if char_count > 160:
            st.warning(f"⚠️ Message is {char_count} characters (will be sent as {(char_count // 160) + 1} SMS messages)")
        else:
            st.success(f"✅ Message is {char_count} characters (single SMS)")
        
        # Send button
        if st.button("📤 Send SMS Now", type="primary", use_container_width=True):
            if not recipient_number:
                st.error("Please enter a recipient phone number in the sidebar")
            else:
                with st.spinner("Sending SMS..."):
                    result = twilio_service.send_sms(
                        st.session_state.preview_message,
                        recipient_number
                    )
                    
                    if result['status'] == 'success':
                        st.success(f"✅ SMS sent successfully! Message SID: {result['message_sid']}")
                        
                        # Store in conversation history
                        conversation_store.add_message(
                            phone_number=recipient_number,
                            direction='outgoing',
                            message_text=st.session_state.preview_message,
                            message_sid=result['message_sid']
                        )
                    else:
                        st.error(f"❌ Failed to send SMS: {result.get('error', 'Unknown error')}")

# Tab 2: Schedule Messages
with tab2:
    st.header("Schedule Daily Bible Verse")
    st.info("📅 Schedule verses to be sent at a specific time daily")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Book selection for scheduling
        sched_book = st.selectbox("Book", books, key="sched_book", index=books.index("Psalms") if "Psalms" in books else 0)
        
        col_ch, col_v1, col_v2 = st.columns(3)
        with col_ch:
            sched_chapter = st.number_input("Chapter", min_value=1, max_value=150, value=23, key="sched_ch")
        with col_v1:
            sched_start = st.number_input("Start Verse", min_value=1, max_value=176, value=1, key="sched_v1")
        with col_v2:
            sched_end = st.number_input("End Verse", min_value=1, max_value=176, value=1, key="sched_v2")
        
        # Schedule time
        sched_time = st.time_input("Send at", value=time(8, 0), help="Time to send the verse daily")
        
        sched_reflection = st.checkbox("Include reflection", value=True, key="sched_refl")
    
    with col2:
        st.info(f"**Schedule:**\n\n{sched_book} {sched_chapter}:{sched_start}" + 
                (f"-{sched_end}" if sched_end != sched_start else "") +
                f"\n\nDaily at {sched_time.strftime('%I:%M %p')}")
    
    if st.button("➕ Add to Schedule", type="primary", use_container_width=True):
        if not recipient_number:
            st.error("Please enter a recipient phone number in the sidebar")
        else:
            conversation_store.add_scheduled_message(
                book=sched_book,
                chapter=sched_chapter,
                start_verse=sched_start,
                end_verse=sched_end,
                schedule_time=sched_time.strftime('%H:%M'),
                include_reflection=sched_reflection,
                recipient_number=recipient_number
            )
            st.success("✅ Verse scheduled successfully!")
            st.rerun()
    
    # Display scheduled messages
    st.markdown("---")
    st.subheader("Scheduled Messages")
    
    scheduled = conversation_store.get_pending_scheduled_messages()
    
    if scheduled:
        for msg in scheduled:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                verse_ref = f"{msg['book']} {msg['chapter']}:{msg['start_verse']}"
                if msg['end_verse'] != msg['start_verse']:
                    verse_ref += f"-{msg['end_verse']}"
                st.write(f"📖 {verse_ref} at {msg['schedule_time']}")
            with col2:
                st.write("✅ Reflection" if msg['include_reflection'] else "📝 Verse only")
            with col3:
                if st.button("🗑️", key=f"del_{msg['id']}", help="Delete"):
                    conversation_store.delete_scheduled_message(msg['id'])
                    st.rerun()
    else:
        st.info("No scheduled messages. Add one above!")
    
    st.markdown("---")
    st.warning("⚠️ Note: Scheduled messages require a background scheduler to run. See the Setup tab for deployment instructions.")

# Tab 3: Conversation History
with tab3:
    st.header("💬 SMS Conversation History")
    
    if recipient_number:
        history = conversation_store.get_conversation_history(recipient_number, limit=20)
        
        if history:
            st.success(f"Showing recent conversation with {recipient_number}")
            
            for msg in reversed(history):  # Show newest first
                if msg['direction'] == 'outgoing':
                    st.markdown(f"""
                    <div style='background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                        <strong>You (SMS Sent)</strong><br/>
                        {msg['message']}<br/>
                        <small>{msg['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                        <strong>Received</strong><br/>
                        {msg['message']}<br/>
                        <small>{msg['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No conversation history yet. Send a verse to get started!")
    else:
        st.warning("Please enter a recipient phone number in the sidebar to view conversation history.")
    
    # Manual Q&A testing
    st.markdown("---")
    st.subheader("🧪 Test Q&A Response")
    st.markdown("Test how the AI would respond to a question (without sending SMS)")
    
    test_question = st.text_area("Enter a test question:", placeholder="What does the Bible say about forgiveness?")
    
    if st.button("Get AI Response", type="secondary"):
        if test_question:
            with st.spinner("Generating response..."):
                # Get conversation history for context
                conv_history = conversation_store.get_conversation_for_openai(recipient_number) if recipient_number else []
                
                answer = openai_service.answer_question(test_question, conv_history)
                
                st.markdown("### 🤖 AI Response:")
                st.success(answer)
        else:
            st.warning("Please enter a question")

# Tab 4: Setup Instructions
with tab4:
    st.header("ℹ️ Setup & Deployment")
    
    st.markdown("""
    ### 🚀 Getting Started
    
    #### 1. Environment Variables
    Create a `.env` file (or use Streamlit secrets) with:
    
    ```bash
    # OpenAI
    OPENAI_API_KEY=your_openai_api_key
    
    # Twilio
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_PHONE_NUMBER=+1234567890
    
    # Configuration
    RECIPIENT_PHONE_NUMBER=+1234567890
    CHURCH_DOCTRINE=Your church's doctrinal perspective
    BIBLE_API_KEY=your_api_bible_key  # Optional
    ```
    
    #### 2. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
    
    #### 3. Run the Application
    ```bash
    streamlit run app.py
    ```
    
    #### 4. Setup Twilio Webhook (for SMS Replies)
    
    For SMS Q&A to work, you need to expose the webhook endpoint:
    
    **Option A: Local Development (using ngrok)**
    ```bash
    # In a separate terminal
    python webhook_handler.py
    
    # In another terminal
    ngrok http 5000
    ```
    
    Then configure your Twilio phone number's messaging webhook to:
    `https://your-ngrok-url.ngrok.io/webhook/sms`
    
    **Option B: Deploy on Cloud Platform**
    - Deploy `webhook_handler.py` separately as a web service
    - Use platforms like: Railway, Render, Heroku, or AWS Lambda
    - Set the webhook URL in your Twilio phone number settings
    
    #### 5. Deploy Streamlit App
    
    **GitHub Deployment:**
    1. Push this code to GitHub
    2. Deploy on Streamlit Community Cloud:
       - Go to share.streamlit.io
       - Connect your GitHub repo
       - Add secrets in the Streamlit dashboard
    
    **Alternative: Deploy on other platforms:**
    - Heroku
    - Google Cloud Run
    - AWS Elastic Beanstalk
    
    ### 📚 API Keys Required
    
    1. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
    2. **Twilio Account**: Sign up at https://www.twilio.com/
    3. **Bible API Key** (Optional): Get from https://scripture.api.bible/
    
    ### 🔧 Features
    
    ✅ Select and send Bible verses via SMS  
    ✅ AI-generated reflections with OpenAI  
    ✅ Schedule daily verse delivery  
    ✅ Two-way SMS conversation with AI Q&A  
    ✅ Doctrinal perspective customization  
    ✅ Conversation history tracking  
    
    ### 📝 Notes
    
    - **Scheduling**: The schedule feature requires a background process. For production, use a cron job or cloud scheduler.
    - **SMS Costs**: Check Twilio pricing for SMS costs
    - **Rate Limits**: Be aware of OpenAI API rate limits
    """)
    
    st.markdown("---")
    st.markdown("### 🐓 Rooster - Wake up to God's Word daily!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Made with ❤️ for daily Bible devotionals | Powered by OpenAI & Twilio"
    "</div>",
    unsafe_allow_html=True
)
