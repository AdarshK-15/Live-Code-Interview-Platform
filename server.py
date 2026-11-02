import json
from datetime import datetime
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Live Technical Interview Engine")

# Mount static folder for frontend assets
app.mount("/static", StaticFiles(directory="static"), name="static")

DEFAULT_TEMPLATES = {
    "javascript": (
        "// Collaborative JavaScript Environment\n"
        "function twoSum(nums, target) {\n"
        "    const map = new Map();\n"
        "    for (let i = 0; i < nums.length; i++) {\n"
        "        const complement = target - nums[i];\n"
        "        if (map.has(complement)) {\n"
        "            return [map.get(complement), i];\n"
        "        }\n"
        "        map.set(nums[i], i);\n"
        "    }\n"
        "    return [];\n"
        "}\n\n"
        "console.log('Result:', twoSum([2, 7, 11, 15], 9));"
    ),
    "python": (
        "# Collaborative Python Environment\n"
        "def two_sum(nums, target):\n"
        "    seen = {}\n"
        "    for idx, num in enumerate(nums):\n"
        "        diff = target - num\n"
        "        if diff in seen:\n"
        "            return [seen[diff], idx]\n"
        "        seen[num] = idx\n"
        "    return []\n\n"
        "print('Result:', two_sum([2, 7, 11, 15], 9))"
    ),
    "java": (
        "// Collaborative Java Environment\n"
        "import java.util.*;\n\n"
        "public class Solution {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"Solution initialized.\");\n"
        "    }\n"
        "}"
    ),
    "cpp": (
        "// Collaborative C++ Environment\n"
        "#include <iostream>\n"
        "#include <vector>\n\n"
        "int main() {\n"
        "    std::cout << \"Ready for execution.\" << std::endl;\n"
        "    return 0;\n"
        "}"
    )
}

class RoomSession:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.language = "javascript"
        self.code = DEFAULT_TEMPLATES["javascript"]
        # Maps WebSocket connection -> Username
        self.clients: Dict[WebSocket, str] = {}

    def get_users_list(self):
        return list(self.clients.values())


class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, RoomSession] = {}

    def get_or_create_room(self, room_id: str) -> RoomSession:
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = RoomSession(room_id)
        return self.active_rooms[room_id]

    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()
        room = self.get_or_create_room(room_id)
        room.clients[websocket] = username

        # Send initial room state exclusively to the new participant
        await websocket.send_text(json.dumps({
            "type": "INIT_STATE",
            "code": room.code,
            "language": room.language,
            "users": room.get_users_list()
        }))

        # Broadcast participant join to other peers
        await self.broadcast_to_room(room_id, {
            "type": "USER_JOINED",
            "username": username,
            "users": room.get_users_list()
        }, exclude=websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_rooms:
            room = self.active_rooms[room_id]
            username = room.clients.pop(websocket, "Unknown User")
            
            # Prune room if completely empty
            if not room.clients:
                del self.active_rooms[room_id]
            return username, room.get_users_list() if room_id in self.active_rooms else []
        return None, []

    async def broadcast_to_room(self, room_id: str, message: dict, exclude: WebSocket = None):
        if room_id not in self.active_rooms:
            return
        payload = json.dumps(message)
        room = self.active_rooms[room_id]
        stale_sockets = []

        for client_ws in room.clients:
            if client_ws != exclude:
                try:
                    await client_ws.send_text(payload)
                except Exception:
                    stale_sockets.append(client_ws)

        for stale in stale_sockets:
            room.clients.pop(stale, None)


manager = ConnectionManager()

@app.get("/")
async def serve_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    # Query parameters for candidate identity
    query_params = dict(websocket.query_params)
    username = query_params.get("username", "Candidate")

    await manager.connect(websocket, room_id, username)
    room = manager.get_or_create_room(room_id)

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            action = data.get("type")

            if action == "CODE_CHANGE":
                room.code = data.get("code", "")
                await manager.broadcast_to_room(room_id, {
                    "type": "CODE_UPDATE",
                    "code": room.code
                }, exclude=websocket)

            elif action == "LANGUAGE_CHANGE":
                new_lang = data.get("language", "javascript")
                room.language = new_lang
                if new_lang in DEFAULT_TEMPLATES:
                    room.code = DEFAULT_TEMPLATES[new_lang]
                await manager.broadcast_to_room(room_id, {
                    "type": "LANGUAGE_UPDATE",
                    "language": room.language,
                    "code": room.code
                })

            elif action == "CHAT_MESSAGE":
                text = data.get("text", "").strip()
                if text:
                    timestamp = datetime.now().strftime("%H:%M")
                    await manager.broadcast_to_room(room_id, {
                        "type": "CHAT_BROADCAST",
                        "username": username,
                        "text": text,
                        "time": timestamp
                    })

    except WebSocketDisconnect:
        leaving_user, updated_users = manager.disconnect(websocket, room_id)
        if leaving_user:
            await manager.broadcast_to_room(room_id, {
                "type": "USER_LEFT",
                "username": leaving_user,
                "users": updated_users
            })

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)