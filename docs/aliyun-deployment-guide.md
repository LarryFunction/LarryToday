# LarryToday 第一版：阿里云服务器部署指南

编写日期：2026-10-20。适用于当前仓库的 Docker Compose、Python 后端及原生前端。本文提供操作步骤，**尚未实际购买、连接或部署你的服务器**。价格、优惠资格、备案条件以购买时阿里云控制台为准。

目标是先让现有版本稳定上线：保留已完成的美术设计和新闻功能，将现有日报迁移到服务器，再逐步启用每日更新。未接入的来源、X 授权和进一步的编辑优化不必全部完成后才部署。

## 目录

1. [推荐方案与购买前确认](#1-推荐方案与购买前确认)
2. [服务器和端口准备](#2-服务器和端口准备)
3. [安装 Docker](#3-安装-docker)
4. [上传项目与已有日报](#4-上传项目与已有日报)
5. [配置密钥并启动网站](#5-配置密钥并启动网站)
6. [迁移数据与私下验收](#6-迁移数据与私下验收)
7. [域名与 HTTPS](#7-域名与-https)
8. [服务器信息源检查](#8-服务器信息源检查)
9. [手动出版与 AI](#9-手动出版与-ai)
10. [自动采集和每日出版](#10-自动采集和每日出版)
11. [备份与恢复](#11-备份与恢复)
12. [升级与回退](#12-升级与回退)
13. [常见问题](#13-常见问题)
14. [首版验收清单与日常维护](#14-首版验收清单与日常维护)

## 1. 推荐方案与购买前确认

### 1.1 首版架构

```text
读者浏览器
    │ HTTPS，443
    ▼
服务器上的 Caddy（证书申请、续期、反向代理）
    │ HTTP，仅服务器本机
    ▼
127.0.0.1:8000 → Docker 中的 LarryToday
                       │
                       └── 持久化数据卷 /app/data

systemd 定时任务 → Docker 内采集 / AI 编辑 / 日报出版
```

当前项目无需额外购买数据库、Redis、GPU、对象存储或负载均衡。Caddy 安装在宿主机上，应用运行在 Docker 中；这样可以直接使用仓库中已有的端口配置。

### 1.2 推荐购买配置

以下是针对个人、小流量首版的工程建议，不是性能保证：

| 项目 | 建议 |
|---|---|
| 云产品 | 学生优惠中的 ECS；若购买轻量应用服务器，也可采用本文主体流程 |
| CPU / 内存 | 2 核 / 2 GB 起步；预算允许时选 4 GB 内存 |
| 系统盘 | 40 GB 起步；持续关注历史刊期、素材与镜像占用 |
| 操作系统 | Ubuntu 24.04 LTS，x86_64，纯系统镜像 |
| 公网 | 确认有公网 IPv4，并核对带宽、月流量和超额规则 |
| 地域 | 结合访问人群、备案资格以及信息源和 AI 服务的实际连通性选择 |
| 付款前 | 核对首购价、续费价、期限、优惠券适用品类和备案服务资格 |

不要为了套用本指南，重装已有重要数据的服务器系统。其他 Linux 发行版需要使用对应的软件安装说明。学生优惠不意味着所有地域、所有产品都适用；先完成认证，再看账户实际可购买内容。[阿里云学生权益说明](https://help.aliyun.com/zh/document_detail/2881975.html)

### 1.3 域名、备案与新闻网站业务

**购买中国内地节点前，应先确认 LarryToday 的实际内容是否符合你的备案主体和所需资质。** 阿里云说明：使用中国内地资源需按要求备案；中国香港及海外节点不需要办理该项中国内地 ICP 备案。后者不等于免除其他适用的业务要求。[阿里云备案资料说明](https://help.aliyun.com/zh/icp-filing/basic-icp-service/user-guide/required-materials)

LarryToday 包含国际政治新闻、聚合、中文摘要和观点比较，不能直接假定“学生个人备案即可公开运营”。阿里云资料将新闻、出版列为可能涉及前置审批的领域。建议购买前向备案支持描述真实功能，确认主体、业务资质和服务器套餐是否适用；不要通过改成“个人博客”的名称来替代业务确认。[同上：前置审批材料要求](https://help.aliyun.com/zh/icp-filing/basic-icp-service/user-guide/required-materials)

可以直接向支持人员提供：

> 我准备部署 LarryToday，展示国际政治、科技 AI、经济等来源的新闻标题、摘要、原文链接，以及 AI 辅助中文概述和多源观点比较，定期发布日报。拟使用学生套餐、个人主体。请确认此业务是否允许按个人网站备案，是否需要前置审批或其他资质，以及拟购买的服务器是否满足备案接入条件。

这些事项确认期间，仍可完成下面的服务器部署，通过 SSH 隧道私下验收。公开上线阶段再完成域名实名、备案及适用的后续手续，并按要求展示备案信息。

## 2. 服务器和端口准备

### 2.1 创建实例

在阿里云控制台完成购买，记录：

- 产品是 ECS 还是轻量应用服务器。
- 地域、实例 ID、公网 IPv4、到期日期。
- 登录用户名及认证方式；不同镜像可能使用 `root` 或普通管理员账户。
- 系统版本，以及是否附带公网带宽。

优先使用 SSH 密钥。私钥只保存在自己电脑上，不上传项目、不发到聊天中。

### 2.2 开放端口

ECS 设置安全组；轻量应用服务器设置实例防火墙。若服务器本身还启用了 UFW 等防火墙，也要保持一致。

| 端口 | 来源 | 用途 |
|---|---|---|
| TCP 22 | 你的公网 IP，例如 `你的IP/32` | SSH 管理 |
| TCP 80 | 准备公开上线时开放给互联网 | HTTPS 证书验证、HTTP 跳转 |
| TCP 443 | 准备公开上线时开放给互联网 | HTTPS 访问 |
| TCP 8000 | **不开放到公网** | 仅供宿主机 Caddy 访问 |

私下验收阶段只需开放 SSH。你的公网 IP 改变后，更新 SSH 规则；保留阿里云控制台远程连接作为恢复渠道，避免将自己锁在服务器外。

官方操作：[ECS 安全组应用场景](https://help.aliyun.com/zh/ecs/user-guide/security-groups-for-different-use-cases)、[轻量应用服务器防火墙](https://help.aliyun.com/zh/simple-application-server/user-guide/manage-the-firewall-of-a-server)。

### 2.3 登录和基础检查

**在 Windows PowerShell 执行**，将占位值替换为实际值：

```powershell
$Server = "ubuntu@你的服务器公网IP"
ssh $Server
```

若使用私钥，命令形式为 `ssh -i "C:\你的私钥路径" $Server`。后续 `scp` 同样可加 `-i`。首次连接时，将 SSH 指纹与控制台提供的信息核对。

**以下标注“服务器”的命令均在 SSH 登录后的 Linux 终端执行。** 本文统一使用管理员 shell，先执行：

```bash
sudo -i
cat /etc/os-release
uname -m
timedatectl
df -h
free -h
```

若已直接登录 `root`，无需再次 `sudo -i`。确认系统为 Ubuntu 24.04，架构为 `x86_64`。

```bash
timedatectl set-timezone Asia/Shanghai
timedatectl set-ntp true
apt update
apt install -y ca-certificates curl nano tar util-linux
```

如果系统提示需要重启，安排重启后重新登录。项目刊期使用北京时间，服务器日志也统一到该时区更方便排障。

## 3. 安装 Docker

**服务器执行。** 本节针对没有安装 Docker 的新 Ubuntu 实例。已有安装时先检查版本，不要直接卸载正在运行其他业务的容器环境。

以下使用 Docker 官方 apt 源安装 Engine 和 Compose 插件。[官方 Ubuntu 安装文档](https://docs.docker.com/engine/install/ubuntu/)

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
docker --version
docker compose version
command -v docker
command -v flock
```

后文 systemd 配置假定路径为 `/usr/bin/docker`、`/usr/bin/flock`。若输出不同，需要替换配置中的路径。

安装失败时，先区分 apt 源不可达、DNS 故障和镜像拉取失败。不要关闭 TLS 校验或复制来历不明的镜像加速地址。中国内地实例可能需要使用账户可用的阿里云镜像服务，或采用第 13 节的离线镜像方案。

## 4. 上传项目与已有日报

### 4.1 准备上传包

推荐首版迁移现有 `data`，这样服务器上线后可立即显示已编辑日报、历史刊期和缓存。Docker 镜像默认排除了 `data`，**只上传代码不会自动带上已有新闻**。

打包前，暂停本机的采集、出版和 AI 编辑任务，确保没有程序正在写入 `data`。不要一边更新一边打包。

**Windows PowerShell：**

```powershell
Set-Location D:\MyProject\LarryToday
$CodeArchive = Join-Path $env:TEMP "larrytoday-code.tar.gz"
$DataArchive = Join-Path $env:TEMP "larrytoday-data.tar.gz"

tar.exe -czf $CodeArchive Dockerfile compose.yaml server.py public scripts config srcs deploy README.md
if ($LASTEXITCODE -ne 0) { throw "代码打包失败，停止上传" }

tar.exe -czf $DataArchive --exclude=.update.lock --exclude=.collect.lock -C data .
if ($LASTEXITCODE -ne 0) { throw "数据打包失败，停止上传" }

tar.exe -tzf $CodeArchive
scp $CodeArchive $DataArchive "${Server}:/tmp/"
```

如果重开了 PowerShell，需要重新设置 `$Server`。检查代码包中没有 `.env`；这里采用明确文件列表，不会打包仓库根目录的密钥文件。数据包可能较大，上传后应妥善保管。

### 4.2 解压代码

**服务器：**

```bash
mkdir -p /opt/larrytoday
tar -xzf /tmp/larrytoday-code.tar.gz -C /opt/larrytoday
cd /opt/larrytoday
ls
```

本文的首次部署步骤假定该目录和数据卷尚无另一套生产数据。以后升级请使用第 12 节，避免覆盖线上配置。

保持路径 `/opt/larrytoday` 不变，现有 systemd 模板依赖它。Compose 项目名也应保持不变，否则可能创建另一个空数据卷，让网站看起来“丢了新闻”。

## 5. 配置密钥并启动网站

### 5.1 创建服务器专用 `.env`

**服务器，在 `/opt/larrytoday`：**

```bash
umask 077
touch .env
chmod 600 .env
nano .env
```

在编辑器中填写实际值。下列仅展示字段，不要原样使用占位文本：

```dotenv
BASE_URL=你的AI接口基础地址
BASE_KEY_1=第一把密钥
BASE_KEY_2=第二把密钥
BASE_KEY_3=第三把密钥
# AI_MODEL=接口实际支持的模型名称
```

保持与你本机已经验证过的接口格式一致。不要把 API 路径猜成另一种格式。`AI_MODEL` 未明确时可先省略，之后用探测命令确认。

当前代码用三把密钥分配编辑、复核、多源比较工作，不代表三家独立机构。X 暂时未启用即可，不需要为了部署补齐其凭证。

如果只展示已有日报、暂不调用 AI，`.env` 可以先保留为空文件；Compose 仍然要求文件存在。不要将 `.env` 放进 `public`，也不要截图或贴出完整 `docker compose config`，其展开结果可能包含密钥。

### 5.2 构建启动

```bash
cd /opt/larrytoday
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=80 web
curl -fsS http://127.0.0.1:8000/health
```

首次构建会下载 `python:3.13-slim`。健康检查需要一点时间才显示 healthy。

此时网页没有新闻不一定是失败：还没有迁移数据。`/health` 只证明服务存活，不证明日报已生成或日期正确。

修改 `.env` 后，应执行以下命令重新创建容器以加载新环境；单纯 `restart` 不会重新注入 Compose 环境变量：

```bash
docker compose up -d --force-recreate web
```

## 6. 迁移数据与私下验收

### 6.1 将本机数据恢复到新卷

**仅用于刚创建、尚无生产内容的数据卷。** 不要将旧数据包直接覆盖到已经运营的服务器。

```bash
cd /opt/larrytoday
docker compose cp /tmp/larrytoday-data.tar.gz web:/tmp/larrytoday-data.tar.gz
docker compose exec -T -u root web tar -xzf /tmp/larrytoday-data.tar.gz -C /app/data
docker compose exec -T -u root web chown -R 10001:10001 /app/data
curl -fsS http://127.0.0.1:8000/api/news
```

应用用户 UID 为 `10001`。恢复后的文件必须可由它写入，不能用 `chmod 777` 代替正确属主设置。

`data` 保存于 Compose 的命名卷中。容器重建通常不会删除数据；**不要执行 `docker compose down -v` 或随意清理 Docker 卷**。

### 6.2 用 SSH 隧道在自己的电脑验收

**另开一个 Windows PowerShell 窗口：**

```powershell
$Server = "ubuntu@你的服务器公网IP"
ssh -N -L 18000:127.0.0.1:8000 $Server
```

保持窗口打开，在浏览器访问：

```text
http://localhost:18000
```

这时页面来自云服务器，不是本机开发服务器。没有开放公网 8000，也无需先完成 HTTPS 配置。

检查首页日期、晨读提要、各分区构成主义图块、单条新闻布局、来源链接、历史刊期及手机窄屏显示。根据处理报告，迁移前最新刊期仍可能是 **2026-10-19**；这不是服务器时钟错误，而是尚未出版新一期。

## 7. 域名与 HTTPS

在确认公开服务条件满足之后进行本节。建议先只使用一个入口，例如 `news.你的域名`，避免首版同时维护多个域名跳转。

### 7.1 设置域名解析

在域名 DNS 控制台新增：

| 类型 | 主机记录 | 值 |
|---|---|---|
| A | `news` | 服务器公网 IPv4 |

如果直接使用根域名，主机记录通常为 `@`。没有配置公网 IPv6 时，不要保留指向错误服务器的 AAAA 记录。首次部署先使用直接解析，不叠加 CDN 或代理。

**Windows 检查：**

```powershell
Resolve-DnsName news.你的域名
```

确认结果指向目标服务器，再开放云端及系统防火墙的 TCP 80、443。

### 7.2 安装 Caddy

**服务器：** 以下采用 Caddy 官方 Debian/Ubuntu 软件源。[官方安装说明](https://caddyserver.com/docs/install)

```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt | tee /etc/apt/sources.list.d/caddy-stable.list
chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
chmod o+r /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy
```

### 7.3 配置反向代理

```bash
nano /etc/caddy/Caddyfile
```

替换为以下内容，域名务必改成自己的真实域名：

```caddyfile
news.example.com {
    encode gzip
    reverse_proxy 127.0.0.1:8000
}
```

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl enable --now caddy
systemctl reload caddy
systemctl status caddy --no-pager
journalctl -u caddy -n 80 --no-pager
```

Caddy 可自动申请、续期证书，并将 HTTP 跳转到 HTTPS；前提包括 DNS 正确、验证端口可达、证书存储目录可写且持久保存。[自动 HTTPS 说明](https://caddyserver.com/docs/automatic-https)

在自己的电脑和手机网络分别访问 `https://你的真实域名`。确认浏览器证书正常，且显示 LarryToday 而非 Caddy 默认欢迎页。不要删除 `/var/lib/caddy` 的证书状态来反复重试。

## 8. 服务器信息源检查

本地可连接不代表云服务器可连接。云端地域、DNS、目标站点策略和服务商限制都可能改变结果。入站安全组开放 80/443 也不等于解决了服务器向外采集的问题。

**服务器：**

```bash
cd /opt/larrytoday
docker compose exec -T web python -m scripts.probe_sources --output data/source-probes.json
docker compose cp web:/app/data/source-probes.json /tmp/larrytoday-source-probes.json
```

这里特意指定 `data/source-probes.json`：探测工具默认写 `docs`，而当前镜像没有可写的 `docs` 目录。

需要下载检查时，**Windows：**

```powershell
scp "${Server}:/tmp/larrytoday-source-probes.json" .
```

确认后执行一次只采集、不出版、不中转 AI 的任务：

```bash
cd /opt/larrytoday
flock -w 3600 /run/lock/larrytoday-jobs.lock docker compose exec -T web python -m scripts.collect
curl -fsS http://127.0.0.1:8000/api/source-health
curl -fsS http://127.0.0.1:8000/api/status
```

按你的 [信息源处理报告](source-treatment-report.md)，应带着以下已知状态验收，而不是把它们都当作云端部署失败：

| 已知事项 | 首版处理 |
|---|---|
| 36 个入口、25 个来源 ID | 部署实际启用配置，不要求覆盖全部原始目录 |
| 原始目录仍有 348 项未配置 | 是待接入清单，不是 348 个已确认连接故障 |
| 人民网 RSS 停更、中国日报旧 RSS 404 | 保留健康提示，后续单独替换入口 |
| arXiv cs.AI 有效空 RSS | 不据此判定整个平台故障 |
| Nature 只有日期精度 | 按现有背景候选规则处理，不补造发布时间 |
| X 未配置 token、总开关关闭 | 可以暂不启用；真实接口仍需以后验收 |
| 新华社官网适配、Lenny 通讯、新增 arXiv 分类 | 随当前代码配置迁移，在云端重新检查可达性 |

不要为了追求“全绿”而关闭证书验证、将旧内容伪装成当日新闻或删除时间精度标记。具体未处理项目继续维护在来源文档中，不阻塞整个首版。

## 9. 手动出版与 AI

### 9.1 推荐首日操作顺序

1. 先确认迁移日报可读。
2. 完成云端探测与一次采集。
3. 确认 AI 接口、余额和模型。
4. 人工执行一次出版，检查成品。
5. 再启用定时任务。

**服务器：**

```bash
cd /opt/larrytoday
docker compose exec -T web python -m scripts.ai_news --probe
```

探测用于验证模型接口及凭证，不等同完整编辑验收；请求费用以供应商实际规则为准。

### 9.2 三种常用操作

以下出版命令都使用与自动任务相同的宿主机锁，避免同时写入。

**A. 发布尚未存在的刊期，不调用 AI：**

```bash
flock -w 3600 /run/lock/larrytoday-jobs.lock docker compose exec -T web python scripts/update_news.py --no-ai
```

`--no-ai` 仍然执行出版流程，只是跳过 AI；不要误以为它和 `scripts.collect` 一样只更新素材池。

**B. 发布新刊，限制本次新文章 AI 编辑量：**

```bash
flock -w 3600 /run/lock/larrytoday-jobs.lock docker compose exec -T web python scripts/update_news.py --ai-limit 12
```

`12` 是首轮验证用的示例，不是最佳固定配置。`--ai-limit` 只限制新处理文章数，**不是所有 AI 调用或费用的硬上限**；多源比较还可能产生额外调用。尤其现在 arXiv 素材量较大，应在供应商账户设置预算提醒并观察实际用量。

**C. 为已发布的当前日报补充 AI 编辑，保留修订说明：**

```bash
flock -w 3600 /run/lock/larrytoday-jobs.lock docker compose exec -T web python scripts/update_news.py --enrich-existing --ai-limit 12 --revision-note "首版上线后补充AI编辑"
```

对已存在刊期重新发布，需要明确 `--revision-note`。系统保留初版和修订，不应通过删除历史文件来绕过保护。

### 9.3 刊期时间的含义

默认使用最近已经到达的北京时间 07:00 作为截稿点；07:00 以前执行，默认仍属于上一刊期。每天 07:00 的任务意味着**开始生成**，不保证页面恰好 07:00 已更新，实际耗时取决于来源请求和 AI。

如需明确日期，可使用 `--edition-date YYYY-MM-DD`，先核对目标刊期和是否已有初版。首版不建议额外自动补刊或循环追赶历史日期。

每次完成后同时查看网页和以下接口：

```bash
curl -fsS http://127.0.0.1:8000/api/news
curl -fsS http://127.0.0.1:8000/api/status
curl -fsS http://127.0.0.1:8000/api/source-health
```

## 10. 自动采集和每日出版

### 10.1 安装现有模板，但先不要启动定时器

**服务器：**

```bash
cd /opt/larrytoday
cp deploy/larrytoday-update.service deploy/larrytoday-update.timer deploy/larrytoday-collect.service deploy/larrytoday-collect.timer /etc/systemd/system/
mkdir -p /etc/systemd/system/larrytoday-update.service.d
mkdir -p /etc/systemd/system/larrytoday-collect.service.d
mkdir -p /etc/systemd/system/larrytoday-collect.timer.d
```

当前模板每逢整点、半点采集，同时每日 07:00 出版，存在同时采集的机会。下面通过**错开时间 + 共用宿主机锁**处理；仅错开时间不能防止慢任务重叠。

### 10.2 让采集在每小时 05、35 分运行

```bash
cat > /etc/systemd/system/larrytoday-collect.timer.d/schedule.conf <<'EOF'
[Timer]
OnCalendar=
OnCalendar=*-*-* *:05,35:00
EOF
```

该规则使用系统时区，因此第 2 节已将服务器设为 Asia/Shanghai。出版 timer 沿用仓库的显式北京时间 07:00 配置。

### 10.3 让两个任务共用锁

```bash
cat > /etc/systemd/system/larrytoday-collect.service.d/runtime.conf <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/flock -w 3600 /run/lock/larrytoday-jobs.lock /usr/bin/docker compose exec -T web python -m scripts.collect
TimeoutStartSec=3h
EOF

cat > /etc/systemd/system/larrytoday-update.service.d/runtime.conf <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/flock -w 3600 /run/lock/larrytoday-jobs.lock /usr/bin/docker compose exec -T web python scripts/update_news.py --ai-limit 12
TimeoutStartSec=3h
EOF
```

此版本采用每日有限量 AI 编辑。尚未确认预算时，将出版配置末尾 `--ai-limit 12` 替换成 `--no-ai`；确认成本后可调整限额。不要把 API 密钥写进 unit 文件。

锁最多等待 1 小时；持续超时应排查慢任务，不要无限堆积。3 小时为包含排队在内的保护超时，不是预计运行时长。超时后仍需检查容器内是否残留任务，不能直接删除应用锁重跑。

### 10.4 验证后启用

```bash
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/larrytoday-collect.service /etc/systemd/system/larrytoday-update.service /etc/systemd/system/larrytoday-collect.timer /etc/systemd/system/larrytoday-update.timer
systemctl cat larrytoday-collect.service
systemctl cat larrytoday-update.service
systemctl cat larrytoday-collect.timer
systemctl start larrytoday-collect.service
journalctl -u larrytoday-collect.service -n 80 --no-pager
systemctl enable --now larrytoday-collect.timer larrytoday-update.timer
systemctl list-timers 'larrytoday-*' --all
```

确认下一次出版显示为北京时间次日 07:00，或与你当前时间相符的下一次触发时间。

`Persistent=true` 会在恢复运行后补触发错过的任务。如果当天刊期已由你手动发布，补触发可能因“刊期已存在、需要修订说明”退出；先核对日报，不要自动加修订说明重复出版。

查看运行情况：

```bash
journalctl -u larrytoday-update.service --since today --no-pager
journalctl -u larrytoday-collect.service --since today --no-pager
systemctl --failed
```

暂停自动任务：

```bash
systemctl stop larrytoday-collect.timer larrytoday-update.timer
```

这只停止后续触发，不中断已经运行的 service。永久取消开机启用可再执行 `systemctl disable` 对应 timer。手动运行始终采用第 9 节的 `flock` 命令，不绕过统一锁。

## 11. 备份与恢复

### 11.1 需要保存什么

| 内容 | 用途 |
|---|---|
| 完整 `/app/data` 数据卷 | 当前日报、历史刊期、修订、素材池、AI 缓存及采集状态 |
| 项目代码和 `config`、`srcs/sources.json` | 重建同一版本 |
| `.env` | 接口配置；单独加密保管 |
| `/etc/caddy/Caddyfile` | 域名和代理配置 |
| systemd unit 和 `.d` 目录 | 定时计划、运行限额、共享锁配置 |
| `/var/lib/caddy` | 证书和相关状态，迁移时按需保留并保护权限 |

同一台服务器上的备份不能防止整机故障或误删。至少下载一份到本机；后续可增加异地存储和自动备份。

### 11.2 备份数据卷

**服务器，管理员 shell：** 此命令使用与采集、出版相同的锁；前提是没有绕过锁启动的其他写入进程。

```bash
cd /opt/larrytoday
install -d -m 700 /opt/larrytoday-backups
BACKUP="/opt/larrytoday-backups/data-$(date +%Y%m%d-%H%M%S).tar.gz"
umask 077
if flock -w 3600 /run/lock/larrytoday-jobs.lock docker compose exec -T web tar -czf - -C /app/data . > "$BACKUP"; then
    tar -tzf "$BACKUP" > /dev/null && sha256sum "$BACKUP"
else
    echo "备份失败，不要将该文件用于恢复：$BACKUP"
fi
```

保留最近若干天和升级前的备份，按磁盘容量制定保留数量。不要把未验证成功的空文件当作备份。

若普通 SSH 用户无法读取 root 私有备份，可以将**要下载的单个备份**复制到该用户家目录，设置属主和 `600` 权限，然后用 `scp` 下载；不要把整个备份目录改成公开可读。下载并验证后清理临时副本。

### 11.3 恢复流程

最稳妥的恢复演练是在新实例或新的、明确隔离的部署中：

1. 恢复对应版本代码和服务器配置。
2. 创建 `.env`，构建并启动空部署，暂不启用定时器和公网入口。
3. 按第 6 节方式，将验证过的数据备份解压到**空数据卷**。
4. 设置 UID `10001` 的属主。
5. 检查当前日报、历史刊期、修订和来源状态。
6. 通过私下验收后切换域名或服务，再启用定时器。

不要直接将旧备份叠加进正在使用的卷：旧版和新版索引、修订文件可能混杂。恢复生产卷前先备份当前状态、停止定时触发，并确认所有写入任务结束。

## 12. 升级与回退

首次上线后，代码升级和每日出版是两件不同的事。日报更新不需要每次重建镜像。

### 12.1 升级

1. 本机完成修改和适用测试。
2. 暂停服务器定时器，等待正在运行的采集、出版结束。
3. 备份数据、配置和当前镜像。
4. 上传新代码包，保留线上 `.env`。
5. 构建启动，验证网页和接口。
6. 恢复定时器。

升级前保存当前镜像的示例：

```bash
cd /opt/larrytoday
IMAGE_ID=$(docker inspect --format '{{.Image}}' "$(docker compose ps -q web)")
ROLLBACK_TAG="larrytoday:before-$(date +%Y%m%d-%H%M%S)"
docker image tag "$IMAGE_ID" "$ROLLBACK_TAG"
echo "$ROLLBACK_TAG"
```

记录输出的镜像标签。上传并解压新代码后：

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
curl -fsS http://127.0.0.1:8000/health
```

`config` 和 `public` 都复制在镜像中，修改这些文件也需要重新构建。

### 12.2 回退

如果新版失败，可建立临时 `compose.rollback.yaml`，将镜像标签替换为刚记录的实际值：

```yaml
services:
  web:
    image: larrytoday:before-实际时间
```

```bash
docker compose -f compose.yaml -f compose.rollback.yaml up -d --no-build
```

这只回退镜像，不回退数据。涉及数据格式变化时，需先核对兼容性，再决定是否恢复升级前备份。回退期间暂停自动出版，处理完后恢复一致的代码、配置和部署命令，再重新启用任务。

若你原先使用了其他 Compose override 文件，回退时也需审查其中的实际设置，不能盲目忽略。不要删除仍需回退的旧镜像。

## 13. 常见问题

### 13.1 Docker 镜像下载失败

首先区分 Docker 软件安装失败与 `python:3.13-slim` 拉取失败。可使用账户实际支持的可信镜像服务；另一种方法是本机构建后传到服务器。

该备用方案要求 Windows 已安装并启动 Docker Desktop、使用 Linux containers，且目标服务器是 x86_64。

**Windows：**

```powershell
Set-Location D:\MyProject\LarryToday
docker build --platform linux/amd64 -t larrytoday:v1 .
docker save -o "$env:TEMP\larrytoday-image.tar" larrytoday:v1
scp "$env:TEMP\larrytoday-image.tar" "${Server}:/tmp/"
```

**服务器：**

```bash
docker load -i /tmp/larrytoday-image.tar
cd /opt/larrytoday
```

创建 `compose.override.yaml`：

```yaml
services:
  web:
    image: larrytoday:v1
```

```bash
docker compose up -d --no-build
```

之后每次更新都要重新构建、保存、传输并加载新镜像，再更新标签或重建容器。上传镜像仍不包含 `.env` 和 `data`。检查每条命令成功后再执行下一条，不要把旧镜像误认为新版本。

### 13.2 故障对照

| 现象 | 优先检查 | 处理 |
|---|---|---|
| SSH 连接超时 | 公网 IP、22 安全组、来源 IP、实例状态 | 用控制台连接核对规则 |
| `docker compose` 不存在 | 是否安装 Compose plugin | 按 Docker 官方方式补齐插件 |
| 容器无法启动 | `docker compose logs --tail=100 web` | 检查 `.env` 是否存在、端口占用和构建错误 |
| `/health` 正常但页面无新闻 | `/api/news`、卷挂载、是否迁移数据 | 恢复日报，或执行一次合适的出版 |
| 数据写入 Permission denied | `/app/data` 属主 | 按第 6 节设置 UID 10001 |
| Caddy 返回 502 | 本机 `curl /health`、容器状态 | 先修后端；代理应指向 `127.0.0.1:8000` |
| 证书申请失败 | A/AAAA、80/443、Caddy 日志、域名接入状态 | 修正后再重载，避免反复清空证书状态 |
| AI 401/403 | 凭证、权限、基础地址 | 在编辑器修复 `.env` 后重建容器 |
| AI 429、余额不足 | 供应商限额及实际调用量 | 降低编辑量或暂时使用 `--no-ai` |
| 部分源 HTTP 404 | 入口是否失效 | 更新该源配置并重新构建，不归咎于服务器整体 |
| DNS/TLS/timeout | 云端探测结果、系统时间、解析、目标可达性 | 区分网络故障，不关闭 TLS 校验 |
| 日报日期没变化 | timer、journal、截稿点、是否全部源失败 | 检查出版结果；旧刊保留可能是保护行为 |
| 提示该期已发布 | 当天是否手动出版或补触发 | 确需修订时提供说明，不删除历史 |
| 健康但页面仍显示旧样式 | 镜像是否重建、浏览器缓存 | 重建前端镜像并强制刷新 |
| 磁盘持续增加 | `df -h`、`docker system df`、备份数量 | 有计划清理过期镜像和备份，保留数据卷 |

### 13.3 出现“已有任务运行”或锁文件残留

应用还使用 `.update.lock`、`.collect.lock` 保护自身。遇到锁冲突时：

```bash
systemctl status larrytoday-update.service larrytoday-collect.service --no-pager
cd /opt/larrytoday
docker compose top web
journalctl -u larrytoday-update.service -u larrytoday-collect.service -n 100 --no-pager
```

先确认是否有任务真实运行。宿主机 `docker compose exec` 中断后，容器内任务可能仍在执行；不要只看 SSH 窗口是否关闭。

只有确认没有写入进程、已备份数据，且锁确实由异常退出残留时，才移除对应残留锁并重试。如果发布中断，先核对刊期与修订文件，避免制造不一致。

## 14. 首版验收清单与日常维护

### 14.1 私下部署验收

- [ ] 云端容器运行正常，`/health` 可访问。
- [ ] 已迁移数据，`/api/news` 含预期文章与刊期。
- [ ] SSH 隧道访问的是云端，桌面和手机布局正常。
- [ ] 来源探测在云端实际运行过，未把本地结果当作云端结果。
- [ ] 手动出版至少成功一次，且明确是无 AI 还是有 AI。
- [ ] 有完整备份，并验证压缩包可以读取。

### 14.2 公开上线验收

- [ ] 域名、主体、备案及实际新闻业务要求已确认并按要求完成。
- [ ] DNS 指向正确服务器，HTTPS 证书正常。
- [ ] 从另一网络可访问，无需本机开发服务。
- [ ] 8000 未开放到公网，SSH 仅允许所需来源。
- [ ] `.env` 不在公开目录、代码包或镜像内。
- [ ] 定时器已启用，采集与出版使用共同锁。
- [ ] 清楚每天 07:00 是开始出版时间，并已检查首次自动出版。
- [ ] 服务器重启后 Docker、Caddy、定时器恢复正常。
- [ ] 已设置服务器续费提醒、磁盘观察和 AI 预算提醒。

### 14.3 上线第一周

每天早晨检查一次网页刊期、晨读内容、来源覆盖和更新日志，记录出版耗时及 AI 费用。先确认连续数日稳定，再扩大 AI 处理量或继续接入信息源。

每次升级前备份；定期下载异地副本。服务器和 API 费用分开记录，不要把学生服务器价格当作网站全部运行成本。

首版完成标准是：**服务器持续可访问、现有日报正确呈现、更新流程可控、数据能恢复**。X 接入、其余来源和进一步的内容优化可以在此基础上继续迭代。
