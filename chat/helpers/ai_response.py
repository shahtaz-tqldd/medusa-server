from google import genai
from django.conf import settings
from chat.v1.res_msg import CHAT_FAILED_MESSAGE
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Intent categories for the chat agent"""
    SMALL_TALK = "small_talk"
    SKILLS = "skills"
    EXPERTISE = "expertise"
    PROJECTS = "projects"
    WORK_EXPERIENCE = "work_experience"
    SCHEDULE_MEETING = "schedule_meeting"
    OUT_OF_SCOPE = "out_of_scope"


class IntentContentProvider:
    """Provides static content for each intent"""
    
    @staticmethod
    def get_content(intent: Intent) -> dict:
        """Returns content dictionary for given intent"""
        
        content_map = {
            Intent.SMALL_TALK: {
                "context": """
                You are Era, Shahtaz's AI assistant. Be friendly, conversational, and helpful.
                You can engage in light conversation while staying professional.
                Common topics: greetings, how you can help, general questions about the portfolio.
                """,
                "guidelines": "Keep it very brief (1-2 sentences). Be warm and naturally guide towards how you can help."
            },
            
            Intent.SKILLS: {
                "context": """
                Shahtaz's Technical Skills:
                
                Frontend: React.js, Next.js, TypeScript, Tailwind CSS, Redux, RTK Query, Tanstack Query, ShadCN, Material UI
                Backend: Node.js, Express.js, Python, Django, FastAPI
                Databases: MongoDB, PostgreSQL
                Tools: Docker, Git, AWS, WebSocket, Playwright
                AI: Agent Development, Google ADK, RAG, Vector Database, Pinecone, Vertex AI
                """,
                "guidelines": "List 3-5 most relevant skills based on query. Keep it to 2-3 sentences max. Offer to elaborate on specific areas."
            },
            
            Intent.EXPERTISE: {
                "context": """
                Shahtaz's Core Expertise (2+ years experience):
                
                1. Full-Stack Development (React/Next.js + Node.js/Django)
                2. Real-Time Systems (Socket.IO, WebSockets)
                3. SaaS & ERP Solutions (HRM, Restaurant Management)
                4. CRM & Business Platforms (Dashboards, Analytics)
                5. AI Agent Development(AI Chatbot Agent)
                6. E-commerce Solutions (Full shopping platforms)
                """,
                "guidelines": "Mention 2-3 key areas. 2-3 sentences total. Ask what area they want to know more about."
            },
            
            Intent.PROJECTS: {
                "context": """
                Shahtaz's Project Categories:
                
                1. SaaS & ERP: Real-time HRM systems, Restaurant management platforms
                2. CRM & Business: Courier dashboards, Employee tracking systems
                3. AI Agent: Chatbot Assistant for Personal Portfolio, AI Chatbot Assistant for Shopping
                4. Business Sites: Landing pages with animations, Third-party integrations
                5. ECommerce & Blogs: Shopping platforms, Content management systems
                """,
                "guidelines": "List 3-4 project types briefly. 2-3 sentences max. Ask which type they'd like details on."
            },
            
            Intent.WORK_EXPERIENCE: {
                "context": """
                Shahtaz's Experience:
                - 2+ years as Full-Stack Developer
                - Built 15+ production applications
                - Specializes in SaaS, ERP, CRM, Ecommerce and AI Agent Development
                - Real-time features and AI integration expert
                - Works with modern tech stacks (React, Next JS, Node JS, Django, FastAPI)
                Professional Experience:
                - Worked at Echologyx Ltd. an UK based Software Company since March, 2024
                - At Echologyx Working in ELX Chatbot's AI Agent Development in FastAPI with Google ADK
                - Worked in ELX Chatbot's Backend with Django and PostgreSQL
                - Worked at AyyKori a fin-tech startup as a MERN Stack Developer
                - Worked in their MVP's backend and frontend along with their HRM Project
                """,
                "guidelines": "Highlight 2-3 key points. Keep to 2-3 sentences. Offer to discuss specific experience areas."
            },
            
            Intent.SCHEDULE_MEETING: {
                "context": f"""
                Meeting Link: {settings.MEETING_LINK}
                
                Available for:
                - Project consultations
                - Technical discussions
                - Collaboration opportunities
                - Freelance inquiries
                """,
                "guidelines": "Confirm they want to schedule first. Share link with 1 sentence context. Ask what they'd like to discuss."
            },
            
            Intent.OUT_OF_SCOPE: {
                "context": """
                This query is outside portfolio scope.
                I can help with: Skills, Projects, Experience, or Scheduling a meeting.
                """,
                "guidelines": "Keep it to 1-2 sentences. Politely redirect. Offer meeting if business-related."
            }
        }
        
        return content_map.get(intent, content_map[Intent.OUT_OF_SCOPE])


class PortfolioChatAgent:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_TOKEN)
        self.model = settings.GEMINI_MODEL
        self.content_provider = IntentContentProvider()
        
    def _classify_intent(self, user_query: str) -> Intent:
        """Classify user intent using AI"""
        
        classification_prompt = f"""
        You are an intent classifier for a portfolio chat assistant. Analyze the user's query and classify it into ONE of these categories:
        
        1. small_talk - Greetings, casual conversation, general inquiries about the assistant
        2. skills - Questions about technical skills, programming languages, frameworks, tools
        3. expertise - Questions about areas of expertise, specializations, what they're good at
        4. projects - Questions about specific projects, portfolio work, examples of work
        5. work_experience - Questions about professional experience, career history, job roles
        6. schedule_meeting - User wants to schedule a meeting, consultation, or discuss opportunities
        7. out_of_scope - Anything not related to the portfolio, personal questions unrelated to work, or off-topic queries
        
        User Query: "{user_query}"
        
        Respond with ONLY the category name (e.g., "skills" or "projects"). No explanation needed.
        """
        
        try:
            response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=classification_prompt
            )
            
            intent_str = response.text.strip().lower()
            
            # Map response to Intent enum
            intent_mapping = {
                "small_talk": Intent.SMALL_TALK,
                "skills": Intent.SKILLS,
                "expertise": Intent.EXPERTISE,
                "projects": Intent.PROJECTS,
                "work_experience": Intent.WORK_EXPERIENCE,
                "schedule_meeting": Intent.SCHEDULE_MEETING,
                "out_of_scope": Intent.OUT_OF_SCOPE
            }
            
            return intent_mapping.get(intent_str, Intent.OUT_OF_SCOPE)
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return Intent.OUT_OF_SCOPE
    
    def _create_response_prompt(self, user_query: str, intent: Intent, conversation_summary: str = ""):
        """Create prompt based on classified intent"""
        
        content = self.content_provider.get_content(intent)
        
        conversation_context = ""
        if conversation_summary.strip():
            conversation_context = f"\n\nPrevious Conversation: {conversation_summary}"
        
        base_info = """
        You are Era, Shahtaz's AI portfolio assistant.
        
        Shahtaz: Full-Stack Developer with 2+ years experience
        """
        
        response_instructions = f"""
        
        {content['context']}
        
        Guidelines: {content['guidelines']}
        
        CRITICAL CHAT RESPONSE RULES:
        - Maximum 2-3 sentences ONLY
        - Be conversational and natural like texting
        - After brief answer, ask ONE follow-up question to engage if applicable
        - NO bullet points, NO long lists, NO markdown formatting
        - Use natural language: "like X, Y, and Z" instead of lists
        - For projects/skills: mention 2-4 items then ask what they want details on
        - If continuing conversation, reference context briefly
        - NO repetitive introductions
        - Keep it SHORT and ENGAGING
        
        RESPONSE FORMAT:
        [Your short 2-3 sentence answer]
        
        ---SUMMARY---
        [A Brief summary of this exchange]
        """
        
        full_prompt = f"{base_info}{conversation_context}{response_instructions}\n\nUser: {user_query}\nIntent: {intent.value}"
        
        return full_prompt
    
    def _extract_response_sections(self, ai_response: str):
        """Extract user response and conversation summary"""
        try:
            parts = ai_response.split("---SUMMARY---")
            
            if len(parts) >= 2:
                user_response = parts[0].strip()
                new_summary = parts[1].strip()
                return user_response, new_summary
            else:
                logger.warning("AI response missing separator")
                return ai_response.strip(), ""
                
        except Exception as e:
            logger.error(f"Error extracting response sections: {e}")
            return ai_response.strip(), ""
    
    def _merge_summaries(self, previous: str, new: str):
        """Merge conversation summaries"""
        if not previous.strip():
            return new
        if not new.strip():
            return previous
        if len(previous) > 200:
            return new
        return f"{previous.strip()} {new.strip()}"
    
    def process_chat_message(self, user_query: str, conversation_summary: str = ""):
        """
        Process chat message with intent classification
        
        Returns:
            dict: {
                'user_response': str,
                'conversation_summary': str,
                'intent': str,
                'success': bool,
                'error': str
            }
        """
        try:
            # Step 1: Classify intent
            intent = self._classify_intent(user_query)
            logger.info(f"Classified intent: {intent.value}")
            
            # Step 2: Generate response based on intent
            prompt = self._create_response_prompt(user_query, intent, conversation_summary)
            
            ai_response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not ai_response or not ai_response.text:
                raise Exception("Empty response from AI")
            
            # Step 3: Extract and structure response
            user_response, new_summary = self._extract_response_sections(ai_response.text)
            updated_summary = self._merge_summaries(conversation_summary, new_summary)
            
            return {
                'user_response': user_response,
                'conversation_summary': updated_summary,
                'intent': intent.value,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                'user_response': CHAT_FAILED_MESSAGE["en"],
                'conversation_summary': conversation_summary,
                'intent': 'error',
                'success': False,
                'error': str(e)
            }


def process_portfolio_chat(user_query: str, conversation_summary: str = ""):
    """
    Process portfolio chat with intent classification
    
    Returns:
        dict: Complete result with user_response, conversation_summary, intent, success, and error
    """
    agent = PortfolioChatAgent()
    return agent.process_chat_message(user_query, conversation_summary)