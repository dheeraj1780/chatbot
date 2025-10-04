from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
import asyncio
from typing import Optional

class SLMService:
    def __init__(self, model_name: str = "phi3.5:3.8b"):
        self.model_name = model_name
        self.llm = OllamaLLM(model=model_name)
        self.prompt_template = self._create_prompt_template_for_response()
        self.prompt_group_template = self._create_prompt_template_for_group_identification()
    
    def _create_prompt_template_for_response(self):
        """Create the prompt template for RAG"""
        template = """You are a helpful AI assistant that answers questions based on provided context.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Answer the question using ONLY the information provided in the context above
- If the context doesn't contain enough information to answer the question, say so clearly
- Be specific and detailed in your response when possible
- Do not make up information that isn't in the context
- Structure your answer clearly with bullet points or numbered lists when appropriate

ANSWER:"""
        
        return ChatPromptTemplate.from_template(template)


    def _create_prompt_template_for_group_identification(self):
        """Create the prompt template for RAG"""
        template = """You are a helpful AI assistant that select which group suits the best for user's query based on the group's description.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Select and return only the group id that suits the best for the user's query based on the group's description.
- If the group's description doesn't contain enough information to answer the question, return 0.
- **MUST** return only the group id.

ANSWER:"""
        
        return ChatPromptTemplate.from_template(template)


    async def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using the SLM"""
        try:
            # Format the prompt
            formatted_prompt = self.prompt_template.format(
                context=context,
                question=question
            )
            
            # Generate response using asyncio to handle blocking call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self.llm.invoke, formatted_prompt
            )
            
            # Handle different response types
            if hasattr(response, "generations"):
                try:
                    response_text = response.generations[0][0].text
                except (IndexError, AttributeError):
                    response_text = str(response)
            else:
                response_text = str(response) if response else "I couldn't generate a response."
            
            return response_text.strip()
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the given text"""
        summary_template = """Summarize the following text in {max_length} words or less:

TEXT:
{text}

SUMMARY:"""
        
        prompt = summary_template.format(text=text, max_length=max_length)
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.llm.invoke, prompt)
            
            if hasattr(response, "generations"):
                try:
                    response_text = response.generations[0][0].text
                except (IndexError, AttributeError):
                    response_text = str(response)
            else:
                response_text = str(response) if response else "Couldn't generate summary."
                
            return response_text.strip()
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    async def identify_relevant_group(self, question: str, context: str) -> Optional[str]:
        """Identify the most relevant group for a given question"""
        try:
            # Format the prompt
            formatted_prompt = self.prompt_group_template.format(
                context=context,
                question=question
            )
            
            # Generate response using asyncio to handle blocking call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self.llm.invoke, formatted_prompt
            )
            
            # Handle different response types
            if hasattr(response, "generations"):
                try:
                    response_text = response.generations[0][0].text
                except (IndexError, AttributeError):
                    response_text = str(response)
            else:
                response_text = str(response) if response else None
            print(f"Group identification response: {response_text}")
            return response_text.strip() if response_text else None
            
        except Exception as e:
            return f"Error identifying group: {str(e)}"
