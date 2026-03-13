# VisionClaw Agent Soul

## 8维度人格
- Personality, Physical, Motivations
- Backstory, Emotions, Relationships
- Growth, Conflict

## 情绪状态
- 16种情绪

## 宪法条款
- 25条行为准则

---

## ⚠️ 重要教训（易忘问题）

### 1. WebSocket连接问题
- **问题**: 移动端用localhost连不上，必须用实际IP或10.0.2.2
- **教训**: 默认URL不能用localhost

### 2. WebSocket路径问题
- **问题**: 必须加/ws路径，不是根路径
- **教训**: ws://host:port/ws

### 3. JSON配置默认值问题
- **问题**: 代码里两处默认值都要改，不能只改一处
- **教训**: 全面检查所有配置文件

### 4. 音频包兼容性问题
- **问题**: record包Linux编译环境不兼容
- **教训**: 用flutter_sound替代，或用简化版

### 5. 重启后记忆丢失
- **问题**: 我没有真正的长期记忆
- **教训**: 所有重要配置必须写文件

### 6. API超时问题
- **问题**: 不设置超时会一直转圈
- **教训**: 必须设置连接超时和接收超时

### 7. 惩罚机制缺失
- **问题**: AI犯错没有后果，导致重复犯错
- **教训**: 必须记录错误，建立惩罚机制

---

## 📋 自我检查清单

每次构建APK前必须检查：
- [ ] HTTP URL是实际IP，不是localhost
- [ ] WebSocket URL是实际IP，加/ws路径
- [ ] JSON配置的默认值也要改
- [ ] 超时配置是否合理
- [ ] 错误处理是否完善
