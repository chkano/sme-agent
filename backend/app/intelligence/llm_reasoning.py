"""
LLM Reasoning - Converts scores into human-readable insights and recommendations
"""
from typing import Dict, Any
from openai import OpenAI
from app.config import settings


class LLMReasoning:
    """Uses LLM to generate explanations and recommendations"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4"  # Can be changed to gpt-3.5-turbo for cost optimization
    
    def generate_explanation(self, scores: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Generate human-readable explanation of credit assessment results
        """
        prompt = self._build_explanation_prompt(scores, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor explaining credit assessment results to SME owners in a clear, actionable way."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def generate_recommendations(self, scores: Dict[str, Any], risk_factors: list = None) -> list:
        """
        Generate actionable recommendations for improving credit readiness
        """
        prompt = self._build_recommendations_prompt(scores, risk_factors)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor providing specific, actionable recommendations for SME credit improvement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            # Parse recommendations (assuming bullet points)
            recommendations_text = response.choices[0].message.content
            recommendations = [
                rec.strip("- •").strip()
                for rec in recommendations_text.split("\n")
                if rec.strip() and (rec.strip().startswith("-") or rec.strip().startswith("•") or rec.strip()[0].isdigit())
            ]
            
            return recommendations if recommendations else [recommendations_text]
        
        except Exception as e:
            return [f"Unable to generate recommendations: {str(e)}"]
    
    def _build_explanation_prompt(self, scores: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Build prompt for explanation generation"""
        prompt = f"""Explain the following credit assessment results in plain language:
        
Financial Strength Score: {scores.get('financial_strength_score', 'N/A')}/100
Financial Health Index: {scores.get('fhi_score', 'N/A')}/100
Liquidity Risk Score: {scores.get('liquidity_risk', 'N/A')}/100

"""
        
        if context:
            prompt += f"Additional Context:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += "\nProvide a clear, concise explanation that helps the SME owner understand their current financial position and credit readiness."
        
        return prompt
    
    def _build_recommendations_prompt(self, scores: Dict[str, Any], risk_factors: list = None) -> str:
        """Build prompt for recommendations generation"""
        prompt = f"""Based on the following credit assessment, provide 3-5 specific, actionable recommendations:
        
Financial Strength Score: {scores.get('financial_strength_score', 'N/A')}/100
Financial Health Index: {scores.get('fhi_score', 'N/A')}/100
Liquidity Risk Score: {scores.get('liquidity_risk', 'N/A')}/100

"""
        
        if risk_factors:
            prompt += "Identified Risk Factors:\n"
            for risk in risk_factors[:5]:  # Limit to top 5
                prompt += f"- {risk.get('message', risk)}\n"
        
        prompt += "\nProvide practical recommendations that the SME can implement to improve their credit readiness."
        
        return prompt
