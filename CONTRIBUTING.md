# Contributing to tai-contract

`tai-contract` holds **pure interface contracts** — protocols, ABCs, and pydantic
models. The one rule that shapes everything: **nothing but `pydantic` at runtime,
and no behaviour beyond a narrow whitelisted surface** — the `tai_app` forwarding
handle, model-level validators/normalizers, the storage path guard, and `Agent`'s
default `astream`/terminal-drain; everything else is a pydantic model, Protocol,
ABC, or enum.

## Ground rules

- **Runtime imports = pydantic only.** Vendor types (fastmcp, langchain,
  starlette, mcp) are referenced for the type-checker only — import them under
  `if TYPE_CHECKING:` and start every module with `from __future__ import
  annotations`. A vendor type must never be a runtime pydantic model **field**.
- **No behaviour outside the whitelist.** Protocol methods are `...`; ABC abstract
  methods carry only signatures + docstrings. The only behavioral members are the
  `tai_app` forwarding handle, model-level validators/normalizers, the storage
  path guard, and `Agent`'s default `astream`/terminal-drain — anything more
  lives in the impl repos.
- **Typed package.** `py.typed` ships; keep pyright clean.

## Layout

One subpackage per contract area, each exporting its protocols, ABCs, models,
and enums:

- `app`, `manifest`, `plugins`, `presets` — the `tai_app` forwarding handle, the
  manifest/plugin/preset schemas that drive loading.
- `tools`, `agent`, `extensions`, `hooks`, `sub_mcp`, `template` — the capability
  surfaces a host loads and runs.
- `access_control`, `accounts`, `connectors`, `webhooks` — identity, login, OAuth
  connectors, and inbound webhook verification.
- `backend`, `backup`, `channels`, `interactions`, `monitoring`, `storage` —
  background execution, backup, human-in-the-loop delivery, telemetry, and
  content storage.
- `clients`, `config`, `errors`, `transport`, `versioning` — the pooled-client,
  configuration, error, transport, and versioning types.

The tests are all self-contained — a public clone runs them green with the `dev`
extra. **No private dependency.**

- **`tests/test_contract.py`** — imports, runtime purity (every model rebuilds
  with vendor libs absent; the purity gate whitelists `tai_app` as the sole
  behavioral member), the facade partition against the frozen 53-member surface,
  enums, protocol shape, and the OS-clean state (no tenant coupling in
  connectors, vendor-neutral monitoring, no brand leak).
- **`tests/test_logic.py`** — the non-validator whitelisted behavior: the
  `Agent` terminal-rule drain + default stream, `ConnectionRecord` helpers,
  `TaiMCPConfig` transport properties, the storage-root guard, and the
  behavioral error/enum members.
- **`tests/test_validators.py`** — the pydantic field/model validators and
  `model_post_init` invariants (a PASS path and RAISE paths per invariant).
- **`tests/test_backup.py`** — the backup contract's typed shape
  (`BackupSectionInfo`).
- **`tests/test_webhooks.py`** — the webhook-verifier types
  (`WebhookVerifier` shape, `WebhookVerificationError`).

## Dev

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest            # self-contained contract tests
```

The runtime-purity guard — every shipped model must rebuild with only `pydantic`
installed:

```bash
uv sync --no-dev && uv run --no-sync python -c "import importlib,pkgutil,pydantic,tai_contract; \
[o.model_rebuild() for m in pkgutil.walk_packages(tai_contract.__path__,'tai_contract.') \
 for o in vars(importlib.import_module(m.name)).values() \
 if isinstance(o,type) and issubclass(o,pydantic.BaseModel) and o.__module__.startswith('tai_contract')]"
uv sync --extra dev
```

Before any commit, run a secret scan over `src/` and `tests/` (e.g.
`detect-secrets scan`).

## License

By contributing you agree your contributions are licensed under Apache-2.0.
