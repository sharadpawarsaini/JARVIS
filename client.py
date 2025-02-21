import time
from openai import OpenAI
import openai  # Import this for error handling

# Initialize OpenAI client with your API key
client = OpenAI(api_key="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")

def ask_jarvis(question):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis."},
                {"role": "user", "content": question}
            ]
        )
        return completion.choices[0].message.content

    except openai.RateLimitError:  # Catch rate limit errors
        print("⚠️ Rate limit exceeded! Waiting 60 seconds before retrying...")
        time.sleep(60)  # Wait 60 seconds before retrying
        return ask_jarvis(question)  # Retry after cooldown

    except openai.OpenAIError as e:  # Catch general OpenAI errors
        print(f"⚠️ OpenAI API Error: {e}")
        return "An error occurred while processing your request."

response = ask_jarvis("What is coding?")
print(response)
