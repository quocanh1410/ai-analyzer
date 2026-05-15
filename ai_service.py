from fastapi import FastAPI, HTTPException
import ollama

app = FastAPI()

@app.post("/analyze")
def analyze(data: dict):

    logs = data.get("logs", "")

    if not logs:
        raise HTTPException(
            status_code=400,
            detail="No logs provided"
        )

    # tránh gửi quá nhiều log
    logs = logs[:5000]

    prompt = f"""
You are a Kubernetes SRE assistant.

The logs/events below are from a Kubernetes cluster.

Important:
- "BackOff pulling image" means Kubernetes cannot download a container image
- "ImagePullBackOff" means container image pull failure
- Do not confuse image pulling with Git pull requests

Analyze the incident below.

Logs:
{logs}

Rules:
- Be precise
- Do not invent information
- Use Kubernetes terminology

Return EXACTLY this format:

Severity:
<Low/Medium/High/Critical>

Root Cause:
<short explanation>

Recommendations:
- item
- item
"""
    try:

        response = ollama.chat(
            model='qwen2:0.5b',
            messages=[
                {
                    'role':'user',
                    'content':prompt
                }
            ]
        )

        return {
            "analysis":
            response["message"]["content"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )