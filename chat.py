import os
import sys
from dotenv import load_dotenv

load_dotenv()

from sarvamai import SarvamAI

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    print("Error: SARVAM_API_KEY not found in .env")
    sys.exit(1)

client = SarvamAI(api_subscription_key=api_key)

print("=" * 55)
print("Sarvam AI Terminal Chat (sarvam-105b-conversations)")
print("Chat in English, Hindi, Hinglish, etc.")
print("Type 'exit' or 'quit' to end the session.")
print("=" * 55)

messages = [
    {
        "role": "system",
        "content": "You are a helpful, knowledgeable AI assistant built by Sarvam AI. You understand and reply naturally in English, Hindi, and code-mixed Indic languages.",
    }
]

while True:
    try:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Session ended.")
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=messages,
        )

        reply = response.choices[0].message.content
        print(f"\nSarvam: {reply}")

        messages.append({"role": "assistant", "content": reply})

    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")
        break
    except Exception as e:
        print(f"\nError: {e}")
