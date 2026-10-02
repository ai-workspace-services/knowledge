import os
import subprocess

OUTPUT_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge/assets/images"
HTML_DIR = "/tmp/canvases_html"
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CANVAS_DATA = [
    {
        "index": "01",
        "title": "个人 AI 聚合网关，究竟该怎么选型？",
        "subtitle": "GitOps 负责声明，APISIX 负责流控，单模型多账号负责收敛",
        "tag": "AI 聚合网关 · 全能架构实战",
        "series_badge": "工程决策画布 系列 01 / 05",
        "footer_series": "系列 01 / 05 · AI Gateway / APISIX / Caddy / Home-Lab",
        "steps": [
            {
                "num": 1,
                "name": "Client Matrix",
                "cn": "终端矩阵",
                "card_title": "痛点：多账号割裂",
                "items": ["Codex / Claude / Gemini CLI", "Cursor / VS Code / Antigravity", "协议 Header 命名互不兼容"]
            },
            {
                "num": 2,
                "name": "Ingress Edge",
                "cn": "边缘接入",
                "card_title": "边缘隔离防直连",
                "items": ["Caddy 自动 HTTPS 证书", "TLS 终结在 443 端口", "仅内网回环转发至网关"]
            },
            {
                "num": 3,
                "name": "Core Gateway",
                "cn": "核心网关",
                "card_title": "统一流控与鉴权",
                "items": ["APISIX Standalone 模式", "读取本地 apisix.yaml", "Real-IP 信任与租户 ACL"]
            },
            {
                "num": 4,
                "name": "Model Router",
                "cn": "模型聚合",
                "card_title": "多渠道调度中枢",
                "items": ["New API 统一模型别名", "CPA 订阅渠道探活轮询", "LiteLLM 承载商用官方 Key"]
            },
            {
                "num": 5,
                "name": "Accounts",
                "cn": "账号上游",
                "card_title": "单账号矩阵隔离",
                "items": ["ChatGPT Plus / Claude Team", "0700 鉴权隔离防串号", "Vault 动态注入内存 tmpfs"]
            }
        ],
        "flow_cards": [
            {"icon": "💻", "title": "Dev Clients", "desc": "CLI / IDE / SDK 统一接入"},
            {"icon": "🔒", "title": "Caddy Edge", "desc": "TLS 终止 · 域名绑定 :443"},
            {"icon": "⚡", "title": "APISIX Standalone", "desc": "纯文件声明 · 鉴权 / ACL / 限流", "primary": True},
            {"icon": "🔀", "title": "New API & LiteLLM", "desc": "模型目录聚合 · 官方 API 兜底"},
            {"icon": "🤖", "title": "CPA Matrix & APIs", "desc": "多订阅账号池 · 官方 Provider"}
        ],
        "flow_arrows": [
            ("[请求] HTTPS / JSON", "[响应] SSE 流式 / JSON"),
            ("[回环转发] 127.0.0.1", "[内网安全响应]"),
            ("[路由分发] /v1/chat", "[上游聚合流式]"),
            ("[协议转换] 会话调度", "[大模型推理响应]")
        ],
        "roles": [
            ("开发者", "发起推理请求，不持有底层敏感凭据", "不可信区", "trust-no"),
            ("Caddy", "终结外网 TLS，向 APISIX 传递 Real-IP", "边缘层", "trust-edge"),
            ("APISIX", "校验网关 Token，执行流控与分流", "核心安全区", "trust-core"),
            ("CPA/Vault", "单账号沙箱，内存 tmpfs 密钥动态挂载", "隔离受信区", "trust-core")
        ],
        "decision": {
            "title": "选 Kong 还是选 APISIX？",
            "rec_title": "APISIX Standalone (推荐)",
            "rec_desc": "• 0 外部数据库与 etcd 强依赖<br>• 本地 YAML GitOps 纯声明式对账<br>• 内置开源 ai-proxy-multi，免商业授权",
            "alt_title": "Kong Traditional",
            "alt_desc": "• 需维护 PostgreSQL 与控制面迁移<br>• 高级 AI 代理插件需商业 License<br>• Home-Lab 环境额外内存与运维负担"
        },
        "warning": {
            "title": "不要将 LiteLLM 作为 CPA 的前置代理！",
            "items": [
                "引发双重重试风暴与网络抖动放大",
                "Token 用量与费用核算发生重复统计",
                "模糊故障隔离边界，排障链路显著拉长"
            ]
        },
        "bottom_title": "选型准则贯穿全栈",
        "chips": ["0 外部数据库依赖", "GitOps 纯文件对账", "单 Token 统一解耦", "开源多模型无授权陷阱"]
    },
    {
        "index": "02",
        "title": "一次大模型请求，流量在网关内部如何流转？",
        "subtitle": "Caddy 负责 TLS 边缘，APISIX 负责流控，New API 负责目录收敛",
        "tag": "AI 聚合网关 · 全能架构实战",
        "series_badge": "工程决策画布 系列 02 / 05",
        "footer_series": "系列 02 / 05 · Caddy / APISIX / TLS / Single-Token",
        "steps": [
            {
                "num": 1,
                "name": "Dev Client",
                "cn": "客户端发起",
                "card_title": "统一标准化调用",
                "items": ["单一 Base URL 访问", "单一网关 sk-xxx 凭据", "请求体遵循 OpenAI 规范"]
            },
            {
                "num": 2,
                "name": "Caddy Edge",
                "cn": "边缘代理",
                "card_title": "TLS 证书与反代",
                "items": ["监听 443 自动 ACME", "捕获真实客户端 IP", "仅回环转发至 127.0.0.1:9080"]
            },
            {
                "num": 3,
                "name": "APISIX Core",
                "cn": "流控中枢",
                "card_title": "安全鉴权与限流",
                "items": ["校验并隐藏 apikey 请求头", "Real-IP 信任与白名单", "Consumer ACL 与局部限流"]
            },
            {
                "num": 4,
                "name": "Dispatch",
                "cn": "平行分流",
                "card_title": "平级上游无嵌套",
                "items": ["/v1/chat -> New API (:3000)", "/litellm/* -> LiteLLM (:4000)", "禁止上游间二次代理"]
            },
            {
                "num": 5,
                "name": "Backend",
                "cn": "推理落地",
                "card_title": "账号与商业服务",
                "items": ["CPA 会话转换 SSE 流", "官方 API 计量计费", "长连接稳定不发生中断"]
            }
        ],
        "flow_cards": [
            {"icon": "💻", "title": "Dev Client", "desc": "发起单一 HTTPS 调用"},
            {"icon": "🛡️", "title": "Caddy (:443)", "desc": "TLS 终结 · 传递 Real-IP"},
            {"icon": "⚡", "title": "APISIX (:9080)", "desc": "校验 apikey · 租户 ACL · 限流", "primary": True},
            {"icon": "🔀", "title": "New API / LiteLLM", "desc": "平级上游路由 · 模型别名映射"},
            {"icon": "🤖", "title": "CPA Matrix / APIs", "desc": "执行推理 · 返回流式数据"}
        ],
        "flow_arrows": [
            ("[请求] POST /v1/chat", "[响应] SSE event-stream"),
            ("[反代] Loopback:9080", "[响应透传] 保持长连接"),
            ("[剥离凭据] 转发上游", "[捕获响应] 审计用量"),
            ("[真实调用] 订阅/官方", "[流式回传] 逐字打字机")
        ],
        "roles": [
            ("客户端", "仅感知单一内网域名与网关 Token", "不可信区", "trust-no"),
            ("Caddy", "公网唯一暴漏面，负责 TLS 与真实 IP", "边缘层", "trust-edge"),
            ("APISIX", "内网核心控制面，执行 ACL 与凭据解耦", "核心安全区", "trust-core"),
            ("上游后端", "仅监听 127.0.0.1，受控访问", "受控区", "trust-core")
        ],
        "decision": {
            "title": "单 Token 还是双 Token 鉴权？",
            "rec_title": "单 Token 网关解耦 (推荐)",
            "rec_desc": "• 客户端只需配置 1 个网关凭据<br>• APISIX 按 Consumer 注入上游业务 Key<br>• 完美适配无法自定义 Header 的各类 IDE",
            "alt_title": "双 Token 显式透传",
            "alt_desc": "• 客户端同时传 apikey 与 Authorization<br>• 内部多层拓扑强暴露给终端<br>• 各种 CLI / IDE 插件适配极繁琐"
        },
        "warning": {
            "title": "严禁将 APISIX 与后端端口直接暴露到公网！",
            "items": [
                "APISIX、New API、LiteLLM 全部绑定 127.0.0.1",
                "公网仅暴露 Caddy 443 端口并严格做 IP 白名单",
                "绕过 Caddy 访问将引发明文泄露与鉴权穿透隐患"
            ]
        },
        "bottom_title": "全链路安全契约",
        "chips": ["边缘 TLS 终结", "仅回环受信转发", "单 Token 统一解耦", "上游平行互斥无嵌套"]
    },
    {
        "index": "03",
        "title": "多账号 OAuth 与 API Key，如何做到绝对零泄露？",
        "subtitle": "CPA 负责单账号进程隔离，Vault 负责密钥注入，内存 tmpfs 负责生命周期",
        "tag": "AI 聚合网关 · 全能架构实战",
        "series_badge": "工程决策画布 系列 03 / 05",
        "footer_series": "系列 03 / 05 · CPA Matrix / Vault / tmpfs / Zero-Leakage",
        "steps": [
            {
                "num": 1,
                "name": "Identity Provider",
                "cn": "凭据源头",
                "card_title": "多源账号体系",
                "items": ["ChatGPT Plus / Pro 订阅", "Claude Team / Google 账号", "商用官方 API Key 资产"]
            },
            {
                "num": 2,
                "name": "CPA Sandbox",
                "cn": "实例沙箱",
                "card_title": "单账号单实例",
                "items": ["每实例独立 Linux 系统用户", "独立监听端口与 systemd", "独立 New API 专属渠道"]
            },
            {
                "num": 3,
                "name": "Auth Storage",
                "cn": "鉴权存储",
                "card_title": "0700 鉴权防护",
                "items": ["/var/lib/.../cpa/<id>/auth/", "严格设置 chmod 0700", "严禁跨用户越权读取"]
            },
            {
                "num": 4,
                "name": "Vault Engine",
                "cn": "密钥管理",
                "card_title": "集中秘密托管",
                "items": ["Vault KV 集中加密托管", "AppRole 受控身份认证", "编排动态下发数据库 DSN"]
            },
            {
                "num": 5,
                "name": "tmpfs RAM",
                "cn": "内存注入",
                "card_title": "生命周期闭环",
                "items": ["敏感凭据写入内存 tmpfs", "进程启动读取，磁盘不留痕", "机器断电或服务销毁即消失"]
            }
        ],
        "flow_cards": [
            {"icon": "👥", "title": "Accounts Pool", "desc": "多订阅账号与官方 Key"},
            {"icon": "🛡️", "title": "CPA Instance Matrix", "desc": "独立 Unix 用户 · 独立进程端口"},
            {"icon": "📁", "title": "0700 Auth Dirs", "desc": "本地加密鉴权目录 · 严防越权", "primary": True},
            {"icon": "🗝️", "title": "Vault Server", "desc": "KV 引擎 · AppRole 凭据注入"},
            {"icon": "⚡", "title": "tmpfs RAM Mount", "desc": "内存无痕注入 · 零磁盘持久化"}
        ],
        "flow_arrows": [
            ("[独立授权] OAuth 登录", "[会话保持] 独立 Refresh"),
            ("[物理隔离] 专属端口", "[进程安全隔离]"),
            ("[启动挂载] 动态注密", "[密钥读取] 内存执行"),
            ("[服务退出] 自动清空", "[无痕销毁] 零数据残留")
        ],
        "roles": [
            ("CPA 实例", "独立承载单一订阅账号，维持会话", "沙箱层", "trust-core"),
            ("宿主目录", "存储本地 OAuth 材料，权限 0700", "防护层", "trust-core"),
            ("Vault", "统一托管数据库密码与全局 API Key", "保险库", "trust-core"),
            ("Git/镜像", "严禁存放任何真实凭据明文", "非凭据区", "trust-no")
        ],
        "decision": {
            "title": "OAuth 认证会话文件存放在哪里？",
            "rec_title": "节点本地独立 0700 目录 (推荐)",
            "rec_desc": "• 每实例分配独立系统用户与隔离目录<br>• 本地文件锁严防并发覆写与串号<br>• 故障影响半径锁定在单实例内部",
            "alt_title": "集中存入数据库或 Git 仓库",
            "alt_desc": "• 误提交或备份泄露导致全部账号瘫痪<br>• 数据库被拖库即造成灾难级暴露<br>• 破坏单账号隔离语义，风险极高"
        },
        "warning": {
            "title": "OAuth 会话材料严禁进入持久化版本库！",
            "items": [
                "严禁将 OAuth 凭据提交至 Git 仓库或打入 Docker 镜像",
                "严禁将敏感凭据输出到网关日志或应用审计记录中",
                "严禁在多实例间共用或软链接同一份 auth session 文件"
            ]
        },
        "bottom_title": "凭据安全准则",
        "chips": ["单账号单实例物理隔离", "0700 鉴权防护", "Vault 内存动态注入", "严禁凭据入库入镜像"]
    },
    {
        "index": "04",
        "title": "终端 CLI 与 IDE 插件，如何实现零心智一键接入？",
        "subtitle": "统一环境基线免改动，声明式 GitOps 自动化编排，秒级热重载业务不断流",
        "tag": "AI 聚合网关 · 全能架构实战",
        "series_badge": "工程决策画布 系列 04 / 05",
        "footer_series": "系列 04 / 05 · Claude Code / Cursor / GitOps / Ansible",
        "steps": [
            {
                "num": 1,
                "name": "Dev Workstations",
                "cn": "开发工具链",
                "card_title": "多端异构应用",
                "items": ["Claude Code / Codex CLI", "Cursor / VS Code / Android Studio", "Python / Node.js 官方 SDK"]
            },
            {
                "num": 2,
                "name": "Unified Baseline",
                "cn": "配置基线",
                "card_title": "单一契约规范",
                "items": ["统一 Base URL: ai-internal.*** ", "统一网关凭据: sk-gateway-***", "标准别名: gpt-5.6 / sonnet-5"]
            },
            {
                "num": 3,
                "name": "GitOps Repo",
                "cn": "声明式仓库",
                "card_title": "配置即代码",
                "items": ["gateway-config.yaml", "声明 Consumers 与 Routes 规则", "明确团队与个人配额限流"]
            },
            {
                "num": 4,
                "name": "Ansible Pipeline",
                "cn": "对账编排",
                "card_title": "自动化校验交付",
                "items": ["模板渲染生成 apisix.yaml", "对账推流至网关生产节点", "配置语法与合法性前置检查"]
            },
            {
                "num": 5,
                "name": "Hot-Reload",
                "cn": "平滑热加载",
                "card_title": "零停机不断流",
                "items": ["APISIX 监听文件变动秒级热载", "长文本推理保持活跃 TCP 状态", "无瞬断、无重连、业务无感知"]
            }
        ],
        "flow_cards": [
            {"icon": "💻", "title": "Developer IDEs", "desc": "配置单 Base URL + 单 Token"},
            {"icon": "📄", "title": "GitOps Declarative", "desc": "Git 提交 gateway-config.yaml"},
            {"icon": "⚙️", "title": "Ansible Pipeline", "desc": "模板渲染 · 自动对账推流", "primary": True},
            {"icon": "⚡", "title": "APISIX Reload", "desc": "秒级加载 apisix.yaml · 零停机"},
            {"icon": "🌐", "title": "Live Routing", "desc": "平滑接管全量大模型流量"}
        ],
        "flow_arrows": [
            ("[代码变更] Git Push", "[版本留存] 变更可追溯"),
            ("[CI 对账] 模板渲染", "[语法校验] 校验合规"),
            ("[下发文件] apisix.yaml", "[热重载生效] 秒级对齐"),
            ("[请求分发] 实时路由", "[业务不断流] 稳定响应")
        ],
        "roles": [
            ("开发者", "按照统一规范配置 IDE 环境变量", "接入层", "trust-no"),
            ("Git 仓库", "存储租户与路由声明式配置，权威事实源", "状态源", "trust-core"),
            ("Ansible", "负责对账与渲染，安全注入私密变量", "流水线", "trust-core"),
            ("网关节点", "热重载本地 apisix.yaml，提供高可用代理", "运行层", "trust-core")
        ],
        "decision": {
            "title": "手工登机修改 vs GitOps 自动化？",
            "rec_title": "GitOps 声明式对账 (推荐)",
            "rec_desc": "• 配置即代码，版本全可追溯一键回滚<br>• Ansible 保证多节点状态严格一致<br>• 语法校验通过才推流，杜绝线上手抖",
            "alt_title": "手工 SSH 登机修改",
            "alt_desc": "• 容易配置漂移与破坏文件权限<br>• 多节点同步极繁琐，排障无据可查<br>• 缺少变更审计，误操作直接断流"
        },
        "warning": {
            "title": "警惕客户端激进重试导致的上游雪崩！",
            "items": [
                "客户端必须配置合理的指数退避重试 (Exponential Backoff)",
                "严禁客户端与网关双层叠加重试，避免瞬间耗尽上游配额",
                "对长耗时非幂等生成接口设定合理的单次调用超时阈值"
            ]
        },
        "bottom_title": "落地接入规范",
        "chips": ["单一 Base URL 契约", "声明式 GitOps 编排", "秒级平滑热加载", "智能指数退避重试"]
    },
    {
        "index": "05",
        "title": "大模型推理卡死报错？全链路排障与运维实战",
        "subtitle": "SSE 解决流式截断，主动探活解决 429 熔断，监控指标护航 Home-Lab",
        "tag": "AI 聚合网关 · 全能架构实战",
        "series_badge": "工程决策画布 系列 05 / 05",
        "footer_series": "系列 05 / 05 · SSE / OpenResty / Prometheus / Home-Lab",
        "steps": [
            {
                "num": 1,
                "name": "Traffic Anomaly",
                "cn": "异常流量",
                "card_title": "典型故障捕获",
                "items": ["SSE 流式输出中途卡死截断", "上游触发 429 Too Many Requests", "网关返回 504 Gateway Timeout"]
            },
            {
                "num": 2,
                "name": "Buffering Tune",
                "cn": "网关调优",
                "card_title": "长连接防缓冲",
                "items": ["显式关闭 proxy_buffering off", "调大 proxy_read_timeout 300s", "优化 TCP keepalive 保活长连接"]
            },
            {
                "num": 3,
                "name": "Failover Hub",
                "cn": "熔断探活",
                "card_title": "智能故障自愈",
                "items": ["New API 实时探活渠道健康度", "触发 429 毫秒级下线并热切备用", "多账号全跪时平滑降级官方 API"]
            },
            {
                "num": 4,
                "name": "Telemetry Pipeline",
                "cn": "监控链路",
                "card_title": "全链路可观测",
                "items": ["APISIX Prometheus 插件上报指标", "VictoriaLogs 集中聚合运行日志", "Grafana Dashboard 展示延迟吞吐"]
            },
            {
                "num": 5,
                "name": "Home-Lab Hygiene",
                "cn": "巡检基线",
                "card_title": "日常运维护航",
                "items": ["监控 tmpfs 内存水位防溢出", "定期轮转清理 Docker 日志", "固化 OpenResty 与 Lua 库版本"]
            }
        ],
        "flow_cards": [
            {"icon": "⚠️", "title": "Client Anomaly", "desc": "捕获 429 / 504 / 流式截断"},
            {"icon": "⚡", "title": "APISIX Tuning", "desc": "关闭缓冲 · 延长超时 300s", "primary": True},
            {"icon": "🔄", "title": "Failover Engine", "desc": "毫秒级切换备用 CPA 账号"},
            {"icon": "📊", "title": "Grafana / Metrics", "desc": "延迟分位值 · 错误率实时告警"},
            {"icon": "🛠️", "title": "Home-Lab Clean", "desc": "日志轮转 · tmpfs 内存基线"}
        ],
        "flow_arrows": [
            ("[异常捕获] 错误拦截", "[诊断分析] 定位根因"),
            ("[策略调优] 禁用缓冲", "[连接保活] SSE 顺畅"),
            ("[故障转移] 毫秒级降级", "[流量恢复] 业务无感"),
            ("[指标暴露] Prometheus", "[全景看板] 实时大盘")
        ],
        "roles": [
            ("流式连接", "长文本推理 SSE 协议，要求禁用代理缓冲", "网络层", "trust-edge"),
            ("健康探活", "动态测量各 CPA 延迟与错误率，主动剔除", "调度层", "trust-core"),
            ("可观测性", "记录全量 access.log 与指标数据，追踪瓶颈", "度量层", "trust-core"),
            ("宿主运维", "确保 Docker 与系统资源健康，防止磁盘击穿", "基石层", "trust-core")
        ],
        "decision": {
            "title": "流式长文本推理卡死中途断开怎么破？",
            "rec_title": "禁用代理缓冲 + 调大超时 (推荐)",
            "rec_desc": "• Caddy 与 APISIX 显式关闭 proxy_buffering<br>• 调大 read_timeout ≥ 300s 开启 Keepalive<br>• 客户端采用标准 EventSource 流式解析",
            "alt_title": "盲目增加网关 Worker 与并发数",
            "alt_desc": "• 无法解决缓冲区满溢造成的流式截断<br>• 反而加剧系统内存与 CPU 资源争抢<br>• 忽略长连接超时根因，无法彻底根治"
        },
        "warning": {
            "title": "严禁忽略 APISIX Standalone 内存字典与 Worker 限制！",
            "items": [
                "必须严格固化 OpenResty 运行时版本（如 3.16.0 源码与 Lua 库）",
                "确保 systemd unit 具有足够的文件描述符限制 (LimitNOFILE=65535)",
                "生产环境日常巡检需定时检查共享字典 (shm) 使用率与日志大小"
            ]
        },
        "bottom_title": "运维巡检铁律",
        "chips": ["流式禁用代理缓冲", "超时放宽至 300s", "429 自动故障转移", "定时内存与日志巡检"]
    }
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  width: 900px;
  height: 1350px;
  background-color: #FAF7F2;
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Heiti SC", sans-serif;
  color: #18181B;
  padding: 32px 36px;
  position: relative;
}

/* Header */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.header-tag {
  display: flex;
  align-items: center;
  font-size: 15px;
  font-weight: 700;
  color: #1E293B;
  letter-spacing: 0.5px;
}
.header-tag::before {
  content: "";
  display: inline-block;
  width: 5px;
  height: 18px;
  background-color: #1D4ED8;
  margin-right: 8px;
  border-radius: 2px;
}
.header-badge {
  display: flex;
  align-items: center;
  border: 1.5px solid #1D4ED8;
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 700;
  color: #1D4ED8;
  background: #FFFFFF;
}
.header-badge svg { margin-right: 6px; }

.main-title {
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -0.5px;
  color: #0F172A;
  margin-bottom: 8px;
}
.sub-title {
  display: flex;
  align-items: center;
  font-size: 14.5px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 22px;
}
.sub-title svg {
  margin-right: 8px;
  color: #2563EB;
  flex-shrink: 0;
}

/* Columns Layout */
.canvas-body {
  display: grid;
  grid-template-columns: 215px 235px 1fr;
  gap: 16px;
  height: 1040px;
}

/* Left Column */
.left-col {
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
}
.left-col::before {
  content: "";
  position: absolute;
  top: 15px;
  bottom: 30px;
  left: 12px;
  width: 2px;
  background: #CBD5E1;
  z-index: 1;
}

.step-item {
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 2;
}
.step-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}
.step-num {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
  margin-right: 8px;
  flex-shrink: 0;
  border: 2px solid #FAF7F2;
}
.num-1 { background-color: #1D4ED8; }
.num-2 { background-color: #DC2626; }
.num-3 { background-color: #B45309; }
.num-4 { background-color: #15803D; }
.num-5 { background-color: #7C3AED; }

.step-title {
  font-size: 14px;
  font-weight: 800;
  color: #0F172A;
}
.step-title span {
  font-size: 12px;
  font-weight: 500;
  color: #64748B;
  display: block;
}
.step-card {
  border: 1px dashed #CBD5E1;
  border-radius: 6px;
  padding: 7px 9px;
  background: rgba(255, 255, 255, 0.7);
  font-size: 11px;
  line-height: 1.45;
  color: #475569;
  margin-left: 12px;
}
.step-card strong {
  color: #991B1B;
  display: block;
  margin-bottom: 2px;
  font-size: 11px;
}
.step-card ul {
  padding-left: 12px;
  margin: 0;
}

/* Middle Flow Column */
.mid-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.flow-card {
  width: 100%;
  background: #FFFFFF;
  border: 1.5px solid #CBD5E1;
  border-radius: 10px;
  padding: 11px 8px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}
.flow-card.primary {
  border-color: #3B82F6;
  background: #F8FAFC;
}
.flow-card-icon {
  font-size: 20px;
  margin-bottom: 2px;
}
.flow-card-title {
  font-size: 13.5px;
  font-weight: 800;
  color: #0F172A;
}
.flow-card-desc {
  font-size: 10.5px;
  color: #64748B;
  margin-top: 1px;
}

.arrow-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 90%;
  padding: 0 6px;
  font-size: 10px;
  font-weight: 700;
  color: #1D4ED8;
}
.arrow-line-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 24px;
}
.arrow-down-double {
  width: 2px;
  height: 22px;
  background: #2563EB;
  position: relative;
}
.arrow-down-double::after {
  content: "";
  position: absolute;
  bottom: -3px;
  left: -3px;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #2563EB;
}

/* Right Column */
.right-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Role / Trust Table */
.role-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #E2E8F0;
}
.role-table th {
  background: #F1F5F9;
  padding: 6px 8px;
  font-weight: 700;
  color: #334155;
  text-align: left;
}
.role-table td {
  padding: 6px 8px;
  border-top: 1px solid #E2E8F0;
  vertical-align: top;
  color: #475569;
  line-height: 1.4;
}
.trust-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 10px;
}
.trust-no { background: #FEE2E2; color: #991B1B; }
.trust-edge { background: #FEF3C7; color: #92400E; }
.trust-core { background: #DCFCE7; color: #166534; }

/* Decision Box */
.decision-card {
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid #2563EB;
  background: #FFFFFF;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.08);
}
.decision-header {
  background: #1D4ED8;
  color: white;
  padding: 7px 12px;
  font-size: 13.5px;
  font-weight: 800;
  text-align: center;
}
.decision-body {
  padding: 10px 12px;
}
.option-item {
  margin-bottom: 8px;
}
.option-item:last-child { margin-bottom: 0; }
.option-title {
  display: flex;
  align-items: center;
  font-size: 12.5px;
  font-weight: 800;
  margin-bottom: 3px;
}
.option-title.recommended {
  color: #15803D;
}
.option-title.alternative {
  color: #92400E;
}
.option-title svg {
  margin-right: 5px;
}
.option-desc {
  font-size: 10.5px;
  color: #475569;
  padding-left: 18px;
  line-height: 1.45;
}
.or-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 4px 0;
}
.or-badge {
  background: #1D4ED8;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 9px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Warning Card */
.warning-card {
  background: #FFF5F5;
  border: 1.5px solid #F87171;
  border-radius: 8px;
  padding: 9px 12px;
}
.warning-header {
  display: flex;
  align-items: center;
  color: #DC2626;
  font-size: 12.5px;
  font-weight: 800;
  margin-bottom: 5px;
}
.warning-header svg { margin-right: 6px; flex-shrink: 0; }
.warning-card ul {
  padding-left: 16px;
  font-size: 10.5px;
  color: #7F1D1D;
  line-height: 1.45;
  margin: 0;
}

/* Bottom Bar */
.bottom-bar {
  position: absolute;
  bottom: 54px;
  left: 36px;
  right: 36px;
  background: #FFFFFF;
  border: 1.5px solid #CBD5E1;
  border-radius: 8px;
  padding: 8px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.bottom-title {
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: 800;
  color: #1E293B;
  flex-shrink: 0;
}
.bottom-title svg { margin-right: 6px; color: #2563EB; }
.bottom-chips {
  display: flex;
  gap: 8px;
  flex-grow: 1;
}
.bottom-chip {
  background: #F1F5F9;
  border: 1px solid #E2E8F0;
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 11px;
  color: #334155;
  font-weight: 600;
}

/* Footer */
.footer-bar {
  position: absolute;
  bottom: 22px;
  left: 36px;
  right: 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: #64748B;
  border-top: 1px dashed #CBD5E1;
  padding-top: 10px;
}
.footer-watermark {
  color: #1E293B;
  font-weight: 700;
}
</style>
</head>
<body>

<div class="header-top">
  <div class="header-tag">{{TAG}}</div>
  <div class="header-badge">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
    {{SERIES_BADGE}}
  </div>
</div>

<div class="main-title">{{MAIN_TITLE}}</div>
<div class="sub-title">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
  {{SUB_TITLE}}
</div>

<div class="canvas-body">
  <!-- Left Column -->
  <div class="left-col">
    {{STEPS_HTML}}
  </div>

  <!-- Middle Column -->
  <div class="mid-col">
    {{FLOW_HTML}}
  </div>

  <!-- Right Column -->
  <div class="right-col">
    <table class="role-table">
      <tr><th>实体</th><th>核心职责</th><th>信任边界</th></tr>
      {{ROLES_HTML}}
    </table>

    <div class="decision-card">
      <div class="decision-header">{{DECISION_TITLE}}</div>
      <div class="decision-body">
        <div class="option-item">
          <div class="option-title recommended">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
            {{DECISION_REC_TITLE}}
          </div>
          <div class="option-desc">{{DECISION_REC_DESC}}</div>
        </div>

        <div class="or-divider"><div class="or-badge">或</div></div>

        <div class="option-item">
          <div class="option-title alternative">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="8" y1="12" x2="16" y2="12"></line></svg>
            {{DECISION_ALT_TITLE}}
          </div>
          <div class="option-desc">{{DECISION_ALT_DESC}}</div>
        </div>
      </div>
    </div>

    <div class="warning-card">
      <div class="warning-header">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
        {{WARNING_TITLE}}
      </div>
      <ul>
        {{WARNING_ITEMS_HTML}}
      </ul>
    </div>
  </div>
</div>

<div class="bottom-bar">
  <div class="bottom-title">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>
    {{BOTTOM_TITLE}}
  </div>
  <div class="bottom-chips">
    {{CHIPS_HTML}}
  </div>
</div>

<div class="footer-bar">
  <div>{{FOOTER_SERIES}}</div>
  <div class="footer-watermark">公众号：行者深蓝</div>
</div>

</body>
</html>
"""

def render_part(data):
    # Steps HTML
    steps_html = ""
    for s in data["steps"]:
        items_li = "".join([f"<li>{item}</li>" for item in s["items"]])
        steps_html += f"""
        <div class="step-item">
          <div class="step-header">
            <div class="step-num num-{s['num']}">{s['num']}</div>
            <div class="step-title">{s['name']}<span>({s['cn']})</span></div>
          </div>
          <div class="step-card">
            <strong>{s['card_title']}</strong>
            <ul>{items_li}</ul>
          </div>
        </div>
        """
        
    # Flow HTML
    flow_html = ""
    cards = data["flow_cards"]
    arrows = data["flow_arrows"]
    for i, c in enumerate(cards):
        primary_cls = " primary" if c.get("primary") else ""
        flow_html += f"""
        <div class="flow-card{primary_cls}">
          <div class="flow-card-icon">{c['icon']}</div>
          <div class="flow-card-title">{c['title']}</div>
          <div class="flow-card-desc">{c['desc']}</div>
        </div>
        """
        if i < len(arrows):
            req_label, resp_label = arrows[i]
            flow_html += f"""
            <div class="arrow-box">
              <span>{req_label}</span>
              <div class="arrow-line-container"><div class="arrow-down-double"></div></div>
              <span>{resp_label}</span>
            </div>
            """
            
    # Roles HTML
    roles_html = ""
    for entity, duty, zone, z_cls in data["roles"]:
        roles_html += f"""
        <tr>
          <td><strong>{entity}</strong></td>
          <td>{duty}</td>
          <td><span class="trust-badge {z_cls}">{zone}</span></td>
        </tr>
        """
        
    # Warning items HTML
    warning_items = "".join([f"<li>{item}</li>" for item in data["warning"]["items"]])
    
    # Chips HTML
    chips_html = "".join([f'<div class="bottom-chip">{c}</div>' for c in data["chips"]])
    
    content = HTML_TEMPLATE
    content = content.replace("{{TAG}}", data["tag"])
    content = content.replace("{{SERIES_BADGE}}", data["series_badge"])
    content = content.replace("{{MAIN_TITLE}}", data["title"])
    content = content.replace("{{SUB_TITLE}}", data["subtitle"])
    content = content.replace("{{FOOTER_SERIES}}", data["footer_series"])
    content = content.replace("{{STEPS_HTML}}", steps_html)
    content = content.replace("{{FLOW_HTML}}", flow_html)
    content = content.replace("{{ROLES_HTML}}", roles_html)
    content = content.replace("{{DECISION_TITLE}}", data["decision"]["title"])
    content = content.replace("{{DECISION_REC_TITLE}}", data["decision"]["rec_title"])
    content = content.replace("{{DECISION_REC_DESC}}", data["decision"]["rec_desc"])
    content = content.replace("{{DECISION_ALT_TITLE}}", data["decision"]["alt_title"])
    content = content.replace("{{DECISION_ALT_DESC}}", data["decision"]["alt_desc"])
    content = content.replace("{{WARNING_TITLE}}", data["warning"]["title"])
    content = content.replace("{{WARNING_ITEMS_HTML}}", warning_items)
    content = content.replace("{{BOTTOM_TITLE}}", data["bottom_title"])
    content = content.replace("{{CHIPS_HTML}}", chips_html)
    
    html_file = os.path.join(HTML_DIR, f"canvas_{data['index']}.html")
    with open(html_file, "w") as f:
        f.write(content)
        
    out_png = os.path.join(OUTPUT_DIR, f"gateway-canvas-{data['index']}-selection.png" if data['index'] == "01" else
                                       f"gateway-canvas-{data['index']}-architecture.png" if data['index'] == "02" else
                                       f"gateway-canvas-{data['index']}-credentials.png" if data['index'] == "03" else
                                       f"gateway-canvas-{data['index']}-integration.png" if data['index'] == "04" else
                                       f"gateway-canvas-{data['index']}-troubleshooting.png")
    
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--force-device-scale-factor=2",
        f"--screenshot={out_png}",
        "--window-size=900,1350",
        html_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated Canvas [{data['index']}]: {out_png}")

def main():
    for d in CANVAS_DATA:
        render_part(d)
    print("\nAll 5 Engineering Decision Canvases generated successfully!")

if __name__ == "__main__":
    main()
