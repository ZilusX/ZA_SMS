from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

# كلاس لإدارة الاتصالات النشطة بين الدول المختلفة
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # إرسال الرسالة فوراً لجميع المتصلين (سواء في العراق أو إيران أو غيرها)
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# واجهة بسيطة لتجربة الشات داخل المتصفح
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>International Fast Chat</title>
        <meta charset="utf-8">
        <style>
            body { font-family: sans-serif; background: #f0f2f5; padding: 20px; }
            #chat-box { background: white; height: 300px; overflow-y: scroll; padding: 15px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ccc; }
            input { width: 70%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
            button { padding: 10px 20px; background: #0084ff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>رسائل دولية فورية ⚡</h2>
        <div id="chat-box"></div>
        <input type="text" id="messageText" autocomplete="off" placeholder="اكتب رسالتك هنا..."/>
        <button onclick="sendMessage()">إرسال</button>

        <script>
            // فتح قناة اتصال مباشرة مع السيرفر (تتغير الـ URL عند رفع الموقع)
            var ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                var chatBox = document.getElementById('chat-box');
                var message = document.createElement('div');
                message.style.margin = "5px 0";
                message.innerText = event.data;
                chatBox.appendChild(message);
                chatBox.scrollTop = chatBox.scrollHeight; // النزول لآخر رسالة تلقائياً
            };

            function sendMessage() {
                var input = document.getElementById("messageText");
                if(input.value.trim() !== "") {
                    ws.send(input.value);
                    input.value = '';
                }
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # استقبال الرسالة من أي دولة
            data = await websocket.receive_text()
            # بثها فوراً للبقية في نفس اللحظة
            await manager.broadcast(f"رسالة جديدة: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

