import asyncio

from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    def __init__(self) -> None:
        self.rooms: dict[int, set[WebSocket]] = {}  # словарь соединений

    async def connect(
        self,
        chat_id: int,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()  # принять соединение

        connections = self.rooms.setdefault(
            chat_id, set()
        )  # если есть берем, или сохраянем
        connections.add(websocket)  # добавляем соединение(участника)

    def disconnect(
        self,
        chat_id: int,
        websocket: WebSocket,
    ) -> None:
        self.rooms[chat_id].discard(websocket)

    async def broadcast(
        self,
        chat_id: int,
        message: dict,
    ) -> None:
        for connection in self.rooms[chat_id].copy():
            await connection.send_json(
                message
            )  # Отправить сообщение всем участником комнаты


ws_manager = WebSocketManager()
