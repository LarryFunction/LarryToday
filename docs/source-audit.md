# LarryToday 信息源排查与接入维护文档

报告生成：2026-10-20 09:01（北京时间）
最近采集：2026-10-20 09:01（北京时间）

## 先看结论

- 原始目录 367 家；配置 36 个入口，对应 25 个来源ID。一个媒体可有多个栏目入口。
- 原始目录中尚无采集配置：348 家。它们是“尚未接入/未验证”，不能直接判为无法连接。
- 本轮状态：可用且含精确时间 32 个；订阅过时 1 个；请求或解析失败 1 个；有效空订阅 1 个；缺少精确时间 1 个。
- 当前已发布刊期 2026-10-19，修订 4。本报告复测发生在截稿后，采集池新增内容不会自动改写本期。
- 目录中某媒体存在、订阅返回成功、文章被收入本期，是三个不同阶段；“未收录”不一定是故障。

## 维护说明

本文件按最新采集结果生成。修复内容、证据、未解决项和手动操作方案见 [信息源处理报告](source-treatment-report.md)。
空订阅、停更、日期不完整、请求失败分别记录；页面适配器可能只有部分文章成功。配置数量不代表完整覆盖。
arXiv RSS 使用公告时间，修订与新稿分别标记；Nature 的日期级元数据留在背景候选池，不进入精确截稿窗口。

## 当前36个入口实测明细

这是一份时间点快照。网络、服务器所在地与订阅更新都会影响后续结果。HTTP错误和连接异常仅记录类型，不包含凭证。

| 来源 / 入口ID | 状态 | 条目数 | 最新稿日期 | HTTP / 错误类型 | 最近成功（北京时间） | 已配置入口 |
|---|---|---:|---|---|---|---|
| The Guardian / guardian-0 | 可用且含精确时间 | 24 | 2026-10-20T00:48:27+00:00 | — | 2026-10-20 09:01 | https://www.theguardian.com/world/rss |
| BBC News / bbc-1 | 可用且含精确时间 | 24 | 2026-10-19T23:30:03+00:00 | — | 2026-10-20 09:01 | https://feeds.bbci.co.uk/news/world/rss.xml |
| France 24 / france24-2 | 可用且含精确时间 | 24 | 2026-10-19T21:39:49+00:00 | — | 2026-10-20 09:01 | https://www.france24.com/en/rss |
| Federal Reserve / fed-3 | 可用且含精确时间 | 20 | 2026-10-16T15:00:00+00:00 | — | 2026-10-20 09:01 | https://www.federalreserve.gov/feeds/press_all.xml |
| NASA / nasa-4 | 可用且含精确时间 | 10 | 2026-10-19T19:28:32+00:00 | — | 2026-10-20 09:01 | https://www.nasa.gov/feed/ |
| The Guardian / guardian-5 | 可用且含精确时间 | 24 | 2026-10-19T22:30:08+00:00 | — | 2026-10-20 09:01 | https://www.theguardian.com/technology/rss |
| The Guardian / guardian-6 | 可用且含精确时间 | 24 | 2026-10-19T18:37:14+00:00 | — | 2026-10-20 09:01 | https://www.theguardian.com/business/rss |
| The Guardian / guardian-7 | 可用且含精确时间 | 24 | 2026-10-19T12:20:08+00:00 | — | 2026-10-20 09:01 | https://www.theguardian.com/environment/rss |
| The Guardian / guardian-8 | 可用且含精确时间 | 24 | 2026-10-19T21:00:06+00:00 | — | 2026-10-20 09:01 | https://www.theguardian.com/culture/rss |
| The New York Times / nyt-9 | 可用且含精确时间 | 24 | 2026-10-20T00:34:01+00:00 | — | 2026-10-20 09:01 | https://rss.nytimes.com/services/xml/rss/nyt/World.xml |
| The New York Times / nyt-10 | 可用且含精确时间 | 20 | 2026-10-19T22:12:02+00:00 | — | 2026-10-20 09:01 | https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml |
| NPR / npr-11 | 可用且含精确时间 | 10 | 2026-10-19T22:29:57+00:00 | — | 2026-10-20 09:01 | https://feeds.npr.org/1004/rss.xml |
| PBS NewsHour / pbs-12 | 可用且含精确时间 | 20 | 2026-10-19T22:55:00+00:00 | — | 2026-10-20 09:01 | https://www.pbs.org/newshour/feeds/rss/world |
| Deutsche Welle / dw-13 | 可用且含精确时间 | 24 | 2026-10-20T00:32:00+00:00 | — | 2026-10-20 09:01 | https://rss.dw.com/rdf/rss-en-all |
| RFI / rfi-14 | 可用且含精确时间 | 21 | 2026-10-19T16:21:17+00:00 | — | 2026-10-20 09:01 | https://www.rfi.fr/en/rss |
| Le Monde / lemonde-15 | 可用且含精确时间 | 20 | 2026-10-20T00:24:12+00:00 | — | 2026-10-20 09:01 | https://www.lemonde.fr/international/rss_full.xml |
| El País / elpais-16 | 可用且含精确时间 | 24 | 2026-10-19T22:30:00+00:00 | — | 2026-10-20 09:01 | https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada |
| 香港电台 / rthk-17 | 可用且含精确时间 | 20 | 2026-10-19T23:00:06+00:00 | — | 2026-10-20 09:01 | https://rthk.hk/rthk/news/rss/c_expressnews_greaterchina.xml |
| South China Morning Post / scmp-18 | 可用且含精确时间 | 24 | 2026-10-20T01:00:11+00:00 | — | 2026-10-20 09:01 | https://www.scmp.com/rss/91/feed |
| CNA / cna-19 | 可用且含精确时间 | 20 | 2026-10-20T00:48:00+00:00 | — | 2026-10-20 09:01 | https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6311 |
| 人民网 / people-20 | 订阅过时 | 24 | 2025-06-05 | — | 2026-10-20 09:01 | https://www.people.com.cn/rss/politics.xml |
| China Daily / chinadaily-21 | 请求或解析失败 | 0 | — | 404 | — | https://www.chinadaily.com.cn/rss/china_rss.xml |
| 新华社 / xinhua-22 | 可用且含精确时间 | 8 | 2026-10-19T07:14:44+00:00 | — | 2026-10-20 09:01 | https://www.news.cn/politics/ |
| OpenAI News / openai-news-23 | 可用且含精确时间 | 24 | 2026-10-19T12:00:00+00:00 | — | 2026-10-20 09:01 | https://openai.com/news/rss.xml |
| arXiv AI / arxiv-24 | 有效空订阅 | 0 | — | — | 2026-10-20 09:01 | https://rss.arxiv.org/rss/cs.AI |
| Nature / nature-25 | 缺少精确时间 | 24 | 2026-10-19 | — | 2026-10-20 09:01 | https://www.nature.com/nature.rss |
| UN News / un-news-26 | 可用且含精确时间 | 24 | 2026-10-19T12:00:00+00:00 | — | 2026-10-20 09:01 | https://news.un.org/feed/subscribe/en/news/all/rss.xml |
| Al Jazeera / aljazeera-27 | 可用且含精确时间 | 24 | 2026-10-20T00:18:48+00:00 | — | 2026-10-20 09:01 | https://www.aljazeera.com/xml/rss/all.xml |
| 中国新闻网 / chinanews-china | 可用且含精确时间 | 24 | 2026-10-19T23:50:50+00:00 | — | 2026-10-20 09:01 | https://www.chinanews.com.cn/rss/china.xml |
| 中国新闻网 / chinanews-finance | 可用且含精确时间 | 24 | 2026-10-20T00:55:38+00:00 | — | 2026-10-20 09:01 | https://www.chinanews.com.cn/rss/finance.xml |
| 中国新闻网 / chinanews-world | 可用且含精确时间 | 24 | 2026-10-20T00:19:26+00:00 | — | 2026-10-20 09:01 | https://www.chinanews.com.cn/rss/world.xml |
| 中国新闻网 / chinanews-culture | 可用且含精确时间 | 24 | 2026-10-19T13:53:35+00:00 | — | 2026-10-20 09:01 | https://www.chinanews.com.cn/rss/culture.xml |
| arXiv Machine Learning / arxiv-lg | 可用且含精确时间 | 200 | 2026-10-19T04:00:00+00:00 | — | 2026-10-20 09:01 | https://rss.arxiv.org/rss/cs.LG |
| arXiv Computer Vision / arxiv-cv | 可用且含精确时间 | 200 | 2026-10-19T04:00:00+00:00 | — | 2026-10-20 09:01 | https://rss.arxiv.org/rss/cs.CV |
| arXiv Computation and Language / arxiv-cl | 可用且含精确时间 | 200 | 2026-10-19T04:00:00+00:00 | — | 2026-10-20 09:01 | https://rss.arxiv.org/rss/cs.CL |
| Lenny's Newsletter / lenny-newsletter | 可用且含精确时间 | 20 | 2026-10-19T15:03:35+00:00 | — | 2026-10-20 09:01 | https://www.lennysnewsletter.com/feed |

## 处理方法

1. **404**：先核对官方当前地址及重定向；找到候选地址后实际解析，不能仅凭搜索结果改配置。
2. **连接失败**：区分DNS、TLS、超时和服务器地区问题。查看健康记录 error_kind（dns/tls/timeout/http/connection/parse_or_validation），并在目标云服务器复测；不关闭TLS验证。
3. **停更**：检查订阅最新稿日期，与官网近期稿件比对。入口返回200不等于内容新鲜。
4. **没有RSS**：可开发针对公开栏目页的适配器；提取真实标题、日期、短摘要与原文URL，逐站检查使用条件。网站结构变动后需要维护。
5. **需要授权**：使用官方授权接口或人工导入；是否需要付费必须逐站核实。本报告未断言所有未接入媒体都需要付费。
6. **个人观点**：可补接作者公开博客或Newsletter的RSS，作为单独观点来源；不能声称覆盖其全部X发言。
7. **收录为空**：先查采集池，再查发布时间/截稿窗口/去重/消费推荐过滤。新闻不在本期不一定是采集失败。

## 文件和复测命令

| 文件 | 用途 |
|---|---|
| `config/feeds.json` | RSS入口、来源ID、主题、地区、机构归属、启用开关 |
| `srcs/sources.json` | 原始候选来源目录；这里列出并不会自动采集 |
| `config/social.json` | X观察账号与启用开关 |
| `scripts/collect.py` | 采集和健康状态判定 |
| `scripts/update_news.py` | 解析、截稿、AI编辑与发布 |
| `data/source-health.json` | 最近一轮逐入口结果 |
| `data/article-pool.json` | 滚动素材池；不等于已发布日报 |
| `data/social-status.json` | X配置及采集状态，不含凭证 |

```powershell
# 只采集，不调用新闻编辑AI，不发布新刊
python -m scripts.collect
# 根据最新健康记录重新生成本文档
python scripts/report_sources.py
# 验证解析和日报逻辑
python -m unittest discover -s tests
```

密钥只放服务器本地 `.env`，不要粘贴进本文档、截图或版本库。新增源先采集验证，再决定是否发布修订；不要把故障排查当成自动改写历史刊期。

## 待接入来源完整清单

以下按原始目录分类列出所有尚无feeds配置的来源。优先级与备注来自原目录，不代表本轮已逐一验证其接口、授权或可达性。没有配置的来源统一状态为“待发现入口、待验证”。

### 国际综合与通讯社（19家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | Reuters 路透社 / reuters | 全球 | https://www.reuters.com/ | 国际与财经快讯；保留署名和原始通讯社来源 |
| P1 | Associated Press 美联社 / ap | 全球 | https://apnews.com/ | 国际现场报道；转载站不另算独立证据 |
| P1 | AFP 法新社 / afp | 全球 | https://www.afp.com/ | 全球通讯社；官网与商业供稿服务需区分 |
| P2 | The Washington Post / washpost | 美国、全球 | https://www.washingtonpost.com/ | 美国政策与调查；订阅权限待确认 |
| P2 | CNN / cnn | 美国、全球 | https://www.cnn.com/ | 突发与直播；直播中的临时数字须更新 |
| P2 | Fox News / fox | 美国 | https://www.foxnews.com/ | 美国政治视角补充；主持评论单独标记 |
| P2 | ABC News 美国 / abc-us | 美国 | https://abcnews.go.com/ | 美国综合；勿与澳大利亚ABC或ABC Color混合 |
| P2 | CBC News / cbc | 加拿大 | https://www.cbc.ca/news | 加拿大公共事务及原住民议题 |
| P2 | ABC News 澳大利亚 / abc-au | 澳大利亚、亚太 | https://www.abc.net.au/news/ | 澳洲及太平洋公共报道 |
| P2 | Euronews / euronews | 欧洲 | https://www.euronews.com/ | 欧洲跨国报道 |
| P2 | Al Arabiya English / al-arabiya | 中东 | https://english.alarabiya.net/ | 海湾与地区视角补充 |
| P1 | NHK World / nhk | 日本、亚太 | https://www3.nhk.or.jp/nhkworld/ | 日本公共广播及亚洲新闻 |
| P2 | Kyodo English / kyodo | 日本 | https://english.kyodonews.net/ | 日本通讯社报道 |
| P2 | Yonhap English / yonhap | 韩国、朝鲜半岛 | https://en.yna.co.kr/ | 半岛政经快讯 |
| P2 | CGTN / cgtn | 中国、全球 | https://www.cgtn.com/ | 中国对外报道视角；与央视同源判断 |
| P2 | TASS / tass | 俄罗斯 | https://tass.com/ | 俄罗斯官方消息与立场；与独立现场证据交叉 |
| P2 | Anadolu Agency / anadolu | 土耳其、中东 | https://www.aa.com.tr/en | 土耳其及地区通讯社视角 |
| P2 | Agencia EFE / efe | 西班牙、拉丁美洲 | https://efe.com/ | 西语通讯社 |
| P2 | ANSA / ansa | 意大利、欧洲 | https://www.ansa.it/english/ | 意大利通讯社 |

### 地区与全球南方补充（64家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P2 | Nikkei Asia / nikkei | 亚洲 | https://asia.nikkei.com/ | 产业供应链与亚洲商业；与FT注意集团关联 |
| P2 | Hong Kong Free Press / hkfp | 香港 | https://hongkongfp.com/ | 香港地方公共事务 |
| P2 | 端传媒 / initium | 华语地区 | https://theinitium.com/ | 华语深度调查；订阅待确认 |
| P2 | 报道者 / reporter-tw | 台湾 | https://www.twreporter.org/ | 公共事务调查 |
| P2 | 中央通讯社 / cna-tw | 台湾 | https://www.cna.com.tw/ | 本地政经与通讯社报道 |
| P2 | Sixth Tone / sixthtone | 中国 | https://www.sixthtone.com/ | 中国社会与生活报道 |
| P1 | 财新 / caixin | 中国 | https://www.caixin.com/ | 经济金融调查；订阅待确认 |
| P1 | 第一财经 / yicai | 中国 | https://www.yicai.com/ | 中国经济产业 |
| P2 | 界面新闻 / jiemian | 中国 | https://www.jiemian.com/ | 商业产业及地方经济 |
| P2 | 澎湃新闻 / thepaper | 中国 | https://www.thepaper.cn/ | 公共事务与社会新闻 |
| P2 | 新京报 / beijingnews | 中国 | https://www.bjnews.com.cn/ | 地方与调查报道 |
| P2 | The Hindu / thehindu | 印度 | https://www.thehindu.com/ | 南亚政策与社会 |
| P2 | The Indian Express / indianexpress | 印度 | https://indianexpress.com/ | 印度政治与调查 |
| P2 | Scroll / scroll | 印度 | https://scroll.in/ | 印度社会与解释性报道 |
| P2 | The Wire / thewire | 印度 | https://thewire.in/ | 印度公共事务与政策批评 |
| P2 | Dawn / dawn | 巴基斯坦 | https://www.dawn.com/ | 巴基斯坦政治经济 |
| P2 | The Daily Star / dailystar-bd | 孟加拉国 | https://www.thedailystar.net/ | 南亚本地报道 |
| P2 | The Kathmandu Post / kathmandu | 尼泊尔 | https://kathmandupost.com/ | 喜马拉雅地区本地报道 |
| P2 | Frontier Myanmar / frontier | 缅甸 | https://www.frontiermyanmar.net/ | 缅甸政治社会；现场访问受限时说明证据来源 |
| P2 | The Irrawaddy / irrawaddy | 缅甸 | https://www.irrawaddy.com/ | 缅甸冲突与政治 |
| P2 | Malaysiakini / malaysiakini | 马来西亚 | https://www.malaysiakini.com/ | 马来西亚政治与调查 |
| P2 | Rappler / rappler | 菲律宾 | https://www.rappler.com/ | 菲律宾公共事务及核查 |
| P2 | Philippine Center for Investigative Journalism / pcij | 菲律宾 | https://pcij.org/ | 菲律宾调查报道 |
| P2 | The Jakarta Post / jakartapost | 印度尼西亚 | https://www.thejakartapost.com/ | 印尼经济政治 |
| P2 | Tempo / tempo | 印度尼西亚 | https://www.tempo.co/ | 本地语言调查报道 |
| P2 | Prachatai / prachatai | 泰国 | https://prachatai.com/english | 泰国人权与社会 |
| P2 | Mekong Eye / mekongeye | 湄公河地区 | https://www.mekongeye.com/ | 跨境水资源环境 |
| P2 | Eurasianet / eurasianet | 中亚、高加索 | https://eurasianet.org/ | 中亚与高加索补盲 |
| P2 | OC Media / ocmedia | 高加索 | https://oc-media.org/ | 高加索地方及跨境报道 |
| P2 | Meduza / meduza | 俄罗斯 | https://meduza.io/en | 俄罗斯事务；与俄官方来源并置但按证据判断 |
| P2 | The Kyiv Independent / kyivindependent | 乌克兰 | https://kyivindependent.com/ | 乌克兰现场与调查；当事国媒体不作中立性保证 |
| P2 | Ukrainska Pravda / ukrainska | 乌克兰 | https://www.pravda.com.ua/eng/ | 乌克兰国内政治 |
| P2 | Balkan Insight / balkaninsight | 巴尔干 | https://balkaninsight.com/ | 地区调查与转型正义 |
| P2 | Der Spiegel / derspiegel | 德国 | https://www.spiegel.de/international/ | 德国与欧洲调查 |
| P2 | POLITICO Europe / politico-eu | 欧洲 | https://www.politico.eu/ | 欧盟政策；与美国版同品牌相关 |
| P2 | Haaretz / haaretz | 以色列、巴勒斯坦 | https://www.haaretz.com/ | 以色列政治社会；订阅待确认 |
| P2 | The Times of Israel / timesisrael | 以色列 | https://www.timesofisrael.com/ | 当地新闻；博客与编辑部稿件分开 |
| P2 | +972 Magazine / mag972 | 以色列、巴勒斯坦 | https://www.972mag.com/ | 以巴人权与调查视角 |
| P2 | WAFA / wafa | 巴勒斯坦 | https://english.wafa.ps/ | 巴勒斯坦官方消息；当事方声明单列 |
| P2 | IRNA / irna | 伊朗 | https://en.irna.ir/ | 伊朗官方消息；当事方声明单列 |
| P2 | Al-Monitor / almonitor | 中东 | https://www.al-monitor.com/ | 中东政治经济分析与报道 |
| P2 | Mada Masr / mada | 埃及 | https://www.madamasr.com/en/ | 埃及公共事务调查 |
| P2 | Daraj / daraj | 中东 | https://daraj.media/ | 阿拉伯语调查与社会议题 |
| P2 | The Africa Report / africareport | 非洲 | https://www.theafricareport.com/ | 泛非商业政治 |
| P1 | The Continent / continent | 非洲 | https://www.thecontinent.org/ | 泛非周刊；PDF及通讯入口 |
| P2 | Daily Maverick / dailymaverick | 南非 | https://www.dailymaverick.co.za/ | 政治经济调查 |
| P2 | amaBhungane / amabhungane | 南非 | https://amabhungane.org/ | 调查报道；联合发表须去重 |
| P2 | Premium Times / premiumtimes | 尼日利亚 | https://www.premiumtimesng.com/ | 西非本地调查 |
| P2 | TheCable / thecable | 尼日利亚 | https://www.thecable.ng/ | 尼日利亚政策与商业 |
| P2 | Nation Africa / nation-africa | 东非 | https://nation.africa/ | 肯尼亚及东非；集团转载去重 |
| P2 | The EastAfrican / eastafrican | 东非 | https://www.theeastafrican.co.ke/ | 东非区域经济与政策 |
| P2 | Addis Standard / addisstandard | 埃塞俄比亚 | https://addisstandard.com/ | 非洲之角本地政治 |
| P2 | Inkyfada / inkyfada | 突尼斯 | https://inkyfada.com/ | 北非数据调查 |
| P2 | Hespress / daily-morocco | 摩洛哥 | https://www.hespress.com/ | 阿拉伯语地方视角 |
| P1 | Agência Pública / publica | 巴西 | https://apublica.org/ | 巴西公共利益调查 |
| P2 | Repórter Brasil / reporterbrasil | 巴西 | https://reporterbrasil.org.br/ | 劳动供应链与环境调查 |
| P2 | CIPER / ciper | 智利 | https://www.ciperchile.cl/ | 智利调查 |
| P2 | El Faro / elfaro | 中美洲 | https://elfaro.net/ | 中美洲调查；运营地点与报道地区区分 |
| P2 | La Silla Vacía / laposta | 哥伦比亚 | https://www.lasillavacia.com/ | 政治权力与政策 |
| P2 | IDL-Reporteros / idl | 秘鲁 | https://www.idl-reporteros.pe/ | 腐败与公共事务调查 |
| P2 | Animal Político / animalpolitico | 墨西哥 | https://animalpolitico.com/ | 政治与事实核查 |
| P1 | Rest of World / restworld | 全球南方 | https://restofworld.org/ | 科技对非欧美社会影响 |
| P1 | RNZ Pacific / rnz | 太平洋岛国 | https://www.rnz.co.nz/international | 太平洋区域补盲 |
| P3 | Pacific Islands News Association / pacificislands | 太平洋岛国 | https://pina.com.fj/ | 地区媒体线索；须回溯实际报道机构 |

### 科技产业与网络安全（30家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P2 | TechCrunch / techcrunch | 全球 | https://techcrunch.com/ | 科技公司与创业融资 |
| P2 | The Verge / verge | 全球 | https://www.theverge.com/ | 科技政策与消费技术 |
| P2 | Ars Technica / arstechnica | 全球 | https://arstechnica.com/ | 技术深度及科学报道 |
| P2 | WIRED / wired | 全球 | https://www.wired.com/ | 科技社会与安全 |
| P2 | The Register / register | 全球 | https://www.theregister.com/ | 企业IT、云与芯片 |
| P2 | MIT Technology Review / mitreview | 全球 | https://www.technologyreview.com/ | 前沿技术影响；不是同行评审论文 |
| P2 | IEEE Spectrum / spectrum | 全球 | https://spectrum.ieee.org/ | 工程、机器人与半导体 |
| P2 | 404 Media / 404media | 全球 | https://404media.co/ | 平台隐私及科技调查 |
| P2 | The Information / information | 全球 | https://www.theinformation.com/ | 科技商业深度；订阅待确认 |
| P2 | VentureBeat / venturebeat | 全球 | https://venturebeat.com/ | 企业AI与商业部署 |
| P2 | Tech in Asia / techinasia | 亚洲 | https://www.techinasia.com/ | 亚洲创业与融资 |
| P2 | KrASIA / kr-asia | 亚洲 | https://kr-asia.com/ | 亚洲科技产业 |
| P2 | TechNode / technode | 中国 | https://technode.com/ | 中国科技商业 |
| P2 | 36氪 / 36kr | 中国 | https://36kr.com/ | 创投及科技；广告与商业合作稿单列 |
| P2 | 机器之心 / jiqizhixin | 中国、全球 | https://www.jiqizhixin.com/ | AI论文与产业线索；回溯论文或产品公告 |
| P2 | 量子位 / qbitai | 中国、全球 | https://www.qbitai.com/ | AI产品与研究；回溯原始材料 |
| P2 | IT之家 / ithome | 中国、全球 | https://www.ithome.com/ | 消费技术快讯；转载去重 |
| P2 | SemiAnalysis / semianalysis | 全球 | https://semianalysis.com/ | 芯片与算力产业分析；估算与实测区分 |
| P2 | TrendForce / trendforce | 亚洲、全球 | https://www.trendforce.com/ | 半导体产业研究；商业预测非已发生事实 |
| P2 | TechPowerUp / anand-techpowerup | 全球 | https://www.techpowerup.com/ | 硬件实测及产业动态 |
| P2 | Phoronix / phoronix | 全球 | https://www.phoronix.com/ | Linux硬件与性能测试 |
| P2 | BleepingComputer / bleeping | 全球 | https://www.bleepingcomputer.com/ | 漏洞勒索与安全事件 |
| P2 | Krebs on Security / krebs | 全球 | https://krebsonsecurity.com/ | 网络犯罪调查 |
| P2 | The Record / record | 全球 | https://therecord.media/ | 网络安全与数字政策 |
| P2 | SecurityWeek / securityweek | 全球 | https://www.securityweek.com/ | 企业安全新闻 |
| P2 | CISA KEV / cisa | 美国、全球 | https://www.cisa.gov/known-exploited-vulnerabilities-catalog | 已知被利用漏洞；漏洞存在不等于全部产品已被攻击 |
| P2 | NIST NVD / nvd | 全球 | https://nvd.nist.gov/ | 漏洞条目与评分；关注更新及评分主体 |
| P2 | 国家互联网应急中心 CNCERT / cert-cn | 中国 | https://www.cert.org.cn/ | 国内安全通告 |
| P2 | CERT-EU / cert-eu | 欧洲 | https://cert.europa.eu/ | 欧盟机构安全通告 |
| P2 | Google Project Zero / googlezero | 全球 | https://googleprojectzero.blogspot.com/ | 漏洞研究；核对修复版本 |

### AI一手发布、测评与研究（29家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | Anthropic News / anthropic | 全球 | https://www.anthropic.com/news | 产品与安全研究；厂商自述 |
| P1 | Google DeepMind / deepmind | 全球 | https://deepmind.google/discover/blog/ | 模型及研究发布；与Google其他渠道同集团 |
| P2 | Google Research / google-research | 全球 | https://research.google/blog/ | 研究原始发布与论文线索 |
| P2 | Meta AI / meta-ai | 全球 | https://ai.meta.com/blog/ | 模型与研究；厂商自述 |
| P2 | Microsoft Research / ms-research | 全球 | https://www.microsoft.com/en-us/research/blog/ | 论文研究与系统发布 |
| P2 | NVIDIA Developer Blog / nvidia | 全球 | https://developer.nvidia.com/blog/ | GPU与软件栈；性能营销需独立复现 |
| P2 | AMD Newsroom / amd | 全球 | https://www.amd.com/en/newsroom.html | 芯片发布一手资料 |
| P1 | DeepSeek 官方GitHub / deepseek | 中国、全球 | https://github.com/deepseek-ai | 代码权重与技术报告；固定commit和模型版本 |
| P1 | Qwen / qwen | 中国、全球 | https://qwenlm.github.io/ | 模型技术说明与权重线索 |
| P2 | Mistral AI News / mistral | 欧洲、全球 | https://mistral.ai/news/ | 欧洲模型发布 |
| P2 | Cohere Blog / cohere | 全球 | https://cohere.com/blog | 企业模型与研究 |
| P1 | Hugging Face Blog / hf | 全球 | https://huggingface.co/blog | 开源生态；公司博客与社区模型作者不能混同 |
| P2 | Allen Institute for AI / allenai | 全球 | https://allenai.org/ | 开放模型及研究 |
| P2 | EleutherAI / eleuther | 全球 | https://www.eleuther.ai/ | 开放研究与评测代码 |
| P2 | 北京智源人工智能研究院 / baai | 中国 | https://www.baai.ac.cn/ | 模型与研究发布 |
| P2 | 上海人工智能实验室 / shanghai-ai | 中国 | https://www.shlab.org.cn/ | 模型评测与研究发布 |
| P1 | Stanford HAI AI Index / stanfordhai | 全球 | https://hai.stanford.edu/ai-index | AI年度趋势；统计滞后及来源链要保留 |
| P1 | Epoch AI / epoch | 全球 | https://epoch.ai/ | 算力和模型趋势；估算方法与区间 |
| P1 | Artificial Analysis / artificialanalysis | 全球 | https://artificialanalysis.ai/ | 模型成本延迟与能力评测；核对设置和版本 |
| P2 | LMArena / lmarena | 全球 | https://lmarena.ai/ | 偏好评测；不将排行榜泛化成所有任务能力 |
| P2 | MLCommons / mlcommons | 全球 | https://mlcommons.org/ | MLPerf等基准；区分提交配置 |
| P2 | METR / metr | 全球 | https://metr.org/ | 模型能力及任务评估；方法与样本限制 |
| P2 | UK AI Security Institute / aisi | 英国、全球 | https://www.aisi.gov.uk/ | AI安全评估与政策研究 |
| P2 | OECD.AI / oecd-ai | 全球 | https://oecd.ai/ | AI政策与指标；部分指标源自第三方 |
| P1 | OpenReview / openreview | 全球 | https://openreview.net/ | 投稿评审讨论；区分投稿、接收和撤稿 |
| P2 | ACL Anthology / acl | 全球 | https://aclanthology.org/ | 自然语言处理论文 |
| P2 | CVF Open Access / cvf | 全球 | https://openaccess.thecvf.com/ | 视觉会议论文 |
| P2 | Proceedings of Machine Learning Research / pmlr | 全球 | https://proceedings.mlr.press/ | 机器学习会议论文 |
| P2 | NeurIPS Proceedings / neurips | 全球 | https://proceedings.neurips.cc/ | 机器学习论文集；不要把会议首页当论文入口 |

### 财经新闻与市场（17家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | Financial Times / ft | 全球 | https://www.ft.com/ | 全球经济商业；订阅与转载权限待确认 |
| P1 | Bloomberg / bloomberg | 全球 | https://www.bloomberg.com/ | 市场与企业；终端、网页和数据授权不同 |
| P2 | The Wall Street Journal / wsj | 全球 | https://www.wsj.com/ | 企业金融与经济政策 |
| P2 | The Economist / economist | 全球 | https://www.economist.com/ | 经济政治解释；分析判断非事实确认 |
| P2 | CNBC / cnbc | 全球 | https://www.cnbc.com/ | 市场实时报道；嘉宾预测与新闻分开 |
| P2 | MarketWatch / marketwatch | 全球 | https://www.marketwatch.com/ | 市场与个人金融；不要当交易所原始行情 |
| P2 | Barron's / barrons | 全球 | https://www.barrons.com/ | 投资分析；观点与已披露事实区分 |
| P2 | The Economic Times / economic-times | 印度 | https://economictimes.indiatimes.com/ | 印度经济与商业 |
| P2 | Business Standard / businessstandard | 印度 | https://www.business-standard.com/ | 印度产业与宏观 |
| P2 | Valor Econômico / valor | 巴西 | https://valor.globo.com/ | 葡语财经 |
| P2 | Business Day / businessday | 南非 | https://www.businesslive.co.za/bd/ | 南非经济与商业 |
| P2 | 财经杂志 / caijing | 中国 | https://www.caijing.com.cn/ | 经济政策与调查 |
| P2 | 21世纪经济报道 / 21jingji | 中国 | https://www.21jingji.com/ | 产业金融与区域经济 |
| P2 | 财联社 / cls | 中国 | https://www.cls.cn/ | A股与产业快讯；回溯上市公司公告 |
| P3 | 东方财富 / eastmoney | 中国 | https://www.eastmoney.com/ | 财经聚合与行情线索；核对源头和数据授权 |
| P2 | CoinDesk / coindesk | 全球 | https://www.coindesk.com/ | 数字资产新闻；与发行方声明和链上记录交叉 |
| P2 | The Block / theblock | 全球 | https://www.theblock.co/ | 数字资产产业；研究与广告分开 |

### 宏观统计、央行与贸易（30家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | International Monetary Fund / imf | 全球 | https://www.imf.org/ | 宏观报告与数据；预测、初值、修订值区分 |
| P1 | World Bank Data / worldbank | 全球 | https://data.worldbank.org/ | 跨国发展指标；追溯国家统计原始来源 |
| P2 | OECD Data Explorer / oecd | 全球 | https://data-explorer.oecd.org/ | 跨国经济社会统计 |
| P2 | Bank for International Settlements / bis | 全球 | https://www.bis.org/ | 国际银行与金融统计 |
| P2 | World Trade Organization / wto | 全球 | https://www.wto.org/ | 贸易争端及政策文书 |
| P2 | UN Trade and Development / unctad | 全球 | https://unctad.org/ | 贸易投资与发展数据 |
| P2 | UN Comtrade / comtrade | 全球 | https://comtradeplus.un.org/ | 商品贸易；出口与进口镜像有口径差异 |
| P2 | ILOSTAT / ilo | 全球 | https://ilostat.ilo.org/ | 就业工资与劳动统计 |
| P2 | FRED / fred | 全球、美国 | https://fred.stlouisfed.org/ | 经济序列聚合；与BLS等源头不算两份独立测量 |
| P2 | ALFRED / alfred | 美国 | https://alfred.stlouisfed.org/ | 宏观数据历史版本；防止修订值造成前视偏差 |
| P1 | European Central Bank / ecb | 欧元区 | https://www.ecb.europa.eu/ | 欧元区货币政策与统计 |
| P2 | Bank of England / boe | 英国 | https://www.bankofengland.co.uk/ | 英国货币政策 |
| P2 | Bank of Japan / boj | 日本 | https://www.boj.or.jp/en/ | 日本政策与统计 |
| P1 | 中国人民银行 / pbc | 中国 | https://www.pbc.gov.cn/ | 货币政策与金融统计 |
| P2 | Reserve Bank of India / rbi | 印度 | https://www.rbi.org.in/ | 印度货币金融政策 |
| P2 | Banco Central do Brasil / bcb | 巴西 | https://www.bcb.gov.br/ | 巴西央行与金融统计 |
| P2 | South African Reserve Bank / sarb | 南非 | https://www.resbank.co.za/ | 南非货币金融统计 |
| P2 | Monetary Authority of Singapore / mas | 新加坡 | https://www.mas.gov.sg/ | 新加坡货币政策与监管 |
| P1 | Bureau of Labor Statistics / bls | 美国 | https://www.bls.gov/ | 就业与CPI；季调及基期必须保留 |
| P2 | Bureau of Economic Analysis / bea | 美国 | https://www.bea.gov/ | GDP、PCE及国际收支 |
| P2 | US Census Bureau / census | 美国 | https://www.census.gov/ | 人口、贸易及零售统计 |
| P2 | Eurostat / eurostat | 欧盟 | https://ec.europa.eu/eurostat/ | 欧洲可比统计 |
| P2 | Office for National Statistics / ons | 英国 | https://www.ons.gov.uk/ | 英国宏观人口数据 |
| P1 | 国家统计局 / stats-cn | 中国 | https://www.stats.gov.cn/ | 中国宏观原始统计；初值与最终值分开 |
| P2 | 海关总署 / customs-cn | 中国 | http://www.customs.gov.cn/ | 中国进出口数据 |
| P2 | 国家外汇管理局 / safe | 中国 | https://www.safe.gov.cn/ | 国际收支与外汇统计 |
| P2 | Statistics Bureau Japan / stat-jp | 日本 | https://www.stat.go.jp/english/ | 日本人口与物价 |
| P2 | MoSPI / mospi | 印度 | https://www.mospi.gov.in/ | 印度官方统计 |
| P2 | IBGE / ibge | 巴西 | https://www.ibge.gov.br/ | 巴西官方统计 |
| P2 | Statistics South Africa / stats-sa | 南非 | https://www.statssa.gov.za/ | 南非官方统计 |

### 公司披露、监管与法律（24家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | SEC EDGAR / sec | 美国 | https://www.sec.gov/search-filings | 财报与监管披露；公司提交内容不等于监管背书 |
| P1 | 巨潮资讯 / cninfo | 中国 | https://www.cninfo.com.cn/ | 上市公司公告原文；保留更正公告 |
| P1 | HKEXnews / hkex | 香港 | https://www.hkexnews.hk/ | 上市公司披露及公告时间 |
| P2 | 上海证券交易所 / sse | 中国 | https://www.sse.com.cn/ | 交易规则与公告 |
| P2 | 深圳证券交易所 / szse | 中国 | https://www.szse.cn/ | 交易规则与公告 |
| P2 | 北京证券交易所 / bse | 中国 | https://www.bse.cn/ | 交易规则与公告 |
| P2 | 中国证监会 / csrc | 中国 | https://www.csrc.gov.cn/ | 证券监管与处罚 |
| P2 | 国家金融监督管理总局 / nfra | 中国 | https://www.nfra.gov.cn/ | 银行保险监管 |
| P2 | 国家市场监督管理总局 / samr | 中国 | https://www.samr.gov.cn/ | 反垄断及市场监管 |
| P2 | 国家互联网信息办公室 / cac | 中国 | https://www.cac.gov.cn/ | 互联网与数据政策 |
| P2 | 工业和信息化部 / miit | 中国 | https://www.miit.gov.cn/ | 通信与工业政策 |
| P2 | 国家发展改革委 / ndrc | 中国 | https://www.ndrc.gov.cn/ | 产业与宏观政策 |
| P2 | 财政部 / mof | 中国 | https://www.mof.gov.cn/ | 财政收支与政策 |
| P2 | 商务部 / mofcom | 中国 | https://www.mofcom.gov.cn/ | 贸易与投资政策 |
| P2 | Federal Trade Commission / ftc | 美国 | https://www.ftc.gov/ | 反垄断及消费者保护 |
| P2 | US Department of Justice / doj | 美国 | https://www.justice.gov/ | 诉讼与执法；起诉指控不等于定罪 |
| P2 | Federal Register / federalregister | 美国 | https://www.federalregister.gov/ | 规则原文；提案与最终生效区分 |
| P2 | Congress.gov / congress | 美国 | https://www.congress.gov/ | 法案与立法进程；提出不等于通过 |
| P2 | EUR-Lex / eurlex | 欧盟 | https://eur-lex.europa.eu/ | 欧盟法律原文及生效日期 |
| P2 | European Commission Press Corner / ecpress | 欧盟 | https://ec.europa.eu/commission/presscorner/home/en | 委员会政策发布；回溯正式法规 |
| P2 | Court of Justice of the EU / curia | 欧盟 | https://curia.europa.eu/ | 欧盟法院判决 |
| P2 | CourtListener / courtlistener | 美国 | https://www.courtlistener.com/ | 法院文书检索；覆盖不完整时查法院原文 |
| P2 | Companies House / companieshouse | 英国 | https://find-and-update.company-information.service.gov.uk/ | 企业注册与提交文件；自报资料须核实 |
| P2 | GLEIF / gleif | 全球 | https://www.gleif.org/ | 法律实体标识与关系；辅助企业去重 |

### 外交、冲突与人道（24家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | UN News / unnews | 全球 | https://news.un.org/ | 联合国机构发声；不能自动等同现场独立证据 |
| P1 | UN Digital Library / undocs | 全球 | https://digitallibrary.un.org/ | 决议、投票与正式文书 |
| P2 | UN Web TV / unwebtv | 全球 | https://webtv.un.org/ | 发言原始视频与完整上下文 |
| P2 | International Court of Justice / icj | 全球 | https://www.icj-cij.org/ | 国际法院文书；临时措施与终局判决区分 |
| P2 | International Criminal Court / icc | 全球 | https://www.icc-cpi.int/ | 国际刑事法院案件；逮捕令与定罪区分 |
| P2 | OHCHR / ohchr | 全球 | https://www.ohchr.org/ | 人权调查与报告；核对调查时间及方法 |
| P2 | OCHA / ocha | 全球 | https://www.unocha.org/ | 人道救援与局势材料 |
| P1 | ReliefWeb / reliefweb | 全球 | https://reliefweb.int/ | 人道报告聚合；署名报告机构才是证据来源 |
| P2 | Humanitarian Data Exchange / hdx | 全球 | https://data.humdata.org/ | 人道数据；多机构数据集不可一概视为UN自测 |
| P2 | UNHCR / unhcr | 全球 | https://www.unhcr.org/ | 难民与流离失所 |
| P2 | IOM / iom | 全球 | https://www.iom.int/ | 移民与流离失所 |
| P2 | World Food Programme / wfp | 全球 | https://www.wfp.org/ | 粮食援助与饥饿状况 |
| P2 | ICRC / icrc | 全球 | https://www.icrc.org/ | 人道救援及国际人道法材料 |
| P2 | Médecins Sans Frontières / msf | 全球 | https://www.msf.org/ | 医疗救援现场声明；局部观察不外推全地区 |
| P2 | The New Humanitarian / newhumanitarian | 全球南方 | https://www.thenewhumanitarian.org/ | 人道危机及救援问责 |
| P2 | ACLED / acled | 全球 | https://acleddata.com/ | 冲突事件编码；媒体输入与原报道不算独立证据 |
| P2 | Uppsala Conflict Data Program / ucdp | 全球 | https://ucdp.uu.se/ | 冲突数据；定义与时间覆盖和ACLED不同 |
| P2 | SIPRI / sipri | 全球 | https://www.sipri.org/ | 军费与军贸；估算方法与数据滞后 |
| P2 | International Crisis Group / crisisgroup | 全球 | https://www.crisisgroup.org/ | 冲突研究与政策建议 |
| P2 | 中国外交部 / mfa-cn | 中国、全球 | https://www.mfa.gov.cn/ | 外交声明与记者会；用于确认该方表态 |
| P2 | US Department of State / state-us | 美国、全球 | https://www.state.gov/ | 外交声明；用于确认该方表态 |
| P2 | European External Action Service / eeas | 欧盟、全球 | https://www.eeas.europa.eu/ | 欧盟外交立场 |
| P2 | African Union / au | 非洲 | https://au.int/ | 非盟公报与地区政策 |
| P2 | ASEAN / asean | 东南亚 | https://asean.org/ | 东盟联合声明 |

### 科学、学术与健康（27家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P2 | European Space Agency / esa | 欧洲、全球 | https://www.esa.int/ | 欧洲航天与空间科学发布 |
| P2 | Science / science | 全球 | https://www.science.org/ | 科学新闻与论文；按内容类型分别处理 |
| P2 | Science News / sciencenews | 全球 | https://www.sciencenews.org/ | 基础科学报道 |
| P2 | SciDev.Net / scidev | 全球南方 | https://www.scidev.net/ | 发展中国家科学与政策 |
| P2 | STAT / statnews | 全球 | https://www.statnews.com/ | 医药产业与健康调查 |
| P2 | KFF Health News / kffnews | 美国 | https://kffhealthnews.org/ | 医疗政策与调查 |
| P2 | The Examination / examination | 全球 | https://www.theexamination.org/ | 健康、食品、污染调查 |
| P1 | PubMed / pubmed | 全球 | https://pubmed.ncbi.nlm.nih.gov/ | 生物医学文献索引；索引收录不代表结论可靠 |
| P2 | Europe PMC / europepmc | 全球 | https://europepmc.org/ | 生命科学文献及开放全文线索 |
| P2 | bioRxiv / biorxiv | 全球 | https://www.biorxiv.org/ | 生物学预印本；未经同行评审 |
| P2 | medRxiv / medrxiv | 全球 | https://www.medrxiv.org/ | 医学预印本；不能直接用于诊疗结论 |
| P2 | ClinicalTrials.gov / clinicaltrials | 全球 | https://clinicaltrials.gov/ | 临床试验注册；注册不等于结果有效 |
| P2 | Cochrane / cochrane | 全球 | https://www.cochrane.org/ | 系统综述；关注证据确定性和截止日期 |
| P1 | WHO / who | 全球 | https://www.who.int/ | 全球公共卫生公告 |
| P2 | WHO Disease Outbreak News / who-don | 全球 | https://www.who.int/emergencies/disease-outbreak-news | 疫情通报；病例定义与统计截止时间 |
| P2 | US CDC / cdc | 美国 | https://www.cdc.gov/ | 公共卫生与监测 |
| P2 | ECDC / ecdc | 欧洲 | https://www.ecdc.europa.eu/ | 欧洲传染病监测 |
| P2 | 中国疾控中心 / china-cdc | 中国 | https://www.chinacdc.cn/ | 国内公共卫生监测 |
| P2 | Africa CDC / africacdc | 非洲 | https://africacdc.org/ | 非洲公共卫生监测 |
| P2 | US FDA / fda | 美国 | https://www.fda.gov/ | 药械监管；批准范围与适应症必须一致 |
| P2 | European Medicines Agency / ema | 欧盟 | https://www.ema.europa.eu/ | 药品审评及安全通报 |
| P2 | 国家药品监督管理局 / nmpa | 中国 | https://www.nmpa.gov.cn/ | 中国药械监管 |
| P2 | Crossref / crossref | 全球 | https://www.crossref.org/ | DOI与出版元数据；与论文原文同源 |
| P2 | OpenAlex / openalex | 全球 | https://openalex.org/ | 学术索引；自动消歧可能有误 |
| P2 | Retraction Watch / retractionwatch | 全球 | https://retractionwatch.com/ | 撤稿与研究诚信；关联原论文和出版商声明 |
| P2 | RePEc / repec | 全球 | https://repec.org/ | 经济学研究；工作论文与发表版本区分 |
| P2 | NBER / nber | 全球、美国 | https://www.nber.org/ | 经济工作论文；非实时宏观官方统计 |

### 气候、能源、农业与灾害（24家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P1 | Carbon Brief / carbonbrief | 全球 | https://www.carbonbrief.org/ | 气候科学及政策解释 |
| P2 | Climate Home News / climatehome | 全球 | https://www.climatechangenews.com/ | 气候谈判与政策 |
| P1 | Mongabay / mongabay | 全球南方 | https://www.mongabay.com/ | 森林生态与环境调查 |
| P2 | Dialogue Earth / dialogueearth | 全球、中国 | https://dialogue.earth/ | 中国与全球环境议题 |
| P2 | Inside Climate News / insideclimate | 全球、美国 | https://insideclimatenews.org/ | 气候与能源调查 |
| P2 | Grist / grist | 美国、全球 | https://grist.org/ | 气候与社区 |
| P2 | IPCC / ipcc | 全球 | https://www.ipcc.ch/ | 气候评估报告；不是实时气象预报 |
| P2 | World Meteorological Organization / wmo | 全球 | https://wmo.int/ | 全球气象与气候通报 |
| P2 | Copernicus Climate Change Service / copernicus | 全球 | https://climate.copernicus.eu/ | 再分析和气候指标；基准期及数据集版本 |
| P2 | NOAA / noaa | 全球、美国 | https://www.noaa.gov/ | 海洋气象与气候观测 |
| P1 | USGS Earthquakes / usgs | 全球 | https://earthquake.usgs.gov/ | 地震事件；初始震级会修订 |
| P2 | GDACS / gdacs | 全球 | https://www.gdacs.org/ | 灾害预警聚合；预警等级非已确认损失 |
| P2 | 中国气象局 / cma | 中国 | https://www.cma.gov.cn/ | 天气与灾害预警 |
| P2 | 中国地震局 / cea | 中国 | https://www.cea.gov.cn/ | 地震官方信息 |
| P2 | International Energy Agency / iea | 全球 | https://www.iea.org/ | 能源统计与展望；预测与观测分开 |
| P2 | US Energy Information Administration / eia | 全球、美国 | https://www.eia.gov/ | 能源供需、库存与价格数据 |
| P2 | IRENA / irena | 全球 | https://www.irena.org/ | 可再生能源统计 |
| P2 | OPEC / opec | 全球 | https://www.opec.org/ | 产油国组织声明与报告；成员利益视角 |
| P2 | Ember / ember | 全球 | https://ember-energy.org/ | 电力转型数据与研究；核对源头 |
| P2 | Energy Institute / energyinstitute | 全球 | https://www.energyinst.org/ | 全球能源统计评估 |
| P2 | FAO / fao | 全球 | https://www.fao.org/ | 粮食价格、农业与粮食安全 |
| P2 | USDA / usda | 全球、美国 | https://www.usda.gov/ | 农业与农产品供需 |
| P2 | FEWS NET / fews | 全球 | https://fews.net/ | 粮食安全预警；预测与实测区别 |
| P2 | Global Forest Watch / globalforest | 全球 | https://www.globalforestwatch.org/ | 森林变化遥感；树冠损失不总等于永久毁林 |

### 教育、文化、体育与社会（16家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P2 | UNESCO / unesco | 全球 | https://www.unesco.org/ | 教育文化与遗产 |
| P2 | UNICEF / unicef | 全球 | https://www.unicef.org/ | 儿童与教育数据 |
| P2 | UN Women / unwomen | 全球 | https://www.unwomen.org/ | 性别与社会政策 |
| P2 | Pew Research Center / pew | 全球、美国 | https://www.pewresearch.org/ | 民调与社会研究；抽样、问题及误差 |
| P2 | Our World in Data / ourworld | 全球 | https://ourworldindata.org/ | 跨领域可视化；与其引用数据源不算独立测量 |
| P2 | The Conversation / conversation | 全球 | https://theconversation.com/ | 学者解释；不是同行评审研究 |
| P2 | The Chronicle of Higher Education / chronicle | 美国、全球 | https://www.chronicle.com/ | 高等教育政策 |
| P2 | Times Higher Education / timeshigher | 全球 | https://www.timeshighereducation.com/ | 高教与排名；商业排名方法需说明 |
| P2 | Variety / variety | 全球 | https://variety.com/ | 影视娱乐产业 |
| P2 | The Hollywood Reporter / hollywood | 全球 | https://www.hollywoodreporter.com/ | 影视产业；与Variety共同集团时注意独立性 |
| P2 | The Art Newspaper / artnewspaper | 全球 | https://www.theartnewspaper.com/ | 艺术文化与博物馆 |
| P2 | IOC Olympics / olympics | 全球 | https://olympics.com/ioc | 奥林匹克官方公告 |
| P2 | FIFA / fifa | 全球 | https://www.fifa.com/ | 足球赛事官方公告；组织自身争议需外部报道 |
| P2 | World Anti-Doping Agency / wada | 全球 | https://www.wada-ama.org/ | 反兴奋剂规则与决定 |
| P2 | ESPN / espn | 全球 | https://www.espn.com/ | 体育报道及赛果；商业数据授权待确认 |
| P2 | The Athletic / athletic | 全球 | https://www.nytimes.com/athletic/ | 体育深度；与纽约时报同集团 |

### 调查、事实核查与证据工具（27家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P2 | ProPublica / propublica | 美国 | https://www.propublica.org/ | 公共利益调查及原始文档 |
| P1 | ICIJ / icij | 全球 | https://www.icij.org/ | 跨国调查；合作稿件共享证据去重 |
| P1 | OCCRP / occrp | 全球 | https://www.occrp.org/ | 跨境腐败调查；联合项目共享来源 |
| P2 | Bellingcat / bellingcat | 全球 | https://www.bellingcat.com/ | 开源调查；回溯图像原始时间地点 |
| P2 | Forensic Architecture / forensic | 全球 | https://forensic-architecture.org/ | 空间与视觉调查；方法及委托关系需保留 |
| P1 | AFP Fact Check / afpcheck | 全球 | https://factcheck.afp.com/ | 图像与跨国谣言核查；与AFP报道共享机构 |
| P2 | Reuters Fact Check / reuterscheck | 全球 | https://www.reuters.com/fact-check/ | 事实核查；与Reuters同机构 |
| P2 | AP Fact Check / apcheck | 全球 | https://apnews.com/hub/ap-fact-check | 美国及国际说法核查；与AP同机构 |
| P2 | Full Fact / fullfact | 英国 | https://fullfact.org/ | 英国公共言论核查 |
| P2 | FactCheck.org / factcheckorg | 美国 | https://www.factcheck.org/ | 美国公共政策说法核查 |
| P2 | PolitiFact / politifact | 美国 | https://www.politifact.com/ | 美国政治言论；应读核查证据而非只读等级 |
| P2 | Snopes / snopes | 全球、美国 | https://www.snopes.com/ | 网络传言及图像 |
| P2 | Africa Check / africacheck | 非洲 | https://africacheck.org/ | 非洲公共言论与传言 |
| P2 | Chequeado / chequeado | 阿根廷、拉丁美洲 | https://chequeado.com/ | 西语事实核查 |
| P2 | Maldita.es / maldita | 西班牙 | https://maldita.es/ | 西语谣言与数据核查 |
| P2 | CORRECTIV / correctiv | 德国 | https://correctiv.org/ | 调查与德语事实核查 |
| P2 | Alt News / altnews | 印度 | https://www.altnews.in/ | 印度网络传言核查 |
| P2 | BOOM / boom | 印度 | https://www.boomlive.in/ | 南亚事实核查 |
| P2 | MAFINDO TurnBackHoax / mafindo | 印度尼西亚 | https://turnbackhoax.id/ | 印尼语谣言核查 |
| P2 | 台湾事实查核中心 / tfc | 台湾 | https://tfc-taiwan.org.tw/ | 繁体中文传言核查 |
| P2 | MyGoPen / mygopen | 台湾 | https://www.mygopen.com/ | 中文网络谣言核查 |
| P2 | Annie Lab / annie | 香港、亚洲 | https://annielab.org/ | 亚洲视觉与信息核查 |
| P2 | 中国互联网联合辟谣平台 / snopes-cn | 中国 | https://www.piyao.org.cn/ | 中文辟谣；继续核对原始证据 |
| P3 | Global Investigative Journalism Network / gijn | 全球 | https://gijn.org/ | 调查方法与区域媒体发现 |
| P3 | International Fact-Checking Network / ifcn | 全球 | https://www.poynter.org/ifcn/ | 核查网络与规范；成员认证需逐期确认 |
| P3 | InVID Verification Plugin / invid | 全球 | https://www.invid-project.eu/tools-and-services/invid-verification-plugin/ | 视频关键帧与核查工具；工具结果不是事实结论 |
| P3 | Internet Archive Wayback Machine / wayback | 全球 | https://web.archive.org/ | 历史页面存档；抓取时间不等于发布时间 |

### 新闻发现、API与社区（17家）

| 优先级 | 来源 / ID | 地区 | 官网 | 原目录备注 |
|---|---|---|---|---|
| P3 | GDELT Project / gdelt | 全球 | https://www.gdeltproject.org/ | 多语种事件与新闻发现；同源报道去重；不要与同名第三方产品混同 |
| P3 | Media Cloud / mediacloud | 全球 | https://www.mediacloud.org/ | 媒体覆盖与话语分析；非独立证据 |
| P3 | Guardian Open Platform / guardian-api | 全球 | https://open-platform.theguardian.com/documentation/ | Guardian API接入文档；与Guardian同源 |
| P3 | NYT Developer Network / nyt-api | 美国、全球 | https://developer.nytimes.com/ | 纽约时报API文档；与NYT同源 |
| P3 | NewsAPI / newsapi | 全球 | https://newsapi.org/ | 商业新闻索引；计划与生产使用许可待查 |
| P3 | NewsData.io / newsdata | 全球 | https://newsdata.io/ | 多语种新闻索引；按实际覆盖测试 |
| P3 | Event Registry / eventregistry | 全球 | https://eventregistry.org/ | 新闻聚类与索引；机器聚类不代表真实性 |
| P3 | Google News / google-news | 全球 | https://news.google.com/ | 检索线索；不把聚合页当报道来源 |
| P3 | Techmeme / techmeme | 全球 | https://www.techmeme.com/ | 科技议题发现；追溯被链接原报道 |
| P3 | Hacker News / hackernews | 全球 | https://news.ycombinator.com/ | 技术社区线索；评论不能当确认 |
| P3 | Lobsters / lobsters | 全球 | https://lobste.rs/ | 技术讨论与原文线索 |
| P3 | GitHub Trending / github | 全球 | https://github.com/trending | 项目线索；星数不代表质量与真实性 |
| P3 | Reddit / reddit | 全球 | https://www.reddit.com/ | 地方及垂直社区线索；身份地点时间需核实 |
| P3 | V2EX / v2ex | 华语地区 | https://www.v2ex.com/ | 开发者与产品问题线索 |
| P3 | RSSHub 文档 / rsshub | 全球 | https://docs.rsshub.app/ | 第三方RSS转换工具；路由可失效且非官方授权 |
| P2 | Global Voices / globalvoices | 全球 | https://globalvoices.org/ | 多语种公民媒体与地区议题；引用链需回溯 |
| P2 | Inter Press Service / ips | 全球南方 | https://www.ipsnews.net/ | 发展、社会与全球南方报道 |

## X观察账号清单

身份状态逐账号记录；official_site_linked 表示作者官网有对应账号链接，不代表发言内容经过核实。其余账号仍待核验。

| 用户名 | 名称 | 身份状态 |
|---|---|---|
| karpathy | Andrej Karpathy | official_site_linked |
| lexfridman | Lex Fridman | official_site_linked |
| lennysan | lennysan | user_supplied_unverified |
| paulg | paulg | user_supplied_unverified |
| nikitabier | nikitabier | user_supplied_unverified |
| rrhoover | rrhoover | user_supplied_unverified |
| bgurley | bgurley | user_supplied_unverified |
| OfficialLoganK | OfficialLoganK | user_supplied_unverified |
| vista8 | vista8 | user_supplied_unverified |
| lijigang_com | lijigang_com | user_supplied_unverified |
| dotey | dotey | user_supplied_unverified |
| op7418 | op7418 | user_supplied_unverified |
| dongxi_nlp | dongxi_nlp | user_supplied_unverified |
| indigo11 | indigo11 | user_supplied_unverified |
| venturetwins | venturetwins | user_supplied_unverified |
| GabrielPeterss4 | GabrielPeterss4 | user_supplied_unverified |
| deedydas | deedydas | user_supplied_unverified |
| bobmcgrewai | bobmcgrewai | user_supplied_unverified |
| ding_liam | ding_liam | user_supplied_unverified |
| levelsio | levelsio | user_supplied_unverified |
