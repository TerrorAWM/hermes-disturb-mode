# Hermes 勿扰模式切换插件

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个小型 Hermes Agent 插件，通过 `/disturb` 指令切换任务忙碌提示和长任务心跳文字，不会影响任务本身的执行。

它控制以下类型的提示消息：

```text
⚡ Interrupting current task...
⏳ Queued for the next turn...
⏩ Steered into current run...
⏳ Still working...
```

开关状态会按消息平台分别保存，默认关闭勿扰模式。

## 安装

```bash
git clone https://github.com/TerrorAWM/hermes-disturb-mode.git \
  ~/.hermes/plugins/disturb-toggle
```

在 `~/.hermes/config.yaml` 中启用插件：

```yaml
plugins:
  enabled:
    - disturb-toggle
```

重启 Hermes：

```bash
systemctl --user restart hermes-gateway.service
```

## 使用

发送无参数指令：

```text
/disturb
```

每次调用都会切换当前消息平台的勿扰模式：

- `ON`：隐藏任务中断、排队等忙碌提示以及 `⏳ Still working...` 长任务心跳。
- `OFF`：恢复显示忙碌提示和长任务心跳。

任务正在运行时也可以直接调用 `/disturb`，不会打断当前任务。

## 长任务心跳

勿扰模式为 `ON` 时，插件会隐藏 Hermes 原生的 `⏳ Still working...` 长任务心跳。

为了让勿扰模式切回 `OFF` 后能够恢复心跳，需要保持 Hermes 原生心跳开启：

```yaml
agent:
  gateway_notify_interval: 180
```

如果设置为 `0`，心跳会被全局关闭，`/disturb` 切回 `OFF` 后也无法恢复显示。

勿扰模式只隐藏提示文字，不会停止任务执行，也不会影响：

- 工具调用和 Agent 持续运行
- 新消息中断任务
- 内部活动状态跟踪
- 无活动警告和超时处理
- 最终结果发送

可以设置其他秒数调整心跳频率，例如 `900` 表示每 15 分钟提示一次。

## 状态保存

插件会把各消息平台的开关状态保存在：

```text
~/.hermes/disturb-toggle.json
```

不同平台可以拥有不同状态，例如飞书关闭提示、Telegram 开启提示。

## 兼容性

插件使用 Hermes Agent 的 `pre_gateway_dispatch` 插件钩子和忙碌会话处理接口，不会替换或修改 Hermes 核心文件。

## 卸载

从 `~/.hermes/config.yaml` 的 `plugins.enabled` 中移除 `disturb-toggle`，然后删除插件目录并重启 Hermes：

```bash
rm -rf ~/.hermes/plugins/disturb-toggle
systemctl --user restart hermes-gateway.service
```

## 许可证

MIT
