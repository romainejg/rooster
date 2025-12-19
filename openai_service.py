"""
OpenAI service for formatting verses and answering questions
"""
import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)
        self.church_doctrine = os.getenv('CHURCH_DOCTRINE', 
            'Protestant Christian perspective with emphasis on grace, faith, and scripture')
        
    def format_verse_with_reflection(self, verse_text: str, verse_reference: str, 
                                     include_reflection: bool = True) -> str:
        """
        Format a Bible verse and optionally add a brief reflection
        
        Args:
            verse_text: The actual verse text
            verse_reference: The verse reference (e.g., "John 3:16")
            include_reflection: Whether to add a reflection
        
        Returns:
            Formatted message ready to send via SMS
        """
        if not include_reflection:
            return f"📖 {verse_reference}\n\n{verse_text}"
        
        try:
            prompt = f"""Format this Bible verse for an SMS devotional message and add a brief, meaningful reflection (2-3 sentences).

Verse Reference: {verse_reference}
Verse Text: {verse_text}

Please provide:
1. The verse formatted nicely for SMS
2. A brief, encouraging reflection that applies the verse to daily life

Keep the total message under 300 characters if possible for SMS compatibility."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates brief, meaningful Bible devotionals for SMS messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            formatted_message = response.choices[0].message.content.strip()
            return formatted_message
            
        except Exception as e:
            print(f"Error formatting verse with OpenAI: {e}")
            # Fallback to simple formatting
            return f"📖 {verse_reference}\n\n{verse_text}\n\nMay God's word guide you today! 🙏"
    
    def answer_question(self, question: str, conversation_history: Optional[list] = None) -> str:
        """
        Answer a question about faith/scripture from church's doctrinal perspective
        
        Args:
            question: The user's question
            conversation_history: Optional list of previous messages
        
        Returns:
            Answer to the question
        """
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system", 
                    "content": f"""You are a knowledgeable Bible assistant answering questions from this doctrinal perspective: {self.church_doctrine}

Guidelines:
- Provide brief, clear answers suitable for SMS (keep under 400 characters when possible)
- Reference specific Bible verses when relevant
- Be warm, encouraging, and pastoral in tone
- If unsure, acknowledge limitations humbly
- Stay true to the doctrinal perspective provided"""
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 3 exchanges
            
            # Add current question
            messages.append({"role": "user", "content": question})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            print(f"Error answering question with OpenAI: {e}")
            return "I'm sorry, I'm having trouble responding right now. Please try again later or contact your church directly for guidance. 🙏"
