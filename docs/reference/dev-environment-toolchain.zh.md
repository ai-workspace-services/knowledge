# 开发环境工具清单（macOS / Windows / Linux / Grok Bot 远程开发机）

> 更新日期：2026-10-26。macOS、Windows 列为常用安装方式，未核实具体版本；最后一列为 Grok Bot 远程开发机（Debian Linux）实测版本。

| 工具 | macOS | Windows | Linux（Debian/Ubuntu） | Grok Bot 远程开发机 |
|---|---|---|---|---|
| git | 系统自带 / `brew install git` | `winget install Git.Git` | `apt install git` | 2.47.3 |
| gh | `brew install gh` | `winget install GitHub.cli` | 官方 apt 源 | 2.103.0 |
| kubectl | `brew install kubectl` | `winget install Kubernetes.kubectl` | 官方二进制 | v1.37.1 |
| helm | `brew install helm` | `winget install Helm.Helm` | 官方安装脚本 | v3.22.1 |
| flux | `brew install fluxcd/tap/flux` | `choco install flux` | 官方安装脚本 | 2.9.6 |
| terraform | `brew install hashicorp/tap/terraform` | `winget install Hashicorp.Terraform` | HashiCorp apt 源 | v1.17.0 |
| vault | `brew install hashicorp/tap/vault` | `winget install Hashicorp.Vault` | HashiCorp apt 源 | v2.2.1 |
| jq / yq | `brew install jq yq` | `winget install jqlang.jq MikeFarah.yq` | apt / 官方二进制 | 1.7 / v4.54.1 |
| psql | `brew install libpq` | PostgreSQL 安装包 | `apt install postgresql-client` | 17.11 |
| curl / openssl | 系统自带 | curl 自带，openssl 需另装 | apt | 8.14.1 / 3.5.7 |
| ssh | 系统自带 | 系统自带 OpenSSH | `apt install openssh-client` | 10.0p2 |
| K3s 本地集群 | 需 k3d 或 colima | 需 WSL2 + k3s 或 k3d | 原生安装脚本 | v1.37.1+k3s1（含 Flux） |

## 远程开发机说明

- 无 systemd：K3s 以后台进程运行，重启后需用启动脚本拉起。
- 网络：flannel `host-gw` 后端（环境不支持 vxlan），未启用 traefik。
- kubeconfig 两个 context：`box-k3s`（本地）与 `dev-k3s-v5`（非生产 Dev 主机，经 SSH 获取）。
- 不在本文记录任何密钥、主机地址或凭据。
