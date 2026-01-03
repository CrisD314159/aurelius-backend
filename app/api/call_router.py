"""This module contains everything needed for establish 
a communication between frontend and backend using websockets"""

import io
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.wav_converter.wav_converter import WavConverter
from app.api.connection_manager import ConnectionManager


call_router = APIRouter()

manager = ConnectionManager()


@call_router.websocket("/ws/call/{chat_id}")
async def electron_prompt(websocket: WebSocket, chat_id: int):
    """
    This method receives and handles the websocket connection from the frontend.
    First, receives the user speech audio, then using STT service converts the waveform
    to text. After that, this method uses the LLM and TTS services to generate 
    and send a response to the frontend

    :param websocket: WebSocket connection
    :type websocket: WebSocket
    """
    await manager.connect(websocket=websocket)

    stt_service = manager.get_stt_model()
    llm_service = manager.get_llm_model()

    audio_buffer = bytearray()
    silence_counter = 0
    min_audio_length = 4096

    try:
        while True:
            chunk = await websocket.receive_bytes()
            audio_buffer.extend(chunk)

            if manager.is_silence(chunk):
                silence_counter += 1
            else:
                silence_counter = 0

            print(
                f"Silence counter: {silence_counter}/{9}")

            if silence_counter >= 8 and len(audio_buffer) >= min_audio_length:

                await websocket.send_text("silence")

                if len(audio_buffer) > 0:
                    try:
                        # This converts the received data into a memory saved wav file
                        wav_header = WavConverter.create_wav_header(
                            sample_rate=16000,
                            channels=1,
                            sample_width=2,
                            data_size=len(audio_buffer)
                        )
                        wav_bytes_to_send = wav_header + bytes(audio_buffer)

                        wav_stream = io.BytesIO(wav_bytes_to_send)

                        transcription = await stt_service.transcript_audio(wav_stream)
                        print(transcription)

                    except (ValueError, IOError, RuntimeError) as e:
                        print(
                            f"Error during audio processing/transcription: {e}")

                    if transcription.strip():
                        print(f"Transcription: {transcription}")
                        await websocket.send_json({
                            "message": transcription,
                            "type": "transcription"
                        })

                        response = await llm_service.assemble_prompt(transcription,
                                                                     websocket=websocket,
                                                                     chat_id=chat_id,
                                                                     use_voice=True)
                        if response:
                            await websocket.send_text("TTS_END")
                    else:
                        print("Empty transcription - no speech detected")

                audio_buffer.clear()
                silence_counter = 0

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except (ValueError, IOError, RuntimeError, ConnectionError) as e:
        print(f"Error in websocket: {e}")
        manager.disconnect(websocket)
