"""Core CLI for local developer workflows (PR-101)."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any, Sequence

from packages.core.agent_registry import InMemoryAgentRegistry
from packages.core.contracts.agent_registry import AgentSpec
from packages.core.contracts.tool_registry import ToolSpec
from packages.core.services.meta_service import MetaService
from packages.core.tool_registry import InMemoryToolRegistry
from packages.core.version import get_version_info


def _json_out(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _text_out(title: str, items: dict[str, Any]) -> None:
    print(title)
    for key, value in items.items():
        print(f"{key}: {value}")


def _build_sample_agent_registry() -> InMemoryAgentRegistry:
    registry = InMemoryAgentRegistry()
    registry.register(
        AgentSpec(
            agent_name="default",
            version="v1",
            description="Default deterministic agent",
            tags=["core", "default"],
        )
    )
    docs_agent = registry.register(
        AgentSpec(
            agent_name="docs",
            version="v1",
            description="Docs persona agent contract stub",
            tags=["persona", "docs"],
        )
    )
    registry.set_enabled(docs_agent.spec.agent_name, enabled=False)
    return registry


def _build_sample_tool_registry() -> InMemoryToolRegistry:
    registry = InMemoryToolRegistry()
    registry.register(
        ToolSpec(
            tool_name="dummy.echo",
            version="v1",
            description="Example echo tool",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            tags=["example", "deterministic"],
        )
    )
    health_tool = registry.register(
        ToolSpec(
            tool_name="system.health",
            version="v1",
            description="Health check contract stub",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {"status": {"type": "string"}}},
            tags=["health", "stub"],
        )
    )
    registry.set_enabled(health_tool.spec.tool_name, enabled=False)
    return registry


def _handle_version(args: argparse.Namespace) -> int:
    info = get_version_info()
    payload = asdict(info)
    if args.format == "json":
        _json_out(payload)
    else:
        _text_out("flowbiz-core version", payload)
    return 0


def _handle_meta(args: argparse.Namespace) -> int:
    payload = MetaService().get_meta()
    if args.format == "json":
        _json_out(payload)
    else:
        _text_out("flowbiz-core meta", payload)
    return 0


def _handle_agents(args: argparse.Namespace) -> int:
    registry = _build_sample_agent_registry()
    items = [
        {
            "agent_name": registration.spec.agent_name,
            "version": registration.spec.version,
            "enabled": registration.enabled,
            "tags": registration.spec.tags,
        }
        for registration in registry.list_all(include_disabled=args.include_disabled)
    ]
    payload = {"count": len(items), "agents": items}
    if args.format == "json":
        _json_out(payload)
    else:
        print("flowbiz-core agents")
        for item in items:
            print(
                f"{item['agent_name']} | version={item['version']} | "
                f"enabled={item['enabled']} | tags={','.join(item['tags'])}"
            )
        print(f"count: {payload['count']}")
    return 0


def _handle_tools(args: argparse.Namespace) -> int:
    registry = _build_sample_tool_registry()
    items = [
        {
            "tool_name": registration.spec.tool_name,
            "version": registration.spec.version,
            "enabled": registration.enabled,
            "tags": registration.spec.tags,
        }
        for registration in registry.list_all(include_disabled=args.include_disabled)
    ]
    payload = {"count": len(items), "tools": items}
    if args.format == "json":
        _json_out(payload)
    else:
        print("flowbiz-core tools")
        for item in items:
            print(
                f"{item['tool_name']} | version={item['version']} | "
                f"enabled={item['enabled']} | tags={','.join(item['tags'])}"
            )
        print(f"count: {payload['count']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flowbiz-core",
        description="FlowBiz AI Core developer CLI (contracts/runtime inspection).",
    )
    subparsers = parser.add_subparsers(dest="command")

    version_parser = subparsers.add_parser("version", help="Show version/build metadata")
    version_parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format"
    )
    version_parser.set_defaults(func=_handle_version)

    meta_parser = subparsers.add_parser("meta", help="Show core service metadata")
    meta_parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format"
    )
    meta_parser.set_defaults(func=_handle_meta)

    agents_parser = subparsers.add_parser(
        "agents", help="List sample agent registry entries (in-memory)"
    )
    agents_parser.add_argument(
        "--include-disabled", action="store_true", help="Include disabled agents"
    )
    agents_parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format"
    )
    agents_parser.set_defaults(func=_handle_agents)

    tools_parser = subparsers.add_parser(
        "tools", help="List sample tool registry entries (in-memory)"
    )
    tools_parser.add_argument(
        "--include-disabled", action="store_true", help="Include disabled tools"
    )
    tools_parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format"
    )
    tools_parser.set_defaults(func=_handle_tools)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 1

    return int(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
