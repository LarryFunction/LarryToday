# 数据字段与计数口径

`sources.json` 顶层包含 `schema_version`、`prepared_at`、`categories`、`sources`。CSV是扁平导出：列表/对象列以JSON字符串保存，UTF-8 BOM便于表格软件打开；可能被解释成公式的文本增加前导单引号，程序导入优先使用JSON。

| 字段 | 含义 |
|---|---|
| id | 稳定条目ID；被接入表和核验组合引用 |
| name / url | 来源显示名及选定入口；可能是栏目、项目或文档站，不保证一个条目对应一家机构 |
| category | 13类中的主分类；跨领域来源仍可服务其他主题 |
| coverage_regions / languages | 报道覆盖地区和主要语种；不是总部和所有语言清单 |
| kind | news / official / data / research / company / analysis / factcheck / discovery |
| evidence_role | 常见证据角色；不代表可信度评级 |
| usage_notes | 适用主题和该来源特有局限 |
| priority | P1优先研究接入；P2扩展覆盖；P3发现工具。不是真实性等级 |
| publisher_family_hint | 少量显然关联渠道的分组提醒；不是全面所有权数据库；null是未知 |
| ownership_verified | 本轮均为false，不能把未知关联当独立 |
| relationship_to_examples | existing_host_enriched：相同主机；existing_name_enriched：有限名称匹配；supplemental_candidate：两者未匹配 |
| example_references | 原始文件、行号、URL或名称；保留溯源，不修改原材料 |
| verification_status | page_observed / fetch_inconclusive / not_checked；仅选定入口的网页访问情况 |
| checked_at / evidence_url | 页面检查日期及直接依据URL；不是文章发布时间 |
| observed_title / observed_redirect | 浏览工具观察到的标题与跳转；不自动替换原链接 |
| access_and_reuse | 当前统一为unknown_per_item_check_required；不假设免费阅读意味着可复制或商业使用 |
| enabled_for_ingestion | 默认false；本任务没有部署采集器 |
| integration_ids | 关联integrations.json的ID |

`official` 包括政府、国际组织和组织自身发布渠道，是“一手材料”标签，并不意味着所有条目都是政府机构，也不授予其事实裁决权。医学论文平台、开放论文索引和数据库需要文章级区分预印本、发表、修订、撤稿。

`verification-log.json` 中 `page_observed` 仅说明浏览工具返回了非空页面；未对全文、登录后内容、最近更新和全部链接逐项审计。`fetch_inconclusive` 包括403、超时、验证码、空响应及工具无法读取，不等于永久失效。

`integrations.json` 独立保存文档状态与端点状态：

- `not_integration_tested`：未直接检验接口。
- `feed_parsed`：一次HTTP请求成功解析RSS/Atom且含条目；未保证持续新鲜度。
- `empty_feed`：格式可解析但本次无条目；不判为停运，也不计入已含内容的OPML。
- `geojson_parsed`：一次样本满足GeoJSON FeatureCollection形状。
- `inconclusive`：连接、证书、权限或格式等问题；查看 `endpoint-probes.json`。

文档可读不等于端点可用；端点可用不等于商业使用已获许可。未填端点时用null，不拼造URL。

原材料索引只对明确的http(s)和www链接提取、去掉片段并补全路径；http/https、不同栏目、不同主机仍可能指同一来源，故740是URL数量，1,039是主机数量，均不是独立机构数量。没有URL的学术平台、论坛和人物名称保存在原文行索引中，后续可逐一完成实体消歧。
