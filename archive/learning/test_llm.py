# test_llm.py
"""
Simple test to verify Gemini API is working
"""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

def test_gemini():
    """
    Test Gemini API connection
    
    TODO:
    - Configure genai with your API key
    - Create a model instance (use "gemini-1.5-flash")
    - Generate a simple response to "What is 2+2?"
    - Print the response
    
    Hints:
    - genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    - model = genai.GenerativeModel('gemini-1.5-flash')
    - response = model.generate_content("Your prompt here")
    - response.text contains the answer
    """
    
    # YOUR CODE HERE
    client = genai.Client()
    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = "Explain how AI works in a few words"
    )

    print(response.text)


if __name__ == "__main__":
    print("Testing Gemini connection...")
    test_gemini()

