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
