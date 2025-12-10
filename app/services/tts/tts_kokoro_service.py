import torch
import numpy as np
from fastapi import WebSocket
from kokoro import KPipeline
from app.exceptions.exception_handling import TTSException


class TTSKokoroService:
    def __init__(self):
        # Configuración del dispositivo
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using {self.device} for Kokoro TTS")

        # Inicializar el Pipeline de Kokoro
        # lang_code='a' es para Inglés Americano. ('b' para británico).
        # El modelo se descargará automáticamente la primera vez.
        self.pipeline = KPipeline(lang_code='a', device=self.device)

        # Selección de voz. Kokoro usa nombres de voces predefinidas.
        # 'af_heart' es una voz femenina muy natural.
        # Otras opciones: 'af_bella', 'af_sarah', 'am_adam' (masculino), etc.
        self.voice_name = 'af_heart'

    async def stream_audio_response(self, websocket: WebSocket, text: str):
        """
        Generates TTS audio chunks via Kokoro and sends them to frontend
        """
        try:
            # Kokoro genera audio frase por frase usando su generador.
            # speed=1.0 es la velocidad normal.
            generator = self.pipeline(
                text,
                voice=self.voice_name,
                speed=1.0,
                split_pattern=r'\n+'  # Dividir por líneas nuevas o puntuación
            )

            # Iteramos sobre el generador. Kokoro devuelve (graphemes, phonemes, audio_tensor)
            for i, (gs, ps, audio) in enumerate(generator):
                if audio is not None:
                    # 'audio' es un Tensor de PyTorch o numpy array en float32.
                    # Convertimos a numpy si es tensor
                    audio_data = audio.numpy() if isinstance(audio, torch.Tensor) else audio

                    # Conversión IMPORTANTE: Float32 (-1.0 a 1.0) -> Int16 (-32768 a 32767)
                    # Esto es lo estándar para enviar audio crudo (PCM) por sockets.
                    audio_int16 = (audio_data * 32767).astype(np.int16)

                    print("audio sent")
                    # Enviar los bytes puros
                    await websocket.send_bytes(audio_int16.tobytes())

        except Exception as e:
            raise TTSException(
                f"An error occurred during Kokoro TTS streaming: {e}") from e
