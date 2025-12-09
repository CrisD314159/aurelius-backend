"""
 This class contains all the tools for STT service
"""
import asyncio
import io
import os
from faster_whisper import WhisperModel
from app.services.stt.stt_config import STTConfig
from app.exceptions.exception_handling import STTException


class STTService:
    """
    This class contains all the methods for STT service
    """

    def __init__(self, config: STTConfig):
        self.config = config
        self.load_model()

    def load_model(self):
        """
          This method loads the faster-whisper model
        """
        try:

            os.makedirs(self.config.stt_models_dir, exist_ok=True)
            self.model = WhisperModel(
                model_size_or_path=self.config.stt_model_size,
                device=self.config.stt_device,
                compute_type=self.config.stt_compute_type,
                download_root=self.config.stt_models_dir
            )
        except Exception as e:
            raise STTException(
                f"An error occurred while loading the STT model {e}"
            ) from e

    async def transcript_audio(self, audio_bytes: io.BytesIO):
        """This method transcribes audio from the backend"""
        if not self.model:
            raise STTException("STT model not found")

        loop = asyncio.get_event_loop()

        try:
            segments, info = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio_bytes,
                    language=self.config.stt_language,
                    beam_size=self.config.stt_beam_size,
                    vad_filter=self.config.stt_vad_filter,
                    vad_parameters={
                        "threshold": 0.5,
                        "min_speech_duration_ms": 250,
                        "min_silence_duration_ms": 100,
                    }
                )
            )

            segments_list = []
            full_text = []

            for segment in segments:
                segments_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                })
                full_text.append(segment.text.strip())
            result = {
                "text": " ".join(full_text),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": segments_list,
            }

            return result

        except Exception as e:
            raise STTException(
                f"An error occurred while transcribing the audio: {str(e)}") from e
