"""Content-led topics, grounded tags and explainable morning selection."""
import re
from collections import Counter, defaultdict

TOPICS = [
 ('桌游', '社会与文化', r'\b(board ?games?|tabletop games?)\b|桌游|桌面游戏'),
 ('体育赛事', '社会与文化', r'\b(football|soccer|formula one|formula 1|grand prix|championship|olympics)\b|世界杯|奥运|足球|篮球|F1'),
 ('影视文化', '社会与文化', r'\b(cinema|film festival|movie|television|novel|museum|concert|music|theatre)\b|电影|电视剧|音乐|博物馆|文学'),
 ('社会生活', '社会与文化', r'\b(school|education|housing|homeless|workers|labour|labor|healthcare)\b|教育|住房|劳动者|养老|医疗服务'),
 ('人工智能', '科技与 AI', r'\b(ai|artificial intelligence|openai|anthropic|llm|chatgpt)\b|人工智能|大模型'),
 ('芯片产业', '科技与 AI', r'\b(semiconductor|chipmaker|nvidia|chip)\b|半导体|芯片'),
 ('网络安全', '科技与 AI', r'\b(cybersecurity|ransomware|data breach)\b|网络安全|数据泄露'),
 ('宏观经济', '经济与投资', r'\b(inflation|central bank|interest rates|gdp|recession)\b|通胀|央行|利率|经济增长|经济衰退'),
 ('金融市场', '经济与投资', r'\b(stock market|bond yields|oil prices|financial market)\b|股市|债券|油价|金融市场'),
 ('贸易政策', '经济与投资', r'\b(tariffs?|trade deal|trade war)\b|关税|贸易协定|贸易战'),
 ('气候变化', '环境与气候', r'\b(climate|carbon emissions|global warming)\b|气候|碳排放|全球变暖'),
 ('生态环境', '环境与气候', r'\b(biodiversity|renewable energy|deforestation|pollution)\b|生物多样性|可再生能源|污染'),
 ('航天探索', '科学与探索', r'\b(nasa|astronomy|spacecraft|galaxy|telescope)\b|航天|天文学|宇宙|望远镜'),
 ('医学研究', '科学与探索', r'\b(clinical trial|vaccine|cancer treatment)\b|临床试验|疫苗|癌症治疗'),
 ('选举政治', '国际政治', r'\b(election|ballot|parliament|presidential|midterms?)\b|选举|议会|投票'),
 ('外交与冲突', '国际政治', r'\b(ceasefire|military strike|invasion|peace talks|diplomacy|sanctions)\b|停火|军事打击|入侵|和谈|外交|制裁'),
]
FALLBACK={'国际政治':'国际事务','科技与 AI':'科技观察','经济与投资':'经济观察','科学与探索':'科学研究','环境与气候':'环境观察','社会与文化':'社会文化'}

def material(row):
    return ' '.join(str(row.get(k) or '') for k in ('title','title_zh','title_en')),' '.join(str(row.get(k) or '') for k in ('feed_excerpt','summary_zh'))

def infer_category(row):
    title,summary=material(row)
    hits=[(3*bool(re.search(pattern,title,re.I))+bool(re.search(pattern,summary,re.I)), -i,category) for i,(_,category,pattern) in enumerate(TOPICS)]
    score,_,category=max(hits)
    return category if score else row.get('category','社会与文化')

def article_tags(row):
    title,summary=material(row)
    existing=row.get('tags') if isinstance(row.get('tags'),list) else []
    tags=[t.strip() for t in existing if isinstance(t,str) and 0<len(t.strip())<=24]
    tags += [label for label,_,pattern in TOPICS if re.search(pattern,title+' '+summary,re.I)]
    tags=list(dict.fromkeys(tags))[:4]
    return tags or [FALLBACK.get(row.get('category'),'专题观察')]

IMPACT=[
 (9,'重大公共安全',r'\b(earthquake|tsunami|pandemic|state of emergency|mass shooting)\b|地震|海啸|大流行|紧急状态|重大伤亡'),
 (8,'战争与外交进展',r'\b(ceasefire|peace deal|invasion|military strike|nuclear|war)\b|停火|和平协议|入侵|战争|核武'),
 (8,'选举与权力变化',r'\b(election|midterms?|president.{0,25}(resign|oust)|coup)\b|选举|政变|总统.{0,8}辞职'),
 (7,'经济政策与系统影响',r'\b(central bank|interest rate|tariff|recession|bank collapse|oil prices)\b|央行|利率|关税|经济衰退|银行倒闭|油价'),
 (7,'公共政策变化',r'\b(supreme court|legislation|law takes effect|nationwide ban|mass layoffs)\b|最高法院|法律生效|全国.{0,8}禁令|大规模裁员'),
 (6,'科技与健康进展',r'\b(clinical trial|vaccine approval|data breach|new.{0,20}(ai model|chip))\b|临床试验|疫苗获批|数据泄露|新一代.{0,8}(模型|芯片)'),
]
STOP=set('the and for with from that this after over says news new into will have been about their more than how why what are was its can could would world'.split())

def terms(row):
    title,_=material(row)
    words=set(re.findall(r'[a-z]{3,}',title.lower()))-STOP
    for run in re.findall(r'[\u4e00-\u9fff]+',title):
        words.update(run[i:i+2] for i in range(len(run)-1))
    return words

def related(a,b):
    shared=a&b
    return len(shared)>=3 and len(shared)/max(1,min(len(a),len(b)))>=.5

def select_briefing(rows, events, limit=8):
    by_id={r['id']:r for r in rows}; leads=[by_id[e['lead_id']] for e in events if e['lead_id'] in by_id]
    tokens={r['id']:terms(r) for r in rows}; index=defaultdict(set)
    for id,words in tokens.items():
        for word in words:index[word].add(id)
    scored={}; reasons={}
    for row in leads:
        title,_=material(row)
        signals=[(weight,label) for weight,label,pattern in IMPACT if re.search(pattern,title,re.I)]
        score,label=max(signals,default=(1,'本期观察'))
        if row.get('content_type') in ('评测','评论','观点') or row.get('research_status')=='preprint':score-=3
        if re.search(r'\b(board ?game|puzzle|horoscope|quiz|shopping|bounty)\b|桌游|谜题|星座|优惠|漏洞赏金',title,re.I):score-=5
        if re.search(r'战争遗留|战争爆炸物|回顾|周年|\b(war remnants|anniversary|retrospective)\b',title,re.I):score-=5
        candidates=set().union(*(index[t] for t in tokens[row['id']])) if tokens[row['id']] else set()
        families={by_id[id].get('upstream_agency') or by_id[id].get('publisher_family') or by_id[id]['source_id'] for id in candidates if related(tokens[row['id']],tokens[id])}
        support=max(1,len(families));score+=min(4,support-1)
        pick=row.get('editorial_pick',{})
        if pick.get('basis')=='ai_shortlist' and isinstance(pick.get('order'),int):
            score+=max(10,20-pick['order'])
            label=pick.get('reason') or label
        scored[row['id']]=score
        reasons[row['id']]={'impact':label,'independent_sources':support,'social_heat':'unavailable'}
    selected=[];publishers=Counter();categories=Counter();impacts=Counter()
    while leads and len(selected)<limit:
        def adjusted(r):
            repetition=max((8 if related(tokens[r['id']],tokens[p['id']]) else 0 for p in selected),default=0)
            return scored[r['id']]-publishers[r.get('publisher_family',r['source_id'])]*.7-categories[r['category']]*.25-impacts[reasons[r['id']]['impact']]*1.5-repetition
        best=max(leads,key=lambda r:(adjusted(r),r.get('published_at') or ''))
        leads.remove(best);selected.append(best)
        publishers[best.get('publisher_family',best['source_id'])]+=1;categories[best['category']]+=1;impacts[reasons[best['id']]['impact']]+=1
    return [(r,reasons[r['id']]) for r in selected]
