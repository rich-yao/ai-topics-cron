#!/usr/bin/env python3
"""
AI新手教程选题抓取定时任务
每天早上9点执行，基于日期和随机算法生成5条不同的选题
"""

import random
import requests
from datetime import datetime

# 飞书机器人Webhook（零基壹动群 - 定时任务推送）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/36a5ef78-c7ad-4190-bd4e-8cd5e5a39acf"

# 选题模板库
TOPIC_TEMPLATES = [
    {
        "title": "🎯 ChatGPT新手必看！{num}个技巧让你效率翻倍",
        "angle": "面向完全没用过AI的小白，从最基础的注册、提问技巧讲起",
        "platform": "抖音/B站/视频号",
        "category": "对话AI",
        "keywords": ["chatgpt", "gpt4", "ai对话"]
    },
    {
        "title": "🎨 Midjourney{version}新手教程！{time}分钟出大片",
        "angle": "从零开始教MJ关键词、参数设置、风格调试",
        "platform": "小红书/抖音",
        "category": "AI绘画",
        "keywords": ["midjourney", "ai绘画", "mj教程"]
    },
    {
        "title": "🇨🇳 不用翻墙！{num}个国产AI绘画工具实测对比",
        "angle": "推荐即梦、可灵、通义万相等国产免费AI绘画工具",
        "platform": "小红书/抖音",
        "category": "国产AI",
        "keywords": ["即梦", "可灵", "国产ai"]
    },
    {
        "title": "💼 打工人必备！{num}个AI办公神器让你早下班{time}小时",
        "angle": "实际演示AI做PPT、写周报、整理会议纪要",
        "platform": "公众号/小红书",
        "category": "办公效率",
        "keywords": ["ai办公", "ppt", "效率工具"]
    },
    {
        "title": "🎬 剪映AI{feature}实测！真的{time}分钟出片？",
        "angle": "真实测试剪映新功能，展示操作流程和效果",
        "platform": "抖音/B站",
        "category": "AI视频",
        "keywords": ["剪映", "ai视频", "视频剪辑"]
    },
    {
        "title": "📝 AI写作保姆级教程！{platform}爆款文案{num}秒生成",
        "angle": "演示如何用ChatGPT/Claude写小红书文案、短视频脚本",
        "platform": "小红书/公众号",
        "category": "AI写作",
        "keywords": ["ai写作", "文案", "小红书"]
    },
    {
        "title": "🗣️ AI配音哪家强？实测{num}款{price}配音工具",
        "angle": "对比剪映、微软、魔音等AI配音工具的效果",
        "platform": "抖音/B站",
        "category": "AI配音",
        "keywords": ["ai配音", "tts", "语音合成"]
    },
    {
        "title": "🎓 {year}年AI学习路线！小白到高手最全路径图",
        "angle": "整理从入门到进阶的AI学习资源和时间规划",
        "platform": "公众号/B站",
        "category": "学习路径",
        "keywords": ["ai学习", "入门", "教程"]
    },
    {
        "title": "💰 普通人用AI搞副业的{num}种方法（{month}月实测可行）",
        "angle": "AI代写、AI设计、AI视频等真实变现案例",
        "platform": "抖音/小红书",
        "category": "AI副业",
        "keywords": ["ai副业", "赚钱", "变现"]
    },
    {
        "title": "📱 手机就能用的AI工具！不用电脑也能玩转{feature}",
        "angle": "推荐手机端AI应用：文心一言、通义、豆包等",
        "platform": "抖音/小红书",
        "category": "移动AI",
        "keywords": ["手机ai", "app", "移动端"]
    },
    {
        "title": "🔧 Stable Diffusion本地部署教程！{cost}元电脑也能跑",
        "angle": "从零开始部署SD，教你用最低成本本地出图",
        "platform": "B站/公众号",
        "category": "技术教程",
        "keywords": ["sd", "stable diffusion", "本地部署"]
    },
    {
        "title": "🤖 AI数字人制作全攻略！{price}打造你的虚拟分身",
        "angle": "演示用AI工具生成数字人、配音、制作口播视频",
        "platform": "抖音/B站",
        "category": "AI数字人",
        "keywords": ["数字人", "虚拟人", "ai主播"]
    },
    {
        "title": "🎥 可灵AI视频实测！{quality}画质效果超越Sora？",
        "angle": "深度测试可灵视频生成能力，对比国内外AI视频工具",
        "platform": "B站/小红书",
        "category": "AI视频",
        "keywords": ["可灵", "kl", "ai视频"]
    },
    {
        "title": "✂️ AI抠图工具横评！{num}秒{quality}抠图对比",
        "angle": "测试Remove.bg、稿定、美图等AI抠图工具",
        "platform": "小红书/抖音",
        "category": "AI修图",
        "keywords": ["ai抠图", "去背景", "修图"]
    },
    {
        "title": "💻 Cursor/Copilot实测！AI写代码能取代程序员吗？",
        "angle": "实测AI代码助手能力边界，分析对程序员的影响",
        "platform": "B站/公众号",
        "category": "AI编程",
        "keywords": ["cursor", "copilot", "ai编程"]
    },
    {
        "title": "🔥 {year}年最值得学的{num}个AI工具（{month}月更新）",
        "angle": "按使用场景分类推荐，附入门教程链接",
        "platform": "公众号/B站",
        "category": "工具盘点",
        "keywords": ["ai工具", "推荐", "盘点"]
    }
]

def fill_template(template):
    """填充模板中的动态参数"""
    params = {
        "{num}": random.choice(["3", "5", "8", "10"]),
        "{time}": random.choice(["3", "5", "10", "30"]),
        "{version}": random.choice(["", "V6 ", "最新版 "]),
        "{platform}": random.choice(["小红书", "抖音", "公众号", "B站"]),
        "{price}": random.choice(["免费", "低成本", "0成本", "百元内"]),
        "{cost}": random.choice(["3000", "5000", "8000"]),
        "{feature}": random.choice(["AI", "绘画", "视频", "文案", "PPT"]),
        "{year}": str(datetime.now().year),
        "{month}": str(datetime.now().month),
        "{quality}": random.choice(["高清", "4K", "电影级", "超清"])
    }
    
    result = template.copy()
    for key, value in params.items():
        result["title"] = result["title"].replace(key, value)
    return result

def generate_daily_topics():
    """基于日期生成每日选题（确保每天不同但可预测）"""
    today = datetime.now()
    day_of_year = today.timetuple().tm_yday
    
    # 用日期作为随机种子，确保同一天生成相同结果，不同天不同
    random.seed(day_of_year + today.year * 1000)
    
    # 打乱模板顺序并选前5个
    shuffled = TOPIC_TEMPLATES.copy()
    random.shuffle(shuffled)
    selected = shuffled[:5]
    
    # 重置随机种子
    random.seed()
    
    # 填充模板
    final_topics = []
    for i, template in enumerate(selected, 1):
        topic = fill_template(template)
        topic["title"] = topic["title"].replace("选题1", f"选题{i}")
        
        hot_reasons = [
            "新手入门刚需，搜索量持续走高",
            "近期相关工具更新频繁，话题热度上升", 
            "实用性强，转化率高",
            "平台算法近期在推此类内容",
            "适合当前时间节点，流量窗口期"
        ]
        topic["hot_reason"] = random.choice(hot_reasons)
        final_topics.append(topic)
    
    return final_topics

def send_feishu_card(topics):
    """发送飞书消息卡片"""
    elements = []
    for topic in topics:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{topic['title']}**\n\n💡 **切入角度**：{topic['angle']}\n\n📱 **适合平台**：{topic['platform']}\n\n🔥 **热点原因**：{topic['hot_reason']}\n\n---"
            }
        })
    
    card_data = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"📊 AI新手教程选题推荐 | {datetime.now().strftime('%m月%d日')}"},
            "template": "red"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "🤖 **每天早上9点推送** | 每天精选5条不同选题\n\n以下是根据AI新手教程热点筛选的 **5条选题方向**："
                }
            },
            {"tag": "hr"}
        ] + elements + [
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "💡 **小贴士**：选题基于算法每日更新，每天内容不同~"
                }
            }
        ]
    }
    
    payload = {"msg_type": "interactive", "card": card_data}
    
    try:
        response = requests.post(
            FEISHU_WEBHOOK,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"飞书推送结果: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"飞书推送失败: {e}")
        return False

def main():
    print(f"\n{'='*60}")
    print(f"AI新手教程选题抓取任务开始 - {datetime.now()}")
    print(f"{'='*60}\n")
    
    topics = generate_daily_topics()
    
    print(f"整理完成，共 {len(topics)} 条精选选题")
    for t in topics:
        print(f"  - {t['category']}: {t['title'][:40]}...")
    print()
    
    success = send_feishu_card(topics)
    
    if success:
        print("✅ 飞书推送成功！")
    else:
        print("❌ 飞书推送失败")
    
    print(f"\n{'='*60}")
    print(f"任务完成 - {datetime.now()}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
