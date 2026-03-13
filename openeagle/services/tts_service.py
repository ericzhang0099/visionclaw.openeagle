"""
真实语音合成服务 - 使用Piper TTS
"""

import base64
import io
import tempfile
import time
from pathlib import Path
from typing import Optional

# 尝试导入piper，如果失败则使用模拟
try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
    print("[TTS] Piper loaded successfully")
except ImportError:
    PIPER_AVAILABLE = False
    print("[TTS] Piper not available, using mock")


class TTSService:
    """语音合成服务"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "./models/piper"
        self.voice = None
        self._loaded = False
        # 延迟加载：不在初始化时加载模型

    def _load_model(self):
        """加载Piper模型（延迟加载）"""
        if self._loaded:
            return

        if PIPER_AVAILABLE:
            try:
                # 查找模型文件
                model_dir = Path(self.model_path)
                onnx_files = list(model_dir.glob("*.onnx"))

                if onnx_files:
                    model_file = onnx_files[0]
                    config_file = model_file.with_suffix(".json")

                    print(f"[TTS] Loading Piper model: {model_file}")
                    start = time.time()
                    self.voice = PiperVoice.load(str(model_file), str(config_file))
                    print(f"[TTS] Model loaded in {time.time() - start:.2f}s")
                else:
                    print(f"[TTS] No model found in {model_dir}")
            except Exception as e:
                print(f"[TTS] Failed to load model: {e}")
                self.voice = None

        self._loaded = True

    async def synthesize(self, text: str, voice: str = "zh_CN", speed: float = 1.0) -> bytes:
        """
        合成语音

        Args:
            text: 要合成的文本
            voice: 语音类型
            speed: 语速 (0.5-2.0)

        Returns:
            WAV音频数据 (bytes)
        """
        # 延迟加载模型
        self._load_model()

        # 尝试从缓存获取
        try:
            from core.cache import tts_cache
            cached_audio = tts_cache.get(text, voice, speed)
            if cached_audio:
                print(f"[TTS] Cache hit for: {text[:20]}...")
                return cached_audio
        except Exception as e:
            print(f"[TTS] Cache check failed: {e}")

        if not PIPER_AVAILABLE or self.voice is None:
            # 模拟模式 - 返回静音WAV
            print("[TTS] Using mock synthesis")
            return self._generate_silent_wav(duration=len(text) * 0.3)

        try:
            start = time.time()

            # 合成音频 - 使用正确的Piper API
            audio_buffer = io.BytesIO()

            # Piper合成 - 使用synthesize方法
            from piper.config import SynthesisConfig
            syn_config = SynthesisConfig(
                length_scale=1.0 / speed  # 语速调节
            )

            # 生成音频数据
            for audio_chunk in self.voice.synthesize(text, syn_config=syn_config):
                audio_buffer.write(audio_chunk.audio_int16_bytes)

            duration = time.time() - start
            print(f"[TTS] Synthesis completed in {duration:.2f}s")
            
            # 保存到缓存
            try:
                from core.cache import tts_cache
                tts_cache.set(text, voice, speed, audio_buffer.getvalue())
                print(f"[TTS] Saved to cache")
            except Exception as e:
                print(f"[TTS] Cache save failed: {e}")
            
            return audio_buffer.getvalue()

        except Exception as e:
            print(f"[TTS] Synthesis error: {e}")
            # 失败时返回模拟数据
            return self._generate_silent_wav(duration=len(text) * 0.3)

    def _generate_silent_wav(self, duration: float = 1.0) -> bytes:
        """生成静音WAV数据（用于模拟）"""
        import struct

        sample_rate = 16000
        num_samples = int(sample_rate * duration)

        # WAV头部
        header = b'RIFF'
        header += struct.pack('<I', 36 + num_samples * 2)  # 文件大小
        header += b'WAVE'
        header += b'fmt '
        header += struct.pack('<I', 16)  # fmt块大小
        header += struct.pack('<H', 1)   # 音频格式 (PCM)
        header += struct.pack('<H', 1)   # 声道数
        header += struct.pack('<I', sample_rate)  # 采样率
        header += struct.pack('<I', sample_rate * 2)  # 字节率
        header += struct.pack('<H', 2)   # 块对齐
        header += struct.pack('<H', 16)  # 采样位数
        header += b'data'
        header += struct.pack('<I', num_samples * 2)  # 数据大小

        # 静音数据
        data = b'\x00\x00' * num_samples

        return header + data


# 全局服务实例
tts_service = TTSService()
