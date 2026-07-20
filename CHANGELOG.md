# Changelog

All notable changes to `tai-contract` are documented here; the format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Until 1.0.0 the contract surface is not stable: **minor (0.x) releases may
contain breaking changes.**

## [Unreleased]

First release (0.1.0) in preparation — nothing published yet.

### Added

- An optional untyped `fanout: dict[str, Any] | None` field on the connection
  lifecycle result types (`NoAuthConnectResult`, `CompleteConnectResult`,
  `DisconnectResult`, `PatchResult`) and their wire-response twins
  (`StartConnectNoAuthResponse`, `PatchSubServicesResponse`, `DisconnectResponse`),
  so a connector mutation's HTTP response carries the awaited per-origin fleet
  report of the manifest broadcast it triggered — matching every other manifest
  writer. `None` on the paths that perform no manifest mutation.
- `AppLifecycle.on_fleet_op_applied(func)` — a handler fired after any
  worker-bus op applies in a process and after the reconnect self-resync. It
  takes one argument (the op name), unlike its zero-arg siblings.
- `ConfigManager.mutate_manifest(mutator)` (atomic read-modify-write on the
  preserved manifest view) and `ConfigManager.replace_manifest(document)`
  (atomic whole-document replace; absent keys are deleted). Both hold exclusive
  access across the whole read→mutate→write span.

### Removed

- `AppAdmin.update(manifest)` — the in-memory-only manifest apply. A manifest
  replacement now crosses the config pipeline (persist → reload → broadcast), so
  the split-brain primitive that applied a manifest without persisting it is
  gone; there is no wire op or admin caller for it.

### Changed

- `Backend` is a task-execution contract only. `launch` is its sole abstract
  member; fleet propagation of config changes is the app's own internal worker
  bus, not a backend responsibility.
- `ConfigManager.write_manifest`'s docstring records the ownership rule: feature
  code mutates through the transactional seams (`mutate_manifest` /
  `replace_manifest`); direct `write_manifest` is reserved for config-layer
  internals.

### Removed

- The `Backend` fleet control plane: `subscribe_control_plane`,
  `update_manifest`, `reload_mcp`, `deregister_mcp`, `reload_tool`,
  `remove_tool`, `reload_config`, `reload_failed_mcps`, `list_failed_mcps`, and
  the census read `list_workers`.
