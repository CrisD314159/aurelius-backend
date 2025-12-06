import struct


class WavConverter:
    def __init__(self):
        pass

    @staticmethod
    def create_wav_header(sample_rate: int, channels: int, sample_width: int, data_size: int) -> bytes:
        """Generates a minimal WAV header."""

        # Format chunk
        sub_chunk_1_size = 16
        audio_format = 1  # PCM = 1
        byte_rate = sample_rate * channels * sample_width
        block_align = channels * sample_width

        # Main header size (44 bytes for a standard WAV file)
        chunk_size = 36 + data_size

        header = bytearray()

        # RIFF chunk
        header.extend(b'RIFF')
        header.extend(struct.pack('<I', chunk_size))
        header.extend(b'WAVE')

        # fmt chunk
        header.extend(b'fmt ')
        header.extend(struct.pack('<I', sub_chunk_1_size))
        header.extend(struct.pack('<H', audio_format))
        header.extend(struct.pack('<H', channels))
        header.extend(struct.pack('<I', sample_rate))
        header.extend(struct.pack('<I', byte_rate))
        header.extend(struct.pack('<H', block_align))
        header.extend(struct.pack('<H', sample_width * 8))

        # data chunk
        header.extend(b'data')
        header.extend(struct.pack('<I', data_size))

        return bytes(header)

    @staticmethod
    def pcm_to_wav(pcm_data: bytes, sample_rate: int = 16000,
                   channels: int = 1, bits_per_sample: int = 16) -> bytes:
        """
        Convert raw PCM data to WAV format.

        :param pcm_data: Raw PCM audio data
        :param sample_rate: Sample rate in Hz
        :param channels: Number of audio channels
        :param bits_per_sample: Bits per sample
        :return: Complete WAV file as bytes
        """
        header = WavConverter.create_wav_header(
            len(pcm_data), sample_rate, channels, bits_per_sample)
        return header + pcm_data
