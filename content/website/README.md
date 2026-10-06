# Portal website content

This is the file-based CMS source for Portal's build-time marketing content.

- Homepage, product marketing, documentation landing copy, and company copy live here.
- Product documentation is canonical under the repository's top-level `docs/`.
- Product technical blogs are canonical under the repository's top-level
  `content/`.
- Portal's `/docs` and `/blogs` remain proxied to the docs service. The service
  publishes those two canonical trees, so do not duplicate their archives here.
- Never commit passwords, API keys, access tokens, refresh tokens, private keys,
  or production configuration values.

## Publishing

1. Create a Git branch and edit the Markdown/YAML content.
2. Review and merge the content PR.
3. Release the relevant consumer: Portal builds from `content/website`, while
   the docs service publishes `docs/` and `content/`.

The backend is portable: Portal consumes a standard Git URL, not a GitHub API
or browser-based editor.
# Public discovery / GEO

`discovery.json` owns bilingual product facts, public resource links and the
small AI resources footer label. Keep platform availability tied to actual
release assets, not source presence or planned app-store support. Free access
is not a separate trial plan and does not imply free upstream infrastructure.

Portal validates this contract and generates product Markdown, `llms.txt`,
`llms-full.txt` and typed UI data during its existing content generation step.
Product overview cards and expandable source-card facts consume the same data.
Do not edit the generated files separately. Documentation and blog archives
remain in content-service; the sitemap reads its catalogs, including pagination.
The brand-domain frontend-router must forward sitemap and discovery documents
to the public Portal build, not replace them with a fixed edge list.
