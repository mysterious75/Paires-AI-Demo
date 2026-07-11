"""
Conversation Summarizer - Generates concise summaries of message threads
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
import os


class ConversationSummarizer:
    """Summarizes conversation threads for quick context"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "demo-key"))
    
    async def summarize(self, messages: List[Dict]) -> Dict[str, Any]:
        """Generate a comprehensive summary of the conversation"""
        
        if not messages:
            return {
                "summary": "No messages in this thread.",
                "key_points": [],
                "action_items": [],
                "next_steps": [],
                "sentiment": "neutral"
            }
        
        # Use AI summarization in non-demo mode
        if os.getenv("DEMO_MODE", "true").lower() != "true":
            return await self._ai_summarize(messages)
        
        # Template-based summary for demo
        return self._template_summarize(messages)
    
    def _template_summarize(self, messages: List[Dict]) -> Dict[str, Any]:
        """Generate summary using templates"""
        
        # Analyze messages
        senders = set()
        topics = []
        has_meeting_request = False
        has_funding_mention = False
        latest_subject = ""
        
        for msg in messages:
            senders.add(msg.get("sender", "Unknown"))
            
            body = msg.get("body", "").lower()
            subject = msg.get("subject", "")
            
            if subject:
                latest_subject = subject
            
            if any(word in body for word in ["meeting", "call", "schedule"]):
                has_meeting_request = True
            
            if any(word in body for word in ["fund", "raise", "invest", "round"]):
                has_funding_mention = True
            
            # Extract topics
            if "ai" in body or "artificial intelligence" in body:
                topics.append("AI/Technology")
            if "investor" in body:
                topics.append("Investor Relations")
            if "pitch" in body or "deck" in body:
                topics.append("Pitch Materials")
        
        # Build summary
        summary_parts = []
        summary_parts.append(f"Conversation between {', '.join(senders)}.")
        
        if latest_subject:
            summary_parts.append(f"Primary topic: {latest_subject}.")
        
        if has_funding_mention:
            summary_parts.append("Discussion includes fundraising/investment elements.")
        
        if has_meeting_request:
            summary_parts.append("Meeting scheduling has been discussed.")
        
        summary = " ".join(summary_parts)
        
        # Key points
        key_points = []
        if has_funding_mention:
            key_points.append("Fundraising or investment opportunity discussed")
        if has_meeting_request:
            key_points.append("Meeting scheduling requested")
        if topics:
            key_points.append(f"Main topics: {', '.join(set(topics))}")
        key_points.append(f"{len(messages)} messages in thread")
        
        # Action items
        action_items = []
        if has_meeting_request:
            action_items.append("Schedule meeting with parties involved")
        if has_funding_mention:
            action_items.append("Review pitch materials and funding details")
        action_items.append("Follow up on open items")
        
        # Next steps
        next_steps = []
        if has_meeting_request:
            next_steps.append("Send calendar invite")
        else:
            next_steps.append("Send follow-up message")
        next_steps.append("Update CRM with conversation status")
        
        return {
            "summary": summary,
            "key_points": key_points[:5],  # Max 5 key points
            "action_items": action_items[:3],  # Max 3 action items
            "next_steps": next_steps[:3],  # Max 3 next steps
            "sentiment": self._analyze_sentiment(messages),
            "participants": list(senders),
            "message_count": len(messages),
            "latest_activity": messages[-1].get("created_at", "Unknown") if messages else "Unknown"
        }
    
    async def _ai_summarize(self, messages: List[Dict]) -> Dict[str, Any]:
        """AI-powered conversation summarization"""
        
        # Format messages for the AI
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(
                f"From: {msg.get('sender', 'Unknown')}\n"
                f"Subject: {msg.get('subject', 'No subject')}\n"
                f"Message: {msg.get('body', '')[:500]}\n"
                f"---"
            )
        
        conversation_text = "\n".join(formatted_messages)
        
        system_prompt = """You are a conversation summarizer for Paires, an AI fundraising platform.

Create a concise summary of the conversation including:
1. Summary (2-3 sentences)
2. Key points (bullet points)
3. Action items (what needs to be done)
4. Next steps (recommended follow-ups)
5. Sentiment (positive/neutral/negative)

Focus on:
- Investment/fundraising details
- Meeting requests
- Commitments made
- Open questions

Respond in JSON format."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Summarize this conversation:\n\n{conversation_text}"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return eval(response.choices[0].message.content)
            
        except Exception as e:
            # Fallback to template-based
            return self._template_summarize(messages)
    
    def _analyze_sentiment(self, messages: List[Dict]) -> str:
        """Analyze overall sentiment of the conversation"""
        
        positive_words = ["thank", "great", "excellent", "appreciate", "excited", "interested", "happy"]
        negative_words = ["concern", "issue", "problem", "disappointed", "frustrated", "unfortunately", "regret"]
        
        pos_count = 0
        neg_count = 0
        
        for msg in messages:
            body = msg.get("body", "").lower()
            pos_count += sum(1 for word in positive_words if word in body)
            neg_count += sum(1 for word in negative_words if word in body)
        
        if pos_count > neg_count * 1.5:
            return "positive"
        elif neg_count > pos_count * 1.5:
            return "negative"
        else:
            return "neutral"
