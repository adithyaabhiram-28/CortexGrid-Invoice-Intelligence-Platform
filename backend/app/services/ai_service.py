import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

class AIService:
    """
    Modular, optional AI-assisted document intelligence service using Google Gemini.
    Provides plain-language invoice summaries and discrepancy explanations.
    Deterministically falls back with informative status when GEMINI_API_KEY is not configured.
    """

    @staticmethod
    def get_api_key():
        return os.getenv('GEMINI_API_KEY', '').strip()

    @staticmethod
    def is_available():
        return bool(AIService.get_api_key())

    @staticmethod
    def analyze_invoice(invoice_dict: dict, extracted_text: str = "") -> dict:
        api_key = AIService.get_api_key()
        if not api_key:
            return {
                "available": False,
                "summary": None,
                "insights": None,
                "message": "AI analysis is optional. Add GEMINI_API_KEY in backend/.env to enable automated AI document insights."
            }

        prompt = f"""
You are an expert accounts payable finance AI assistant for CortexGrid.
Analyze this processed invoice and provide a concise, factual 2-sentence executive summary and brief explanation of any risks.

Invoice Details:
- Invoice Number: {invoice_dict.get('invoice_number')}
- Vendor: {invoice_dict.get('vendor_name')} (Match Status: {invoice_dict.get('vendor_match_status')})
- Invoice Date: {invoice_dict.get('invoice_date')}
- Total Amount: {invoice_dict.get('currency')} {invoice_dict.get('total_amount')}
- Linked PO: {invoice_dict.get('po_number') or invoice_dict.get('linked_po_number')} (PO Match: {invoice_dict.get('po_match_status')})
- Is Duplicate: {invoice_dict.get('is_duplicate')}
- Risk Level: {invoice_dict.get('risk_level')} (Score: {invoice_dict.get('risk_score')}/100)
- Risk Factors: {json.dumps(invoice_dict.get('risk_factors', []))}

Document Text Excerpt:
\"\"\"{extracted_text[:1200] if extracted_text else "No text excerpt"}\"\"\"

Respond with a JSON object in this exact format:
{{
  "summary": "2 concise sentences summarizing the invoice facts.",
  "risk_explanation": "Brief explanation of any inconsistencies or confirmations.",
  "recommended_action": "e.g. Approve for payment, Request corrected invoice, or Review PO variance."
}}
"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                result_raw = response.read().decode('utf-8')
                result_json = json.loads(result_raw)

                candidates = result_json.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    parts = candidates[0]['content'].get('parts', [])
                    if parts and 'text' in parts[0]:
                        raw_ai_text = parts[0]['text'].strip()
                        parsed_ai = json.loads(raw_ai_text)
                        return {
                            "available": True,
                            "summary": parsed_ai.get('summary'),
                            "insights": parsed_ai.get('risk_explanation'),
                            "recommended_action": parsed_ai.get('recommended_action'),
                            "message": "AI analysis generated successfully."
                        }

        except Exception as e:
            logger.warning(f"Gemini AI analysis request failed: {e}")
            return {
                "available": False,
                "summary": None,
                "insights": None,
                "message": f"AI service temporarily unavailable: {str(e)}"
            }

        return {
            "available": False,
            "summary": None,
            "insights": None,
            "message": "No response received from AI model."
        }
