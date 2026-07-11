"""
Tests for the Paires AI Messaging Agent
Demonstrates eval methodology and test coverage
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agent.classifier import MessageClassifier
from agent.extractor import EntityExtractor
from agent.summarizer import ConversationSummarizer
from guardrails.content_filter import ContentFilter
from evals.quality_tracker import QualityTracker


class TestClassifier:
    """Tests for message classification"""
    
    def setup_method(self):
        self.classifier = MessageClassifier()
    
    @pytest.mark.asyncio
    async def test_investor_inquiry_classification(self):
        """Test classification of investor inquiry messages"""
        message = "Hi, I'm interested in learning about your Series A round. We at Sequoia would love to discuss investment opportunities."
        subject = "Investment Interest"
        
        result = await self.classifier.classify(message, subject)
        
        assert result["type"] == "investor_inquiry"
        assert result["confidence"] > 0.6
        assert result["urgency"] in ["low", "medium", "high"]
        assert result["sentiment"] in ["positive", "neutral", "negative"]
    
    @pytest.mark.asyncio
    async def test_founder_pitch_classification(self):
        """Test classification of founder pitch messages"""
        message = "We are raising an $8M Series A at $50M pre-money valuation. Currently at $2M ARR with 80% gross margins."
        subject = "Raising Funds"
        
        result = await self.classifier.classify(message, subject)
        
        assert result["type"] == "founder_pitch"
        assert result["requires_human_review"] is not None
        assert "routing_suggestion" in result
    
    @pytest.mark.asyncio
    async def test_follow_up_classification(self):
        """Test classification of follow-up messages"""
        message = "Following up on our conversation last week. Have you had a chance to review our materials?"
        subject = "Following up"
        
        result = await self.classifier.classify(message, subject)
        
        assert result["type"] == "follow_up"
    
    @pytest.mark.asyncio
    async def test_meeting_request_classification(self):
        """Test classification of meeting requests"""
        message = "Would you be available for a 30-minute call next Tuesday or Wednesday afternoon?"
        subject = "Meeting Request"
        
        result = await self.classifier.classify(message, subject)
        
        assert result["type"] == "meeting_request"
    
    @pytest.mark.asyncio
    async def test_urgency_detection(self):
        """Test urgency level detection"""
        urgent_message = "URGENT: We need to close this round by Friday. Please respond ASAP."
        
        result = await self.classifier.classify(urgent_message, "Urgent")
        
        assert result["urgency"] == "high"
    
    def test_routing_suggestion(self):
        """Test that routing suggestions are provided"""
        import asyncio
        
        message = "I'd like to learn more about your platform."
        result = asyncio.run(self.classifier.classify(message, "Question"))
        
        assert "routing_suggestion" in result
        assert "department" in result["routing_suggestion"]
        assert "priority" in result["routing_suggestion"]
        assert "assign_to" in result["routing_suggestion"]


class TestExtractor:
    """Tests for entity extraction"""
    
    def setup_method(self):
        self.extractor = EntityExtractor()
    
    @pytest.mark.asyncio
    async def test_email_extraction(self):
        """Test email address extraction"""
        message = "Contact me at john.doe@example.com for more information."
        
        result = await self.extractor.extract(message)
        
        assert "john.doe@example.com" in result["emails"]
        assert result["confidence_scores"]["emails"] > 0.9
    
    @pytest.mark.asyncio
    async def test_money_amount_extraction(self):
        """Test monetary amount extraction"""
        message = "We are raising $5,000,000 in our Series A round."
        
        result = await self.extractor.extract(message)
        
        assert len(result["money_amounts"]) > 0
        assert "$5,000,000" in result["money_amounts"] or "5,000,000" in str(result["money_amounts"])
    
    @pytest.mark.asyncio
    async def test_company_name_extraction(self):
        """Test company name extraction"""
        message = "Best regards,\nJohn Smith\nCEO, TechCorp Inc."
        
        result = await self.extractor.extract(message)
        
        # Should extract company from signature
        assert result["company_name"] is not None
    
    @pytest.mark.asyncio
    async def test_funding_stage_extraction(self):
        """Test funding stage extraction"""
        message = "We are currently raising our Series B round."
        
        result = await self.extractor.extract(message)
        
        assert result["funding_stage"] is not None
        assert "series" in result["funding_stage"].lower()
    
    @pytest.mark.asyncio
    async def test_topic_extraction(self):
        """Test topic extraction"""
        message = "I'm interested in your AI platform and would like to discuss a potential partnership."
        
        result = await self.extractor.extract(message)
        
        assert len(result["topics"]) > 0
        assert any(topic in ["technology", "partnership", "ai"] for topic in result["topics"])
    
    @pytest.mark.asyncio
    async def test_confidence_scores(self):
        """Test that confidence scores are provided"""
        message = "Hello, I have a question about your product."
        
        result = await self.extractor.extract(message)
        
        assert "confidence_scores" in result
        assert len(result["confidence_scores"]) > 0


class TestContentFilter:
    """Tests for guardrails/content filtering"""
    
    def setup_method(self):
        self.filter = ContentFilter()
    
    @pytest.mark.asyncio
    async def test_pii_detection(self):
        """Test PII detection"""
        content = "My SSN is 123-45-6789 and my credit card is 1234-5678-9012-3456."
        
        result = await self.filter.check(content)
        
        assert result["passed"] is False
        assert len(result["checks"]["pii"]["pii_found"]) > 0
    
    @pytest.mark.asyncio
    async def test_inappropriate_content_detection(self):
        """Test inappropriate content detection"""
        content = "This is a scam and you should act now for guaranteed returns!"
        
        result = await self.filter.check(content)
        
        assert result["passed"] is False
    
    @pytest.mark.asyncio
    async def test_compliance_violations(self):
        """Test compliance violation detection"""
        content = "Invest now! Guaranteed 50% returns with no risk!"
        
        result = await self.filter.check(content)
        
        assert result["checks"]["compliance"]["passed"] is False
    
    @pytest.mark.asyncio
    async def test_length_validation(self):
        """Test content length validation"""
        short_content = "Hi"
        
        result = await self.filter.check(short_content)
        
        assert result["checks"]["length"]["passed"] is False
    
    @pytest.mark.asyncio
    async def test_professional_content_passes(self):
        """Test that professional content passes all checks"""
        content = """Dear John,

Thank you for your interest in our platform. I'd be happy to schedule a call to discuss your requirements.

Please let me know your availability for next week.

Best regards,
Sarah"""
        
        result = await self.filter.check(content)
        
        assert result["passed"] is True
        assert result["risk_level"] == "low"
    
    @pytest.mark.asyncio
    async def test_risk_score_calculation(self):
        """Test risk score calculation"""
        content = "Normal professional message with no issues."
        
        result = await self.filter.check(content)
        
        assert 0 <= result["risk_score"] <= 1
        assert result["risk_level"] in ["low", "medium", "high", "critical"]


class TestQualityTracker:
    """Tests for quality evaluation"""
    
    def setup_method(self):
        self.tracker = QualityTracker()
    
    @pytest.mark.asyncio
    async def test_draft_scoring(self):
        """Test draft quality scoring"""
        original = "I'm interested in investing in your company."
        draft = "Thank you for your interest. I'd be happy to discuss our investment opportunity with you."
        classification = {"type": "investor_inquiry", "confidence": 0.9}
        
        score = await self.tracker.score_draft(original, draft, classification)
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    @pytest.mark.asyncio
    async def test_dashboard_metrics(self):
        """Test dashboard metrics generation"""
        # Add some test data
        self.tracker.quality_scores.extend([0.8, 0.85, 0.9])
        self.tracker.drafts_log.append({
            "draft_id": "test-123",
            "quality_score": 0.85,
            "guardrail_passed": True,
            "timestamp": "2024-01-01T00:00:00"
        })
        
        metrics = self.tracker.get_dashboard_metrics()
        
        assert "total_drafts_generated" in metrics
        assert "avg_quality_score" in metrics
    
    @pytest.mark.asyncio
    async def test_accuracy_metrics(self):
        """Test accuracy metrics calculation"""
        self.tracker.classifications_log.extend([
            {"classification": {"confidence": 0.9}, "extraction": {"email": "test@test.com"}},
            {"classification": {"confidence": 0.85}, "extraction": {"phone": "123-456-7890"}}
        ])
        
        metrics = self.tracker.get_accuracy_metrics()
        
        assert "classification_accuracy" in metrics
        assert "extraction_accuracy" in metrics
        assert metrics["sample_size"] == 2
    
    @pytest.mark.asyncio
    async def test_approval_rate(self):
        """Test approval rate calculation"""
        self.tracker.approvals_log.extend([
            {"approved": True, "had_edits": False},
            {"approved": True, "had_edits": True},
            {"approved": False, "had_edits": False}
        ])
        
        rate = self.tracker.get_approval_rate()
        
        assert rate == 0.67  # 2/3 approved


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def setup_method(self):
        self.classifier = MessageClassifier()
        self.extractor = EntityExtractor()
        self.filter = ContentFilter()
    
    @pytest.mark.asyncio
    async def test_complete_message_processing(self):
        """Test complete message processing pipeline"""
        message = """Hi,

I'm Sarah from Sequoia Capital. We're interested in your Series A round.
Currently looking to deploy $10M in enterprise AI companies.

Would you be available for a call next week?

Best regards,
Sarah Chen
Partner, Sequoia Capital"""
        
        # Classify
        classification = await self.classifier.classify(message, "Investment Interest")
        assert classification["type"] == "investor_inquiry"
        
        # Extract
        entities = await self.extractor.extract(message)
        assert entities["sender_name"] is not None
        
        # Guardrails
        guardrail_result = await self.filter.check(message)
        assert guardrail_result["passed"] is True
    
    @pytest.mark.asyncio
    async def test_full_demo_flow(self):
        """Test the complete demo flow"""
        from data.sample_messages import SAMPLE_MESSAGES
        
        # Process each sample message
        for msg in SAMPLE_MESSAGES:
            classification = await self.classifier.classify(msg["body"], msg["subject"])
            entities = await self.extractor.extract(msg["body"])
            guardrails = await self.filter.check(msg["body"])
            
            # Verify all components work together
            assert classification["type"] is not None
            assert entities is not None
            assert guardrails is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
