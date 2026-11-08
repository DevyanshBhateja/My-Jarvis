import os
import sys
import httpx
from openai import OpenAI

def main():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        # Load from .env if present
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip("\"'")
        api_key = os.getenv("NVIDIA_API_KEY")

    print(f"API Key present: {bool(api_key)}, prefix: {api_key[:12] if api_key else 'None'}...")
    base_url = os.getenv("JARVIS_NVIDIA_URL", "https://integrate.api.nvidia.com/v1")
    model = os.getenv("JARVIS_NVIDIA_MODEL", "deepseek-ai/deepseek-v4.1-flash")

    print(f"Connecting to: {base_url} with model: {model}")
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=httpx.Timeout(15.0, connect=5.0)
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Respond with 'NVIDIA DeepSeek connected successfully' in exactly that phrase."}],
            max_tokens=30,
            stream=False,
        )
        print("Response received:")
        print(response.choices[0].message.content)
        print("[SUCCESS] DeepSeek model is working with your API key!")
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
