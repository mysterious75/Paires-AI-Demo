"""
Quality Tracker - Evals and metrics for AI-generated content
Tracks accuracy, quality, and performance over time
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict


class QualityTracker:
    """Tracks quality metrics for AI-generated content"""
    
    def __init__(self):
        # In-memory storage (would be DB in production)
        self.drafts_log: List[Dict] = []
        self.approvals_log: List[Dict] = []
        self.classifications_log: List[Dict] = []
        self.response_times: List[float] = []
        self.quality_scores: List[float] = []
        self.guardrail_results: List[Dict] = []
    
    async def score_draft(
        self,
        original: str,
        draft: str,
        classification: Dict
    ) -> float:
        """Score a draft on multiple quality dimensions"""
        
        scores = {
            "relevance": self._score_relevance(original, draft),
            "tone": self._score_tone(draft, classification),
            "completeness": self._score_completeness(original, draft),
            "professionalism": self._score_professionalism(draft),
            "conciseness": self._score_conciseness(draft)
        }
        
        # Weighted average
        weights = {
            "relevance": 0.30,
            "tone": 0.20,
            "completeness": 0.25,
            "professionalism": 0.15,
            "conciseness": 0.10
        }
        
        overall_score = sum(
            scores[k] * weights[k] for k in scores
        )
        
        self.quality_scores.append(overall_score)
        
        return round(overall_score, 2)
    
    def _score_relevance(self, original: str, draft: str) -> float:
        """Score how relevant the draft is to the original message"""
        
        original_words = set(original.lower().split())
        draft_words = set(draft.lower().split())
        
        # Simple word overlap metric
        if not original_words:
            return 0.5
        
        overlap = len(original_words & draft_words)
        relevance = min(overlap / len(original_words) * 2, 1.0)
        
        # Check if key topics are addressed
        key_terms = ["meeting", "call", "invest", "fund", "pitch", "schedule"]
        addressed = sum(1 for term in key_terms if term in draft.lower())
        topic_score = min(addressed / 3, 1.0)
        
        return (relevance * 0.6 + topic_score * 0.4)
    
    def _score_tone(self, draft: str, classification: Dict) -> float:
        """Score the tone appropriateness"""
        
        score = 0.8  # Base score
        
        # Check for professional language
        professional_indicators = [
            "dear", "sincerely", "best regards", "thank you",
            "please", "would", "appreciate"
        ]
        
        professional_count = sum(
            1 for ind in professional_indicators 
            if ind in draft.lower()
        )
        score += min(professional_count * 0.05, 0.15)
        
        # Check for appropriate formality
        informal_words = ["hey", "gonna", "wanna", "lol", "omg"]
        informal_count = sum(1 for word in informal_words if word in draft.lower())
        score -= informal_count * 0.1
        
        return max(min(score, 1.0), 0.0)
    
    def _score_completeness(self, original: str, draft: str) -> float:
        """Score how completely the draft addresses the original"""
        
        # Check if draft is longer than greeting only
        word_count = len(draft.split())
        
        if word_count < 20:
            return 0.4
        elif word_count < 50:
            return 0.6
        elif word_count < 100:
            return 0.8
        else:
            return 0.9
    
    def _score_professionalism(self, draft: str) -> float:
        """Score professionalism of the draft"""
        
        score = 0.85  # Base
        
        # Check for proper grammar indicators
        has_proper_greeting = any(g in draft.lower() for g in ["dear", "hello", "hi"])
        has_proper_closing = any(c in draft.lower() for c in ["regards", "sincerely", "best", "thank"])
        
        if has_proper_greeting:
            score += 0.05
        if has_proper_closing:
            score += 0.05
        
        # Penalize excessive exclamation marks
        if draft.count("!") > 2:
            score -= 0.1
        
        return max(min(score, 1.0), 0.0)
    
    def _score_conciseness(self, draft: str) -> float:
        """Score how concise the draft is"""
        
        word_count = len(draft.split())
        
        # Ideal length is 50-150 words
        if word_count < 30:
            return 0.6  # Too short
        elif word_count < 50:
            return 0.8
        elif word_count <= 150:
            return 1.0  # Ideal
        elif word_count <= 200:
            return 0.8
        else:
            return 0.6  # Too long
    
    async def log_inbound_processing(
        self,
        message_id: str,
        classification: Dict,
        extraction: Dict
    ):
        """Log inbound message processing metrics"""
        
        self.classifications_log.append({
            "message_id": message_id,
            "classification": classification,
            "extraction": extraction,
            "timestamp": datetime.now().isoformat()
        })
    
    async def log_draft_generation(
        self,
        draft_id: str,
        quality_score: float,
        guardrail_passed: bool
    ):
        """Log draft generation metrics"""
        
        self.drafts_log.append({
            "draft_id": draft_id,
            "quality_score": quality_score,
            "guardrail_passed": guardrail_passed,
            "timestamp": datetime.now().isoformat()
        })
        
        self.guardrail_results.append({
            "draft_id": draft_id,
            "passed": guardrail_passed,
            "timestamp": datetime.now().isoformat()
        })
    
    async def log_approval(
        self,
        draft_id: str,
        approved: bool,
        had_edits: bool,
        feedback: Optional[str]
    ):
        """Log human approval metrics"""
        
        self.approvals_log.append({
            "draft_id": draft_id,
            "approved": approved,
            "had_edits": had_edits,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics"""
        
        total_drafts = len(self.drafts_log)
        total_approvals = len(self.approvals_log)
        
        approved_count = sum(1 for a in self.approvals_log if a["approved"])
        edited_count = sum(1 for a in self.approvals_log if a["had_edits"])
        
        guardrail_passed = sum(1 for g in self.guardrail_results if g["passed"])
        
        return {
            "total_messages_processed": len(self.classifications_log),
            "total_drafts_generated": total_drafts,
            "total_approvals": total_approvals,
            "approval_rate": approved_count / total_approvals if total_approvals > 0 else 0,
            "edit_rate": edited_count / total_approvals if total_approvals > 0 else 0,
            "avg_quality_score": sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0,
            "guardrail_pass_rate": guardrail_passed / total_drafts if total_drafts > 0 else 0,
            "classification_accuracy": self.get_classification_accuracy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_evals(self, limit: int = 20) -> List[Dict]:
        """Get recent evaluation results"""
        
        recent = self.drafts_log[-limit:] if self.drafts_log else []
        
        return [
            {
                "draft_id": d["draft_id"],
                "quality_score": d["quality_score"],
                "guardrail_passed": d["guardrail_passed"],
                "timestamp": d["timestamp"]
            }
            for d in reversed(recent)
        ]
    
    def get_accuracy_metrics(self) -> Dict[str, Any]:
        """Get classification and extraction accuracy"""
        
        if not self.classifications_log:
            return {
                "classification_accuracy": 0,
                "extraction_accuracy": 0,
                "sample_size": 0
            }
        
        # Calculate classification accuracy (based on confidence scores)
        confidences = [
            c["classification"].get("confidence", 0.5)
            for c in self.classifications_log
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Calculate extraction completeness
        extraction_completeness = []
        for log in self.classifications_log:
            extraction = log.get("extraction", {})
            fields_extracted = sum(
                1 for k, v in extraction.items()
                if v and k not in ["raw_text", "confidence_scores"]
            )
            total_fields = len([k for k in extraction.keys() if k not in ["raw_text", "confidence_scores"]])
            if total_fields > 0:
                extraction_completeness.append(fields_extracted / total_fields)
        
        avg_extraction = sum(extraction_completeness) / len(extraction_completeness) if extraction_completeness else 0
        
        return {
            "classification_accuracy": round(avg_confidence, 2),
            "extraction_accuracy": round(avg_extraction, 2),
            "sample_size": len(self.classifications_log)
        }
    
    def get_approval_rate(self) -> float:
        """Get approval rate"""
        if not self.approvals_log:
            return 0
        approved = sum(1 for a in self.approvals_log if a["approved"])
        return round(approved / len(self.approvals_log), 2)
    
    def get_avg_quality_score(self) -> float:
        """Get average quality score"""
        if not self.quality_scores:
            return 0
        return round(sum(self.quality_scores) / len(self.quality_scores), 2)
    
    def get_by_classification(self) -> Dict[str, int]:
        """Get message count by classification type"""
        
        counts = defaultdict(int)
        for log in self.classifications_log:
            msg_type = log["classification"].get("type", "unknown")
            counts[msg_type] += 1
        
        return dict(counts)
    
    def get_by_hour(self) -> Dict[str, int]:
        """Get message count by hour"""
        
        counts = defaultdict(int)
        for log in self.classifications_log:
            try:
                hour = datetime.fromisoformat(log["timestamp"]).hour
                counts[f"{hour:02d}:00"] += 1
            except:
                pass
        
        return dict(sorted(counts.items()))
    
    def get_avg_response_time(self) -> float:
        """Get average response time in ms"""
        if not self.response_times:
            return 0
        return round(sum(self.response_times) / len(self.response_times), 2)
    
    def get_classification_accuracy(self) -> float:
        """Get classification accuracy"""
        if not self.classifications_log:
            return 0
        confidences = [
            c["classification"].get("confidence", 0.5)
            for c in self.classifications_log
        ]
        return round(sum(confidences) / len(confidences), 2) if confidences else 0
    
    def get_extraction_accuracy(self) -> float:
        """Get extraction accuracy"""
        metrics = self.get_accuracy_metrics()
        return metrics.get("extraction_accuracy", 0)
    
    def get_guardrail_pass_rate(self) -> float:
        """Get guardrail pass rate"""
        if not self.guardrail_results:
            return 0
        passed = sum(1 for g in self.guardrail_results if g["passed"])
        return round(passed / len(self.guardrail_results), 2)
    
    def get_human_edit_rate(self) -> float:
        """Get human edit rate"""
        if not self.approvals_log:
            return 0
        edited = sum(1 for a in self.approvals_log if a["had_edits"])
        return round(edited / len(self.approvals_log), 2)
