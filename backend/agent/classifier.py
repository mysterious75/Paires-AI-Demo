"""
Message Classifier - Categorizes inbound messages by type and intent
Uses LLM + rule-based hybrid approach for accuracy
"""

from typing import Dict, Any, List
from openai import OpenAI
import os
import re


class MessageClassifier:
    """Classifies messages into categories for routing"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "demo-key"))
        
        self.categories = {
            "investor_inquiry": {
                "description": "Investor asking about platform, deals, or opportunities",
                "keywords": ["invest", "fund", "portfolio", "deal", "opportunity", "return", "exit"]
            },
            "founder_pitch": {
                "description": "Founder seeking investment or platform services",
                "keywords": ["raise", "fundraise", "pitch", "deck", "valuation", "seed", "series"]
            },
            "follow_up": {
                "description": "Continuation of existing conversation",
                "keywords": ["following up", "checking in", "previous", "last time", "update"]
            },
            "meeting_request": {
                "description": "Request to schedule a meeting or call",
                "keywords": ["meeting", "call", "schedule", "available", "calendar", "time"]
            },
            "general_inquiry": {
                "description": "General questions about the platform",
                "keywords": ["question", "how", "what", "information", "learn", "details"]
            },
            "partnership": {
                "description": "Business development or partnership proposal",
                "keywords": ["partner", "collaborate", "integration", "api", "white-label"]
            },
            "support": {
                "description": "Technical support or issue report",
                "keywords": ["issue", "problem", "error", "bug", "help", "not working"]
            }
        }
        
        self.urgency_indicators = {
            "high": ["urgent", "asap", "immediately", "deadline", "today", "critical"],
            "medium": ["soon", "this week", "follow up", "pending"],
            "low": ["whenever", "no rush", "eventually", "thinking about"]
        }
    
    async def classify(self, message_body: str, subject: str = "") -> Dict[str, Any]:
        """Classify a message by type, intent, and urgency"""
        
        # Combine subject and body for classification
        full_text = f"Subject: {subject}\n\nBody: {message_body}"
        
        # Use AI classification in non-demo mode
        if os.getenv("DEMO_MODE", "true").lower() != "true":
            return await self._ai_classify(full_text)
        
        # Rule-based classification for demo
        return self._rule_based_classify(full_text, subject)
    
    def _rule_based_classify(self, text: str, subject: str) -> Dict[str, Any]:
        """Rule-based classification for demo mode"""
        
        text_lower = text.lower()
        
        # Score each category
        scores = {}
        for category, config in self.categories.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 1
            scores[category] = score
        
        # Get top category
        max_score = max(scores.values())
        if max_score == 0:
            predicted_type = "general_inquiry"
            confidence = 0.5
        else:
            predicted_type = max(scores, key=scores.get)
            confidence = min(0.6 + (max_score * 0.1), 0.95)
        
        # Detect urgency
        urgency = "low"
        for level, indicators in self.urgency_indicators.items():
            for indicator in indicators:
                if indicator in text_lower:
                    urgency = level
                    break
        
        # Detect sentiment (simple rule-based)
        positive_words = ["thank", "great", "excellent", "appreciate", "excited", "interested"]
        negative_words = ["concern", "issue", "problem", "disappointed", "frustrated", "unfortunately"]
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "type": predicted_type,
            "confidence": confidence,
            "all_scores": scores,
            "urgency": urgency,
            "sentiment": sentiment,
            "requires_human_review": confidence < 0.7,
            "routing_suggestion": self._get_routing(predicted_type)
        }
    
    async def _ai_classify(self, text: str) -> Dict[str, Any]:
        """AI-powered classification using LLM"""
        
        system_prompt = """You are a message classifier for Paires, an AI fundraising platform.

Classify the message into one of these categories:
- investor_inquiry: Investor asking about platform/deals
- founder_pitch: Founder seeking investment
- follow_up: Continuation of conversation
- meeting_request: Scheduling request
- general_inquiry: General questions
- partnership: Business development
- support: Technical issues

Also determine:
- Urgency: high/medium/low
- Sentiment: positive/neutral/negative
- Whether human review is needed

Respond in JSON format."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = eval(response.choices[0].message.content)
            result["requires_human_review"] = result.get("confidence", 0.8) < 0.7
            result["routing_suggestion"] = self._get_routing(result.get("type", "general_inquiry"))
            
            return result
            
        except Exception as e:
            # Fallback to rule-based
            return self._rule_based_classify(text, "")
    
    def _get_routing(self, msg_type: str) -> Dict[str, str]:
        """Suggest routing based on message type"""
        
        routing_map = {
            "investor_inquiry": {
                "department": "investor_relations",
                "priority": "high",
                "assign_to": "IR Team"
            },
            "founder_pitch": {
                "department": "deal_flow",
                "priority": "medium",
                "assign_to": "Deal Team"
            },
            "follow_up": {
                "department": "general",
                "priority": "low",
                "assign_to": "Auto-reply"
            },
            "meeting_request": {
                "department": "scheduling",
                "priority": "medium",
                "assign_to": "Calendar Bot"
            },
            "general_inquiry": {
                "department": "support",
                "priority": "medium",
                "assign_to": "Support Team"
            },
            "partnership": {
                "department": "business_dev",
                "priority": "high",
                "assign_to": "BD Team"
            },
            "support": {
                "department": "technical",
                "priority": "high",
                "assign_to": "Tech Support"
            }
        }
        
        return routing_map.get(msg_type, routing_map["general_inquiry"])
