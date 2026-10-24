"""Contract tests for 10 core platform services OrbStack deployment and acceptance matrix."""
import os
from pathlib import Path
import re
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs" / "reference" / "platform-core-services-orbstack-acceptance-matrix.zh.md"
INDEX_PATH = REPO_ROOT / "docs" / "reference" / "index.md"
OVERVIEW_PATH = REPO_ROOT / "docs" / "reference" / "overview.zh.md"
VERIFY_DIR = REPO_ROOT / "scripts" / "orbstack-verification"
VERIFY_SCRIPT = VERIFY_DIR / "verify-orbstack-all-services.sh"


class TestOrbStack10CoreServicesMatrix(unittest.TestCase):
    def test_acceptance_matrix_document_exists(self):
        self.assertTrue(DOC_PATH.exists(), f"Missing acceptance document: {DOC_PATH}")
        content = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("title: 10 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵", content)
        self.assertIn("slug: platform-core-services-orbstack-acceptance-matrix", content)
        self.assertIn("status: approved", content)
        self.assertIn("open-platform Umbrella Chart", content)
        self.assertIn("ai-workspace-infra/artifacts/oci/charts/open-platform", content)

    def test_all_10_service_categories_in_matrix(self):
        content = DOC_PATH.read_text(encoding="utf-8")
        expected_projects = [
            "platform-gitea",
            "platform-harbor",
            "platform-silo",
            "platform-cmdb",
            "platform-vault-zitadel",
            "platform-doco-cd",
            "platform-k3s-pgvector",
            "platform-pg-backup",
            "platform-ai-gateway",
            "platform-mcp-server",
        ]
        for project in expected_projects:
            self.assertIn(project, content, f"Project {project} not found in acceptance matrix")

        expected_pinned_images = [
            "gitea/gitea:1.22.6",
            "goharbor/harbor-portal:v2.15.4",
            "pgsty/silo:RELEASE.2026-10-18T00-00-00Z",
            "hashicorp/vault:1.17.6",
            "ghcr.io/kimdre/doco-cd:0.1.28",
            "pgvector/pgvector:pg16",
            "postgres:16-alpine",
            "calciumion/new-api:v0.4.10",
            "ghcr.io/berriai/litellm:v1.51.0",
        ]
        for image in expected_pinned_images:
            self.assertIn(image, content, f"Image {image} not documented in matrix")

    def test_verification_script_and_compose_directories(self):
        self.assertTrue(VERIFY_SCRIPT.exists(), f"Verification script missing: {VERIFY_SCRIPT}")
        self.assertTrue(os.access(VERIFY_SCRIPT, os.X_OK), "Verification script must be executable")

        expected_dirs = [
            "01-git-ci-gitea",
            "02-artifact-harbor",
            "03-s3-storage-silo",
            "04-cmdb-inventory",
            "05-identity-vault-zitadel",
            "06-gitops-doco-cd",
            "07-container-vector-node",
            "08-pg-backup-drill",
            "09-ai-gateway",
            "10-mcp-server",
        ]
        assigned_ports = set()
        for d in expected_dirs:
            compose_file = VERIFY_DIR / d / "docker-compose.yml"
            self.assertTrue(compose_file.exists(), f"Missing docker-compose.yml in {d}")
            compose_text = compose_file.read_text(encoding="utf-8")
            # Extract published host ports (e.g. "127.0.0.1:13000:3000")
            ports = re.findall(r'127\.0\.0\.1:(\d+):', compose_text)
            self.assertTrue(len(ports) > 0, f"No host loopback ports found in {compose_file}")
            for p in ports:
                self.assertNotIn(p, assigned_ports, f"Duplicate port collision detected: {p} in {d}")
                assigned_ports.add(p)

        # Ensure all key platform ports are assigned
        critical_ports = {"13000", "13001", "14000", "15434", "15435", "15436", "18000", "18080", "18200", "18888", "19000", "19001", "19088", "19128"}
        self.assertTrue(critical_ports.issubset(assigned_ports), f"Missing critical ports: {critical_ports - assigned_ports}")

    def test_index_and_overview_cross_references(self):
        index_content = INDEX_PATH.read_text(encoding="utf-8")
        self.assertIn("platform-core-services-orbstack-acceptance-matrix.zh.md", index_content)
        self.assertIn("10 大核心服务类别 macOS OrbStack 单机部署与健康验收矩阵", index_content)

        overview_content = OVERVIEW_PATH.read_text(encoding="utf-8")
        self.assertIn("platform-core-services-orbstack-acceptance-matrix.zh.md", overview_content)
        self.assertIn("10 大核心服务类别", overview_content)


if __name__ == "__main__":
    unittest.main()
