# Hermes Disturb Toggle

[English](README.md) | [简体中文](README.zh-CN.md)

A small Hermes Agent plugin that adds `/disturb` to toggle busy-task
acknowledgments and long-running heartbeat messages without changing task
execution.

It controls messages such as:

```text
⚡ Interrupting current task...
⏳ Queued for the next turn...
⏩ Steered into current run...
⏳ Still working...
```

The setting is persisted per messaging platform. Busy acknowledgments are
disabled by default.

## Install

```bash
git clone https://github.com/TerrorAWM/hermes-disturb-mode.git \
  ~/.hermes/plugins/disturb-toggle
```

Enable the plugin in `~/.hermes/config.yaml`:

```yaml
plugins:
  enabled:
    - disturb-toggle
```

Restart Hermes:

```bash
systemctl --user restart hermes-gateway.service
```

## Usage

Send the parameterless command:

```text
/disturb
```

Each call toggles disturb mode for the current platform:

- `ON`: busy-task acknowledgments and long-running heartbeats are silent.
- `OFF`: Hermes shows busy-task acknowledgments and long-running heartbeats.

## Long-running heartbeat

The plugin hides native `⏳ Still working...` messages while disturb mode is
`ON`. Hermes must still have its native heartbeat enabled for it to reappear
when disturb mode is `OFF`:

```yaml
agent:
  gateway_notify_interval: 180
```

Setting `gateway_notify_interval` to `0` disables heartbeats globally, so
`/disturb` cannot restore them.

## Compatibility

The plugin uses Hermes Agent's `pre_gateway_dispatch` plugin hook and busy
session handler API. It does not replace Hermes core files.

## License

MIT
