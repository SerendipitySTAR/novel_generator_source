"""
LLM抽象层初始化文件
"""
from app.core.llm.llm_interface import LLMInterface, LLMResponse
from app.core.llm.openai_llm import OpenAILLM

__all__ = ["LLMInterface", "LLMResponse", "OpenAILLM"]
