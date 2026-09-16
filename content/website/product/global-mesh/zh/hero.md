---
hero:
  badge: '全球云中立基础设施架构中枢'
  title: 'Global Mesh'
  subtitle: 'Cloud-Neutral Global Service Mesh · 5 大核心 VPS 异构算力 · 48+ 全球 PoP · 0 端口公网入站暴露 · 成本节约 90%+'
  cta:
    label: '进入产品控制台'
    href: 'https://console.onwalk.net/products/global-mesh'
  downloadUrl: 'https://console.onwalk.net/products/global-mesh'
  supportedPlatforms: 'macOS · Windows · Linux · iOS · Android · Web WASM'
wizard:
  title: '3 步接入 Global Mesh 云中立服务网格'
  description: '快速将异构计算节点、Serverless BFF 与边缘存储融入零信任自治网格。'
  steps:
    - step: 1
      title: '生成节点密钥与网络配置'
      description: '在控制台生成受信 WireGuard 覆盖网密钥，分配专用内网 IP (10.240.0.0/16)。'
      link: 'https://console.onwalk.net/products/global-mesh'
      platforms: 'Linux · Docker · macOS · Windows · ARM64'
    - step: 2
      title: '配置边缘 Ingress 与 0 端口安全策略'
      description: '挂载 Cloudflare Anycast WAF 与 R2 零出网费存储，关闭宿主机所有非 WG 公网入站端口。'
    - step: 3
      title: '启用双轨数据与全栈无盲区遥测'
      description: '接入 Supabase PG (RLS) 与 VictoriaMetrics APM，启动跨云独立看门狗哨兵探针。'
showcases:
  - title: '异构算力池与 177 国高精内联矢量地图'
    description: '集成 Vultr、Linode、Hetzner、Contabo、UCloud 5 大运营商 48+ PoPs，支持 GPU/CPU 异构调度与毫秒级 RTT 遥测。'
    icon: 'server'
    image: '/assets/images/global-mesh/02-vps-pop-map.png'
  - title: 'SaaS 零信任服务网格拓扑'
    description: 'Cloudflare Ingress + Cloud Run Scale-to-Zero BFF + WireGuard 0 端口专网 + 双轨存储，综合成本节约 90%+。'
    icon: 'shield-check'
    image: '/assets/images/global-mesh/03-saas-mesh.png'
    reverse: true
  - title: '应用架构五层流动与 360° 生命周期闭环'
    description: '端-边-控-算-数五层流动模型，配合 Trunk-Based 有状态分支与发布 Tag 闭环，实现告警自动回写 Issue 证据链。'
    icon: 'workflow'
    image: '/assets/images/global-mesh/05-lifecycle.png'
---
