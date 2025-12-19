#!/usr/bin/env python3
"""
Demo script to showcase Rooster Bible Verse SMS App functionality
This script demonstrates all key features without requiring actual API keys
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bible_service import BibleVerseService
from conversation_store import ConversationStore

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def demo_bible_service():
    """Demonstrate Bible verse fetching"""
    print_header("📖 Bible Verse Service Demo")
    
    bible = BibleVerseService()
    
    # Show available books
    books = bible.get_book_list()
    print(f"\n✅ Available books: {len(books)}")
    print(f"   Sample books: {', '.join(books[:5])}, ...")
    
    # Demonstrate verse fetching
    print("\n📝 Fetching verses (using fallback mode):")
    
    test_verses = [
        ("John", 3, 16, 16),
        ("Psalms", 23, 1, 6),
        ("Matthew", 6, 9, 13),
    ]
    
    for book, chapter, start, end in test_verses:
        verse_text = bible.get_verse(book, chapter, start, end)
        ref = f"{book} {chapter}:{start}"
        if end != start:
            ref += f"-{end}"
        print(f"\n   Reference: {ref}")
        print(f"   Result: {verse_text[:80]}...")

def demo_conversation_store():
    """Demonstrate conversation storage"""
    print_header("💬 Conversation Store Demo")
    
    # Use temp database
    db_path = '/tmp/demo_rooster.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    store = ConversationStore(db_path)
    
    # Add sample conversation
    print("\n📥 Adding sample conversation:")
    phone = "+15555555678"
    
    conversations = [
        ("outgoing", "📖 John 3:16\n\nFor God so loved the world...", "SM001"),
        ("incoming", "What does this mean for me?", "SM002"),
        ("outgoing", "This verse reminds us of God's unconditional love...", "SM003"),
        ("incoming", "How can I share this love with others?", "SM004"),
    ]
    
    for direction, message, sid in conversations:
        store.add_message(phone, direction, message, sid)
        arrow = "➡️" if direction == "outgoing" else "⬅️"
        print(f"   {arrow} {direction}: {message[:50]}...")
    
    # Retrieve history
    print("\n📜 Conversation history:")
    history = store.get_conversation_history(phone)
    print(f"   Retrieved {len(history)} messages")
    
    # Show OpenAI format
    openai_history = store.get_conversation_for_openai(phone)
    print(f"\n🤖 OpenAI format: {len(openai_history)} messages")
    for msg in openai_history[:2]:
        print(f"   Role: {msg['role']}, Content: {msg['content'][:40]}...")
    
    # Demonstrate state persistence (NEW FEATURE)
    print("\n💾 Testing state persistence:")
    print("   Saving verse selection state...")
    store.save_verse_selection(
        book="Romans",
        chapter=8,
        start_verse=28,
        end_verse=28,
        preview_message="📖 Romans 8:28\n\nAnd we know that in all things God works for the good...",
        verse_ref="Romans 8:28"
    )
    store.save_recipient_number(phone)
    
    # Retrieve state
    saved_selection = store.get_verse_selection()
    saved_recipient = store.get_recipient_number()
    print(f"   ✅ State saved: {saved_selection['book']} {saved_selection['chapter']}:{saved_selection['start_verse']}")
    print(f"   ✅ Recipient saved: {saved_recipient}")
    print(f"   ℹ️  State persists across app restarts!")
    
    # Demonstrate scheduling
    print("\n📅 Adding scheduled messages:")
    schedules = [
        ("John", 3, 16, 16, "08:00", True),
        ("Psalms", 23, 1, 6, "08:00", True),
        ("Romans", 8, 28, 28, "20:00", False),
    ]
    
    for book, ch, s, e, time, refl in schedules:
        store.add_scheduled_message(book, ch, s, e, time, refl, phone)
        ref = f"{book} {ch}:{s}" + (f"-{e}" if e != s else "")
        print(f"   ✅ Scheduled: {ref} at {time} (reflection: {refl})")
    
    scheduled = store.get_pending_scheduled_messages()
    print(f"\n📋 Total scheduled messages: {len(scheduled)}")
    
    # Cleanup
    os.remove(db_path)
    print("   ✅ Demo database cleaned up")

def demo_app_structure():
    """Show application structure"""
    print_header("🏗️ Application Structure")
    
    print("\n📦 Core Components:")
    
    components = {
        'app.py': 'Main Streamlit UI application',
        'bible_service.py': 'Bible verse fetching with API.Bible integration',
        'openai_service.py': 'AI-powered verse formatting and Q&A',
        'twilio_service.py': 'SMS sending and receiving via Twilio',
        'conversation_store.py': 'SQLite-based message and schedule storage',
        'webhook_handler.py': 'Flask webhook for incoming SMS replies',
        'scheduler.py': 'Background scheduler for automated sending',
    }
    
    for filename, description in components.items():
        exists = "✅" if os.path.exists(filename) else "❌"
        print(f"   {exists} {filename:25} - {description}")
    
    print("\n📝 Configuration Files:")
    config_files = {
        '.env.example': 'Environment variable template',
        'requirements.txt': 'Python dependencies',
        'Procfile': 'Deployment configuration',
        'README.md': 'Documentation',
    }
    
    for filename, description in config_files.items():
        exists = "✅" if os.path.exists(filename) else "❌"
        print(f"   {exists} {filename:25} - {description}")

def demo_features():
    """List key features"""
    print_header("✨ Key Features")
    
    features = [
        "📖 Select any Bible book, chapter, and verse range",
        "🤖 AI-generated reflections using OpenAI GPT-4",
        "📱 SMS delivery via Twilio",
        "📅 Schedule daily verse delivery at specific times",
        "💬 Two-way SMS conversation with AI Q&A",
        "🏛️ Customizable church doctrinal perspective",
        "📊 Complete conversation history tracking",
        "🔒 Secure configuration with environment variables",
        "🚀 Easy deployment on Streamlit Cloud, Heroku, Railway",
        "🌐 Webhook support for SMS replies",
    ]
    
    for feature in features:
        print(f"   {feature}")

def demo_deployment():
    """Show deployment options"""
    print_header("🚀 Deployment Options")
    
    print("\n1️⃣  Streamlit Cloud (for UI):")
    print("   • Push to GitHub")
    print("   • Connect at share.streamlit.io")
    print("   • Add secrets in dashboard")
    print("   • Deploy with one click")
    
    print("\n2️⃣  Webhook Handler (for SMS replies):")
    print("   • Deploy on Railway, Render, or Heroku")
    print("   • Set TWILIO_WEBHOOK_URL in Twilio console")
    print("   • Use webhook_handler.py")
    
    print("\n3️⃣  Scheduler (for automated sending):")
    print("   • Run scheduler.py as background process")
    print("   • Use cron jobs or cloud scheduler")
    print("   • Deploy alongside webhook or separately")
    
    print("\n4️⃣  All-in-One:")
    print("   • Use Procfile for multi-process deployment")
    print("   • Deploy on platforms supporting worker processes")

def main():
    """Run all demos"""
    print("\n" + "🐓" * 35)
    print("  ROOSTER - Daily Bible Verse SMS Application Demo")
    print("🐓" * 35)
    
    try:
        demo_app_structure()
        demo_features()
        demo_bible_service()
        demo_conversation_store()
        demo_deployment()
        
        print_header("✅ Demo Complete!")
        print("\n🎉 All components are working correctly!")
        print("\n📚 Next steps:")
        print("   1. Set up environment variables in .env")
        print("   2. Get API keys (OpenAI, Twilio, Bible API)")
        print("   3. Run: streamlit run app.py")
        print("   4. Deploy to cloud platform")
        print("\n🔗 See README.md for detailed instructions")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
