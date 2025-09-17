#!/usr/bin/env python3
import json
import os
import sys

def generate_ai_summary():
    # Get environment variables
    try:
        endpoint = os.environ['AOAI_ENDPOINT'].rstrip('/')
        deployment = os.environ['AOAI_DEPLOYMENT']
        key = os.environ['AOAI_KEY']
        status = os.environ['STATUS']
        
        # Read the prompt from file
        with open('prompt.txt', 'r') as f:
            base_prompt = f.read()
        
        # Format the context
        context = """Outcome: {status}

        Error/Context:
        {ctx}""".format(status=status, ctx=os.environ.get('CONTEXT', '(none)'))

        # Create the request body
        body = {
            "messages": [
                {"role": "system", "content": "You are an expert CI assistant."},
                {"role": "user", "content": base_prompt + "\n\n" + context}
            ],
            "temperature": 0.2
        }
        
        # Make the request to Azure OpenAI
        import urllib.request
        req = urllib.request.Request(
            f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "api-key": key},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                # Extract the first message content
                content = ""
                if "choices" in data and data["choices"]:
                    msg = data["choices"][0].get("message", {})
                    content = msg.get("content", "")
                # Output to GITHUB_OUTPUT
                content = content.strip() or "No AI summary generated."
                print(f"summary<<EOF\n{content}\nEOF")
        except Exception as e:
            print(f"summary<<EOF\nAI summary unavailable. Fallback: Build likely failed due to missing requests. Fix: add requests==2.31.0 and upgrade flask to 2.3.3.\nEOF")
    
    except Exception as e:
        print(f"summary<<EOF\nError generating AI summary: {str(e)}\nEOF")

if __name__ == "__main__":
    generate_ai_summary()