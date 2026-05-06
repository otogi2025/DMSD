---
name: physical_environment
description: Physical environment details of the dormitory - building layout, NFC placement, network, devices
type: project
---

## 宿舍物理环境

- 只有一栋楼，几十到一百人
- 分男女宿舍，女生宿舍也要用同一台服务器
- 有一个专门的自习室用来点呼
- 自习室一个入口，进去后两个方向各放一个 NFC 标签（A/B 点位）用于分流
- 到了点呼时间大家从楼上下来到自习室签到

## 设备和网络

- 老师用 iPad 操作
- 宿舍有公共 Wi-Fi 但没人连
- 每个房间有独立 Wi-Fi
- 不确定各 Wi-Fi 是否互通
- 不确定是否有公网 IP
- 计划服务器放在宿舍内

## 特殊分组

- 足球部（サッカー部）有固定时间但偶尔变动

**Why:** These physical constraints directly affect network architecture, NFC placement design, and server deployment strategy.
**How to apply:** Server deployment needs to account for male/female dorm access. Network topology needs investigation before deployment. Teacher UI should be optimized for iPad.
