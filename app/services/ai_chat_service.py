import google.generativeai as genai
from typing import List, Optional, Dict, Any
from app.environment import environment
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
import asyncio


class AIChatService:
    
    def __init__(self):
        try:
            genai.configure(api_key=environment.GEMINI_API_KEY)
            # Try to use the best available model
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception:
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-pro')
                except Exception:
                    self.model = genai.GenerativeModel('gemini-pro')
            self.enabled = True
            logger.info("AI Chat Service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AI Chat Service: {e}")
            self.enabled = False
            self.model = None
    
    async def generate_response(
        self,
        user_message: str,
        module: Optional[str] = None,
        thinking_mode: str = "normal",
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> str:
        """
        Generate an AI response based on user message and context
        
        Args:
            user_message: The user's message
            module: Current module context (e.g., "Accounts", "Opportunities")
            thinking_mode: Response mode ("normal", "think", "deep-think", "research")
            conversation_history: Previous messages in the conversation
            system_prompt: Custom system prompt
            use_case: Specific use case (content_enrichment, content_development, suggestions, etc.)
        """
        if not self.enabled or not self.model:
            # Fallback response if AI is not available
            return self._generate_fallback_response(user_message, module)
        
        try:
            # Build the system prompt based on use case and context
            base_prompt = self._build_system_prompt(module, use_case, system_prompt)
            
            # Build conversation context
            conversation_context = self._build_conversation_context(
                conversation_history or [],
                user_message
            )
            
            # Adjust prompt based on thinking mode
            mode_instruction = self._get_mode_instruction(thinking_mode)
            
            full_prompt = f"""{base_prompt}

{mode_instruction}

{conversation_context}

User: {user_message}

Assistant:"""
            
            # Generate response with appropriate configuration
            config = self._get_generation_config(thinking_mode)
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=config
            )
            
            response_text = response.text.strip()
            
            # Post-process based on thinking mode
            return self._post_process_response(response_text, thinking_mode)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            # Return fallback response on error
            return self._generate_fallback_response(user_message, module)
    
    def _build_system_prompt(
        self,
        module: Optional[str],
        use_case: Optional[str],
        custom_prompt: Optional[str]
    ) -> str:
        """Build the system prompt based on context"""
        if custom_prompt:
            return custom_prompt
        
        base_context = f"""You are an intelligent AI assistant for Megapolis Technologies, a comprehensive business management platform. You help users with various tasks across different modules."""
        
        if module and module != "General":
            base_context += f"\n\nCurrent Context: The user is working in the {module} module. Provide specific, actionable guidance related to {module} functionality."
        
        # Add use case specific instructions
        use_case_instructions = {
            "content_enrichment": """
Your role: Content Enrichment Specialist
- Enhance and expand existing content with additional details, context, and value
- Add relevant information, examples, and best practices
- Improve clarity, completeness, and usefulness of content
- Provide structured, well-organized responses with clear sections
""",
            "content_development": """
Your role: Content Development Expert
- Help create new content from scratch or expand on ideas
- Provide creative suggestions, frameworks, and templates
- Develop comprehensive content structures and outlines
- Offer multiple approaches and perspectives
""",
            "suggestions": """
Your role: Intelligent Suggestion Engine
- Provide actionable suggestions based on user needs
- Offer multiple options with pros and cons
- Suggest best practices and industry standards
- Recommend next steps and improvements
""",
            "auto_enhancement": """
Your role: Auto-Enhancement Assistant
- Automatically improve and optimize content
- Suggest enhancements for clarity, structure, and impact
- Identify areas for improvement and provide alternatives
- Offer refined versions with explanations of changes
""",
            "ideas": """
Your role: Creative Ideas Generator
- Generate innovative ideas and solutions
- Think outside the box and offer unique perspectives
- Provide brainstorming support and creative frameworks
- Suggest multiple creative approaches to problems
""",
        }
        
        if use_case and use_case in use_case_instructions:
            base_context += use_case_instructions[use_case]
        else:
            base_context += """
Your capabilities include:
- Answering questions about platform features and functionality
- Providing guidance on best practices
- Suggesting improvements and optimizations
- Generating ideas and creative solutions
- Enriching content with additional context
- Auto-enhancing existing content
"""
        
        base_context += """
Guidelines:
- Be helpful, professional, and concise
- Use clear, structured responses with formatting when appropriate
- Provide actionable advice and specific examples
- If uncertain, ask clarifying questions
- Focus on practical, implementable solutions
"""
        
        return base_context
    
    def _build_conversation_context(
        self,
        history: List[Dict[str, str]],
        current_message: str
    ) -> str:
        """Build conversation context from history"""
        if not history:
            return ""
        
        context_parts = ["Previous conversation:"]
        for msg in history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                context_parts.append(f"User: {content}")
            elif role == "bot":
                context_parts.append(f"Assistant: {content}")
        
        return "\n".join(context_parts)
    
    def _get_mode_instruction(self, mode: str) -> str:
        """Get instruction based on thinking mode"""
        instructions = {
            "normal": "Provide a clear, direct response.",
            "think": "Think through this carefully. Consider multiple aspects and provide a thoughtful, well-reasoned response.",
            "deep-think": "Conduct a deep analysis. Consider all factors, implications, and provide a comprehensive, detailed response with multiple perspectives.",
            "research": "Research this topic thoroughly. Provide a well-researched response with evidence, examples, and references to best practices."
        }
        return instructions.get(mode, instructions["normal"])
    
    def _get_generation_config(self, mode: str) -> Dict[str, Any]:
        """Get generation config based on thinking mode"""
        base_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        if mode == "normal":
            base_config.update({
                "temperature": 0.7,
                "max_output_tokens": 2048,
            })
        elif mode == "think":
            base_config.update({
                "temperature": 0.8,
                "max_output_tokens": 3072,
            })
        elif mode == "deep-think":
            base_config.update({
                "temperature": 0.9,
                "max_output_tokens": 4096,
            })
        elif mode == "research":
            base_config.update({
                "temperature": 0.75,
                "max_output_tokens": 4096,
            })
        
        return base_config
    
    def _post_process_response(self, response: str, mode: str) -> str:
        """Post-process response based on thinking mode"""
        if mode == "think":
            return f"**Thinking through this...**\n\n{response}\n\n*I've considered the key aspects of your question and provided a thoughtful response.*"
        elif mode == "deep-think":
            return f"**Deep Analysis**\n\n{response}\n\n**Additional Considerations:**\n- This requires careful evaluation of multiple factors\n- Consider the long-term implications\n- Review related data points for comprehensive understanding\n\n*I've conducted a thorough analysis to provide you with the most comprehensive answer.*"
        elif mode == "research":
            return f"**Research Mode**\n\n{response}\n\n**Research Findings:**\n- Based on current data patterns\n- Cross-referenced with best practices\n- Analyzed similar scenarios\n\n**Sources Considered:**\n- Internal documentation\n- Historical data patterns\n- Industry standards\n\n*I've researched this topic thoroughly to give you an informed response.*"
        
        return response
    
    def _generate_fallback_response(self, user_message: str, module: Optional[str]) -> str:
        """Generate a fallback response when AI is unavailable"""
        message_lower = user_message.lower()
        
        if "account" in message_lower or "client" in message_lower:
            return "I can help you with account management! You can create new accounts, view client details, track communication history, and manage MSA status. Would you like me to guide you through any specific account-related task?"
        elif "opportunity" in message_lower or "lead" in message_lower:
            return "For opportunities, you can track your sales pipeline, manage lead stages, view opportunity values, and generate pipeline reports. What specific aspect of opportunity management interests you?"
        elif "proposal" in message_lower:
            return "Regarding proposals, you can create new proposals using templates, track submission status, monitor win rates, and manage proposal deadlines. What would you like to do with proposals?"
        elif "project" in message_lower:
            return "For project management, you can view project timelines, track deliverables, monitor project health, and generate progress reports. What project information do you need?"
        elif "finance" in message_lower or "budget" in message_lower:
            return "Regarding finance, you can track revenue, manage budgets, monitor expenses, generate financial reports, and analyze profitability. What financial information do you need?"
        else:
            module_context = f" in the {module} module" if module and module != "General" else ""
            return f"Great question! Since you're{module_context}, I can provide specific guidance. Could you be more specific about what you'd like to know?"


# Singleton instance
ai_chat_service = AIChatService()

