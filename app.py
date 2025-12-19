"""
Streamlit Bible Verse Application
Daily Bible verse reader with AI-generated reflections and Q&A via OpenAI
"""
import streamlit as st
import os
from datetime import datetime, time
from dotenv import load_dotenv

# Import our services
from bible_service import BibleVerseService
from openai_service import OpenAIService
from conversation_store import ConversationStore

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Daily Bible Verse Reader",
    page_icon="📖",
    layout="wide"
)

# Custom CSS for inspirational churchy styling
st.markdown("""
    <style>
    /* Semi-transparent chat boxes */
    .stChatMessage {
        background-color: rgba(139, 105, 20, 0.15) !important;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Info boxes with transparency */
    .stAlert {
        background-color: rgba(139, 105, 20, 0.12) !important;
        border-left: 4px solid #8B6914;
    }
    
    /* Headers with spiritual styling */
    h1, h2, h3 {
        color: #8B6914 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Verse display boxes */
    .verse-box {
        background: linear-gradient(135deg, rgba(255, 248, 231, 0.9) 0%, rgba(139, 105, 20, 0.1) 100%);
        border-left: 5px solid #8B6914;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(139, 105, 20, 0.2);
    }
    
    /* Q&A response boxes */
    .qa-box {
        background: rgba(255, 255, 255, 0.7);
        border: 2px solid rgba(139, 105, 20, 0.3);
        border-radius: 12px;
        padding: 18px;
        margin: 12px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services (cached)"""
    try:
        bible_service = BibleVerseService()
        openai_service = OpenAIService()
        conversation_store = ConversationStore()
        return bible_service, openai_service, conversation_store
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        st.info("Please ensure all required environment variables are set. See .env.example for reference.")
        return None, None, None

bible_service, openai_service, conversation_store = init_services()

# Title and description with spiritual styling
st.markdown("<h1 style='text-align: center; color: #8B6914;'>📖 Daily Bible Verse Reader 🙏</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: #2C1810;'>Experience God's Word with AI-powered reflections and thoughtful Q&A</p>", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Display current settings (masked)
    if os.getenv('OPENAI_API_KEY'):
        st.success("✅ OpenAI API configured")
    else:
        st.error("❌ OpenAI API not configured")
    
    st.markdown("---")
    st.markdown("### 📚 About")
    st.markdown("""
    This app allows you to:
    - 📖 Read Bible verses with context
    - ✨ View AI-generated reflections
    - 💭 Ask questions about faith
    - 📅 Plan your Bible reading schedule
    """)
    
    st.markdown("---")
    st.markdown("### 🙏 Features")
    st.markdown("""
    - Daily verse exploration
    - Theological Q&A
    - Reading plan management
    - Inspirational reflections
    """)

# Check if services are initialized
if not all([bible_service, openai_service, conversation_store]):
    st.stop()

# Restore last verse selection from persistent storage
last_selection = conversation_store.get_verse_selection()

# Main interface tabs
tab1, tab2, tab3 = st.tabs(["📖 Bible Verses & Q&A", "📅 Reading Plan", "ℹ️ Setup"])

# Tab 1: Bible Verses & Q&A
with tab1:
    st.header("📖 Bible Verses with Reflections")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Book selection with restoration of last selection
        books = bible_service.get_book_list()
        
        # Determine default book index
        default_book = last_selection.get('book') or "John"
        default_book_index = books.index(default_book) if default_book in books else (books.index("John") if "John" in books else 0)
        
        selected_book = st.selectbox("Select Book", books, index=default_book_index)
        
        # Chapter and verse selection with restoration
        col_ch, col_v1, col_v2 = st.columns(3)
        with col_ch:
            chapter = st.number_input("Chapter", min_value=1, max_value=150, value=last_selection.get('chapter', 3))
        with col_v1:
            start_verse = st.number_input("Start Verse", min_value=1, max_value=176, value=last_selection.get('start_verse', 16))
        with col_v2:
            end_verse = st.number_input("End Verse", min_value=1, max_value=176, value=last_selection.get('end_verse', 16))
        
        # Options
        include_reflection = st.checkbox("Include AI-generated reflection", value=True)
    
    with col2:
        st.markdown(f"""
        <div class='verse-box'>
            <strong>Selected Verse:</strong><br/>
            {selected_book} {chapter}:{start_verse}{f"-{end_verse}" if end_verse != start_verse else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # Preview section
    if st.button("📖 View Verse & Reflection", type="primary", use_container_width=True):
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
                
                # Save to both session state and persistent storage
                st.session_state.preview_message = formatted_message
                st.session_state.current_verse_ref = verse_ref
                
                # Save to persistent storage so it survives app restarts
                conversation_store.save_verse_selection(
                    book=selected_book,
                    chapter=chapter,
                    start_verse=start_verse,
                    end_verse=end_verse,
                    preview_message=formatted_message,
                    verse_ref=verse_ref
                )
            else:
                st.error("Could not fetch verse. Please check the reference.")
    
    # Initialize session state from persistent storage if not already set
    if 'preview_message' not in st.session_state and last_selection.get('preview_message'):
        st.session_state.preview_message = last_selection['preview_message']
        st.session_state.current_verse_ref = last_selection.get('current_verse_ref', '')
    
    # Display verse and reflection
    if 'preview_message' in st.session_state:
        st.markdown("---")
        st.markdown(f"""
        <div class='verse-box'>
            <h3 style='margin-top: 0;'>{st.session_state.get('current_verse_ref', 'Scripture')}</h3>
            <div style='font-size: 1.1em; line-height: 1.6;'>
                {st.session_state.preview_message.replace(chr(10), '<br/>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Q&A Section
    st.markdown("---")
    st.markdown("### 💭 Ask a Question")
    st.markdown("Ask any question about the Bible, faith, or theology and receive thoughtful, doctrine-based answers.")
    
    question = st.text_area(
        "Your Question:", 
        placeholder="What does this verse mean in daily life?\nHow can I apply this teaching?\nWhat does the Bible say about forgiveness?",
        height=100,
        key="qa_question"
    )
    
    col_qa1, col_qa2 = st.columns([1, 3])
    with col_qa1:
        ask_button = st.button("🤔 Get Answer", type="secondary", use_container_width=True)
    
    if ask_button and question:
        with st.spinner("Seeking wisdom..."):
            # Get conversation history for context (if any)
            conv_history = []
            
            answer = openai_service.answer_question(question, conv_history)
            
            st.markdown(f"""
            <div class='qa-box'>
                <h4 style='color: #8B6914; margin-top: 0;'>📜 Answer:</h4>
                <div style='line-height: 1.6;'>
                    {answer.replace(chr(10), '<br/>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    elif ask_button and not question:
        st.warning("Please enter a question to receive an answer.")


# Tab 2: Reading Plan
with tab2:
    st.header("📅 Bible Reading Plan")
    st.markdown("Plan your Bible reading journey in advance. Add verses you want to study and organize your devotional time.")
    
    # Book selection for scheduling
    books = bible_service.get_book_list()
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("➕ Add to Reading Plan")
        
        # Create a form for adding verses
        with st.form("add_reading_plan", clear_on_submit=True):
            plan_book = st.selectbox("Book", books, key="plan_book", index=books.index("Psalms") if "Psalms" in books else 0)
            
            col_ch, col_v1, col_v2 = st.columns(3)
            with col_ch:
                plan_chapter = st.number_input("Chapter", min_value=1, max_value=150, value=1, key="plan_ch")
            with col_v1:
                plan_start = st.number_input("Start Verse", min_value=1, max_value=176, value=1, key="plan_v1")
            with col_v2:
                plan_end = st.number_input("End Verse", min_value=1, max_value=176, value=6, key="plan_v2")
            
            plan_reflection = st.checkbox("Include reflection", value=True, key="plan_refl")
            plan_notes = st.text_area("Notes (optional)", placeholder="Why this passage? What are you hoping to learn?", key="plan_notes")
            
            submitted = st.form_submit_button("➕ Add to Plan", type="primary", use_container_width=True)
            
            if submitted:
                # Add a dummy recipient since we're not sending
                conversation_store.add_scheduled_message(
                    book=plan_book,
                    chapter=plan_chapter,
                    start_verse=plan_start,
                    end_verse=plan_end,
                    schedule_time="00:00",  # Dummy time since we're not scheduling
                    include_reflection=plan_reflection,
                    recipient_number="reading_plan"  # Dummy recipient
                )
                st.success(f"✅ Added {plan_book} {plan_chapter}:{plan_start}-{plan_end} to your reading plan!")
                st.rerun()
    
    with col2:
        st.subheader("📊 Reading Plan Overview")
        scheduled = conversation_store.get_pending_scheduled_messages()
        
        if scheduled:
            st.metric("Total Passages", len(scheduled))
            
            # Count by book
            books_in_plan = {}
            for msg in scheduled:
                books_in_plan[msg['book']] = books_in_plan.get(msg['book'], 0) + 1
            
            st.markdown("**Books in Plan:**")
            for book, count in sorted(books_in_plan.items()):
                st.markdown(f"- {book}: {count} passage(s)")
        else:
            st.info("No passages in your reading plan yet!")
    
    # Display reading plan
    st.markdown("---")
    st.subheader("📖 Your Reading Plan")
    
    scheduled = conversation_store.get_pending_scheduled_messages()
    
    if scheduled:
        for idx, msg in enumerate(scheduled, 1):
            verse_ref = f"{msg['book']} {msg['chapter']}:{msg['start_verse']}"
            if msg['end_verse'] != msg['start_verse']:
                verse_ref += f"-{msg['end_verse']}"
            
            with st.container():
                col1, col2, col3 = st.columns([1, 6, 1])
                with col1:
                    st.markdown(f"**#{idx}**")
                with col2:
                    st.markdown(f"""
                    <div class='verse-box' style='margin: 5px 0;'>
                        <strong>📖 {verse_ref}</strong><br/>
                        <small>{'✨ With reflection' if msg['include_reflection'] else '📝 Verse only'}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    if st.button("🗑️", key=f"del_{msg['id']}", help="Remove from plan"):
                        conversation_store.delete_scheduled_message(msg['id'])
                        st.rerun()
    else:
        st.info("📝 Your reading plan is empty. Add passages above to get started!")
    
    st.markdown("---")
    st.markdown("""
    <div style='background-color: rgba(139, 105, 20, 0.1); padding: 15px; border-radius: 10px;'>
        <strong>💡 Reading Plan Tips:</strong><br/>
        • Add verses you want to study in order<br/>
        • Use this as your daily devotional guide<br/>
        • Come back and work through your plan verse by verse<br/>
        • Mix passages from different books for variety
    </div>
    """, unsafe_allow_html=True)

# Tab 3: Setup Instructions
with tab3:
    st.header("ℹ️ Setup & Information")
    
    st.markdown("""
    ### 🚀 Getting Started
    
    #### 1. Environment Variables
    Create a `.env` file (or use Streamlit secrets) with:
    
    ```bash
    # OpenAI (Required)
    OPENAI_API_KEY=your_openai_api_key
    
    # Church Configuration
    CHURCH_DOCTRINE=Your church's doctrinal perspective
    
    # Bible API (Optional - for full verse text)
    BIBLE_API_KEY=your_api_bible_key
    ```
    
    #### 2. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
    
    #### 3. Run the Application
    ```bash
    streamlit run app.py
    ```
    
    #### 4. Deploy on Streamlit Cloud
    
    **GitHub Deployment:**
    1. Push this code to GitHub
    2. Deploy on Streamlit Community Cloud:
       - Go to share.streamlit.io
       - Connect your GitHub repo
       - Add secrets in the Streamlit dashboard
    
    **Alternative Platforms:**
    - Heroku
    - Google Cloud Run
    - AWS Elastic Beanstalk
    
    ### 📚 API Keys Required
    
    1. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
    2. **Bible API Key** (Optional): Get from https://scripture.api.bible/
    
    ### 🔧 Features
    
    ✅ Browse and read Bible verses  
    ✅ AI-generated reflections with OpenAI  
    ✅ Ask theological questions with AI Q&A  
    ✅ Create and manage reading plans  
    ✅ Doctrinal perspective customization  
    ✅ Beautiful, inspirational interface  
    
    ### 📖 How to Use This App
    
    **Bible Verses & Q&A Tab:**
    - Select any Bible passage and view it with optional AI reflection
    - Ask questions about faith, theology, or specific verses
    - Receive thoughtful answers based on your church's doctrine
    
    **Reading Plan Tab:**
    - Add verses to your personal reading plan
    - Organize your Bible study schedule
    - Track which passages you want to explore
    - Remove completed readings
    
    ### 🎨 Customization
    
    **Church Doctrine:**
    Customize the `CHURCH_DOCTRINE` environment variable to reflect your theological perspective:
    
    ```env
    CHURCH_DOCTRINE="Reformed Baptist perspective emphasizing the sovereignty of God, justification by faith alone, and the authority of Scripture"
    ```
    
    This influences how the AI answers questions about faith and doctrine.
    
    ### 📝 Notes
    
    - **Bible API**: Without an API key, verse references will be shown but full text may be limited
    - **AI Responses**: Powered by OpenAI GPT models, answers reflect your configured doctrine
    - **Privacy**: All data stored locally in SQLite database
    - **Reading Plans**: Use as a personal devotional guide
    """)
    
    st.markdown("---")
    st.markdown("### 🐓 Rooster - Wake up to God's Word daily!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8B6914; font-style: italic;'>"
    "Made with ❤️ for daily Bible devotionals | Powered by OpenAI"
    "</div>",
    unsafe_allow_html=True
)
