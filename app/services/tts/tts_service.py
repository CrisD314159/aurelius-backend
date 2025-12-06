from TTS.api import TTS
import torch
from fastapi import WebSocket
from app.exceptions.exception_handling import TTSException


class TTSService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using {self.device} for TTS")
        self.tts_model = TTS(
            "tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        self.voice_seed_path = "/app/utils/voice_seed/friday.mp3"

    async def stream_audio_response(self,
                                    websocket: WebSocket,
                                    text: str):
        """
        Generates TTS audio chunks that will be send to frontend
        """
        try:
            audio_stream_generator = self.tts_model.tts_stream(
                text=text,
                speaker_wav=self.voice_seed_path,
                language="en",
                split_sentences=True
            )

            for chunk in audio_stream_generator:
                await websocket.send_bytes(chunk.tobytes())

            await websocket.send_text("TTS_END")

        except Exception as e:
            raise TTSException(
                f"An error occurred during TTS streaming: {e}") from e
