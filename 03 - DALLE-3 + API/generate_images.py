import os
import openai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Predefined styles
STYLES = [
    "realistic photography",
    "oil painting",
    "watercolor painting",
    "anime style",
    "cyberpunk futuristic",
    "pixel art",
    "sketch drawing",
    "surrealism art",
    "3D render"
]


def generate_images(prompt):
    """Generate 9 images with different styles from DALL·E 3 and print the URLs."""

    for style in STYLES:
        styled_prompt = f"{prompt}, in {style} style"
        print(f"Generating: {styled_prompt}")

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=styled_prompt,
                size="1024x1024",
                n=1
            )

            if response and response.data:
                image_url = response.data[0].url
                print(f"{style}: {image_url}\n")
            else:
                print(f"Failed to generate image for style: {style}")

        except openai.OpenAIError as e:
            print(f"Error generating image for {style}: {e}")


if __name__ == "__main__":
    user_prompt = input("Enter your prompt: ")
    generate_images(user_prompt)
