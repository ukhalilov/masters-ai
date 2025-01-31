import openai
import os
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Please check your .env file.")

# Create an OpenAI client
client = openai.OpenAI(api_key=api_key)

# Read the transcript from the file
input_filename = "lesson-1-transcript.txt"

try:
    with open(input_filename, "r", encoding="utf-8") as file:
        transcript_text = file.read()
except FileNotFoundError:
    print(f"Error: {input_filename} not found.")
    exit()

# Define the system message (role-based guidance)
system_message = {
    "role": "system",
    "content": (
        "You are an expert blog writer. Your task is to transform lecture transcripts into engaging and "
        "well-structured blog posts. The output should include: \n"
        "- A catchy title\n"
        "- An engaging introduction\n"
        "- Main points formatted with appropriate headings\n"
        "- A conclusion summarizing key takeaways\n"
        "Ensure clarity, readability, and professional formatting."
    )
}

# Define the user message (transcript input)
user_message = {
    "role": "user",
    "content": f"Convert the following lecture transcript into a blog post:\n\n{transcript_text}"
}

# Request OpenAI to generate a blog post
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[system_message, user_message]
)

# Extract and print the AI-generated blog post
blog_post = response.choices[0].message.content

# Print the blog post to the screen
print("\n=== GENERATED BLOG POST ===\n")
print(blog_post)
print("\n===========================")