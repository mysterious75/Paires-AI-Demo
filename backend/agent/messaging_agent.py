"""
Messaging Agent - Core AI component for drafting replies
Handles context-aware reply generation with tone control
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI
import os
from datetime import datetime


class MessagingAgent:
    """Production-grade messaging agent for investor-founder communications"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "demo-key"))
        self.model = "gpt-4"
        
        self.tone_profiles = {
            "professional": "Formal, clear, and business-appropriate. Use proper salutations and closings.",
            "warm": "Friendly but professional. Show genuine interest and enthusiasm.",
            "concise": "Brief and to-the-point. Minimize filler while staying polite.",
            "detailed": "Thorough and comprehensive. Address all points mentioned.",
            "follow_up": "Gentle reminder tone. Reference previous context."
        }
        
        self.reply_templates = {
            "investor_inquiry": self._investor_inquiry_template,
            "founder_pitch": self._founder_pitch_template,
            "follow_up": self._follow_up_template,
            "meeting_request": self._meeting_request_template,
            "general_inquiry": self._general_inquiry_template
        }
    
    async def draft_reply(
        self,
        original_message: str,
        classification: Dict[str, Any],
        entities: Dict[str, Any],
        thread_context: List[Dict],
        tone: str = "professional",
        additional_context: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> str:
        """Generate an AI-drafted reply based on message context"""
        
        msg_type = classification.get("type", "general_inquiry")
        confidence = classification.get("confidence", 0.8)
        
        # Use provided sender_name or extract from entities
        if not sender_name:
            sender_name = entities.get("sender_name") or "there"
        
        # Build context for the AI
        context_parts = []
        
        # Add thread history summary
        if thread_context:
            thread_summary = self._summarize_thread(thread_context)
            context_parts.append(f"Conversation history: {thread_summary}")
        
        # Add extracted entities
        if entities:
            entity_summary = self._format_entities(entities)
            context_parts.append(f"Key information extracted: {entity_summary}")
        
        # Add tone instruction
        tone_instruction = self.tone_profiles.get(tone, self.tone_profiles["professional"])
        context_parts.append(f"Tone: {tone_instruction}")
        
        # Add any additional context
        if additional_context:
            context_parts.append(f"Additional context: {additional_context}")
        
        full_context = "\n".join(context_parts)
        
        # Generate reply using AI
        system_prompt = f"""You are an expert communications agent for Paires, an AI-first fundraising platform.

Your role: Draft professional, context-aware replies to messages between founders and investors.

Message type: {msg_type}
Confidence: {confidence}

Guidelines:
- Be concise but thorough
- Reference specific details from the original message
- Maintain the appropriate tone: {tone_instruction}
- Include clear next steps or calls to action
- Never make up information not provided in context
- If uncertain, acknowledge and offer to follow up

{full_context}"""
        
        user_prompt = f"""Draft a reply to this message:

---
FROM: {entities.get('sender_name', 'Unknown')}
SUBJECT: {entities.get('subject', 'No subject')}
MESSAGE: {original_message}
---

Draft a professional reply that addresses the sender's points and moves the conversation forward."""
        
        # For demo mode, use template-based replies
        if os.getenv("DEMO_MODE", "true").lower() == "true":
            return await self._generate_template_reply(
                msg_type, original_message, entities, tone, sender_name
            )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to template-based reply
            return await self._generate_template_reply(
                msg_type, original_message, entities, tone
            )
    
    async def _generate_template_reply(
        self,
        msg_type: str,
        original_message: str,
        entities: Dict,
        tone: str,
        sender_name: Optional[str] = None
    ) -> str:
        """Generate reply using templates (for demo/fallback)"""
        
        # Use provided sender_name or fall back to extracted name
        if not sender_name:
            sender_name = entities.get("sender_name") or "there"
        company = entities.get("company_name", "") or entities.get("company", "")
        funding_stage = entities.get("funding_stage", "")
        
        template_func = self.reply_templates.get(
            msg_type, 
            self._general_inquiry_template
        )
        
        return template_func(sender_name, company, funding_stage, original_message, tone)
    
    def _investor_inquiry_template(self, name, company, stage, message, tone):
        return f"""Dear {name},

Thank you for your interest in Paires and for reaching out.

{'We appreciate your inquiry about our platform. ' if 'warm' in tone else ''}Paires connects founders with the right investors from our engaged global network. Our AI-powered platform handles the outreach and relationship management that turns connections into meetings.

{'Based on your profile, ' + stage + ' stage companies are particularly well-suited for our network. ' if stage else ''}I'd be happy to schedule a brief call to discuss how Paires can support your investment objectives.

Would any of the following times work for a 15-minute introduction?
- This week: [Available slots]
- Next week: [Available slots]

Looking forward to connecting.

Best regards,
Paires Team"""
    
    def _founder_pitch_template(self, name, company, stage, message, tone):
        company_text = f"about {company} and " if company else ""
        return f"""Hi {name},

{'Great to hear from you! ' if 'warm' in tone else ''}Thanks for sharing {company_text}your fundraising plans.

Paires pairs founders with investors from our large, engaged global network. Our AI agents handle the outreach and manage relationships that convert into meetings.

{'As a ' + stage + ' stage company, ' if stage else ''}here's how we can help:
1. Match you with investors aligned with your sector and stage
2. Run personalized outreach on your behalf
3. Manage follow-ups and scheduling

To get started, I'll need:
- Your pitch deck
- Company one-pager
- Target raise amount

Once we have these, our AI will begin matching and outreach within 48 hours.

Shall we schedule a quick onboarding call?

Best,
Paires Team"""
    
    def _follow_up_template(self, name, company, stage, message, tone):
        company_text = f"help {company} " if company else ""
        return f"""Hi {name},

Following up on our previous conversation.

{'Just checking in on the items we discussed. ' if 'warm' in tone else ''}I wanted to make sure you have everything you need to move forward.

If you have any questions about Paires or need additional information, please don't hesitate to reach out.

We're here to help {company_text}successfully close your round.

Best regards,
Paires Team"""
    
    def _meeting_request_template(self, name, company, stage, message, tone):
        return f"""Hi {name},

Thank you for your interest in scheduling a meeting.

{'I\'d be happy to set that up for you. ' if 'warm' in tone else ''}Please let me know your availability and I'll coordinate the details.

For reference, our meetings typically cover:
- Platform overview and capabilities
- Investor network matching
- Onboarding requirements
- Timeline and next steps

Looking forward to our conversation.

Best,
Paires Team"""
    
    def _general_inquiry_template(self, name, company, stage, message, tone):
        return f"""Dear {name},

Thank you for reaching out to Paires.

{'We appreciate your message. ' if 'warm' in tone else ''}I'd be happy to help with your inquiry.

Paires is an AI-first platform that connects founders with investors through intelligent matching and automated outreach management.

Please let me know how I can assist you further, or if you'd like to schedule a call to discuss your specific needs.

Best regards,
Paires Team"""
    
    def _summarize_thread(self, thread_messages: List[Dict]) -> str:
        """Create a brief summary of conversation thread"""
        if not thread_messages:
            return "No previous messages."
        
        summary_parts = []
        for msg in thread_messages[-3:]:  # Last 3 messages
            sender = msg.get("sender", "Unknown")
            subject = msg.get("subject", "No subject")
            summary_parts.append(f"- {sender}: {subject}")
        
        return "\n".join(summary_parts)
    
    def _format_entities(self, entities: Dict) -> str:
        """Format extracted entities for context"""
        parts = []
        for key, value in entities.items():
            if value and key not in ["raw_text", "confidence_scores"]:
                parts.append(f"{key}: {value}")
        return ", ".join(parts) if parts else "None extracted"
