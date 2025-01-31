import openai
import os
from dotenv import load_dotenv
from pydub import AudioSegment

# Load API key from .env file
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Audio file name
AUDIO_FILE = "meeting_recording.mp3"

def extract_audio_segment(file_path, start_minute=5, end_minute=10):
    """Extract a specific portion of the audio file (from 5:00 to 10:00 minutes)."""
    audio = AudioSegment.from_file(file_path)

    start_ms = start_minute * 60 * 1000  # Convert minutes to milliseconds
    end_ms = end_minute * 60 * 1000

    extracted_audio = audio[start_ms:end_ms]

    output_path = "extracted_audio.wav"
    extracted_audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(file_path):
    """Transcribe the extracted audio using OpenAI Whisper API."""
    extracted_path = extract_audio_segment(file_path)

    with open(extracted_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )

    if response and hasattr(response, "text"):
        print("\n**Transcription (from 5:00 to 10:00):**")
        print(response.text)
    else:
        print("Error: No transcript received.")

if __name__ == "__main__":
    print(f"Processing '{AUDIO_FILE}' from 5:00 to 10:00...")
    transcribe_audio(AUDIO_FILE)
