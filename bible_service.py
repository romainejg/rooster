"""
Bible verse fetching module using API.Bible
Falls back to local data if API is unavailable
"""
import os
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class BibleVerseService:
    def __init__(self):
        self.api_key = os.getenv('BIBLE_API_KEY', '')
        self.base_url = "https://api.scripture.api.bible/v1"
        # Using KJV Bible ID from API.Bible
        self.bible_id = "de4e12af7f28f599-02"  # KJV
        
    def get_verse(self, book: str, chapter: int, start_verse: int, end_verse: Optional[int] = None) -> Optional[str]:
        """
        Fetch Bible verses from API.Bible or fallback
        
        Args:
            book: Book name (e.g., "Genesis", "John")
            chapter: Chapter number
            start_verse: Starting verse number
            end_verse: Ending verse number (optional)
        
        Returns:
            Formatted verse text or None if not found
        """
        if not end_verse:
            end_verse = start_verse
            
        try:
            if self.api_key:
                return self._fetch_from_api(book, chapter, start_verse, end_verse)
            else:
                return self._fetch_fallback(book, chapter, start_verse, end_verse)
        except Exception as e:
            print(f"Error fetching verse: {e}")
            return self._fetch_fallback(book, chapter, start_verse, end_verse)
    
    def _fetch_from_api(self, book: str, chapter: int, start_verse: int, end_verse: int) -> Optional[str]:
        """Fetch from API.Bible"""
        try:
            # Convert book name to Bible book ID (simplified mapping)
            book_id = self._get_book_id(book)
            if not book_id:
                return None
                
            # Build passage reference
            if start_verse == end_verse:
                passage_id = f"{book_id}.{chapter}.{start_verse}"
            else:
                passage_id = f"{book_id}.{chapter}.{start_verse}-{book_id}.{chapter}.{end_verse}"
            
            headers = {
                'api-key': self.api_key
            }
            
            url = f"{self.base_url}/bibles/{self.bible_id}/passages/{passage_id}"
            params = {
                'content-type': 'text',
                'include-notes': 'false',
                'include-titles': 'false',
                'include-chapter-numbers': 'false',
                'include-verse-numbers': 'true'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('content', '')
            return None
        except requests.RequestException as e:
            print(f"Network error fetching verse: {e}")
            return None
    
    def _fetch_fallback(self, book: str, chapter: int, start_verse: int, end_verse: int) -> str:
        """Fallback when API is not available - return formatted reference"""
        if start_verse == end_verse:
            reference = f"{book} {chapter}:{start_verse}"
        else:
            reference = f"{book} {chapter}:{start_verse}-{end_verse}"
        
        # Return a placeholder that can be replaced with actual verses
        return f"[{reference}] Please configure BIBLE_API_KEY to fetch actual verse text from API.Bible"
    
    def _get_book_id(self, book_name: str) -> Optional[str]:
        """Convert book name to API.Bible book ID"""
        # Simplified mapping - extend as needed
        book_mapping = {
            # Old Testament
            'genesis': 'GEN', 'gen': 'GEN',
            'exodus': 'EXO', 'exo': 'EXO', 
            'leviticus': 'LEV', 'lev': 'LEV',
            'numbers': 'NUM', 'num': 'NUM',
            'deuteronomy': 'DEU', 'deu': 'DEU',
            'joshua': 'JOS', 'jos': 'JOS',
            'judges': 'JDG', 'jdg': 'JDG',
            'ruth': 'RUT', 'rut': 'RUT',
            '1 samuel': '1SA', '1sa': '1SA', '1 sam': '1SA',
            '2 samuel': '2SA', '2sa': '2SA', '2 sam': '2SA',
            '1 kings': '1KI', '1ki': '1KI', '1 kg': '1KI',
            '2 kings': '2KI', '2ki': '2KI', '2 kg': '2KI',
            'psalms': 'PSA', 'psa': 'PSA', 'psalm': 'PSA',
            'proverbs': 'PRO', 'pro': 'PRO',
            'isaiah': 'ISA', 'isa': 'ISA',
            'jeremiah': 'JER', 'jer': 'JER',
            # New Testament
            'matthew': 'MAT', 'mat': 'MAT', 'matt': 'MAT',
            'mark': 'MRK', 'mrk': 'MRK',
            'luke': 'LUK', 'luk': 'LUK',
            'john': 'JHN', 'jhn': 'JHN',
            'acts': 'ACT', 'act': 'ACT',
            'romans': 'ROM', 'rom': 'ROM',
            '1 corinthians': '1CO', '1co': '1CO', '1 cor': '1CO',
            '2 corinthians': '2CO', '2co': '2CO', '2 cor': '2CO',
            'galatians': 'GAL', 'gal': 'GAL',
            'ephesians': 'EPH', 'eph': 'EPH',
            'philippians': 'PHP', 'php': 'PHP',
            'colossians': 'COL', 'col': 'COL',
            '1 thessalonians': '1TH', '1th': '1TH', '1 thess': '1TH',
            '2 thessalonians': '2TH', '2th': '2TH', '2 thess': '2TH',
            '1 timothy': '1TI', '1ti': '1TI', '1 tim': '1TI',
            '2 timothy': '2TI', '2ti': '2TI', '2 tim': '2TI',
            'titus': 'TIT', 'tit': 'TIT',
            'hebrews': 'HEB', 'heb': 'HEB',
            'james': 'JAS', 'jas': 'JAS',
            '1 peter': '1PE', '1pe': '1PE', '1 pet': '1PE',
            '2 peter': '2PE', '2pe': '2PE', '2 pet': '2PE',
            '1 john': '1JN', '1jn': '1JN',
            '2 john': '2JN', '2jn': '2JN',
            '3 john': '3JN', '3jn': '3JN',
            'jude': 'JUD', 'jud': 'JUD',
            'revelation': 'REV', 'rev': 'REV',
        }
        return book_mapping.get(book_name.lower())
    
    def get_book_list(self) -> List[str]:
        """Return list of available books"""
        return [
            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
            "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
            "1 Kings", "2 Kings", "Psalms", "Proverbs", "Isaiah", "Jeremiah",
            "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
            "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
            "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
            "1 Timothy", "2 Timothy", "Titus", "Hebrews", "James",
            "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
        ]
