from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL")

settings = Settings()

"""
This module is overkill for 2 secrets but it illustrates how something like
this could be extended if more need to be added in a modular way so you dont have 
to call load_dotenv() in every file where you need a secret 
"""

