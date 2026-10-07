#!/usr/bin/env python3
"""Read immutable Git objects; render Daily tables and a bounded source audit.

No deployment, credential retrieval, checkout or branch modification is performed.
PyYAML is the only external Python dependency. See the adjacent configuration.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

try:
    import yaml
except ImportError:
    sys.exit("需要 PyYAML：在独立 Python 环境执行 python -m pip install PyYAML")


class WorkflowLoader(yaml.SafeLoader):
    """Keep GitHub's `on` a string rather than YAML 1.1's boolean True."""


WorkflowLoader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
for initial, resolvers in WorkflowLoader.yaml_implicit_resolvers.items():
    WorkflowLoader.yaml_implicit_resolvers[initial] = [
        item for item in resolvers if item[0] != "tag:yaml.org,2002:bool"
    ]
WorkflowLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), list("tTfF")
)

BEGIN = "<!-- BEGIN GENERATED DAILY SNAPSHOT AUDIT -->"
END = "<!-- END GENERATED DAILY SNAPSHOT AUDIT -->"
SCRIPT_RE = re.compile(r"(?<![\w.-])(?:\./)?((?:\.github/scripts|scripts)/[A-Za-z0-9_./-]+\.(?:sh|py|rb))")
COMMAND_RE = re.compile(
    r"(?:^|[\s;&|])(?P<command>terraform|ansible(?:-playbook|-galaxy)?|ssh|scp|"
    r"gcloud|aws|wrangler|systemctl|apt-get|psql|pg_dump|pg_restore|docker)(?=[\s;]|$)"
)
OWNER_RE = re.compile(r"^ai-workspace-infra/(iac_modules|playbooks)/(.+)@([^@]+)$")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        # Do not echo command stderr: remote URLs may contain credentials.
        raise ValueError(f"Git 读取失败：{root.name} / {args[0]}")
    return result.stdout.rstrip("\n")


class Repository:
    def __init__(self, root: Path, name: str, ref: str, remote: str):
        self.root, self.name, self.remote = root, name, remote
        self.sha = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}")
        if not re.fullmatch(r"[0-9a-f]{40}", self.sha):
            raise ValueError(f"未解析为完整 commit SHA：{name}")

    def read(self, path: str, sha: str | None = None) -> str:
        return git(self.root, "show", f"{sha or self.sha}:{path}")

    def exists(self, path: str, sha: str | None = None) -> bool:
        result = subprocess.run(
            ["git", "-C", str(self.root), "cat-file", "-e", f"{sha or self.sha}:{path}"],
            capture_output=True,
        )
        return result.returncode == 0

    def link(self, path: str, line: int | None = None, sha: str | None = None) -> str:
        suffix = f"#L{line}" if line else ""
        return f"https://github.com/{self.remote}/blob/{sha or self.sha}/{path}{suffix}"


def load_yaml(text: str) -> dict:
    value = yaml.load(text, Loader=WorkflowLoader)
    if not isinstance(value, dict):
        raise ValueError("workflow 必须是 YAML mapping")
    return value


def cell(value) -> str:
    if value is None or value == "":
        return "—"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).replace("|", "&#124;").replace("\r", "").replace("\n", "<br>")


def table(headers: list[str], rows: list[list]) -> str:
    return "\n".join([
        "| " + " | ".join(map(cell, headers)) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(map(cell, row)) + " |" for row in rows],
    ])


def script_paths(run: str) -> list[str]:
    return sorted(set(match.group(1) for match in SCRIPT_RE.finditer(run)))


def replace_region(document: str, generated: str) -> str:
    if document.count(BEGIN) != 1 or document.count(END) != 1:
        raise ValueError("文档必须包含唯一的自动生成开始／结束标记")
    before, rest = document.split(BEGIN)
    _, after = rest.split(END)
    return before + BEGIN + "\n\n" + generated.rstrip() + "\n\n" + END + after


def audit(config: dict, repos: dict[str, Repository]) -> dict:
    toolkit = repos["platform-ops-toolkit"]
    entry = config["entry_workflow"]
    findings, workflows, files, actions, edges = [], [], {}, [], []

    def finding(code, severity, repo, path, detail, line=None):
        item = dict(code=code, severity=severity, repository=repo, path=path, detail=detail)
        if line:
            item["line"] = line
        if repos[repo].exists(path):
            item["source_url"] = repos[repo].link(path, line)
        findings.append(item)

    queue = list(config["workflow_scope"])
    seen = set()
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if not toolkit.exists(path):
            finding("MISSING_WORKFLOW", "error", toolkit.name, path, "登记的 workflow 不存在；需要更新范围映射")
            continue
        text = toolkit.read(path)
        files[path] = text
        doc = load_yaml(text)
        workflows.append(dict(path=path, document=doc))
        source_jobs = doc.get("jobs", {})
        if isinstance(doc.get("runs"), dict):
            source_jobs = {"__composite_action__": doc["runs"]}
        for job_id, job in source_jobs.items():
            uses_items = [("job", job.get("uses"))]
            uses_items += [(str(i), s.get("uses")) for i, s in enumerate(job.get("steps", []), 1)]
            for location, uses in uses_items:
                if not uses:
                    continue
                actions.append(dict(workflow=path, job=job_id, location=location, uses=uses))
                owner = OWNER_RE.fullmatch(uses)
                if owner:
                    repo, target, ref = owner.groups()
                    pinned = bool(re.fullmatch(r"[0-9a-f]{40}", ref))
                    if not pinned:
                        finding("FLOATING_OWNER_REF", "warning", toolkit.name, path,
                                f"{job_id} 的 owner uses 未固定完整 SHA：{uses}")
                    elif not repos[repo].exists(target, ref):
                        finding("OWNER_REF_UNVERIFIED", "warning", toolkit.name, path,
                                f"无法在本地 Git 对象确认 owner 的实际消费版本：{uses}；不可用 main 代替")
                elif uses.startswith("./"):
                    directory = uses[2:]
                    action_file = next((f"{directory}/{f}" for f in ("action.yml", "action.yaml")
                                        if toolkit.exists(f"{directory}/{f}")), None)
                    if not action_file:
                        finding("MISSING_LOCAL_ACTION", "error", toolkit.name, path, f"本地 Action 不存在：{directory}")
                    else:
                        edges.append(dict(caller=path, callee=action_file, kind="local_action"))
                        queue.append(action_file)
            # Composite local actions are scanned below via their source text.
            for step in job.get("steps", []):
                for script in script_paths(str(step.get("run", ""))):
                    edges.append(dict(caller=path, callee=script, kind="script_literal"))
        dispatch = doc.get("on", {}).get("workflow_dispatch", {}) or {}
        for name in dispatch.get("inputs", {}):
            pattern = rf"(?:\binputs\.{re.escape(name)}\b|\binputs\[['\"]{re.escape(name)}['\"]\])"
            if not re.search(pattern, text):
                finding("UNREFERENCED_INPUT", "warning", toolkit.name, path,
                        f"输入 {name} 未发现 inputs 引用；动态消费需人工核对")

    # Follow only literal, repository-local script paths; dynamic paths stay an explicit limitation.
    pending = [edge["callee"] for edge in edges if edge["kind"] == "script_literal"]
    for path, text in list(files.items()):
        pending.extend(script_paths(text))
    while pending:
        path = pending.pop(0)
        if path in files:
            continue
        if not toolkit.exists(path):
            finding("UNRESOLVED_SCRIPT_LITERAL", "warning", toolkit.name, path,
                    "字面脚本路径不在 Toolkit 基线；可能属于 checkout 的其他仓库，需人工判定")
            continue
        text = toolkit.read(path)
        files[path] = text
        for target in script_paths(text):
            edges.append(dict(caller=path, callee=target, kind="script_literal"))
            pending.append(target)

    for path, text in sorted(files.items()):
        for number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            command = COMMAND_RE.search(line)
            if command:
                finding("EXECUTION_CANDIDATE", "review", toolkit.name, path,
                        f"出现 {command.group('command')} 命令词；按副作用人工判定 owner，不自动认定违规", number)
            if re.search(r"--ref\s+[\"']?main\b|^\s*ref:\s*[\"']?main\b|source_ref[=:]main\b", line):
                finding("FLOATING_MAIN_CANDIDATE", "warning", toolkit.name, path,
                        "发现 main 引用候选；需要区分初始选择与执行期重新解析", number)

    mappings = copy.deepcopy(config["execution_mappings"])
    for mapping in mappings:
        checks = []
        for implementation in mapping["implementations"]:
            repo, path = implementation["repository"], implementation["path"]
            exists = repos[repo].exists(path)
            checks.append(dict(repository=repo, path=path, exists=exists,
                               source_url=repos[repo].link(path) if exists else None))
            if not exists:
                finding("MAPPING_PATH_MISSING", "error", repo, path,
                        f"人工映射 {mapping['id']} 的现有实现路径不存在；禁止自动标记为已接入")
        mapping["path_checks"] = checks

    daily = next((item["document"] for item in workflows if item["path"] == entry), None)
    if daily is None:
        raise ValueError("入口 workflow 不存在或未登记在 workflow_scope")
    for job_id, annotations in config["job_annotations"].items():
        if job_id not in daily["jobs"]:
            finding("STALE_JOB_MAPPING", "error", toolkit.name, entry, f"已登记 job 被删除／重命名：{job_id}")
            continue
        names = {step.get("name") for step in daily["jobs"][job_id].get("steps", [])}
        for name in annotations.get("steps", {}):
            if name not in names:
                finding("STALE_STEP_MAPPING", "error", toolkit.name, entry, f"已登记 step 被删除／重命名：{job_id} / {name}")
        for name in names - annotations.get("steps", {}).keys():
            finding("UNMAPPED_STEP", "warning", toolkit.name, entry, f"新增 step 需补输出与验证映射：{job_id} / {name}")
    for job_id in daily["jobs"].keys() - config["job_annotations"].keys():
        finding("UNMAPPED_JOB", "warning", toolkit.name, entry, f"新增 job 需补输入输出映射：{job_id}")

    unique = {json.dumps(f, sort_keys=True): f for f in findings}
    findings = sorted(unique.values(), key=lambda f: (f["severity"], f["path"], f.get("line", 0), f["code"], f["detail"]))
    return dict(schema_version=1, evidence_level="source_only", audit_date=config["audit_date"],
                baselines={name: dict(sha=repo.sha, remote=repo.remote) for name, repo in repos.items()},
                entry_workflow=entry, daily=daily, workflows=workflows, uses=actions,
                edges=sorted({json.dumps(e, sort_keys=True): e for e in edges}.values(),
                             key=lambda e: (e["caller"], e["callee"], e["kind"])),
                execution_mappings=mappings, findings=findings,
                source_hashes={p: hashlib.sha256(t.encode()).hexdigest() for p, t in sorted(files.items())})


def render(config: dict, report: dict, repos: dict[str, Repository]) -> str:
    daily = report["daily"]
    toolkit = repos["platform-ops-toolkit"]
    entry = config["entry_workflow"]
    triggers = daily.get("on", {})
    trigger_description = "、".join(triggers) + "; cron=" + str(
        [item.get("cron") for item in triggers.get("schedule", [])])
    parts = ["## 自动生成：流水线与调用盘点", "",
             "证据等级：**源码盘点**。人工映射的路径存在检查不等于调用、运行或业务验收。", "",
             table(["仓库", "固定 SHA"], [[k, f"`{v['sha']}`"] for k, v in report["baselines"].items()]), "",
             table(["流水线", "触发", "jobs", "steps 定义", "输出"], [[
                 f"[{daily['name']}]({toolkit.link(entry)})", trigger_description, len(daily["jobs"]),
                 sum(len(j.get("steps", [])) for j in daily["jobs"].values()), "构建状态、环境派发回执、最终汇总"]]), "",
             "### Jobs 汇总", ""]
    rows = []
    for job_id, job in daily["jobs"].items():
        info = config["job_annotations"].get(job_id, {})
        rows.append([job_id, info.get("task", job.get("name")), job.get("needs"),
                     info.get("inputs", "待人工补充"), job.get("outputs"),
                     info.get("outputs", "待人工补充"), job.get("if"), job.get("strategy", {}).get("matrix")])
    parts += [table(["Job", "任务", "依赖", "输入", "源码 outputs", "结果／制品", "条件", "矩阵"], rows), ""]
    parts += ["### Steps 关联汇总", ""]
    for job_number, (job_id, job) in enumerate(daily["jobs"].items(), 1):
        annotations = config["job_annotations"].get(job_id, {}).get("steps", {})
        rows = []
        for step_number, step in enumerate(job.get("steps", []), 1):
            note = annotations.get(step.get("name"), {})
            if step.get("uses"):
                call = f"uses: `{step['uses']}`"
            else:
                paths = script_paths(str(step.get("run", "")))
                call = "run: " + ("<br>".join(f"[{p}]({toolkit.link(p)})" for p in paths)
                                  if paths else note.get("run_label", "内联控制逻辑，见 workflow 源码"))
            rows.append([f"{job_number}.{step_number}", step.get("name", "未命名"), call,
                         note.get("playbooks", "—"), note.get("iac", "—"),
                         note.get("verify", "待人工补充"), step.get("if")])
        parts += [f"#### {job_number}. `{job_id}`", "", table(
            ["Step", "任务", "Action uses／脚本 run", "Playbook／Role", "IaC", "输出／验证", "条件"], rows), ""]
    parts += ["### 下游 workflow 范围（人工登记，非全链路可达性证明）", "", table(
        ["路径", "用途"], [[f"[{x}]({toolkit.link(x)})", config["workflow_scope"][x]]
                          for x in config["workflow_scope"]]), ""]
    parts += ["### 下游 Role／IaC 映射（人工登记 + 固定版本路径检查）", "", table(
        ["ID", "任务", "Owner", "入口／实现", "目标接入状态", "输入", "输出／验证", "路径检查"], [
            [m["id"], m["task"], m["owner"], "<br>".join(
                f"[{p['repository']}/{p['path']}]({p['source_url']})" if p["exists"]
                else f"缺失：{p['repository']}/{p['path']}" for p in m["path_checks"]) or "待新增，名称未确定",
             m["status"], m["inputs"], m["outputs"],
             "路径存在；不证明调用" if m["path_checks"] and all(p["exists"] for p in m["path_checks"])
             else "待新增" if not m["path_checks"] else "映射失效"] for m in report["execution_mappings"]]), ""]
    parts += ["### 源码实际 uses（含条件分支；不等于 Daily 必跑）", "", table(
        ["Workflow", "Job", "位置", "实际 uses"], [[u["workflow"], u["job"], u["location"], f"`{u['uses']}`"]
                                                  for u in report["uses"]]), ""]
    parts += ["### 审计分类汇总", "", table(["类别", "数量"], [[code, sum(f["code"] == code for f in report["findings"])]
                      for code in sorted({f["code"] for f in report["findings"]})]), "",
              "完整候选明细见同目录 audit.md 和 audit.json；规则命中需要人工判断，不是部署验收。"]
    return "\n".join(parts)


def render_findings(report: dict) -> str:
    return "# Daily Snapshot 源码审计候选\n\n" + table(
        ["级别", "规则", "仓库", "源码位置", "说明"], [[f["severity"], f["code"], f["repository"],
            f"[{f['path']}:{f.get('line', '')}]({f['source_url']})" if f.get("source_url") else f["path"], f["detail"]]
            for f in report["findings"]]) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_config = Path(__file__).with_name("platform_ops_snapshot_audit.json")
    parser.add_argument("--config", type=Path, default=default_config)
    parser.add_argument("--infra-root", type=Path, default=Path.home() / "workspaces/ai-workspace-infra")
    parser.add_argument("--ref", action="append", default=[], metavar="REPOSITORY=REF", help="覆盖一个仓库的审计 ref；不 checkout")
    parser.add_argument("--refresh-main", action="store_true", help="只 fetch 各仓远端 main，再冻结 FETCH_HEAD；不改变工作目录")
    parser.add_argument("--update-lock", action="store_true", help="将本次解析的 SHA 和上海日期写回配置；与 --check 互斥")
    parser.add_argument("--document", type=Path, help="只替换已有文档的自动生成区；未传则只写独立报告")
    parser.add_argument("--output-dir", type=Path, help="JSON／Markdown 报告目录")
    parser.add_argument("--check", action="store_true", help="对比现有报告／文档，不写文件；漂移返回 1")
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="error", help="规则退出门槛；人工 review 不自动阻断")
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text())
        if args.check and args.update_lock:
            raise ValueError("--check 与 --update-lock 互斥")
        overrides = {}
        for item in args.ref:
            if "=" not in item:
                raise ValueError("--ref 格式必须为 REPOSITORY=REF")
            name, ref = item.split("=", 1)
            if name not in config["repositories"] or not ref or ref.startswith("-"):
                raise ValueError("--ref 包含未知仓库或无效 ref")
            overrides[name] = ref
        repos = {}
        for name, metadata in config["repositories"].items():
            root = args.infra_root / name
            ref = overrides.get(name, metadata["sha"])
            if args.refresh_main:
                git(root, "fetch", "origin", "main")
                ref = overrides.get(name, "FETCH_HEAD")
            repos[name] = Repository(root, name, ref, metadata["remote"])
        if args.update_lock:
            for name, repo in repos.items():
                config["repositories"][name]["sha"] = repo.sha
            config["audit_date"] = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
        report = audit(config, repos)
        generated = render(config, report, repos)
        output = args.output_dir or args.config.parent.parent / "docs/reference/platform-ops-toolkit-daily-main-snapshot"
        # Raw YAML may contain embedded literals. Persist only allowlisted metadata, not env/with/run bodies.
        safe_report = {k: v for k, v in report.items() if k not in ("daily", "workflows")}
        safe_report["jobs"] = [{"id": jid, "name": job.get("name"), "needs": job.get("needs"),
            "steps": [{"index": i, "name": step.get("name"), "uses": step.get("uses"),
                       "scripts": script_paths(str(step.get("run", "")))}
                      for i, step in enumerate(job.get("steps", []), 1)]}
            for jid, job in report["daily"]["jobs"].items()]
        writes = {output / "audit.json": json.dumps(safe_report, ensure_ascii=False, indent=2) + "\n",
                  output / "audit.md": render_findings(report), output / "tables.md": generated + "\n"}
        if args.update_lock:
            writes[args.config] = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
        if args.document:
            writes[args.document] = replace_region(args.document.read_text(), generated)
        drift = []
        for path, content in writes.items():
            if not path.exists() or path.read_text() != content:
                drift.append(str(path))
                if not args.check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
        print(json.dumps({"mode": "check" if args.check else "write", "jobs": len(report["daily"]["jobs"]),
            "steps": sum(len(j.get("steps", [])) for j in report["daily"]["jobs"].values()),
            "findings": len(report["findings"]), "changed_files": drift,
            "baselines": {k: v["sha"] for k, v in report["baselines"].items()}}, ensure_ascii=False))
        severities = {f["severity"] for f in report["findings"]}
        threshold_failed = ("error" in severities and args.fail_on != "none") or (
            "warning" in severities and args.fail_on == "warning")
        return 1 if threshold_failed or (args.check and drift) else 0
    except (ValueError, KeyError, OSError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"审计失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
