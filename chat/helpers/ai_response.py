from google import genai
from django.conf import settings
from chat.v1.res_msg import CHAT_FAILED_MESSAGE

import logging
logger = logging.getLogger(__name__)

class PortfolioChatAgent:
    def __init__(self):
        self.gemini_client = genai.Client(api_key=settings.GEMINI_TOKEN)
        self.model = settings.GEMINI_MODEL
        
        # System context about Shahtaz (always remains the same)
        self.system_context = """
        You are Era, an AI assistant for Shahtaz's professional portfolio.
        Your primary goal is to provide helpful, conversational, and accurate information about Shahtaz, his skills, and his projects.

        --- Shahtaz's Profile ---
        Name: Shahtaz
        Role: Software Developer
        Experience: 2 years of full-stack development.
        Key Expertise: React.js, Next.js, Tailwind CSS, Redux, RTK Query, Tanstack Query, Node.js, MongoDB, Python, Django, PostgreSQL, FastAPI, Docker, Socket.IO, and AI integrations.

       --- Key Projects ---
        1. SaaS & ERP Solutions:
          - Developed real-time HRM systems and restaurant management tools with features like payroll automation, attendance tracking, delivery logging, and socket-based live updates.
          - Technologies: React.js, Next.js, Node.js, Django, PostgreSQL, MongoDB, Socket.IO.

        2. CRM & Business Platforms:
          - Built internal and client-facing dashboards for courier and service-based businesses. Integrated role-based access control, employee performance tracking, dynamic PDF-to-JSON parsing, and visual analytics.
          - Technologies: React.js, TypeScript, Express.js, MongoDB, Chart.js, and PDF.js.

        3. AI-Powered Chatbot:
          - Engineered a portfolio-integrated AI assistant capable of answering questions, showcasing projects, and generating resumes or cover letters on demand.
          - Technologies: Python, Django, Google Gemini API, and custom prompt pipelines.

        4. Web Presence & Integrations:
          - Designed responsive business landing pages with animated UI, theme toggles, and section-based layouts. Integrated third-party services like Google Maps, Google Analytics, Crisp Chat, and payment gateways.
          - Technologies: Next.js, Tailwind CSS, Framer Motion, ShadCN, and Vercel.

        5. eCommerce & Blog Platforms
          - Delivered personalized eCommerce sites and blog systems with features like product filtering, cart and checkout systems, blog categorization, and secure user authentication.
          - Technologies: React.js, Next.js, Node.js, MongoDB, JWT, and Markdown/MDX for content.
        
        --- Business Inquiries & Next Steps ---
        For business inquiries, potential collaborations, or in-depth discussions, provide specific details about Shahtaz's relevant experience and encourage scheduling a meeting.
        Meeting Link: https://calendly.com/shahtaz67
        """

    def _create_conversation_prompt(self, user_query: str, conversation_summary: str = ""):
        """Create the full prompt for the AI including system context and conversation history"""
        
        conversation_context = ""
        if conversation_summary.strip():
            conversation_context = f"\n\nConversation Context: {conversation_summary}"
        
        # Define the response format requirement with better instructions
        response_format = (
            "\n\nIMPORTANT INSTRUCTIONS:\n"
            "- If this is a continuing conversation (context provided above), build upon what was already discussed\n"
            "- DO NOT repeat introductions if you've already introduced yourself\n"
            "- Reference previous topics naturally to maintain conversation flow\n"
            "- Be conversational and helpful, focusing on the user's current question\n"
            "- Only share the Meeting Link if the user explicitly asks to schedule a meeting. First, confirm whether the user wants to schedule one before providing the link.\n"
            "RESPONSE FORMAT: Structure your response in exactly two sections separated by '---SUMMARY---':\n"
            "1. First section: Your natural response to the user's query (no repetitive introductions)\n"
            "2. Second section: Updated conversation summary (50-100 words) including this exchange\n\n"
            "Example:\n"
            "[Your direct response to the current query]\n\n"
            "---SUMMARY---\n"
            "[Updated summary of the entire conversation including this exchange]"
        )
        
        full_prompt = (
            f"{self.system_context}"
            f"{conversation_context}"
            f"{response_format}"
            f"\n\nCurrent User Query: {user_query}"
        )
        
        return full_prompt

    def _extract_response_sections(self, ai_response: str):
        """Extract user response and conversation summary from AI response"""
        try:
            # Split by the separator
            parts = ai_response.split("---SUMMARY---")
            
            if len(parts) >= 2:
                user_response = parts[0].strip()
                new_summary = parts[1].strip()
                return user_response, new_summary
            else:
                # Fallback if separator not found
                logger.warning("AI response doesn't contain expected separator")
                return ai_response.strip(), ""
                
        except Exception as e:
            logger.error(f"Error extracting response sections: {e}")
            return ai_response.strip(), ""

    def _merge_conversation_summaries(self, previous_summary: str, new_summary: str):
        """Merge previous summary with new summary to maintain conversation context"""
        if not previous_summary.strip():
            return new_summary
        
        if not new_summary.strip():
            return previous_summary
            
        # Simple merge - let the AI handle the context in the next interaction
        # Focus on keeping the most recent and relevant information
        if len(previous_summary) > 200:  # If getting too long, prioritize recent info
            return new_summary
        else:
            return f"{previous_summary.strip()} {new_summary.strip()}"

    def process_chat_message(self, user_query: str, conversation_summary: str = ""):
        """
        Main method to process a chat message and return structured response
        
        Returns:
            dict: {
                'user_response': str,  # Response to send to user
                'conversation_summary': str,  # Updated summary for storage
                'success': bool,  # Whether the operation was successful
                'error': str  # Error message if any
            }
        """
        try:
            # Create the full prompt
            full_prompt = self._create_conversation_prompt(user_query, conversation_summary)
            
            # Generate AI response
            ai_response = self.gemini_client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            
            if not ai_response or not ai_response.text:
                raise Exception("Empty response from AI")
            
            # Extract the two sections
            user_response, new_summary = self._extract_response_sections(ai_response.text)
            
            # Merge with previous summary if needed
            updated_summary = self._merge_conversation_summaries(conversation_summary, new_summary)
            
            return {
                'user_response': user_response,
                'conversation_summary': updated_summary,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                'user_response': CHAT_FAILED_MESSAGE["en"],
                'conversation_summary': conversation_summary,  # Keep previous summary
                'success': False,
                'error': str(e)
            }


# Enhanced function with full result details
def process_portfolio_chat(user_query: str, conversation_summary: str = ""):
    """
    Process portfolio chat with full result details
    
    Returns:
        dict: Complete result with user_response, conversation_summary, success, and error
    """
    agent = PortfolioChatAgent()
    return agent.process_chat_message(user_query, conversation_summary)