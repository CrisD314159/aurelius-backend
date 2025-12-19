"""
This module contains a class used for convert text to voice
"""

import torch
import numpy as np
from fastapi import WebSocket
from kokoro import KPipeline
from app.exceptions.exception_handling import socket_exeption_handling


class TTSKokoroService:
    """
    This class contains a TTS model that converts text into natural voice
    """

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using {self.device} for Kokoro TTS")
        self.pipeline = KPipeline(lang_code='a', device=self.device)
        # other voices: 'af_bella', 'af_sarah', 'am_adam', af_heart
        self.voice_name = 'af_heart'

    async def stream_audio_response(self, websocket: WebSocket, text: str):
        """
        Generates TTS audio chunks via Kokoro and sends them to frontend
        """
        try:
            generator = self.pipeline(
                text,
                voice=self.voice_name,
                speed=1.1,
                split_pattern=r'\n+'
            )

            for i, (gs, ps, audio) in enumerate(generator):
                if audio is not None:
                    audio_data = audio.numpy() if isinstance(audio, torch.Tensor) else audio

                    # PCM RAW convertion
                    audio_int16 = (audio_data * 32767).astype(np.int16)

                    print("audio sent")
                    # Enviar los bytes puros
                    await websocket.send_bytes(audio_int16.tobytes())

        except (RuntimeError, ValueError, ConnectionError, OSError) as e:
            await socket_exeption_handling(ws=websocket, error_type="error",
                                           message="An error occurred on TTS service",
                                           details=str(e))
