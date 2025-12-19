"""
This module contains a class with tools for websocket connection handling
"""

from typing import List
import math
import numpy as np
from fastapi import WebSocket
from app.utils.model_loading.model_loading import aurelius_models


class ConnectionManager:
    """
    This class is used as an auxiliar for 
    connect, and disconnect websockets
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    def get_llm_model(self):
        """
        Returns the current llm class instance
        """
        return aurelius_models['llm']

    def get_stt_model(self):
        """
        Returns the current stt instance
        """
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

        except (ValueError, TypeError, ZeroDivisionError) as e:
            print(f"Error detecting silence: {e}")
            return False  # Default to False so we don't cut off user on errors
