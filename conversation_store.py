"""
Simple conversation storage using SQLite
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class ConversationStore:
    def __init__(self, db_path: str = 'conversations.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                direction TEXT NOT NULL,
                message_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_sid TEXT
            )
        ''')
        
        # Create scheduled_messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book TEXT NOT NULL,
                chapter INTEGER NOT NULL,
                start_verse INTEGER NOT NULL,
                end_verse INTEGER NOT NULL,
                schedule_time TEXT NOT NULL,
                include_reflection INTEGER DEFAULT 1,
                recipient_number TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user_state table for persisting UI state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_message(self, phone_number: str, direction: str, message_text: str, 
                   message_sid: Optional[str] = None):
        """
        Add a message to the conversation history
        
        Args:
            phone_number: The phone number
            direction: 'incoming' or 'outgoing'
            message_text: The message content
            message_sid: Twilio message SID (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (phone_number, direction, message_text, message_sid)
            VALUES (?, ?, ?, ?)
        ''', (phone_number, direction, message_text, message_sid))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """
        Get recent conversation history for a phone number
        
        Args:
            phone_number: The phone number
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of message dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT direction, message_text, timestamp 
            FROM messages 
            WHERE phone_number = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (phone_number, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'direction': row[0],
                'message': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        return list(reversed(messages))  # Return in chronological order
    
    def get_conversation_for_openai(self, phone_number: str, limit: int = 6) -> List[Dict]:
        """
        Get conversation history formatted for OpenAI API
        
        Args:
            phone_number: The phone number
            limit: Maximum number of messages (exchanges) to retrieve
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        history = self.get_conversation_history(phone_number, limit)
        
        openai_messages = []
        for msg in history:
            role = "assistant" if msg['direction'] == 'outgoing' else "user"
            openai_messages.append({
                "role": role,
                "content": msg['message']
            })
        
        return openai_messages
    
    def add_scheduled_message(self, book: str, chapter: int, start_verse: int, 
                            end_verse: int, schedule_time: str, 
                            include_reflection: bool, recipient_number: str):
        """Add a scheduled message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_messages 
            (book, chapter, start_verse, end_verse, schedule_time, include_reflection, recipient_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (book, chapter, start_verse, end_verse, schedule_time, 
              1 if include_reflection else 0, recipient_number))
        
        conn.commit()
        conn.close()
    
    def add_reading_plan_item(self, book: str, chapter: int, start_verse: int, 
                            end_verse: int, include_reflection: bool):
        """
        Add an item to the reading plan (uses scheduled_messages table for storage)
        
        Args:
            book: Bible book name
            chapter: Chapter number
            start_verse: Starting verse number
            end_verse: Ending verse number
            include_reflection: Whether to include AI reflection
        """
        # Use the existing scheduled_messages table with dummy values for time/recipient
        # since we're repurposing it as a reading plan
        self.add_scheduled_message(
            book=book,
            chapter=chapter,
            start_verse=start_verse,
            end_verse=end_verse,
            schedule_time="00:00",  # Not used for reading plans
            include_reflection=include_reflection,
            recipient_number="reading_plan"  # Marker for reading plan items
        )
    
    def get_pending_scheduled_messages(self) -> List[Dict]:
        """Get all pending scheduled messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, book, chapter, start_verse, end_verse, schedule_time, 
                   include_reflection, recipient_number
            FROM scheduled_messages
            WHERE status = 'pending'
            ORDER BY schedule_time
        ''')
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'book': row[1],
                'chapter': row[2],
                'start_verse': row[3],
                'end_verse': row[4],
                'schedule_time': row[5],
                'include_reflection': bool(row[6]),
                'recipient_number': row[7]
            })
        
        conn.close()
        return messages
    
    def mark_scheduled_message_sent(self, message_id: int):
        """Mark a scheduled message as sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_messages 
            SET status = 'sent'
            WHERE id = ?
        ''', (message_id,))
        
        conn.commit()
        conn.close()
    
    def delete_scheduled_message(self, message_id: int):
        """Delete a scheduled message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM scheduled_messages WHERE id = ?', (message_id,))
        
        conn.commit()
        conn.close()
    
    def save_state(self, key: str, value: str):
        """
        Save a state value to persistent storage
        
        Args:
            key: The state key (e.g., 'last_book', 'preview_message')
            value: The value to store (will be converted to string)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_state (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET 
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_state(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a state value from persistent storage
        
        Args:
            key: The state key to retrieve
            default: Default value if key doesn't exist
        
        Returns:
            The stored value or default if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM user_state WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        return row[0] if row else default
    
    def save_verse_selection(self, book: str, chapter: int, start_verse: int, 
                           end_verse: int, preview_message: Optional[str] = None,
                           verse_ref: Optional[str] = None):
        """
        Save the last verse selection for persistence across sessions
        
        Args:
            book: Bible book name
            chapter: Chapter number
            start_verse: Starting verse number
            end_verse: Ending verse number
            preview_message: Optional preview message text
            verse_ref: Optional verse reference string
        """
        self.save_state('last_book', book)
        self.save_state('last_chapter', str(chapter))
        self.save_state('last_start_verse', str(start_verse))
        self.save_state('last_end_verse', str(end_verse))
        
        if preview_message:
            self.save_state('preview_message', preview_message)
        
        if verse_ref:
            self.save_state('current_verse_ref', verse_ref)
    
    def get_verse_selection(self) -> Dict:
        """
        Retrieve the last verse selection
        
        Returns:
            Dictionary with last verse selection or defaults
        """
        # Get values with defaults to avoid None
        chapter_str = self.get_state('last_chapter', '3')
        start_str = self.get_state('last_start_verse', '16')
        end_str = self.get_state('last_end_verse', '16')
        
        return {
            'book': self.get_state('last_book'),
            'chapter': int(chapter_str) if chapter_str else 3,
            'start_verse': int(start_str) if start_str else 16,
            'end_verse': int(end_str) if end_str else 16,
            'preview_message': self.get_state('preview_message'),
            'current_verse_ref': self.get_state('current_verse_ref')
        }
    
    def save_recipient_number(self, phone_number: str):
        """
        Save the recipient phone number
        
        Args:
            phone_number: The phone number to save
        """
        self.save_state('recipient_number', phone_number)
    
    def get_recipient_number(self) -> Optional[str]:
        """
        Retrieve the saved recipient phone number
        
        Returns:
            The saved phone number or None
        """
        return self.get_state('recipient_number')
