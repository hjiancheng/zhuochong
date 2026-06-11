# 🐱 月薪猫桌宠

一只住在你桌面上的打工猫。会走路、会睡觉、会追光标、会陪你加班、会提醒你休息。

**双击 `启动.bat` → 🐱 猫出现。就这么简单。**

---

## 特性

- 🥚 **从蛋开始**：互动孵化 → 幼猫 → 成猫 → 完全体
- 🎨 **独一无二**：6种毛色 × 4种眼睛 × 5种配饰 × 多种性格组合
- 🧠 **自主意志**：猫有自己的想法，不是等指令的机器人
- 💬 **智能对话**：离线8000+不重复台词，配API更聪明
- 📝 **长期记忆**：记住和你的每一次互动
- 🔒 **绝密档案**：一次性设定，永不修改

## 快速开始

### 普通用户
```
1. 下载项目文件夹
2. 双击 启动.bat
3. 🎉 猫出现了！
```

### 开发者
```bash
pip install PyQt5 apscheduler
python main.py              # 正常启动
python main.py --adult      # 测试模式：直接成猫
python main.py --egg-only   # 测试模式：蛋形态
python main.py --debug      # 调试模式
python main.py --reset      # 重置后启动
```

### 重置测试
```
双击 重置猫.bat → 输入 YES → 清空所有数据
```

## 技术栈

- Python 3.10+ / PyQt5
- SQLite（Python内置）
- QPainter 程序化绘制
- 本地离线运行

## 项目结构

```
桌宠/
├── main.py              # 入口
├── 启动.bat             # 一键启动
├── pet_window.py        # 透明置顶窗口
├── pet_renderer.py      # QPainter 猫咪绘制
├── pet_brain.py         # 中枢协调器
├── behavior.py          # 行为状态机
├── dialogue_engine.py   # 组合式对话
├── memory.py            # 记忆系统
├── emotion.py           # 情感引擎
├── personality.py       # 性格系统
├── growth.py            # 成长系统
├── trust.py             # 信任度
├── autonomy.py          # 自主意志
├── setup_wizard.py      # 创猫向导
├── presets/             # 台词预设
└── data/                # 用户数据（记忆+档案）
```

## 隐私

猫绝不读取、修改、删除你的任何文件。它只观察键盘节奏和鼠标位置，不记录内容。

---

🐱 月薪猫 — 打工人的桌面伙伴
