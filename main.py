import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

# API Key Render environment variable se read hogi
API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

SYSTEM_INSTRUCTION = """
You are 'CSU Student Assistant', created and maintained by Harsh. 
Your intelligence is powered by Google's Gemini Flash technology.

Rules:
1. Help students with Central Sanskrit University (CSU, sanskrit.nic.in) queries: Admissions, Campuses (Bhopal, Jaipur, Puri, Lucknow, etc.), Courses (Prak-Shastri, Shastri, Acharya, Shiksha Shastri B.Ed, M.Ed), Exams, Results, and Hostels.
2. If asked 'Who created you?' or 'Who made you?', answer clearly: 'I was created and am maintained by Harsh. My underlying AI is powered by Google's Gemini Flash technology.'
3. Respond politely in Hindi, English, Sanskrit, or Hinglish matching the user's input language.
4. Prioritize official facts from sanskrit.nic.in. If unsure, suggest visiting sanskrit.nic.in.
"""

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        return {"reply": "Kripya apna sawal likhein."}
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=req.message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSU Student Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; }
        header { background: #1e293b; padding: 14px 20px; border-bottom: 1px solid #334155; text-align: center; }
        header h1 { font-size: 1.1rem; color: #38bdf8; }
        header p { font-size: 0.75rem; color: #94a3b8; margin-top: 4px; }
        #chat-box { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 0.95rem; line-height: 1.4; word-wrap: break-word; white-space: pre-wrap; }
        .bot { background: #1e293b; color: #f1f5f9; align-self: flex-start; border: 1px solid #334155; }
        .user { background: #0284c7; color: white; align-self: flex-end; }
        .input-area { background: #1e293b; padding: 12px; display: flex; gap: 8px; border-top: 1px solid #334155; }
        input { flex: 1; background: #0f172a; border: 1px solid #475569; border-radius: 8px; padding: 12px; color: white; font-size: 0.95rem; outline: none; }
        button { background: #0284c7; color: white; border: none; padding: 0 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <header>
        <h1>🏛️ CSU Student Assistant</h1>
        <p>Created & Maintained by Harsh | Powered by Gemini Flash</p>
    </header>
    <div id="chat-box">
        <div class="msg bot">Namaste! Main Central Sanskrit University (CSU) ka student assistant hoon. Main aapki kya madad kar sakta hoon?</div>
    </div>
    <div class="input-area">
        <input type="text" id="user-input" placeholder="Apna sawal likhein..." onkeypress="if(event.key==='Enter') sendMsg()">
        <button onclick="sendMsg()">Send</button>
    </div>
    <script>
        async function sendMsg() {
            const input = document.getElementById('user-input');
            const box = document.getElementById('chat-box');
            const text = input.value.trim();
            if (!text) return;
            
            box.innerHTML += `<div class="msg user">${text}</div>`;
            input.value = '';
            box.scrollTop = box.scrollHeight;
            
            const botMsg = document.createElement('div');
            botMsg.className = 'msg bot';
            botMsg.innerText = 'Soch raha hoon...';
            box.appendChild(botMsg);
            box.scrollTop = box.scrollHeight;
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                botMsg.innerText = data.reply;
            } catch (err) {
                botMsg.innerText = 'Error: Jawab laane mein pareshani hui.';
            }
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_home():
    return HTML_PAGE
