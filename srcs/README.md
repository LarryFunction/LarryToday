# LarryToday 新闻信息源资料库

整理日期：2026-10-18。这里只搜集和整理信息源，没有开发网站、订阅付费服务或启用新闻采集。原有 `examples/` 文件保持原样。

## 本轮成果

- **367 个结构化条目，13 个主题分类**。涵盖国际政治、地区媒体、科技安全、AI、经济投资、宏观统计、公司披露、外交人道、科学健康、气候农业、社会文化体育、事实核查及发现工具。
- 按 URL 主机及部分名称与原材料匹配：**314 个补充候选、53 个原有来源的补全条目**。名称识别不是完整实体消歧，所以314不应解释成精确新增媒体数量。
- 将原材料中的 **740 个不同 URL** 建立带原文件和行号的索引；与扩充目录合计覆盖 **1,039 个不同主机名**。主机名不等于独立媒体，也不等于国家数。
- 对367个目录入口均进行了网页访问尝试：**253 个读到页面，114 个待复核**。这是页面级检查，不是对机构独立性、内容真实性、持续更新或采集许可的认证。浏览工具可能使用缓存。
- **30 项接入资料**，包含RSS、API、数据下载、授权供稿和网页入口。8个公开端点做了直接格式探测：**5个RSS有条目、1个GeoJSON通过解析、1个RSS返回空列表、1个证书验证未通过**。

## 从哪里开始

| 文件 | 用途 |
|---|---|
| [CATALOG.md](CATALOG.md) | 按主题浏览全部367个来源，直接点击官网 |
| [sources.json](sources.json) / [sources.csv](sources.csv) | 后续程序导入的结构化目录；JSON为主格式 |
| [CROSS_VALIDATION.md](CROSS_VALIDATION.md) | 如何回溯原始证据、识别同源转载、处理冲突说法 |
| [verification-recipes.json](verification-recipes.json) | 按主题配置的交叉验证组合；引用目录中的稳定ID |
| [integrations.json](integrations.json) / [integrations.csv](integrations.csv) | 文档入口、候选端点、鉴权提示和实测状态 |
| [INGESTION.md](INGESTION.md) | 接入顺序、发布与更新建议、已知限制 |
| [feeds.checked.opml](feeds.checked.opml) | 可导入RSS阅读器的5个已解析且有条目的订阅 |
| [verification-log.json](verification-log.json) | 官网、文档等网页检查记录与观察到的跳转 |
| [endpoint-probes.json](endpoint-probes.json) | 8个公开端点的HTTP及格式探测结果 |
| [LINK_REVIEW.md](LINK_REVIEW.md) | 待复核入口和跳转清单 |
| [legacy-url-index.json](legacy-url-index.json) / [legacy-url-index.csv](legacy-url-index.csv) | 原材料URL索引；不继承其“权威”“可直接访问”等判断 |
| [legacy-unresolved-notes.json](legacy-unresolved-notes.json) | 原材料无URL行，包括名称、说明和小标题；不是新增来源计数 |
| [SCHEMA.md](SCHEMA.md) / [sources.schema.json](sources.schema.json) | 字段及校验规范 |
| [manifest.json](manifest.json) | 分类统计、数量口径及原始文件SHA-256 |

## 使用原则

**广泛覆盖不等于已交叉证实。** 目录提供可组成证据链的材料；每一条新闻仍须在“具体事实/主张”层面核验。Reuters稿被20家转载只算一个报道链；政府或企业声明可以确认“它说了什么”，不能单独证明其主张成立。

优先组合“原始文书/数据 + 直接采写的报道 + 当地来源”。争议双方的说法用于呈现争议，不能用平均数或简单投票生成事实。没有足够独立证据时标注待核实，不强行给结论。

地区字段描述报道覆盖范围，不是总部、国籍、主权或所有权断言。语言字段为主要可见语种，非穷尽。类型表示常见用途，不替代文章级类型判断。所有权尚未逐家完成审计，未知不能解释为彼此独立。

不以中国大陆直连速度筛选，不作VPN要求标签。付费墙、商业转载许可、登录、接口密钥和动态页面依然影响后续接入，因此单独保留待核实状态。未提供无法核实的RSS猜测地址或付费API的虚构价格、配额。

## 维护方式

仅编辑 `catalog.seed.psv`、`integrations.seed.psv` 及核验资料，再运行：

```powershell
python srcs/build_catalog.py
python srcs/validate_catalog.py
```

可选择重新检查8个公开端点：

```powershell
python srcs/probe_endpoints.py
python srcs/build_catalog.py
```

构建脚本离线执行；端点探测才会联网。不要把重新构建日期当成重新核验日期。增加网页核验记录时保留具体URL、实际检查日期、方法与结果。统计变化后同步本说明。
