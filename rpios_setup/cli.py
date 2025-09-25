from __future__ import annotations
import json
from pathlib import Path
from typing import List
import typer

from .engine import Planner
from .facts import detect_facts

app = typer.Typer(add_completion=False, help="Raspberry Pi OS declarative setup")

# ---------- Helpers ----------

def existing_file(value: str) -> Path:
    """
    Validator to ensure a file path exists and is a readable file.
    Use this as a callback for any CLI option that expects a file path.
    """
    p = Path(value)
    if not p.exists():
        typer.secho(f"Error: file not found: {p}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)
    if not p.is_file():
        typer.secho(f"Error: not a file: {p}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)
    # (Optional) you can add readability checks here if you want:
    # try:
    #     p.open("r").close()
    # except OSError as e:
    #     typer.secho(f"Error: cannot read file {p}: {e}", fg=typer.colors.RED, err=True)
    #     raise typer.Exit(code=2)
    return p

def parse_tags(tags: str) -> List[str]:
    return [t.strip() for t in tags.split(",") if t.strip()]

# ---------- Commands ----------

@app.command()
def facts(
    pretty: bool = typer.Option(
        True,
        "--pretty/--no-pretty",
        help="Human-readable summary (default) vs raw JSON",
    )
):
    """
    Print detected system facts (Pi model, OS release, desktop/Wayland).
    """
    data = detect_facts()
    if pretty:
        typer.echo("System facts:\n")
        typer.echo(f"  Platform : {data.get('platform')}")
        typer.echo(f"  Kernel   : {data.get('kernel')}")
        typer.echo(f"  Model    : {data.get('pi_model')}")
        typer.echo("")
        typer.echo("OS Release:")
        for k, v in data.get("os_release", {}).items():
            typer.echo(f"  {k:20} {v}")
        typer.echo("")
        typer.echo(f"Desktop  : {data.get('desktop') or '(none)'}")
        typer.echo(f"Wayland  : {data.get('wayland')}")
    else:
        typer.echo(json.dumps(data, indent=2))


@app.command()
def apply(
    config: Path = typer.Option(
        ...,
        "--config", "-c",
        callback=existing_file,
        help="Path to YAML config file",
    ),
    profile: str = typer.Option("base", "--profile", "-p", help="Profile name to merge (e.g., base, dev)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change, without applying"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags to limit tasks (e.g., apt,apps,desktop)"),
):
    """
    Apply the desired state from the config/profile to the current machine.
    """
    tag_list = parse_tags(tags)
    plan = Planner.from_config(str(config), profile, tags=tag_list)

    results = []
    if dry_run:
        typer.echo("Dry-run: showing checks only. No changes will be made.\n")

    for task in plan.tasks:
        if plan.tags and plan.tags.isdisjoint(task.tags):
            continue
        ok, changed, msg = task.check()
        typer.echo(f"[CHECK] {task.name}: {'present' if ok else 'absent'} | {msg}")
        if not dry_run and not ok:
            ok2, msg2 = task.apply()
            status = "CHANGED" if ok2 else "FAILED"
            typer.echo(f"[APPLY] {task.name}: {status} | {msg2}")
            results.append((task.name, ok2, msg2))

    typer.echo("\nDone.")
    if any(not r[1] for r in results):
        raise typer.Exit(code=1)


@app.command()
def diff(
    config: Path = typer.Option(
        ...,
        "--config", "-c",
        callback=existing_file,
        help="Path to YAML config file",
    ),
    profile: str = typer.Option("base", "--profile", "-p", help="Profile name to merge"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags to limit tasks"),
):
    """
    Show which tasks would change state (without applying).
    """
    tag_list = parse_tags(tags)
    plan = Planner.from_config(str(config), profile, tags=tag_list)
    for task in plan.tasks:
        if plan.tags and plan.tags.isdisjoint(task.tags):
            continue
        ok, changed, msg = task.check()
        typer.echo(f"{task.name}: {'no change' if ok else 'would change'} - {msg}")


@app.command()
def verify(
    config: Path = typer.Option(
        ...,
        "--config", "-c",
        callback=existing_file,
        help="Path to YAML config file",
    ),
    profile: str = typer.Option("base", "--profile", "-p", help="Profile name to merge"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags to limit tasks"),
):
    """
    Verify the system matches the desired state (non-zero exit if any task is not satisfied).
    """
    tag_list = parse_tags(tags)
    plan = Planner.from_config(str(config), profile, tags=tag_list)
    errs = []
    for task in plan.tasks:
        if plan.tags and plan.tags.isdisjoint(task.tags):
            continue
        ok, _, msg = task.check()
        if not ok:
            errs.append((task.name, msg))
    if errs:
        for n, m in errs:
            typer.echo(f"[FAIL] {n}: {m}")
        raise typer.Exit(code=2)
    typer.echo("All good!")


if __name__ == "__main__":
    app()
