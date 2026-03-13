"""
缓存模块 - 提供TTS结果缓存功能
"""

import hashlib
import time
from pathlib import Path
from typing import Optional


class TTSCache:
    """
    TTS结果缓存
    
    缓存语音合成结果，避免重复合成相同文本
    """
    
    def __init__(self, cache_dir: str = "./cache/tts", max_age_hours: int = 24):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录
            max_age_hours: 缓存最大存活时间（小时）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age_seconds = max_age_hours * 3600
    
    def _get_cache_key(self, text: str, voice: str, speed: float) -> str:
        """
        生成缓存键
        
        Args:
            text: 文本内容
            voice: 语音类型
            speed: 语速
            
        Returns:
            MD5哈希值作为缓存键
        """
        content = f"{text}:{voice}:{speed}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, text: str, voice: str, speed: float) -> Optional[bytes]:
        """
        获取缓存的音频数据
        
        Args:
            text: 文本内容
            voice: 语音类型
            speed: 语速
            
        Returns:
            缓存的音频数据，如果不存在或已过期则返回None
        """
        cache_key = self._get_cache_key(text, voice, speed)
        cache_file = self.cache_dir / f"{cache_key}.wav"
        
        if not cache_file.exists():
            return None
        
        # 检查缓存是否过期
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > self.max_age_seconds:
            # 删除过期缓存
            try:
                cache_file.unlink()
            except:
                pass
            return None
        
        # 读取缓存
        try:
            return cache_file.read_bytes()
        except:
            return None
    
    def set(self, text: str, voice: str, speed: float, audio_data: bytes):
        """
        保存音频数据到缓存
        
        Args:
            text: 文本内容
            voice: 语音类型
            speed: 语速
            audio_data: 音频数据
        """
        cache_key = self._get_cache_key(text, voice, speed)
        cache_file = self.cache_dir / f"{cache_key}.wav"
        
        try:
            cache_file.write_bytes(audio_data)
        except Exception as e:
            print(f"[TTSCache] Failed to write cache: {e}")
    
    def clear_expired(self):
        """清理过期缓存文件"""
        now = time.time()
        expired_count = 0
        
        for cache_file in self.cache_dir.glob("*.wav"):
            file_age = now - cache_file.stat().st_mtime
            if file_age > self.max_age_seconds:
                try:
                    cache_file.unlink()
                    expired_count += 1
                except:
                    pass
        
        if expired_count > 0:
            print(f"[TTSCache] Cleared {expired_count} expired cache files")
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        total_files = 0
        total_size = 0
        
        for cache_file in self.cache_dir.glob("*.wav"):
            total_files += 1
            total_size += cache_file.stat().st_size
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir)
        }


# 全局缓存实例
tts_cache = TTSCache()
