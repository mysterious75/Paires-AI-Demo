"""
Entity Extractor - Extracts key information from messages
Uses regex + NER for structured data extraction
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime


class EntityExtractor:
    """Extracts structured entities from unstructured messages"""
    
    def __init__(self):
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}',
            "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*',
            "money": r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B|K|k))?',
            "date": r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,?\s+\d{4})?\b',
            "percentage": r'\d+(?:\.\d+)?%'
        }
        
        self.funding_stages = [
            "pre-seed", "seed", "series a", "series b", "series c",
            "series d", "series e", "growth", "late stage", "ipo",
            "pre-ipo", "bridge", "convertible note", "safe"
        ]
        
        self.company_indicators = [
            "inc", "llc", "ltd", "corp", "co", "company", "technologies",
            "labs", "ventures", "capital", "partners"
        ]
    
    async def extract(self, text: str) -> Dict[str, Any]:
        """Extract all entities from text"""
        
        entities = {
            "raw_text": text[:500],  # First 500 chars for reference
            "emails": self._extract_emails(text),
            "phones": self._extract_phones(text),
            "urls": self._extract_urls(text),
            "money_amounts": self._extract_money(text),
            "dates": self._extract_dates(text),
            "percentages": self._extract_percentages(text),
            "company_name": self._extract_company(text),
            "sender_name": self._extract_sender_name(text),
            "funding_stage": self._extract_funding_stage(text),
            "ask_amount": self._extract_ask_amount(text),
            "topics": self._extract_topics(text),
            "confidence_scores": {}
        }
        
        # Calculate confidence scores for each extraction
        for key, value in entities.items():
            if key not in ["raw_text", "confidence_scores"]:
                entities["confidence_scores"][key] = self._calculate_confidence(key, value)
        
        return entities
    
    def _extract_emails(self, text: str) -> List[str]:
        return re.findall(self.patterns["email"], text)
    
    def _extract_phones(self, text: str) -> List[str]:
        return re.findall(self.patterns["phone"], text)
    
    def _extract_urls(self, text: str) -> List[str]:
        return re.findall(self.patterns["url"], text)
    
    def _extract_money(self, text: str) -> List[str]:
        return re.findall(self.patterns["money"], text, re.IGNORECASE)
    
    def _extract_dates(self, text: str) -> List[str]:
        return re.findall(self.patterns["date"], text, re.IGNORECASE)
    
    def _extract_percentages(self, text: str) -> List[str]:
        return re.findall(self.patterns["percentage"], text)
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from signature or body"""
        
        # Look for common signature patterns
        signature_patterns = [
            r'(?:Best regards|Sincerely|Thanks|Cheers),?\s*\n\s*(.+?)(?:\n|$)',
            r'--\s*\n(.+?)(?:\n|$)',
            r'(\w+(?:\s+\w+)?(?:\s+(?:Inc|LLC|Ltd|Corp|Co|Technologies|Labs|Ventures|Capital|Partners))?)',
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_company = match.group(1).strip()
                # Check if it looks like a company name
                if any(indicator in potential_company.lower() for indicator in self.company_indicators):
                    return potential_company
        
        return None
    
    def _extract_sender_name(self, text: str) -> Optional[str]:
        """Extract sender name from greeting or signature"""
        
        # Look for greeting patterns (more flexible)
        greeting_patterns = [
            r'(?:Hi|Hello|Hey|Dear)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s*[,!\n])',
            r'(?:Hi|Hello|Hey|Dear)\s+([A-Z][a-z]+)',
            r'I\'m\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'This is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'(?:Best regards|Sincerely|Thanks|Cheers|Regards),?\s*\n+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'--\s*\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'\n([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n',  # Name on its own line
        ]
        
        for pattern in greeting_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                name = match.group(1).strip().rstrip(',!').strip()
                # Filter out common non-name words
                skip_words = {"the", "you", "our", "your", "team", "all", "everyone", "there", "us"}
                if name.lower() not in skip_words and len(name) > 2:
                    return name
        
        # Try to extract from signature (name before company)
        signature_patterns = [
            r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\n.*(?:Inc|LLC|Ltd|Corp|Co|Capital|Ventures|Partners)',
            r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*\n.*@',
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_funding_stage(self, text: str) -> Optional[str]:
        """Extract funding stage from message"""
        
        text_lower = text.lower()
        
        for stage in self.funding_stages:
            if stage in text_lower:
                return stage.title()
        
        # Check for variations
        stage_variations = {
            "raising": "Seed",
            "looking to raise": "Seed",
            "series a round": "Series A",
            "series b round": "Series B",
            "ipo": "IPO",
            "going public": "IPO"
        }
        
        for variation, stage in stage_variations.items():
            if variation in text_lower:
                return stage
        
        return None
    
    def _extract_ask_amount(self, text: str) -> Optional[str]:
        """Extract the fundraising ask amount"""
        
        # Look for patterns like "raising $X" or "looking for $X"
        ask_patterns = [
            r'(?:raising|seeking|looking for|asking for)\s+(\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B|K|k))?)',
            r'(?:round|target|goal)\s+(?:of\s+)?(\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|M|B|K|k))?)',
        ]
        
        for pattern in ask_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fall back to any money amount if context suggests fundraising
        if any(word in text.lower() for word in ["raise", "fund", "invest"]):
            amounts = self._extract_money(text)
            if amounts:
                return amounts[0]
        
        return None
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from message"""
        
        topics = []
        text_lower = text.lower()
        
        topic_keywords = {
            "fundraising": ["raise", "fund", "invest", "capital", "round"],
            "technology": ["ai", "machine learning", "software", "platform", "api"],
            "partnership": ["partner", "collaborate", "integrate", "work together"],
            "meeting": ["meeting", "call", "schedule", "discuss", "talk"],
            "product": ["product", "feature", "service", "solution"],
            "market": ["market", "industry", "sector", "trend", "opportunity"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics if topics else ["general"]
    
    def _calculate_confidence(self, entity_type: str, value: Any) -> float:
        """Calculate confidence score for extracted entity"""
        
        if value is None or (isinstance(value, list) and len(value) == 0):
            return 0.0
        
        # Base confidence by entity type
        base_confidence = {
            "emails": 0.95,
            "phones": 0.90,
            "urls": 0.95,
            "money_amounts": 0.85,
            "dates": 0.80,
            "company_name": 0.70,
            "sender_name": 0.75,
            "funding_stage": 0.80,
            "ask_amount": 0.75,
            "topics": 0.70
        }.get(entity_type, 0.60)
        
        # Adjust based on value quality
        if isinstance(value, str) and len(value) > 2:
            return min(base_confidence + 0.05, 0.99)
        elif isinstance(value, list) and len(value) > 0:
            return min(base_confidence + 0.02, 0.99)
        
        return base_confidence
