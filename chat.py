#!/usr/bin/env python

import openai
import argparse
import os
from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
import time
import json

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and Assistant ID from environment variables
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

if not api_key or not assistant_id:
    print("Error: Required environment variables (API Key or Assistant ID) not found.")
    exit(1)

# Set the API key for OpenAI
openai.api_key = api_key
## create client
client = openai.OpenAI()


# Other parts of your script, including argument parsing and main logic
# ...

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def show_json(obj):
    # Parse the JSON string
    parsed_json = json.loads(obj.model_dump_json())

    # Pretty print the JSON
    print(json.dumps(parsed_json, indent=4))


def main():
    # Start a new Thread for the conversation
    thread = client.beta.threads.create()

    # Session and prompt setup
    user_prompt = "\nUser > "
    prompt_history = FileHistory(".gptsh_history")
    session = PromptSession(history=prompt_history)

    # Conversation loop
    while True:
        user_input = session.prompt(user_prompt)

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        # Create a Message on the thread with the user's message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        # Create a Run on the thread with the user's message
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        run = wait_on_run(run, thread)

        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        # Extract and display the response from the run
        messages = client.beta.threads.messages.list(
            thread_id=thread.id, order="asc", after=message.id
        )
        # show_json(messages)
        # Iterate over each message and print the content
        for message in messages:
            if message.role == 'assistant':  # Check if the role is 'assistant'
                # Assuming each message has at least one content item
                for content in message.content:
                    if content.type == 'text':  # Check if the content type is 'text'
                        print(f"assistant > {content.text.value}")  # Access attributes with dot notation
        print('\n')




# ...

if __name__ == "__main__":
    main()
