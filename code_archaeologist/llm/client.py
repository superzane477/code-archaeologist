"""
LLM client for generating analysis reports
"""
from typing import Dict, Any, Optional, List
import os


class LLMClient:
    """Client for interacting with various LLM backends"""
    
    BACKENDS = {
        "openai": "https://api.openai.com/v1",
        "ollama": "http://localhost:11434/v1",
        "groq": "https://api.groq.com/openai/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "azure": None
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.backend = self.config.get("backend", "openai")
        self.api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.base_url = self.config.get("base_url") or self.BACKENDS.get(self.backend)
        self.model = self.config.get("model", "gpt-4")
        
        self._client = None
    
    def _get_client(self):
        """Get or create the OpenAI-compatible client"""
        if self._client is None:
            try:
                from openai import OpenAI
                
                if self.backend == "azure":
                    self._client = OpenAI(
                        api_key=self.api_key,
                        api_version="2024-02-01",
                        azure_endpoint=self.base_url
                    )
                else:
                    self._client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
            except ImportError:
                raise ImportError("openai package is required. Install with: pip install openai")
        
        return self._client
    
    def generate_report(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a report from the given prompt.
        
        Args:
            prompt: The user prompt containing analysis context
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated text response
        """
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def generate_streaming_report(self, prompt: str, system_prompt: Optional[str] = None):
        """
        Generate a report with streaming response.
        
        Args:
            prompt: The user prompt containing analysis context
            system_prompt: Optional system prompt for context
            
        Yields:
            Text chunks as they are generated
        """
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error generating report: {str(e)}"
    
    @classmethod
    def list_backends(cls) -> List[str]:
        """Return list of supported backends"""
        return list(cls.BACKENDS.keys())
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the client configuration.
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        
        if not self.api_key and self.backend != "ollama":
            errors.append("API key is required")
        
        if self.backend not in self.BACKENDS:
            errors.append(f"Unknown backend: {self.backend}")
        
        if self.backend == "azure" and not self.base_url:
            errors.append("Azure endpoint is required for Azure backend")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }