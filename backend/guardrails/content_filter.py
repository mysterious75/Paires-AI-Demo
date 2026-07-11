"""
Content Filter / Guardrails - Ensures AI output meets quality and safety standards
Checks for PII, inappropriate content, tone, and compliance
"""

from typing import Dict, Any, List
import re


class ContentFilter:
    """Guardrails for AI-generated content"""
    
    def __init__(self):
        self.pii_patterns = {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "phone": r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        }
        
        self.inappropriate_words = [
            # Placeholder - in production, use a comprehensive list
            "spam", "scam", "guarantee", "no risk", "act now"
        ]
        
        self.compliance_rules = {
            "no_guarantees": [
                r'guarantee.*return',
                r'guaranteed.*profit',
                r'risk.?free'
            ],
            "no_pressure": [
                r'act now',
                r'limited time',
                r'expires? (?:today|soon|tomorrow)',
                r'last chance'
            ],
            "professional_tone": [
                r'!!{2,}',  # Multiple exclamation marks
                r'\b(?:lol|omg|wtf)\b',  # Informal abbreviations
                r'\$\$\$'  # Excessive symbols
            ]
        }
        
        self.length_limits = {
            "min_words": 20,
            "max_words": 300,
            "max_chars": 2000
        }
    
    async def check(self, content: str) -> Dict[str, Any]:
        """Run all guardrail checks on content"""
        
        results = {
            "passed": True,
            "checks": {},
            "issues": [],
            "warnings": [],
            "content_length": len(content),
            "word_count": len(content.split())
        }
        
        # Run each check
        pii_result = self._check_pii(content)
        results["checks"]["pii"] = pii_result
        
        inappropriate_result = self._check_inappropriate(content)
        results["checks"]["inappropriate"] = inappropriate_result
        
        compliance_result = self._check_compliance(content)
        results["checks"]["compliance"] = compliance_result
        
        length_result = self._check_length(content)
        results["checks"]["length"] = length_result
        
        tone_result = self._check_tone(content)
        results["checks"]["tone"] = tone_result
        
        # Aggregate results
        all_issues = []
        all_warnings = []
        
        for check_name, check_result in results["checks"].items():
            if not check_result["passed"]:
                results["passed"] = False
                all_issues.extend(check_result.get("issues", []))
            all_warnings.extend(check_result.get("warnings", []))
        
        results["issues"] = all_issues
        results["warnings"] = all_warnings
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(results["checks"])
        results["risk_score"] = risk_score
        results["risk_level"] = self._get_risk_level(risk_score)
        
        return results
    
    def _check_pii(self, content: str) -> Dict[str, Any]:
        """Check for personally identifiable information"""
        
        found_pii = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                found_pii.append({
                    "type": pii_type,
                    "count": len(matches),
                    "masked": self._mask_pii(matches[0])
                })
        
        passed = len(found_pii) == 0
        
        return {
            "passed": passed,
            "pii_found": found_pii,
            "issues": [f"PII detected: {p['type']}" for p in found_pii],
            "warnings": []
        }
    
    def _mask_pii(self, value: str) -> str:
        """Mask PII for safe logging"""
        if len(value) > 4:
            return "*" * (len(value) - 4) + value[-4:]
        return "****"
    
    def _check_inappropriate(self, content: str) -> Dict[str, Any]:
        """Check for inappropriate content"""
        
        content_lower = content.lower()
        found = [word for word in self.inappropriate_words if word in content_lower]
        
        return {
            "passed": len(found) == 0,
            "inappropriate_words": found,
            "issues": [f"Inappropriate content: '{word}'" for word in found],
            "warnings": []
        }
    
    def _check_compliance(self, content: str) -> Dict[str, Any]:
        """Check for compliance violations"""
        
        violations = []
        content_lower = content.lower()
        
        for rule_name, patterns in self.compliance_rules.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    violations.append({
                        "rule": rule_name,
                        "pattern": pattern
                    })
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "issues": [f"Compliance: {v['rule']}" for v in violations],
            "warnings": []
        }
    
    def _check_length(self, content: str) -> Dict[str, Any]:
        """Check content length"""
        
        word_count = len(content.split())
        char_count = len(content)
        
        issues = []
        warnings = []
        
        if word_count < self.length_limits["min_words"]:
            issues.append(f"Too short: {word_count} words (minimum: {self.length_limits['min_words']})")
        elif word_count < self.length_limits["min_words"] * 1.5:
            warnings.append(f"Content is short: {word_count} words")
        
        if word_count > self.length_limits["max_words"]:
            issues.append(f"Too long: {word_count} words (maximum: {self.length_limits['max_words']})")
        
        if char_count > self.length_limits["max_chars"]:
            issues.append(f"Character limit exceeded: {char_count} (maximum: {self.length_limits['max_chars']})")
        
        return {
            "passed": len(issues) == 0,
            "word_count": word_count,
            "char_count": char_count,
            "issues": issues,
            "warnings": warnings
        }
    
    def _check_tone(self, content: str) -> Dict[str, Any]:
        """Check tone appropriateness"""
        
        warnings = []
        content_lower = content.lower()
        
        # Check for overly casual tone
        casual_indicators = ["hey", "yo", "sup", "cool", "awesome"]
        casual_count = sum(1 for word in casual_indicators if word in content_lower)
        if casual_count > 1:
            warnings.append("Tone may be too casual")
        
        # Check for overly aggressive tone
        aggressive_indicators = ["must", "require", "demand", "insist"]
        aggressive_count = sum(1 for word in aggressive_indicators if word in content_lower)
        if aggressive_count > 2:
            warnings.append("Tone may be too aggressive")
        
        # Check for excessive punctuation
        if content.count("!") > 3:
            warnings.append("Excessive exclamation marks")
        
        if content.count("?") > 3:
            warnings.append("Excessive question marks")
        
        return {
            "passed": True,  # Tone issues are warnings, not blockers
            "tone_indicators": {
                "casual_count": casual_count,
                "aggressive_count": aggressive_count
            },
            "issues": [],
            "warnings": warnings
        }
    
    def _calculate_risk_score(self, checks: Dict) -> float:
        """Calculate overall risk score (0-1, higher = more risk)"""
        
        weights = {
            "pii": 0.40,
            "inappropriate": 0.25,
            "compliance": 0.25,
            "length": 0.05,
            "tone": 0.05
        }
        
        score = 0
        for check_name, check_result in checks.items():
            weight = weights.get(check_name, 0.1)
            if not check_result.get("passed", True):
                score += weight
        
        return round(min(score, 1.0), 2)
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score"""
        
        if score == 0:
            return "low"
        elif score < 0.3:
            return "medium"
        elif score < 0.6:
            return "high"
        else:
            return "critical"
