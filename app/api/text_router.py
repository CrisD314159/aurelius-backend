"""This module contains everything needed for establish 
a communication between frontend and backend using websockets"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.connection_manager import ConnectionManager


text_router = APIRouter()

manager = ConnectionManager()


@text_router.websocket("/ws/text/{chat_id}")
async def electron_prompt(websocket: WebSocket, chat_id: int):
    """
    This method receives and handles the websocket connection from the frontend.
    :param websocket: WebSocket connection
    :type websocket: WebSocket
    """
    await manager.connect(websocket=websocket)
    llm_service = manager.get_llm_model()

    try:
        while True:
            prompt = await websocket.receive_text()

            await llm_service.assemble_prompt(prompt,
                                              websocket=websocket,
                                              chat_id=chat_id,
                                              use_voice=False)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except (ValueError, IOError, RuntimeError, ConnectionError) as e:
        print(f"Error in websocket: {e}")
        manager.disconnect(websocket)
