"""This module contains everything needed for establish 
a communication between frontend and backend using websockets"""

from typing import List
import io
import math
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.wav_converter.wav_converter import WavConverter
from app.utils.model_loading.model_loading import aurelius_models
from app.services.stt.stt_service import STTService
from app.services.llm.llm_service import LLMService


router = APIRouter()


class ConnectionManager:
    """
    This class is used as an auxiliar for 
    connect, and disconnect websockets
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    def get_llm_model(self):
        return aurelius_models['llm']

    def get_stt_model(self):
        return aurelius_models['stt']

    async def connect(self, websocket: WebSocket):
        """This method receives a websocket from the frontend"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """This method disconnects a websocket from the frontend"""
        self.active_connections.remove(websocket)

    def is_silence(self, chunk: bytes, threshold_db: int = -40) -> bool:
        """
        Detect silence using Math/Numpy on Raw PCM data.
        It only works with PCM Audio
        """
        try:
            if len(chunk) == 0:
                return True
            audio_data = np.frombuffer(chunk, dtype=np.int16)

            if len(audio_data) == 0:
                return True

            # Calculate RMS (Root Mean Square) Amplitude
            rms = np.sqrt(np.mean(audio_data.astype(np.int64)**2))

            # 3. Convert RMS to Decibels (dB)
            # 32768 is the max amplitude for 16-bit audio
            if rms > 0:
                db = 20 * math.log10(rms / 32768)
            else:
                db = -999  # Absolute silence

            is_silent = db < threshold_db

            return is_silent

        except Exception as e:
            print(f"Error detecting silence: {e}")
            return False  # Default to False so we don't cut off user on errors


manager = ConnectionManager()


@router.websocket("/ws/call")
async def electron_prompt(websocket: WebSocket):
    """
    This method receives and handles the websocket connection from the frontend.
    First, receives the user speech audio, then using STT service converts the waveform
    to text. After that, this method uses the LLM and TTS services to generate 
    and send a response to the frontend

    :param websocket: WebSocket connection
    :type websocket: WebSocket
    """
    await manager.connect(websocket=websocket)

    stt_service: STTService = manager.get_stt_model()
    llm_service: LLMService = manager.get_llm_model()

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

            if silence_counter >= 9 and len(audio_buffer) >= min_audio_length:

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

                    except Exception as e:
                        print(
                            f"Error during audio processing/transcription: {e}")

                    if transcription.strip():
                        print(f"Transcription: {transcription}")

                        answer = await llm_service.assemble_prompt(transcription, websocket=websocket)
                        print(f"LLM Response: {answer}")

                        # Send response back to front (this will be replaced with the tts answer)
                        await websocket.send_json({
                            "type": "response",
                            "transcription": transcription,
                            "answer": answer
                        })
                    else:
                        print("Empty transcription - no speech detected")

                audio_buffer.clear()
                silence_counter = 0

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket: {e}")
        manager.disconnect(websocket)
