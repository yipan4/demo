#!/usr/bin/env python3
import json
import os
import sys

def generate_ai_summary():
    # Get environment variables
    try:
        # Print debug info for troubleshooting
        print("DEBUG: Environment variables available:", list(os.environ.keys()), file=sys.stderr)
        
        # Get required environment variables with better error handling
        endpoint = os.environ.get('AOAI_ENDPOINT', '')
        if not endpoint:
            raise ValueError("AOAI_ENDPOINT environment variable is not set")
        endpoint = endpoint.rstrip('/')
            
        deployment = os.environ.get('AOAI_DEPLOYMENT', '')
        if not deployment:
            raise ValueError("AOAI_DEPLOYMENT environment variable is not set")
            
        key = os.environ.get('AOAI_KEY', '')
        if not key:
            raise ValueError("AOAI_KEY environment variable is not set")
            
        status = os.environ.get('STATUS', '')
        if not status:
            raise ValueError("STATUS environment variable is not set")
        
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
        
        # Debug values before making request
        print(f"DEBUG: Making request to endpoint: {endpoint}", file=sys.stderr)
        print(f"DEBUG: Using deployment: {deployment}", file=sys.stderr)
        print(f"DEBUG: Body preview: {json.dumps(body)[:100]}...", file=sys.stderr)
        
        try:
            req = urllib.request.Request(
                f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json", "api-key": key},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_data = resp.read().decode()
                print(f"DEBUG: Got response status: {resp.status}", file=sys.stderr)
                
                data = json.loads(response_data)
                
                # Extract the first message content
                content = ""
                if "choices" in data and data["choices"]:
                    msg = data["choices"][0].get("message", {})
                    content = msg.get("content", "")
                elif "error" in data:
                    raise Exception(f"API Error: {json.dumps(data['error'])}")
                else:
                    raise Exception(f"Unexpected response format: {json.dumps(data)[:200]}")
                    
                # Output to GITHUB_OUTPUT
                content = content.strip() or "No AI summary generated."
                print(f"summary<<EOF\n{content}\nEOF")
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode() if hasattr(e, 'read') else str(e)
            print(f"DEBUG: HTTP Error: {e.code} - {error_msg}", file=sys.stderr)
            print(f"summary<<EOF\nAI summary unavailable due to HTTP error {e.code}. Fallback: Build likely failed due to missing requests. Fix: add requests==2.31.0 and upgrade flask to 2.3.3.\nEOF")
        except Exception as e:
            print(f"DEBUG: Exception: {str(e)}", file=sys.stderr)
            print(f"summary<<EOF\nAI summary unavailable ({str(e)}). Fallback: Build likely failed due to missing requests. Fix: add requests==2.31.0 and upgrade flask to 2.3.3.\nEOF")
    
    except Exception as e:
        import traceback
        error_tb = traceback.format_exc()
        print(f"DEBUG: Exception in main function: {str(e)}", file=sys.stderr)
        print(f"DEBUG: Traceback: {error_tb}", file=sys.stderr)
        print(f"summary<<EOF\nError generating AI summary: {str(e)}\nEOF")

if __name__ == "__main__":
    generate_ai_summary()