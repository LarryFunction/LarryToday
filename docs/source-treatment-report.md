# 信息源处理报告

处理日期：2026-10-20（北京时间）。完整采集最近检查时间：09:01。

## 结果与范围

本轮阅读了项目说明、采集/解析/选编/刊期保存代码、来源目录、原审计、X名单及学术来源原始材料，修改并实测采集流程。项目采用 Python 标准库后端、原生网页；目录、素材池、07:00 截稿日报是三层数据。此次只更新配置、采集池、健康记录及文档，没有调用付费新闻编辑 AI，没有发布新刊或修订历史刊期。当前最新刊期仍为 2026-10-19。

配置从 **32 增至 36 个入口、24 增至 25 个来源 ID**。新增 arXiv 三个分类与 Lenny 作者通讯；新华社在原来源 ID 下更换为官网适配器。原始 367 项目录中仍有 348 项没有 feeds 配置，完整名单见 [自动审计](source-audit.md)。它们并非348个已确认故障的站点，也不在本轮逐站实测范围。

| 最后一轮状态 | 入口数 | 说明 |
|---|---:|---|
| 可解析且含精确时间 | 32 | 包括新华社官网、三个新增 arXiv 分类、作者通讯 |
| 停更 | 1 | 人民网 RSS 最新日期 2025-06-05 |
| 请求失败 | 1 | 中国日报原 RSS HTTP 404 |
| 有效空 RSS | 1 | arXiv cs.AI；不能据此推断整个平台无更新 |
| 仅日期 | 1 | Nature，已恢复日期和相关元数据，未捏造时分 |

“可用”指本轮有可解析元数据，不代表完整覆盖、持续稳定或内容已证实。初次网络检查遇到 DNS/TLS 错误，获准联网后的批量复测大部分成功。初轮 Guardian 科技超时、UN 返回不可解析内容，末轮均恢复；保留分轮记录，不将暂时失败宣称为永久故障。

## 已完成的修复

### 社交媒体大V与作者通讯

1. **新增 Lenny's Newsletter 公开 RSS**，实测20条，其中10条在14天保留期内。`kind: opinion` 的条目从新闻池分出，保存至 `data/opinion-posts.json` 并合入 `data/social-posts.json`，后续刊期在科技版“业界声音”展示。没有 X 凭证也可以采集此通讯；不代表覆盖 Lenny 的全部 X 发言，也不代表获得付费全文。
2. **核验2个账号的官网关联**：Karpathy 的 [官网](https://karpathy.ai/) 与 [博客](https://karpathy.bearblog.dev/) 链接其账号；Lex Fridman 的 [官网](https://lexfridman.com/) 链接其 X。`config/social.json` 保存核验状态、证据URL及日期。官网关联只是身份线索，不是观点真实性认证；数字 user_id 尚待官方API确认。
3. **X采集身份门槛**：仅允许 `official_site_linked` 或 `manually_verified` 状态发起读取；支持单账号 `enabled: false`。每次解析用户名并核对返回身份；如配置了数字 user_id 且不一致，报 `identity_mismatch`，不悄悄切换人物。
4. **修复成功/失败误判**：HTTP 200 内的 `errors` 不再被当成“成功但没有帖子”；逐账号记录401、402、403、404、429、连接及解析问题，不写入凭证、响应正文或异常消息。
5. **增加分页和增量检查点**：每页100条，每账号默认最多3页；成功取完后才更新 `since_id`。达到页数上限标记 `coverage_limited`，保留旧检查点，避免悄悄跳过缺口。只读取公开原创/引用帖，排除回复与转发；保留作者ID、时间、引用帖ID及长帖正文（如返回）。
6. **观点归属**：个人发言持续标为“观点”；前端能正确显示 X 作者名称，AI材料带上观点与研究状态，预印本不会仅因标题含“review”被标成消费评测。

本轮本地只检查凭证是否存在，没有打印密钥。结果：`X_BEARER_TOKEN` 未配置、总开关关闭，**尚无真实 X API 帖子采集验收**；X 分支通过模拟接口回归测试，不能等同真实授权环境验收。

### 学术论文

1. 增加官方 `cs.LG`（机器学习）、`cs.CV`（计算机视觉）、`cs.CL`（计算语言学）RSS，保留 `cs.AI`。末轮每个新分类读取200条，跨分类按论文原文链接去重后，池内 **558条 arXiv 记录**，均保留作者。
2. 原通用解析器固定只看前24项；arXiv现支持独立 `max_items: 200`。**本轮三个分类均达到上限，不能称为全量采集**。代码新增 `item_limit/limit_reached`，下次采集写入健康记录；本轮上限情况由配置与条目数确认。RSS滚动窗口之外的历史内容仍需另行回补。
3. 修复 Atom 把 XML 中先出现的 `updated` 当作发表时间的问题：仅 `published` 参与发表窗口，`updated_at` 单独保存，只有更新时间的内容不假装新发表。
4. 修复 RDF/Nature 日期在转换过程中丢失的问题。`YYYY-MM-DD` 保存为 `published_day`，不会补零点或抓取时间。Nature 的24条近期日期级内容已保存到 `data/background-candidates.json`，作为人工背景候选，**不会自动进入本期或网页背景阅读**。
5. 解析保留作者、可用的DOI、期刊引用、arXiv论文ID、版本与公告类型。RSS 时间标为 `rss_announcement`；新公告、跨类、修订不混为首次提交。末轮记录分别为：new 324、cross 108、replace 100、replace-cross 26。修订在网页标为“预印本修订”。
6. 学术摘要和标题是索引/订阅材料，未读取论文全文；有DOI或期刊引用也不自动宣称当前版本经过同行评审。Nature 综合RSS同时包含新闻、评论和研究，保持混合来源性质，未将整本期刊的所有条目标成论文。

时间语义依据 [arXiv RSS官方说明](https://info.arxiv.org/help/rss_specifications.html)；Atom首次提交与修订字段依据 [arXiv API官方文档源文件](https://github.com/arXiv/arxiv-docs/blob/develop/source/help/api/user-manual.md)。本轮没有启用 API 查询，也未接入其历史回补。

### 新闻源

1. **新华社已修复**：旧英文RSS复测返回2017-05-07内容；改为 [官网时政栏目](https://www.news.cn/politics/)，通过站内文章页标题、发布日、可见时分秒和来源字段生成元数据。本轮8篇均成功，时间为北京时间文章头部换算UTC，原文链接保留；`attribution`保留转载来源，明确新华社/新华网署名时记录上游机构。
2. 适配器限定 `www.news.cn` 和时政文章路径，每次最多8篇，按URL日期优先取近期链接，逐篇失败可显示 `partial`。**不是新华社全站采集**，同日超过8篇会遗漏；页面模板变化需维护。原RSS地址保存在配置的 `legacy_url`，不会继续当作新闻入口。
3. **诊断细化**：健康记录新增 `error_kind`，区分 DNS、TLS、timeout、HTTP、connection、parse_or_validation。修复 XML ParseError 自带数字 `code` 被误认成 HTTP 状态码的问题。
4. **独立复测工具**：`python -m scripts.probe_sources` 只读取公开入口，保存检查结果；不发布、不调用AI、不覆盖生产素材池。支持指定候选配置文件，便于逐个验收后启用。

## 尚未解决、需要人工操作的项目

### A. X授权和18个待核验账号（优先处理）

1. 登录 [X开发者文档入口](https://docs.x.com/make-your-first-request.md) 对应的开发者控制台，确认自己的应用能够读取用户名与用户时间线。是否付费、可读配额和限流以自己的控制台为准；本轮不承诺某个价格或免费额度，也没有替你购买服务。
2. 在运行采集的服务器本地 `.env` 添加 `X_BEARER_TOKEN=你的真实令牌`。不要在聊天、报告或版本库粘贴令牌；DeepSeek/OpenAI密钥不能替代。
3. 编辑 `config/social.json`。先选1—2个已核验账号试运行，其余设 `enabled: false`；将总 `enabled` 设为 `true`。对新核验账号填写 `identity_status: manually_verified`、`identity_evidence`、`identity_checked_at`，能确认时填写稳定数字 `user_id`。
4. 执行 `python -m scripts.collect`，读取 `data/social-status.json` 的 `account_statuses`，并核对 `data/social-posts.json` 中作者、原文URL与真实时间。确认后再逐批启用其余账号。
5. Docker部署时，编辑的是宿主机项目 `.env`；使用 `docker compose up -d --force-recreate web` 使注入环境更新，再执行 `docker compose exec -T web python -m scripts.collect`。只在容器里运行采集时，本机 `data/` 不代表容器卷数据。

| 状态 | 操作 |
|---|---|
| identity_required | 从作者官网/所属机构页找到账号链接；记录证据再改状态，不凭同名或认证徽章推断 |
| identity_mismatch | 对照官网确认是否改名、转让、配置错误；核实数字ID，勿直接删除校验字段掩盖问题 |
| credentials_required / unauthorized | 检查服务进程读到的环境、令牌是否过期/撤销；必要时在控制台轮换 |
| billing_required / forbidden | 检查应用权限、账户配额、访问计划及账号是否受保护，按控制台提示处理 |
| not_found | 核对拼写、账号改名、删除或停用 |
| rate_limited | 降低采集频率/启用账号数量，按控制台限流周期后重试 |
| coverage_limited | 默认最多300条；审查API预算后将 `max_pages_per_account` 增至最多10，重新采集；若仍有缺口，需另做历史回补，不能宣称全覆盖 |
| available / empty | 前者核对原帖；后者仅表示该次请求无符合条件的新帖，不表示失效 |

待核验清单：`lennysan`、`paulg`、`nikitabier`、`rrhoover`、`bgurley`、`OfficialLoganK`、`vista8`、`lijigang_com`、`dotey`、`op7418`、`dongxi_nlp`、`indigo11`、`venturetwins`、`GabrielPeterss4`、`deedydas`、`bobmcgrewai`、`ding_liam`、`levelsio`。没有用猜测补真实姓名。Lenny通讯身份与账号 `lennysan` 的对应关系仍须另核对；接入通讯不会自动将X账号标成已核验。

补充公开渠道检查：Karpathy博客RSS可以解析，但最新日期2026-04-30，本轮未启用为每日新内容；Lex站点feed未通过本项目XML解析，未启用。Paul Graham官网本轮页面提取没有明确账号链接，Ryan Hoover与levels个人站访问未成功，继续保留待核验；其余账号尚未完成逐一官网核验。没有将这些情况概括为“账号不存在”。

如果不准备开通X权限，可以保持关闭，先使用作者公开RSS；从官方主页发现feed后写入候选配置，以 `kind: opinion` 验证再启用。不要把第三方转述或截图当作原始帖子。当前没有独立的社交手工导入命令，不建议直接覆盖 `social-posts.json`。

### B. 学术来源后续覆盖

以下是原 `srcs/examples/scholar.txt` 中尚未接入项的操作路线，不是本轮已验证成功的接口清单。先做小样本元数据验收，再开发专门适配器；不直接把HTML页面URL塞进RSS配置。

| 来源/类别 | 当前边界 | 手动操作与后续接入 |
|---|---|---|
| arXiv全量/历史 | 4分类RSS，三类达到200项上限 | 先查看每类源实际条目数与响应大小；审查需求后调整 `max_items`，以复测脚本确认。历史回补按官方API约束另建缓存查询；保留首次提交/修订两个时间，不以查询时刻充发表日期 |
| Nature | 仅日期，无法判定07:00窗口 | 打开背景候选原文，查看正式发布日期；仅在原页面明确提供含时区时分时才补 `published_at`，仅有日期则保持背景候选。不要用页面修改时间、Crossref入库时间补齐 |
| OpenAlex、PubMed | 尚无生产适配器 | 在各自官网文档确定检索条件、身份/配额要求；导出少量记录，核对DOI/PMID、作者、文献类型、发表日期精度后实现元数据适配器。不要把索引收录时间当论文发表时间 |
| Web of Science、Scopus、知网、EconLit、MathSciNet | 未验证机构订阅及接口权限 | 通过单位图书馆确认可用数据库和API/导出授权；先导出RIS/BibTeX/CSV样本，保留原始ID和出处，再编写转换器。现有 `update_news --import-file` 不能直接读取RIS/BibTeX |
| ACM DL、IEEE Xplore | 未接入，全文和元数据权限需区分 | 选定期刊/会议及时间范围，从官方页面导出引用或使用获批接口；记录DOI、会议信息和公开摘要，不绕过全文付费墙 |
| SSRN、RePEc、zbMATH Open、ChinaXiv、Preprints.org | 尚未逐站验证入口与协议 | 从官网确认RSS/API/引用导出；用3—5个条目核对原文ID、日期、修订及文献类型。工作论文/预印本保持明确标注 |
| bioRxiv、medRxiv | 未接入专门适配器 | 按官方元数据文档小样本验证，保留版本、日期和预印本标识；若只有日期，先入背景候选，不强塞晨报窗口 |
| NeurIPS、ICML、ICLR、AAAI、IJCAI、CVPR、ICCV | 未接入会议年度论文集 | 先指定年份与主题，从会议官网指向的正式论文集/OpenReview/出版商页面取元数据；区分投稿、接受、正式发表与网页上线，不把所有OpenReview条目当作已接收论文 |
| SOSP、OSDI、USENIX ATC、SIGCOMM | 未接入系统/网络会议 | 同样按会议官方论文集逐年导出；检查公开摘要和稳定论文URL，日期不完整时保留候选 |
| Google Scholar | 仅人工发现工具 | 使用网页检索/提醒发现论文，沿DOI或作者原文核验；本项目没有使用未经核实的Scholar API或自动绕过验证码 |

没有逐站声称上述数据库需要付费或都能免费自动抓取；具体取决于官方入口及用户权限。当前重点已落实在AI论文；临床、经济及其他学科尚未形成每日自动采集。

### C. 新闻源剩余问题

| 对象 | 本轮证据 | 你可执行的步骤与完成标准 |
|---|---|---|
| 中国日报 | 原 `china_rss.xml` 与候选 `cndy_rss.xml` 均404；官网栏目可读；样本文章给出日期与“Updated”时刻 | 访问官网栏目或联系网站确认当前RSS/元数据服务。把提供的官方地址加入候选JSON后用复测命令验证；必须有近期标题、原文URL及可靠发表时间。现有样本只证明更新时间，尚未上线文章适配器 |
| 人民网 | politics RSS最新2025-06-05；ywkx候选不含解析器可用的日期；当前栏目两次直连失败 | 在目标服务器分别查DNS、HTTPS和栏目访问。官网新入口能够稳定获取后，再开发独立适配器或使用授权数据。不要把“HTTP 200”当作已修复 |
| 新华社覆盖量 | 当前时政栏目每轮最多8篇 | 若需要更广覆盖，先明确栏目和预算，增加逐栏目入口/链接轮换，验证各自模板及来源字段；不能简单认为当前适配器涵盖全站 |
| 其余目录媒体 | 348项未配置 | 按地区/主题缺口分批建立候选；官方RSS/Atom优先，授权供稿单独处理；每批验证内容、时间、来源、健康和截稿结果再启用 |

本轮保留人民网与中国日报原配置及故障状态，方便继续观察；未通过验证的替代地址没有启用。中国新闻网等中文新闻入口继续正常提供内容，但不能当成这两家媒体已经修复。

网络排障可以在 Windows 运行：

```powershell
Resolve-DnsName politics.people.com.cn
Test-NetConnection politics.people.com.cn -Port 443
curl.exe -I --max-time 20 https://politics.people.com.cn/
python -m scripts.probe_sources
```

DNS失败检查服务器解析器；443不通检查出站网络；TLS失败检查系统时间、证书链及代理设置；HTTP 403/429检查官方限制。保持TLS验证开启。HEAD成功仅证明响应可达，最终仍以GET解析记录为准。

## 如何复测、启用与发布

```powershell
# 在项目根目录执行；离线回归
python -m unittest discover -s tests
node --check public/app.js

# 只验证当前配置，不更新生产池
python -m scripts.probe_sources --output docs/source-probes-latest.json

# 验证候选；候选配置为JSON数组，每项至少有id/url
python -m scripts.probe_sources --config docs/source-candidates.json --output docs/source-candidate-probes-latest.json

# 更新采集池，不调用AI，不发布
python -m scripts.collect
python scripts/report_sources.py
```

检查 `source-health.json`、`social-status.json`、`article-pool.json`、`background-candidates.json`、`social-posts.json`。确认数据后，后续正常日报会按截稿窗口选入；要修改既有一期，需要明确修订说明。以下是**可选发布操作，本轮未执行**：

```powershell
# 发布当期；既有刊期需要修订说明
python scripts/update_news.py --no-ai --revision-note '补充信息源修复后的素材'
```

该命令仍会再次采集。若使用人工导入：复制 `data/manual.example.json`，填写真实标题、原文、source_id、六个主题之一、带时区发表时间，再使用现有 `--import-file`；它导入完整一期，**不是向已有刊期增补一条**。仅有日期的材料保持候选，不能猜测时间绕过校验。

## 交付与验证证据

| 文件 | 用途 |
|---|---|
| `docs/source-health-after.json` | 本轮完整采集快照，不随日常采集变化 |
| `docs/source-probes.json` | 修改入口前的32源独立复测 |
| `docs/source-candidate-probes.json` | 博客、arXiv分类、新闻候选的实测 |
| `docs/xinhua-page-probe.json` | 新华社8篇原文、时间、归属的适配器验收 |
| `docs/source-audit.md` | 最新自动审计及完整未配置目录 |
| `config/feeds.json`、`config/social.json` | 已启用入口与身份门槛配置 |
| `scripts/news_pages.py`、`scripts/social.py`、`scripts/probe_sources.py` | 新华社、X分页、独立复测模块 |
| `tests/test_source_repairs.py` | 日期精度、身份、分页、错误和新闻解析回归 |

回归共31项通过；前端 `node --check` 通过。测试未调用真实X接口、未评估第三方内容真实性、未验证云服务器部署。报告与代码保留这些边界，未将模拟测试或单次成功扩大为生产稳定性保证。
