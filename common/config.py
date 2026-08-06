"""
Enterprise AI Engineering Lab
Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME  = os.getenv("OPENAI_MODEL", "gpt-5-nano")
