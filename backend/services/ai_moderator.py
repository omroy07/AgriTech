import os
import re
from datetime import datetime
import google.generativeai as genai
from backend.models import ForumThread, PostComment, UserReputation
from backend.extensions import db
from backend.utils.logger import logger


class AIModerator:
    """
    AI-Powered Content Moderation Service using Gemini API
    Handles sentiment analysis, toxicity detection, and auto-answering FAQs
    """
    
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Common farming FAQ patterns
        self.faq_patterns = {
            r'(how|when).*(plant|sow).*(rice|wheat|cotton)': 'planting_timing',
            r'(pest|insect).*(control|management)': 'pest_control',
            r'(fertilizer|nutrient).*(recommend|use)': 'fertilizer_advice',
            r'(loan|credit|subsidy)': 'financial_assistance',
            r'(weather|rain|monsoon)': 'weather_guidance',
            r'(price|market|sell)': 'market_info'
        }
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment and toxicity of user content
        Returns: dict with sentiment_score (-1 to 1) and toxicity_score (0 to 1)
        """
        try:
            prompt = f"""
            Analyze the following text for sentiment and potential harmful content.
            
            Text: "{text}"
            
            Provide your analysis in this exact JSON format:
            {{
                "sentiment": <number between -1.0 (very negative) and 1.0 (very positive)>,
                "toxicity": <number between 0.0 (safe) and 1.0 (toxic/harmful)>,
                "is_appropriate": <true/false>,
                "reason": "<brief explanation if inappropriate>"
            }}
            
            Consider context specific to farming communities. Mild frustration about crops or weather is normal.
            Only flag as toxic if it contains:
            - Personal attacks or harassment
            - Hate speech or discrimination
            - Spam or scam attempts
            - Misinformation that could harm farmers
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
            if json_match:
                import json
                analysis = json.loads(json_match.group())
                return {
                    'sentiment_score': float(analysis.get('sentiment', 0)),
                    'toxicity_score': float(analysis.get('toxicity', 0)),
                    'is_approved': analysis.get('is_appropriate', True),
                    'moderation_reason': analysis.get('reason', '')
                }
            else:
                # Fallback if JSON parsing fails
                logger.warning(f"Failed to parse AI moderation response: {result_text}")
                return {
                    'sentiment_score': 0.0,
                    'toxicity_score': 0.0,
                    'is_approved': True,
                    'moderation_reason': ''
                }
                
        except Exception as e:
            logger.error(f"AI moderation failed: {str(e)}")
            return {
                'sentiment_score': 0.0,
                'toxicity_score': 0.0,
                'is_approved': True,  # Default to approved on error
                'moderation_reason': ''
            }
    
    def detect_faq(self, question_text):
        """
        Detect if a question matches common FAQ patterns
        Returns: category string or None
        """
        question_lower = question_text.lower()
        for pattern, category in self.faq_patterns.items():
            if re.search(pattern, question_lower):
                return category
        return None
    
    def generate_auto_answer(self, thread_title, thread_content):
        """
        Automatically generate helpful answers for common FAQs
        Returns: dict with answer text and confidence score
        """
        try:
            faq_category = self.detect_faq(thread_title + " " + thread_content)
            
            if not faq_category:
                return None
            
            prompt = f"""
            You are an expert agricultural advisor helping farmers in India.
            
            Thread Title: {thread_title}
            Thread Content: {thread_content}
            
            Provide a helpful, accurate, and practical answer in 3-5 paragraphs.
            Use simple language suitable for farmers.
            Include specific actionable advice.
            If relevant, mention government schemes or resources.
            
            Format your response as plain text, friendly and supportive in tone.
            """
            
            response = self.model.generate_content(prompt)
            answer_text = response.text.strip()
            
            # Calculate confidence based on FAQ detection
            confidence = 0.85 if faq_category else 0.5
            
            return {
                'content': answer_text,
                'confidence': confidence,
                'category': faq_category,
                'is_ai_generated': True
            }
            
        except Exception as e:
            logger.error(f"Auto-answer generation failed: {str(e)}")
            return None
    
    def moderate_thread(self, thread):
        """
        Moderate a forum thread - analyze and update moderation fields
        """
        try:
            # Combine title and content for analysis
            full_text = f"{thread.title}\n\n{thread.content}"
            analysis = self.analyze_sentiment(full_text)
            
            # Update thread with moderation results
            thread.sentiment_score = analysis['sentiment_score']
            thread.toxicity_score = analysis['toxicity_score']
            thread.is_ai_approved = analysis['is_approved']
            
            if not analysis['is_approved']:
                thread.is_flagged = True
                thread.flag_reason = f"AI Auto-flagged: {analysis['moderation_reason']}"
            
            db.session.commit()
            
            # If approved and looks like FAQ, generate auto-answer
            if analysis['is_approved'] and analysis['toxicity_score'] < 0.3:
                auto_answer = self.generate_auto_answer(thread.title, thread.content)
                if auto_answer and auto_answer['confidence'] > 0.7:
                    return auto_answer
            
            return analysis
            
        except Exception as e:
            logger.error(f"Thread moderation failed: {str(e)}")
            return None
    
    def moderate_comment(self, comment):
        """
        Moderate a comment - analyze sentiment and flag if needed
        """
        try:
            analysis = self.analyze_sentiment(comment.content)
            
            comment.sentiment_score = analysis['sentiment_score']
            comment.is_ai_approved = analysis['is_approved']
            
            if not analysis['is_approved']:
                comment.is_flagged = True
                comment.flag_reason = f"AI Auto-flagged: {analysis['moderation_reason']}"
            
            db.session.commit()
            return analysis
            
        except Exception as e:
            logger.error(f"Comment moderation failed: {str(e)}")
            return None
    
    def search_knowledge_base(self, query, limit=5):
        """
        Use AI to search through existing threads and find relevant answers
        Returns: list of relevant thread IDs with relevance scores
        """
        try:
            # Get recent threads (simplified - in production, use vector search)
            threads = ForumThread.query.filter_by(is_ai_approved=True).order_by(
                ForumThread.last_activity.desc()
            ).limit(50).all()
            
            if not threads:
                return []
            
            # Create context from threads
            thread_context = "\n\n".join([
                f"[Thread {t.id}] {t.title}: {t.content[:200]}..."
                for t in threads
            ])
            
            prompt = f"""
            User Query: "{query}"
            
            Available Threads:
            {thread_context}
            
            Which threads are most relevant to answer this query?
            Return a JSON array of thread IDs sorted by relevance (most relevant first), maximum {limit} items.
            Format: [{{"thread_id": <id>, "relevance": <0.0 to 1.0>}}]
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            import json
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group())
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {str(e)}")
            return []


# Singleton instance
ai_moderator = AIModerator()
