from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any


STATE_PATH = Path.home() / ".hermes" / "disturb-toggle.json"
LONG_RUNNING_PREFIX = "⏳ Still working..."


def _platform_name(source: Any) -> str:
    platform = getattr(source, "platform", None)
    return str(getattr(platform, "value", platform) or "unknown").lower()


def _load_state() -> dict[str, bool]:
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        platforms = data.get("platforms", {})
        if isinstance(platforms, dict):
            return {str(key): bool(value) for key, value in platforms.items()}
    except Exception:
        pass
    return {}


def _save_state(platforms: dict[str, bool]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(
        json.dumps({"platforms": platforms}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(STATE_PATH)


def _is_enabled(platform: str) -> bool:
    return _load_state().get(platform, False)


def _toggle(platform: str) -> bool:
    platforms = _load_state()
    platforms[platform] = not platforms.get(platform, False)
    _save_state(platforms)
    return platforms[platform]


async def _send(gateway: Any, event: Any, text: str) -> None:
    source = event.source
    adapter = gateway.adapters.get(source.platform)
    if adapter:
        await adapter.send(source.chat_id, text)


def _command_parts(event: Any) -> tuple[str, str]:
    text = str(getattr(event, "text", "") or "").strip()
    if not text.startswith("/"):
        return "", ""
    head, _, args = text.partition(" ")
    command = head[1:].split("@", 1)[0].lower()
    return command, args.strip()


def _install_busy_wrapper(gateway: Any) -> None:
    if getattr(gateway, "_disturb_toggle_installed", False):
        return

    original = gateway._handle_active_session_busy_message

    async def wrapped_busy_handler(event: Any, session_key: str) -> bool:
        command, args = _command_parts(event)
        platform = _platform_name(event.source)

        if command == "disturb":
            if args:
                await _send(gateway, event, "Usage: `/disturb`")
                return True
            enabled = _toggle(platform)
            state = "ON" if enabled else "OFF"
            detail = (
                "Busy-task acknowledgments and long-running heartbeats are now silent."
                if enabled
                else "Busy-task acknowledgments and long-running heartbeats will be shown."
            )
            await _send(gateway, event, f"`/disturb`: **{state}** for **{platform}**\n{detail}")
            return True

        if not _is_enabled(platform):
            return await original(event, session_key)

        # Hermes already suppresses repeated busy acknowledgments through this
        # timestamp map. Refreshing it preserves interrupt/queue behavior while
        # making the original handler return before sending the acknowledgment.
        gateway._busy_ack_ts[session_key] = time.time()
        return await original(event, session_key)

    gateway._handle_active_session_busy_message = wrapped_busy_handler
    gateway._disturb_toggle_installed = True
    for adapter in gateway.adapters.values():
        if hasattr(adapter, "set_busy_session_handler"):
            adapter.set_busy_session_handler(wrapped_busy_handler)


def _install_send_wrappers(gateway: Any) -> None:
    wrapped_platforms = getattr(gateway, "_disturb_toggle_wrapped_platforms", set())

    for platform, adapter in gateway.adapters.items():
        platform_name = str(getattr(platform, "value", platform) or "unknown").lower()
        if platform_name in wrapped_platforms:
            continue

        original_send = adapter.send

        async def filtered_send(
            chat_id: Any,
            content: Any,
            *args: Any,
            _platform_name: str = platform_name,
            _original_send: Any = original_send,
            **kwargs: Any,
        ) -> Any:
            if (
                _is_enabled(_platform_name)
                and isinstance(content, str)
                and content.startswith(LONG_RUNNING_PREFIX)
            ):
                return None
            return await _original_send(chat_id, content, *args, **kwargs)

        adapter.send = filtered_send
        wrapped_platforms.add(platform_name)

    gateway._disturb_toggle_wrapped_platforms = wrapped_platforms


def _pre_gateway_dispatch(event: Any, gateway: Any, **_: Any) -> dict[str, str] | None:
    _install_busy_wrapper(gateway)
    _install_send_wrappers(gateway)

    command, args = _command_parts(event)
    if command != "disturb":
        return None

    async def respond() -> None:
        platform = _platform_name(event.source)
        if args:
            await _send(gateway, event, "Usage: `/disturb`")
            return
        enabled = _toggle(platform)
        state = "ON" if enabled else "OFF"
        detail = (
            "Busy-task acknowledgments and long-running heartbeats are now silent."
            if enabled
            else "Busy-task acknowledgments and long-running heartbeats will be shown."
        )
        await _send(gateway, event, f"`/disturb`: **{state}** for **{platform}**\n{detail}")

    try:
        asyncio.get_running_loop().create_task(respond())
    except RuntimeError:
        asyncio.run(respond())
    return {"action": "skip", "reason": "disturb_toggle_command"}


def register(ctx: Any) -> None:
    ctx.register_hook("pre_gateway_dispatch", _pre_gateway_dispatch)
