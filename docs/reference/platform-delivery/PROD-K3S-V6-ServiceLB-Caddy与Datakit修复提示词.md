# V6 下一批执行提示词：ServiceLB、Caddy 与 Datakit

2026-11-02。以下可直接交给 Antigravity / Gemini Argon；接手时重新读取现场，参考 V5 可运行配置。本文是交接计划，不是执行成功回执。

## 共用提示词

```text
目标节点 root@172.237.24.232；V5 root@104.105.141.213 仅只读参考。
交付采用 Playbooks + GitOps + Flux，入口使用 Caddy + K3s ServiceLB。
本批只修复当前配置：不迁移 Traefik/Flagger、不建设流水线、不做全面 rootless 或数据库身份体系重做，不重建集群、网络、PVC 或数据库，不修改 V5/canonical DNS。
先读取仓库 AGENTS.md、system-db-three-role-security；检查 git status，从最新 origin/main 创建独立 worktree，保留用户修改。
不使用 QMD；通过本提示词、PR、固定 SHA、脱敏命令回执交接。
A/B 并行分析和准备 PR，由 C 串行部署。继承用户既有执行/合并授权，不绕过门禁。不得输出 Secret、token、私钥、DataWay URL 或 DSN。
```

## A：ServiceLB + Caddy

```text
负责文件：
GitOps resources/svc.plus/prod/akamai/prod-k3s-v6.yaml 的 V6 host_vars；
services/prod-k3s-v6/ingress-prod/{helmrelease,kustomization,oci-repository,vault-tls}.yaml。
Playbooks roles/vhosts/k3s-cluster-server/{defaults/main.yml,templates/k3s-config.yaml.j2,tasks/}；
roles/vhosts/k3s_platform_bootstrap/tasks/main.yml；k3s_platform_bootstrap.yml、k3s_platform_bootstrap_with_gitops.yml。

本地仓库定位：/Users/shenlan/workspaces/ai-workspace-infra/playbooks；GitOps 可从 /Users/shenlan/workspaces/ai-workspace-infra/gitops-v6-identity-mount 定位远端并另建 worktree。

V5 参考：web-saas-k3s-v5/web-saas-caddy-ingress 为 LoadBalancer，443→8443，external IP 为 V5 节点，ServiceLB DaemonSet Ready。
V6 最近观察：ingress-prod/caddy-ingress-caddy-ingress 为 LoadBalancer，443→8443，external IP pending，NodePort 22299；config.yaml disable 包含 "traefik"、"servicelb"。
接手必须核对当前配置、覆盖文件、systemd 参数、控制器日志，不能仅凭旧 role 默认值认定现场根因。

在 V6 专属声明中从 disable 列表移除 servicelb，继续禁用 traefik，保留其他已确认配置。不修改所有环境共用默认值。
通过现有 Playbooks 配置更新入口交付；先确认实际入口与参数，不编造 tags，不运行 reset/uninstall/killall。
保留 Pod CIDR 10.52.0.0/16、Service CIDR 10.53.0.0/16、CoreDNS 10.53.0.10、存储 /data/k3s/storage。
保持 Caddy Service 443→8443，由 ServiceLB 暴露节点 443；不添加 Caddy hostPort，不强改自动 NodePort 为 443。

验收：节点 Ready、PVC Bound、四个业务应用 Ready；ServiceLB Ready、Service 获得节点地址。
通过 curl --resolve 验证以下域名直达 V6 的 443，并校验证书链/SNI和实际后端响应，最终不用 -k：
console-selfhost-prod-v6.svc.plus
accounts-selfhost-prod-v6.svc.plus
billing-selfhost-prod-v6.svc.plus
Ingress HelmRelease/Kustomization Ready；不为 Vault/Observability 新增公网路由。
本批不发布真实 DNS，未发布仍标待验收。
回退通过同一 Playbooks 入口恢复原参数，明确可能恢复节点 443 不可用的旧状态。
```

## B：Datakit 资源

```text
独占修改 GitOps services/prod-k3s-v6/observability-prod/datakit-helmrelease.yaml。
只读参考同目录 kustomization.yaml、datakit-vault-secret.yaml、datakit-helmrepository.yaml。

V5 namespace=datakit，chart=2.16.1，实际 requests=100m/128Mi、limits=500m/512Mi，采样约195Mi，重启0。
V6 namespace=observability-prod，同 chart，requests=25m/64Mi、limits=50m/128Mi；最近 OOMKilled、累计重启9次，HelmRelease/Kustomization False。
固定镜像：pubrepo.guance.com/datakit/datakit:2.16.1@sha256:1cd545f7f14dc08935ec6557936b1e6422a3d7d9728b57d6e1d6b57ea1703fc6。

重新核对 V5/V6资源、OOM时间及 V6 2C4G 容量。以 V5 requests 100m/128Mi、limits 500m/512Mi 为首选候选，确认预算后显式写入 V6；不能采用时给出测量依据与替代值，不自动扩容。
保留 chart、镜像 digest、采集配置、标签及共享 DataWay Secret 引用，不新增采集器或复制凭据。
渲染确认资源进入 DaemonSet，提交独立 PR 给 C。修复生效后才重试失败调谐，不能只 reset 状态。

验收：DaemonSet desired/current/ready/available 符合单节点预期；实际资源匹配；至少观察15分钟且覆盖正常采集周期，无新增OOM/重启，记录CPU、内存和节点余量。
Datakit HelmRelease、Observability Kustomization Ready；取得 V6 新鲜遥测接收证据，否则单列待验收；四个应用保持就绪。
回退通过 GitOps revert，明确旧资源可能恢复 OOM 风险。
```

## C：唯一集成者

```text
A 独占 V6 主机参数和 ingress-prod/，B 独占 datakit-helmrelease.yaml；C 负责最终调谐和 Knowledge 最新记录。任何人不改 auditor-rbac.yaml、数据库 schema、业务镜像或 NetworkPolicy。
先记录基线 SHA/Flux revision；按授权合并 A/B PR，先应用 ServiceLB 主机配置并验证控制面/业务，再滚动 Datakit。节点操作串行，不同时重启控制面和滚动采集器。
不以命令超时推断控制器停止；读取实际状态后决定是否重试。
Knowledge PR #287 已合并，更新归档必须从最新 main 新建 PR，不追加到已合并分支。
最终交付：PR/合并SHA、Playbooks入口及结果、Flux revision、ServiceLB/Caddy HTTPS证据、Datakit资源与观察窗口/遥测、四应用回归、未完成项及回退范围。
真实DNS、SMTP、auditor权限、完整schema/数据迁移继续单列，不宣称本批完成即生产整体验收通过。
```
