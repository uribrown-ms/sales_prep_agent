# agents/ceo_agent.py

import openai

def respond(conversation, company_data):
    """
    Generates a response from the CEO agent.
    """
    # Load System Prompt
    with open("prompts/ceo_prompt.txt", "r") as file:
        system_prompt = file.read().format(**company_data)

    # Prepare Messages
    # Ensure the system prompt is only added once at the beginning
    messages = [{"role": "system", "content": system_prompt}] + conversation

    # OpenAI API Call
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or the model you're using
        messages=messages,
        max_tokens=500,  # Adjust as needed
        temperature=0.7  # Adjust creativity
    )

    # Extract Assistant's Reply
    assistant_message = response['choices'][0]['message']['content']
    return assistant_message
