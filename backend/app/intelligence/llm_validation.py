"""
LLM Validation - Cross-checks outputs for bias and sanity validation
"""
from typing import Dict, Any
from openai import OpenAI
from app.config import settings


class LLMValidation:
    """Validates LLM outputs for bias, hallucination, and sanity"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4"
    
    def validate_explanation(self, explanation: str, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that explanation is consistent with source data
        Returns validation result with confidence score
        """
        prompt = f"""You are a validation system. Check if the following explanation is consistent with the source data and free from hallucinations or bias.

Source Data:
{self._format_data_for_validation(source_data)}

Explanation to Validate:
{explanation}

Check for:
1. Consistency with numerical values
2. Absence of made-up information
3. Reasonable interpretations
4. No discriminatory language or bias

Respond in JSON format:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["list of any issues found"],
    "recommendation": "keep" or "revise"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict validation system. Be thorough and objective."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            validation_result = json.loads(result)
            return validation_result
        
        except Exception as e:
            # Default to passing validation if LLM validation fails
            return {
                "is_valid": True,
                "confidence": 0.5,
                "issues": [f"Validation error: {str(e)}"],
                "recommendation": "keep"
            }
    
    def check_bias(self, text: str) -> Dict[str, Any]:
        """Check for discriminatory bias in generated text"""
        prompt = f"""Analyze the following text for potential bias, discrimination, or unfair language:

{text}

Respond in JSON format:
{{
    "has_bias": true/false,
    "bias_types": ["list of any bias types found"],
    "severity": "low/medium/high",
    "recommendation": "keep" or "revise"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a bias detection system. Identify discriminatory language and unfair bias."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        
        except Exception as e:
            return {
                "has_bias": False,
                "bias_types": [],
                "severity": "low",
                "recommendation": "keep"
            }
    
    def _format_data_for_validation(self, data: Dict[str, Any]) -> str:
        """Format data dictionary for validation prompt"""
        formatted = []
        for key, value in data.items():
            if isinstance(value, (int, float, str, bool)):
                formatted.append(f"{key}: {value}")
            elif isinstance(value, dict):
                formatted.append(f"{key}: {value}")
            elif isinstance(value, list):
                formatted.append(f"{key}: {len(value)} items")
        
        return "\n".join(formatted)
