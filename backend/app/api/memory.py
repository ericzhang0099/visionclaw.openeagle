"""
Memory API - 基于OpenClaw MEMORY.md
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime

router = APIRouter()

# 存储路径
MEMORY_DIR = "./memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

# 记忆模型
class MemoryEntry(BaseModel):
    content: str
    memory_type: str = "episodic"  # episodic/semantic/procedural/working
    importance: float = 0.5
    metadata: Optional[Dict[str, Any]] = {}


class UserPreference(BaseModel):
    key: str
    value: Any


@router.post("/memory")
async def add_memory(entry: MemoryEntry):
    """添加记忆"""
    memory_id = f"{datetime.now().timestamp()}"
    
    memory_data = {
        "id": memory_id,
        "content": entry.content,
        "type": entry.memory_type,
        "importance": entry.importance,
        "metadata": entry.metadata,
        "created_at": datetime.now().isoformat()
    }
    
    # 保存到文件
    file_path = os.path.join(MEMORY_DIR, f"{memory_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)
    
    return {"code": 0, "data": {"memory_id": memory_id}}


@router.get("/memory")
async def get_memories(
    memory_type: Optional[str] = None,
    limit: int = 50
):
    """获取记忆列表"""
    memories = []
    
    for filename in os.listdir(MEMORY_DIR):
        if not filename.endswith('.json'):
            continue
            
        file_path = os.path.join(MEMORY_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if memory_type is None or data.get('type') == memory_type:
                    memories.append(data)
        except Exception:
            continue
    
    # 按时间排序
    memories.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return {"code": 0, "data": memories[:limit]}


@router.get("/memory/search")
async def search_memories(q: str, limit: int = 10):
    """搜索记忆"""
    results = []
    
    for filename in os.listdir(MEMORY_DIR):
        if not filename.endswith('.json'):
            continue
            
        file_path = os.path.join(MEMORY_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if q.lower() in data.get('content', '').lower():
                    results.append(data)
        except Exception:
            continue
    
    return {"code": 0, "data": results[:limit]}


@router.post("/memory/preference")
async def set_preference(pref: UserPreference):
    """设置用户偏好"""
    pref_file = os.path.join(MEMORY_DIR, "preferences.json")
    
    preferences = {}
    if os.path.exists(pref_file):
        with open(pref_file, 'r', encoding='utf-8') as f:
            preferences = json.load(f)
    
    preferences[pref.key] = pref.value
    
    with open(pref_file, 'w', encoding='utf-8') as f:
        json.dump(preferences, f, ensure_ascii=False, indent=2)
    
    return {"code": 0, "message": "偏好已保存"}


@router.get("/memory/preference")
async def get_preferences():
    """获取用户偏好"""
    pref_file = os.path.join(MEMORY_DIR, "preferences.json")
    
    if not os.path.exists(pref_file):
        return {"code": 0, "data": {}}
    
    with open(pref_file, 'r', encoding='utf-8') as f:
        preferences = json.load(f)
    
    return {"code": 0, "data": preferences}


@router.post("/memory/profile")
async def update_user_profile(profile: Dict[str, Any]):
    """更新用户画像"""
    profile_file = os.path.join(MEMORY_DIR, "profile.json")
    
    current_profile = {}
    if os.path.exists(profile_file):
        with open(profile_file, 'r', encoding='utf-8') as f:
            current_profile = json.load(f)
    
    current_profile.update(profile)
    current_profile['updated_at'] = datetime.now().isoformat()
    
    with open(profile_file, 'w', encoding='utf-8') as f:
        json.dump(current_profile, f, ensure_ascii=False, indent=2)
    
    return {"code": 0, "message": "画像已更新"}


@router.get("/memory/profile")
async def get_user_profile():
    """获取用户画像"""
    profile_file = os.path.join(MEMORY_DIR, "profile.json")
    
    if not os.path.exists(profile_file):
        return {"code": 0, "data": {}}
    
    with open(profile_file, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    return {"code": 0, "data": profile}


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    """删除记忆"""
    file_path = os.path.join(MEMORY_DIR, f"{memory_id}.json")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"code": 0, "message": "记忆已删除"}
    
    raise HTTPException(status_code=404, detail="记忆不存在")


@router.delete("/memory")
async def clear_memory(memory_type: Optional[str] = None):
    """清理记忆"""
    count = 0
    
    for filename in os.listdir(MEMORY_DIR):
        if not filename.endswith('.json'):
            continue
        
        if memory_type and memory_type not in filename:
            continue
            
        file_path = os.path.join(MEMORY_DIR, filename)
        os.remove(file_path)
        count += 1
    
    return {"code": 0, "message": f"已清理{count}条记忆"}
