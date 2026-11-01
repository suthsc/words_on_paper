"""Command-line interface for Words on Paper."""

import time
from typing import Optional

import click
import yaml

from words_on_paper.config.loader import load_config
from words_on_paper.video.assembler import generate_video


@click.group()
def cli() -> None:
    """Words on Paper - Video generator for animated text."""
    pass


@cli.command()
@click.argument("config", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    required=True,
    help="Output video file path",
)
def generate(config: str, output: str) -> None:
    """Generate a video from a configuration file.

    CONFIG: Path to the configuration file (JSON or YAML)
    """
    try:
        click.echo(f"Words on Paper - starting at {time.asctime(time.localtime())}")
        click.echo(f"Loading configuration from {config}...")
        video_config = load_config(config)

        click.echo(
            f"Generating video ({video_config.video['width']}x"
            f"{video_config.video['height']} @ "
            f"{video_config.video['fps']}fps)..."
        )
        generate_video(video_config, output)

        click.echo(f"Video saved to {output}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.exceptions.Exit(1) from e


@cli.command()
@click.argument("config", type=click.Path(exists=True))
@click.option(
    "--resolved",
    is_flag=True,
    help="Print each text's effective settings after defaults and styles apply.",
)
@click.option(
    "--text",
    "text_index",
    type=int,
    default=None,
    help="With --resolved, print only the text at this index (0-based).",
)
def validate(config: str, resolved: bool, text_index: Optional[int]) -> None:
    """Validate a configuration file.

    CONFIG: Path to the configuration file (JSON or YAML)
    """
    try:
        click.echo(f"Validating {config}...")
        video_config = load_config(config)
        if resolved or text_index is not None:
            _echo_resolved_texts(video_config.texts, text_index)

        click.echo("✓ Configuration is valid")
        width = video_config.video["width"]
        height = video_config.video["height"]
        fps = video_config.video["fps"]
        click.echo(f"  Resolution: {width}x{height}")
        click.echo(f"  FPS: {fps}")
        click.echo(f"  Text sequences: {len(video_config.texts)}")
        click.echo(f"  Duration: {video_config.get_video_duration():.1f} seconds")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.exceptions.Exit(1) from e


def _echo_resolved_texts(texts: list, text_index: Optional[int]) -> None:
    """Print texts as YAML with every field filled in, like computed styles."""
    if text_index is not None and not 0 <= text_index < len(texts):
        raise click.BadParameter(
            f"text index {text_index} out of range (0-{len(texts) - 1})",
            param_hint="--text",
        )
    indices = range(len(texts)) if text_index is None else [text_index]
    for i in indices:
        click.echo(f"# texts[{i}]")
        fields = texts[i].model_dump()
        style = fields.pop("style")
        if style is not None:
            fields = {"style": style, **fields}
        dumped = yaml.safe_dump([fields], sort_keys=False, allow_unicode=True)
        click.echo(dumped.rstrip())


if __name__ == "__main__":
    cli()
