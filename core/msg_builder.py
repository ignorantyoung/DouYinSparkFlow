"""
core/msg_builder.py
解析消息模板构建具体发送的消息内容
支持模板池随机选取 🎲 + 国内AI API支持 🇨🇳
"""

import random
from utils.config import get_config
from utils.hitokoto import request_hitokoto
from datetime import date

# 🎨 消息模板池
# 每次运行随机选择一个，让每天的续火消息都有新鲜感
# 每个模板都支持 [API] 占位符（会被一言API内容替换）
MESSAGE_TEMPLATES = [
    # 🌿 模板1：温柔陪伴风
    """🌿 今天是和你续火花的第 N 天

有时候觉得，每天的这条消息
就像是我们之间不打扰的默契
不说话，但每天都在

[API]

续火花，也是在续一段关系
愿我们都被这个世界温柔以待
早安 ☀️""",

    # ✨ 模板2：文艺诗意风
    """✨ 烟火气里藏着最真的感情

城市和城市之间
屏幕和屏幕之间
我们隔着千里万里
却每天在这一小簇火花里相遇

[API]

今天的火花，我帮你续上了
明天的，就交给你啦 🔥""",

    # 🌙 模板3：深夜感怀风
    """🌙 夜深了，替你续上今天的火花

有人说，每天坚持做一件小事
是世界上最浪漫的事之一
我想，我们都在做这样的事

[API]

不管今天过得怎样
明天太阳照常升起
火花也是 🔥""",

    # 💫 模板4：温暖治愈风
    """💫 你知道吗
每一次续火花
都是在说「我还记得你」

忙的时候不打扰
闲的时候不忘记
这就是成年人最舒服的关系吧

[API]

今天也辛苦了，早点休息 🌙
火花我帮你续着呢""",

    # 🍃 模板5：哲理深意风
    """🍃 日子是一天天过的
火花是一天天续的
感情也是

不需要每天都有说不完的话
但只要每天都有这一条消息
就知道，彼此都还在

[API]

愿你今天也有小小的开心 🌸
火花 +1""",

    # ☀️ 模板6：阳光励志风
    """☀️ 早安！今天的火花我来了

生活不总是一帆风顺
但有个人每天记得和你续火花
这件事本身，就很美好

[API]

新的一天，新的开始
愿你今天遇到所有美好的事 🌈""",

    # 🌸 模板7：感恩珍惜风
    """🌸 感恩每天都有你的火花

在这个快节奏的世界里
能有一个人，每天都记得和你互动
真的是一件很奢侈的事

[API]

珍惜每一次续火花
珍惜每一个还在身边的人 💎""",

    # 🔥 模板8：轻松幽默风
    """🔥 火花续上啦！

你知道吗，抖音火花超过 30 天的话
会解锁特殊标识哦
我们一起努力，冲冲冲！

[API]

（这条消息是自动发送的
但我保证心意是真的 😊）""",

    # 🌊 模板9：平淡珍贵风
    """🌊 最珍贵的感情
不是每天都轰轰烈烈
而是平淡里藏着细水长流

今天的火花到了
明天的，我们继续

[API]

愿你今晚好梦，明日可期 🌅""",

    # 🍂 模板10：思念传递风
    """🍂 季节更替，火花不变

风来了又走
花开了又谢
但每天的这条续火消息
一直都在

[API]

你在远方还好吗？
火花替我陪着你 🤍""",
]


def build_message_with_openai() -> str:
    """
    通过 AI 接口生成续火花消息，内容丰富，不超过50字
    支持 OpenAI 及国内兼容模型（DeepSeek、Kimi、智谱、通义等）
    """
    from openai import OpenAI
    import os

    config = get_config()
    openai_config = config.get("openai", {})
    api_key = os.getenv("OPENAI_API_KEY", openai_config.get("api_key", ""))
    model = openai_config.get("model", "deepseek-chat")
    
    # 🇨🇳 支持自定义 base_url（国内模型兼容 OpenAI SDK）
    base_url = openai_config.get("base_url", "https://api.deepseek.com")

    if not api_key:
        # 如果没有配置 AI API，回退到模板池
        return build_message()

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个擅长写续火花消息的助手。用户需要你生成一段不超过50字的续火花消息，内容要温馨、有深意、适合发给聊天对象。请直接输出消息内容，不要加引号或其他修饰。",
            },
            {"role": "user", "content": "生成一段有深意的续火花消息，直接输出内容不要思考过程"},
        ],
    )

    return response.choices[0].message.content.strip()


def build_message() -> str:
    """
    构建消息内容
    从模板池中随机选择一个模板，每天都不一样 🎲
    """
    # 从模板池中随机选择一个模板
    message = random.choice(MESSAGE_TEMPLATES)
    
    # 替换 [API] 占位符（一言API内容）
    if "[API]" in message:
        api_content = request_hitokoto()
        message = message.replace("[API]", api_content)

    return message.strip()
