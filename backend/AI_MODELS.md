# VisionClaw AI模型配置

## LLM (大语言模型)

### 主模型: MiniMax
- API: https://api.minimax.chat/v1/chat/completions
- 模型: MiniMax-M2.5
- Key: sk-cp-lAg96b64ITHi7kzT-E2iDunuuhF7iMT5TgFiQBYMlsJEkVcSOgK_Ms_dR9ghE7zwUkBzf-09jiyOkTwAC5RHmF3lUGfnjcuTevRNHQwIfeeiroKIXDMRFg0

### 备用模型
- DeepSeek: deepseek-chat
- OpenAI: gpt-3.5-turbo

## 视觉模型

### 图像分析 (首选)
- 模型: Qwen-VL-Max
- 用途: 图像理解、问答

### 目标检测 (首选)
- 模型: YOLO v8
- 用途: 目标检测、分割

### OCR识别 (首选)
- 模型: EasyOCR / PaddleOCR
- 用途: 文字识别

### 动作检测 (首选)
- 模型: MediaPipe / OpenPose
- 用途: 人体姿态、动作分析

## 语音模型

### 语音识别 (首选)
- 模型: Whisper (large-v3)
- 用途: 语音转文字

### 语音合成 (首选)
- 模型: CosyVoice / GPT-SoVITS
- 用途: 文字转语音

## 模型优先级

1. 优先使用免费/开源模型
2. 备用商业模型
3. 本地部署模型
