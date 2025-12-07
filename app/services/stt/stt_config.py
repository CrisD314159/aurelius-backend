"""
This module contains the required configuration for the Speech to text (STT) model
"""


class STTConfig:
    """
    This class contains all the configuration for the STT Model
    - The used model is called Faster-Whisper
    - The general config defines the size, device and compute type of the model
    - The performance config defines the beam size and the silence filter 
    """
    # General config
    stt_model_size: str = "base"
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"
    stt_language: str = "en"

    # Performance config
    stt_beam_size: int = 5
    stt_vad_filter: bool = True

    stt_models_dir: str = "/app/stt_models"
