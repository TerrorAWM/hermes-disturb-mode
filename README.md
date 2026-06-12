# Hermes Disturb Toggle

[English](README.md) | [简体中文](README.zh-CN.md)

A small Hermes Agent plugin that adds `/disturb` to toggle busy-task
acknowledgment messages without changing task execution.

It controls messages such as:

```text
⚡ Interrupting current task...
⏳ Queued for the next turn...
⏩ Steered into current run...
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

Each call toggles busy acknowledgments for the current platform:

- `ON`: Hermes sends busy-task acknowledgment messages.
- `OFF`: Hermes handles the message normally but stays silent.

## Long-running heartbeat

This plugin does not control the native long-running heartbeat:

```text
⏳ Still working...
```

Disable that independently in `~/.hermes/config.yaml`:

```yaml
agent:
  gateway_notify_interval: 0
```

Setting it to `0` only hides the heartbeat message. It does not stop task
execution, interruption handling, activity tracking, or inactivity timeouts.

## Compatibility

The plugin uses Hermes Agent's `pre_gateway_dispatch` plugin hook and busy
session handler API. It does not replace Hermes core files.

## License

MIT
