# LarryToday

古典报纸 × 构成主义风格的每日环球新闻网站。Python 3.11+ 标准库服务，原生 HTML / CSS / JavaScript，无第三方运行依赖。

## 启动与阅读

```powershell
python server.py
# 首次采集并发布
python scripts/update_news.py
```

访问 http://localhost:8000；通过 HOST、PORT 调整监听地址。默认仅本机访问。

保留七个日期门面、版面主题色与单行新闻布局。晨读默认显示三条提要，可展开八条，并定位事件；支持只看精选、关键词/标签检索、背景阅读、同事件来源展开、多源视角和跨期本地收藏。收藏保存文章快照，不跨浏览器同步。

## 刊期与修订

北京时间每日 07:00 截稿，收录前一日 07:00（含）至当日 07:00（不含）的新闻；07:00 前运行默认仍为上一期。没有可靠时分的新闻不混入当日窗口；较早内容另列背景阅读，最多十二条。日期是新闻发布时间，不以采集时间代替。

初版 `data/editions/YYYY-MM-DD.json` 永久保留。修订新增到 `data/revisions/YYYY-MM-DD/`，需要说明，不覆盖原刊；`latest.json` 只是最新版本指针。网页可查看版本记录、切换初版和修订版。社交观点也随版本保存。

```powershell
python scripts/update_news.py --revision-note '补充新来源并更正导读'
python scripts/update_news.py --enrich-existing --revision-note '补齐AI编辑'
python scripts/update_news.py --enrich-existing --ai-limit 12 --revision-note '补齐12篇编辑'
python scripts/update_news.py --no-ai --revision-note '更新原始素材'
python scripts/update_news.py --edition-date 2026-10-18 --revision-note '补刊说明'
```

人工导入：复制 `data/manual.example.json` 后填写真实内容，运行 `python scripts/update_news.py --import-file data/manual.json`，已有刊期须加修订说明。导入为完整一期。`published_at` 应为带时区 ISO 8601；缺失时间的记录无法进入当期。分类使用网站六个主题名称。

## 来源与采集

`srcs/sources.json` 是来源目录，不等于全部已接入。`config/feeds.json` 现配置 36 个采集入口（包含新华社官网适配器），覆盖中国新闻网、NYT、NPR、PBS、BBC、Guardian、France24、DW、RFI、Le Monde、El País、RTHK、SCMP、CNA、NASA、Fed、UN 等。RSS 2.0、Atom 和 RDF 均有解析支持。目录合并新增来源，显示订阅健康、最近成功时间和本期收录数。

2026-10-20处理后：新华社已切换到官网时政栏目并实测8篇；新增arXiv机器学习、视觉、自然语言分类，以及Lenny作者通讯。36个入口中32个可用，人民网订阅停更、中国日报RSS仍404、cs.AI本轮空订阅、Nature仅日期。详细边界与手动操作见[信息源处理报告](docs/source-treatment-report.md)。

```powershell
# 仅采集素材，不发布，也不调用新闻编辑AI
python -m scripts.collect
```

采集池保留14天以缓解RSS滚动遗漏；定时采集可改善覆盖，不能保证收全。来源地区代表媒体所在地，不是事件发生地。选编对重复来源施加软性降权，不为凑地域比例编造报道。转载机构可识别时用于避免把同一家通讯社误当独立报道。

X观察名单仍默认关闭，20个账号中2个已记录官网关联、18个待核验；本地尚无X凭证。服务端配置 `X_BEARER_TOKEN`、核实接口权限，并逐账号填写身份状态后启用。支持逐账号错误、分页及增量检查点；未完成真实X授权环境验收。个人观点与作者通讯进入独立“业界声音”池；通讯可在X关闭时运行，不能等同全部X发言。

arXiv保留作者、论文ID、版本和公告类型，区分预印本与修订；每分类最多200项，达到上限不代表全量覆盖。Nature日期级元数据保存到 `data/background-candidates.json`，供人工核验，不会进入精确截稿窗口。`python -m scripts.probe_sources` 可单独复测而不更新生产素材池。

## AI 编辑

`.env` 使用 `BASE_URL`、`BASE_KEY_1/2/3`，可选 `AI_MODEL`。三个密钥依次用于双语标题/中文概述/标签、材料依据复核、同事件多源比较。当前配置属于同一供应商，不能当作三家独立事实核查机构。

只发送公开标题、订阅摘要和来源元数据。正文不可得时不会假装读过全文。术语表位于 `config/glossary.json`。摘要注明AI辅助、未独立核验；失败保留原始信息。缓存按素材、模型、提示版本保存；429及暂时性故障有限重试，结构验证失败拆分为单篇。`ai_status` 记录结果，API调用按供应商账户计费。

多源比较使用全部符合条件的已编辑文章，按时间分成30篇、步长24的重叠窗口，每窗最多请求三组。标注信息互补、侧重点不同、说法冲突或主要信息一致；仅同事件且至少两家来源的内容可合并。窗口法可能漏掉远距离相关文章，不代表穷尽事件或独立核验。晨读重要性和文章分类也是启发式自动选编，仍适合人工审阅。

密钥仅服务端读取，`.env` 不进入网页、版本管理和镜像。不要在日志、截图或提交中包含密钥。

## GitHub Pages

公开站点：https://larryfunction.github.io/LarryToday/

GitHub Pages 只托管静态文件，不运行 `server.py`。前端通过相对路径读取 `api/*.json`，由 `scripts/build_pages.py` 从 `public/`、`data/editions/`、`data/revisions/` 和来源目录生成。`.github/workflows/pages.yml` 会在推送到 `main` 后运行测试、构建并部署。

本地预览静态构建：

```powershell
python scripts/build_pages.py
python -m http.server 8001 --directory dist
```

当前仓库部署的是已发布快照。更新报纸后提交 `data/` 并推送即可触发重新部署：

```powershell
python scripts/update_news.py
git add data
git commit -m "Update daily edition"
git push
```

首次部署需在仓库 `Settings → Pages → Build and deployment` 将 Source 设为 `GitHub Actions`。`dist/` 是构建产物，不进入版本管理。

## 云端部署

阿里云首版上线请按[详细部署指南](docs/aliyun-deployment-guide.md)操作，包含学生套餐选择、备案确认、Windows 上传、已有日报迁移、HTTPS、任务互斥、备份和回退。下方为基础模板说明；实际启用定时任务前，应先应用指南中的共享锁和错峰配置。

部署模板已提供，尚未连接云服务器或启用系统定时任务。Linux项目默认目录 `/opt/larrytoday`，不同路径需修改service。

```sh
docker compose up -d --build
docker compose exec -T web python scripts/update_news.py
sudo cp deploy/larrytoday-update.service deploy/larrytoday-update.timer deploy/larrytoday-collect.service deploy/larrytoday-collect.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now larrytoday-collect.timer larrytoday-update.timer
systemctl list-timers 'larrytoday-*'
```

采集每30分钟，发布每天北京时间07:00。Compose从服务器 `.env` 注入凭证，`news-data`卷保存素材、缓存、刊期和修订；首次部署须采集，不自动复制本机日报。用 `docker compose cp data/manual.json web:/app/data/manual.json` 可上传人工稿。

配置域名和 `deploy/Caddyfile`，将示例域名替换为真实域名。Caddy通过80/443提供HTTPS，应用端口仅本机访问。只读API无管理写入入口；发布工作台按约定留待后续版本。

备份整个 `news-data` 卷。异常退出可能留下 `.update.lock` / `.collect.lock`，先确认没有任务运行再清理。发布中断应检查修订文件及索引，保留已存在版本并用修订说明重试。当前标准库HTTP服务适合个人小流量；更高并发可迁移静态API/CDN或生产服务。

## 验证与排障

```sh
python -m unittest discover -s tests
node --check public/app.js
journalctl -u larrytoday-update.service
journalctl -u larrytoday-collect.service
docker compose logs web
```

`/health`检查存活；`/api/status`查看采集结果；`/api/source-health`查看来源健康。全部订阅失败时保留旧刊，部分失败会明确提示。新闻原文应以链接媒体为准。

晨读界面采用与各版面同色系的浅底构成主义卡片，桌面默认三列，窄屏单列。分版优先显示精选，不足三条时按发布时间补充本版报道。未接入来源处理清单见 `docs/source-plan.md`。

完整来源排查文档：[`docs/source-audit.md`](docs/source-audit.md)，包含当前入口实测及所有待接入来源。每次采集后执行 `python scripts/report_sources.py` 可重新生成（会覆盖该生成文件，人工笔记请另存）。
