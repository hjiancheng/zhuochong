"""
AI 批量生成 10 万+ 条预设对话
用法：
  python generate_dialogues.py --test      → 先生成 200 条测试质量
  python generate_dialogues.py --batch 100 → 每批 100 次 API 调用（≈2000 条）
  python generate_dialogues.py             → 全量生成（直到 10 万条）
"""
import json, os, time, sys, hashlib, random, argparse

API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets", "default_api.json")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets", "dialogues_mega.json")
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "generate_progress.json")

# ═══════════════════════════════════════════
# 250+ 话题分类
# ═══════════════════════════════════════════
TOPICS = [
    # ── 日常生活 (40+) ──
    "早晨起床","洗漱准备","出门上班","通勤路上","坐地铁公交","骑共享单车","打车经历",
    "到达公司","打卡签到","午餐吃什么","点外卖纠结","等外卖","吃了什么","午休时间",
    "下午犯困","喝咖啡","喝奶茶","吃零食","下午工作","快下班了","加班中","下班回家",
    "晚饭时间","做饭","洗碗打扫","洗衣服","收拾房间","整理桌面","倒垃圾","拆快递",
    "洗澡放松","护肤保养","睡前准备","失眠了","熬夜中","睡过头","周末睡懒觉",
    # ── 工作学习 (30+) ──
    "开会中","做PPT","写报告","写代码","改bug","设计稿","写文档","发邮件","回复消息",
    "面试准备","面试紧张","考试复习","考试结束了","成绩出来","学新技能","考证","考研",
    "写论文","答辩","毕设","找实习","实习第一天","转正了","跳槽","离职","失业",
    "被领导批评","被表扬了","升职加薪","同事关系","客户沟通","甲方改需求",
    # ── 情感心理 (35+) ──
    "心情不好","很难过","想哭","好烦躁","焦虑不安","压力山大","心态崩了","陷入自我怀疑",
    "感觉自己不行","被打击了","被人误解","被人欺负","失恋了","冷战","吵架了",
    "想前任","想家了","想爸妈","想朋友","孤独感","感到迷茫","不知道怎么办","无助",
    "对不起自己","后悔了","担心未来","害怕改变","失去动力","崩溃边缘",
    "需要安慰","需要鼓励","需要抱抱","需要力量","需要认可",
    # ── 开心时刻 (20+) ──
    "开心的事","好消息","惊喜","收到礼物","被夸奖了","有人表白","表白成功了",
    "年终奖","涨工资","项目成功了","考试通过了","中奖了","抢到票了",
    "今天特别开心","幸运日","成就感","幸福感爆棚","满足","感恩","充满希望",
    # ── 兴趣爱好 (30+) ──
    "音乐推荐","听歌感受","看电影","看电视剧","看动漫","看综艺","看书阅读",
    "画画创作","写作","拍照摄影","做手工","弹吉他","弹钢琴","唱歌",
    "玩游戏","刷视频","刷微博","刷小红书","刷B站","刷抖音",
    "养宠物","养花种草","健身运动","跑步","瑜伽","游泳","打篮球",
    "旅行","露营","爬山","看海",
    # ── 社交关系 (25+) ──
    "交朋友","闺蜜聊天","兄弟聚会","室友关系","同学聚会","同事聚餐",
    "相亲","恋爱日常","异地恋","情侣吵架","那个TA","单身生活",
    "家人关系","和爸妈打电话","亲戚催婚","过年回家",
    "被借钱","借钱给别人","帮朋友忙","收到意外的帮助",
    # ── 消费生活 (15+) ──
    "逛街购物","网购剁手","双十一","618","快递还没到","省钱计划","理财投资",
    "房租涨价","买房","装修","买车","换手机","换电脑",
    # ── 健康身体 (15+) ──
    "生病了","感冒发烧","咳嗽","头痛","胃不舒服","牙疼","生理期",
    "看医生","吃药","体检报告","减肥了","变胖了","健身效果","睡眠不好",
    # ── 天气季节 (15+) ──
    "下雨天","下雪了","刮风了","台风天","雾霾天","大晴天","阴天",
    "春天来了","夏天好热","秋天凉爽","冬天好冷","回南天","梅雨季",
    # ── 节日节气 (20+) ──
    "春节过年","情人节","元宵节","清明节","劳动节","端午节","七夕","中秋节",
    "国庆节","元旦","圣诞节","万圣节","感恩节","生日","纪念日",
    "立春","立夏","立秋","立冬","冬至","除夕",
    # ── 深度话题 (15+) ──
    "人生意义","梦想与现实","时间流逝","成长感悟","孤独与陪伴",
    "爱与自由","幸福定义","成功定义","美丽定义","命运","记忆","遗憾",
    # ── 趣味互动 (20+) ──
    "讲个笑话","冷笑话","脑筋急转弯","猜谜语","成语接龙","绕口令",
    "真心话大冒险","星座运势","算命","许愿","塔罗牌","MBTI人格",
    "毒鸡汤","反鸡汤","哲理段子","沙雕日常","吐槽","凡尔赛",
]

# ═══════════════════════════════════════════
# 32 种性格组合 (8物种 × 4话风)
# ═══════════════════════════════════════════
SPECIES_INFO = {
    "cat": "猫", "dog": "狗", "rabbit": "兔", "bear": "熊",
    "chick": "小鸡", "hamster": "仓鼠", "fox": "狐狸", "penguin": "企鹅",
}
TALK_STYLES = {
    "喵系": "说话奶声奶气，常用'喵'结尾，像小猫一样撒娇卖萌，可可爱爱",
    "吐槽系": "说话幽默犀利，爱吐槽生活琐事，毒舌但温暖，像损友一样亲切",
    "撒娇系": "说话软绵绵，喜欢撒娇卖萌，容易感动，像黏人的小家伙",
    "高冷系": "说话简洁冷静，偶尔冷淡但不失温暖，像傲娇的霸道总裁范",
}

def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            return json.load(f).get('key', '')
    return ''

def call_api(prompt, max_retries=3):
    import urllib.request
    key = load_api_key()
    if not key:
        print("❌ 未找到 API Key，请确保 presets/default_api.json 存在")
        sys.exit(1)
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                'https://api.deepseek.com/v1/chat/completions',
                data=json.dumps({
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': '你是一个专业的内容生成助手。严格按照要求格式输出，不要添加额外说明。'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 2000,
                    'temperature': 0.9,
                }).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json; charset=utf-8'
                }
            )
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"  ⚠ API 调用失败 (尝试 {attempt+1}/{max_retries}): {e}")
            time.sleep(2)
    return None

def parse_response(text):
    """从 API 返回中提取对话列表"""
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        # 去掉编号前缀 (1. 2. - 等)
        if line and len(line) > 3:
            # 去掉各种可能的编号
            for prefix in ['1.','2.','3.','4.','5.','6.','7.','8.','9.','10.',
                          '11.','12.','13.','14.','15.','16.','17.','18.','19.','20.',
                          '- ','• ','· ','> ']:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
                    break
            # 过滤非对话行
            if len(line) >= 8 and not line.startswith('【') and not line.startswith('以下'):
                # 去掉首尾引号
                if line.startswith('"') and line.endswith('"'):
                    line = line[1:-1]
                lines.append(line)
    return lines

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"completed": [], "total_items": 0}

def save_progress(progress):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, ensure_ascii=False)

def load_existing():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_output(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_batch(species, style, topic, count=20):
    """生成一批对话"""
    sp_name = SPECIES_INFO[species]
    style_desc = TALK_STYLES[style]
    prompt = f"""请生成{count}条不同的对话台词，每行一条。

角色：一只{sp_name}桌宠，{style_desc}
话题：{topic}

要求：
1. 每条台词独立成行，以数字编号开头（如 1. 2. 3.）
2. 风格多样：可以有反问、感叹、陈述、疑问等不同语气
3. 自然口语化，像朋友之间闲聊
4. 每条控制在15-40字
5. 不要出现角色名字，用「我」自称，用「你」称呼对方
6. 要有创意和个性，避免千篇一律"""

    text = call_api(prompt)
    if not text:
        return []
    lines = parse_response(text)
    return [l for l in lines if 5 <= len(l) <= 60]

def main():
    parser = argparse.ArgumentParser(description='批量生成桌宠对话')
    parser.add_argument('--test', action='store_true', help='测试模式：只生成少量样本')
    parser.add_argument('--batch', type=int, default=0, help='只生成指定批次数（每批2000条）')
    parser.add_argument('--target', type=int, default=100000, help='目标总条数（默认10万）')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)

    data = load_existing()
    progress = load_progress()
    total = sum(len(v) for v in data.values())

    print(f"=" * 50)
    print(f"🐱 月薪猫对话批量生成器")
    print(f"   目标: {args.target} 条")
    print(f"   已生成: {total} 条 ({len(data)} 个分类)")
    print(f"   性格组合: {len(SPECIES_INFO)}物种 × {len(TALK_STYLES)}话风 = {len(SPECIES_INFO)*len(TALK_STYLES)}种")
    print(f"   话题数: {len(TOPICS)}")
    print(f"=" * 50)

    if args.test:
        print("🧪 测试模式：生成 10 条样本\n")
        combos = [("cat", "喵系")]  # 只测试猫+喵系
        test_topics = TOPICS[:5]  # 只测试前5个话题
        for sp, style in combos:
            for topic in test_topics:
                key = f"{sp}|{style}|{topic}"
                lines = generate_batch(sp, style, topic, count=4)
                if lines:
                    data[key] = lines
                    print(f"  ✅ {key}: {len(lines)}条")
                time.sleep(0.5)
        save_output(data)
        print(f"\n✅ 测试完成，共 {sum(len(v) for v in data.values())} 条")
        return

    # 构建所有组合
    all_combos = []
    for sp in SPECIES_INFO:
        for style in TALK_STYLES:
            for topic in TOPICS:
                key = f"{sp}|{style}|{topic}"
                if key not in progress.get("completed", []):
                    all_combos.append((sp, style, topic, key))

    print(f"📋 剩余组合: {len(all_combos)} 个")
    if args.batch:
        all_combos = all_combos[:args.batch]
        print(f"📋 本次处理: {len(all_combos)} 个（batch={args.batch}）")

    count = 0
    for sp, style, topic, key in all_combos:
        if total >= args.target:
            print(f"\n🎉 已达到目标 {args.target} 条！")
            break

        lines = generate_batch(sp, style, topic, count=20)
        if lines:
            data[key] = lines
            total += len(lines)
            count += 1
            progress["completed"].append(key)
            progress["total_items"] = total

            if count % 10 == 0:
                save_output(data)
                save_progress(progress)
                print(f"  [{count}/{len(all_combos)}] {key}: +{len(lines)}条 (累计{total}条)")

        # 速率控制：每100次调用停一下
        if count % 100 == 0 and count > 0:
            print(f"  ⏸ 休息 5 秒… (已完成 {count} 次调用, {total} 条)")
            time.sleep(5)
        else:
            time.sleep(0.3)

    save_output(data)
    save_progress(progress)
    print(f"\n✅ 完成！总条数: {sum(len(v) for v in data.values())}")
    print(f"   文件路径: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
