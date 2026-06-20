"""
core/msg_builder.py
解析消息模板构建具体发送的消息内容
优先使用 AI 生成（如果配置了 API Key）
支持模板池随机选取 🎲
"""

import random
import os
from utils.config import get_config
from utils.hitokoto import request_hitokoto


# 🎨 消息模板池（AI 失败时的后备方案）
# 每个模板作为「AI 主消息」的替代品，会与每日一言 + footer 组装
MESSAGE_TEMPLATES = [
    "无论相隔多远，每天的问候都是我惦记你的证明 🌟\n今天的你，也在认真生活吧？",
    "火花不熄，牵挂不止。愿今天的你被温柔以待 ☀️",
    "日子平平淡淡，但有人天天记得和你续火花，就是一种浪漫 💫\n希望你今天也一切顺利～",
    "生活忙碌，但每天的这一句问候，我从来没忘过 🌸\n因为你值得被惦记。",
    "世界很大，能每天和你续火花，是我的小幸运 ✨\n愿我们都能在平淡里找到光。",
]


def build_message_with_openai() -> str:
    """
    通过 AI 接口生成续火花消息
    支持 OpenAI、DeepSeek、Kimi 等兼容 API
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("⚠️ 未安装 openai SDK，请运行：pip install openai")
        return None

    config = get_config()
    openai_config = config.get("openai", {})
    
    # 优先从环境变量读取（.env 文件），其次从配置文件
    api_key = os.getenv("OPENAI_API_KEY", openai_config.get("api_key", ""))
    model = os.getenv("OPENAI_MODEL", openai_config.get("model", "gpt-4o"))
    base_url = os.getenv("OPENAI_BASE_URL", openai_config.get("base_url", "https://models.inference.ai.azure.com"))
    
    if not api_key:
        print("⚠️ 未配置 OPENAI_API_KEY，跳过 AI 生成")
        return None
    
    try:
        # 创建 OpenAI 客户端（兼容 DeepSeek 等）
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        print(f"🤖 正在调用 AI 生成消息（模型：{model}）...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """你是一个擅长写续火花消息的助手。

要求：
1. 生成一段 30-100 字的续火花消息
2. 内容要温馨、有深意、有感情
3. 可以引用诗词、名言，或表达真挚情感
4. 风格可以多样：温柔、文艺、治愈、哲理、感恩
5. 不要使用过于华丽的辞藻，真诚最重要
6. 直接输出消息内容，不要加引号、不要解释、不要加"助手："等前缀""",
                },
                {"role": "user", "content": "请生成一段有深意的续火花消息，今天是美好的一天"},
            ],
            temperature=0.9,  # 增加随机性，每次都不一样
            max_tokens=300,
        )
        
        ai_message = response.choices[0].message.content.strip()
        print(f"✅ AI 生成成功：{ai_message[:50]}...")
        return ai_message
        
    except Exception as e:
        print(f"❌ AI 生成失败：{e}")
        return None


def build_message() -> str:
    """
    构建消息内容，格式：
    [AI 生成的主消息]
    —— 每日一言 ——
    [一言 API 内容]
    [星星]火花续上啦[庆祝]
    今天也要开心哦～
    🌸 Day +1
    """
    footer = "[星星]火花续上啦[庆祝]\n今天也要开心哦～\n🌸 Day +1"

    # 1. 尝试 AI 生成主消息
    ai_body = build_message_with_openai()

    # 2. 尝试获取每日一言（一言 API）
    hitokoto = None
    try:
        hitokoto = request_hitokoto()
        print(f"✅ 每日一言获取成功：{hitokoto[:30]}...")
    except Exception as e:
        print(f"⚠️ 一言 API 调用失败：{e}")

    # 3. 组装消息
    parts = []

    if ai_body:
        # ✅ AI 成功 → AI内容 + 一言 + footer
        parts.append(ai_body)
        if hitokoto:
            parts.append(f"—— 每日一言 ——\n{hitokoto}")
        parts.append(footer)
        return "\n\n".join(parts).strip()
    else:
        # ❌ AI 失败 → 模板池选一个作为主消息
        template_body = random.choice(MESSAGE_TEMPLATES)
        parts.append(template_body)
        if hitokoto:
            parts.append(f"—— 每日一言 ——\n{hitokoto}")
        parts.append(footer)
        print(f"ℹ️ AI 未配置/失败，使用模板 + 一言 + footer")
        return "\n\n".join(parts).strip()
