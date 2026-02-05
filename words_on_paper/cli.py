"""Command-line interface for Words on Paper."""

import time

import click

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
        raise click.Exit(1) from e


@cli.command()
@click.argument("config", type=click.Path(exists=True))
def validate(config: str) -> None:
    """Validate a configuration file.

    CONFIG: Path to the configuration file (JSON or YAML)
    """
    try:
        click.echo(f"Validating {config}...")
        video_config = load_config(config)

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
        raise click.Exit(1) from e


if __name__ == "__main__":
    cli()
