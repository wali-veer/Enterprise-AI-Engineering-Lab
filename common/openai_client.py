"""
Enterprise AI Engineering Lab
OpenAI Client
"""

from openai import OpenAI
from common.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)