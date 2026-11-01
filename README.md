# Words on Paper

A Python video generator that creates beautiful animated text on paper-like backgrounds. Perfect for creating intros, tutorials, and text-based animations.

## Features

- **Animated Text**: Fade in/out effects for smooth text transitions
- **Typing Effect**: Text appears character-by-character as if being typed
- **Drop Shadows**: Add depth with configurable drop shadow effects
- **Multiple Orientations**: Render text horizontally or vertically
- **Z-Ordering**: Layer multiple text sequences with proper overlap handling
- **Flexible Positioning**: Center, absolute (pixels), or relative (percentage) positioning
- **Paper Texture**: Configurable background with subtle paper texture
- **HD Resolution**: Generate videos up to 4K resolution (tested at 1920×1080)
- **Configuration Files**: YAML or JSON config for easy customization

## Installation

### Requirements

- Python 3.9+
- FFmpeg (for video output)

### Install with pip

```bash
pip install words-on-paper
```

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd words_on_paper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Quick Start

### Using the CLI

```bash
# Validate a configuration
words-on-paper validate examples/simple_fade.yaml

# Show each text's effective settings after defaults/styles are applied
words-on-paper validate examples/waiting_for_godot_full_scene.yaml --resolved
words-on-paper validate examples/waiting_for_godot_full_scene.yaml --text 14

# Generate a video
words-on-paper generate examples/simple_fade.yaml -o output.mp4
```

### Using Python API

```python
from words_on_paper import load_config, generate_video

# Load configuration
config = load_config("examples/simple_fade.yaml")

# Generate video
generate_video(config, "output.mp4")
```

## Configuration

Configuration files define all aspects of your video using YAML or JSON format.

### Basic Configuration Example

```yaml
video:
  width: 1920
  height: 1080
  fps: 30

background:
  type: paper
  color: "#FFFFFF"
  texture_intensity: 0.05

texts:
  - content: "Hello World"
    start_time: 0.0
    fade_in_duration: 1.0
    display_duration: 3.0
    fade_out_duration: 1.0
    orientation: horizontal
    position:
      mode: center
    font:
      family: Arial
      size: 72
      color: "#000000"
    effects:
      typing:
        enabled: false
      drop_shadow:
        enabled: true
        offset_x: 3
        offset_y: 3
        blur_radius: 4
    z_index: 0
```

### Configuration Schema

#### Video Settings

```yaml
video:
  width: 1920        # Video width in pixels
  height: 1080       # Video height in pixels
  fps: 30            # Frames per second
```

#### Background Settings

```yaml
background:
  type: paper                # "paper" or "solid"
  color: "#FFFFFF"          # Background color (hex)
  texture_intensity: 0.05   # Texture intensity (0.0 - 1.0)
```

#### Text Sequence

```yaml
texts:
  - content: "Your text here"
    start_time: 0.0              # When text starts (seconds)
    fade_in_duration: 1.0        # Fade in time (seconds)
    display_duration: 3.0        # Display time at full opacity (seconds)
    fade_out_duration: 1.0       # Fade out time (seconds)
    orientation: horizontal      # "horizontal" or "vertical"
    position:
      mode: center              # "center", "absolute", or "relative"
      x: null                   # X position (for absolute/relative)
      y: null                   # Y position (for absolute/relative)
    font:
      family: Arial             # Font name
      size: 72                  # Font size in pixels
      color: "#000000"          # Text color (hex)
    effects:
      typing:
        enabled: false          # Enable typing effect
        chars_per_second: 10    # Typing speed
      drop_shadow:
        enabled: true           # Enable drop shadow
        offset_x: 3             # Shadow X offset
        offset_y: 3             # Shadow Y offset
        blur_radius: 4          # Shadow blur
        color: "#00000040"      # Shadow color with alpha
    z_index: 0                  # Layer order (higher = on top)
```

### Positioning Modes

- **center**: Centers text on screen
- **absolute**: Pixel coordinates (x, y) from top-left
- **relative**: Percentage coordinates (0.0 - 1.0) where 0.5 = 50%

### Color Format

Colors use hex format: `#RRGGBB` or `#RRGGBBAA` (with alpha)

Examples:
- `#000000` - Black
- `#FFFFFF` - White
- `#FF0000` - Red
- `#00000040` - Black with 50% opacity

### Defaults and Styles

Long scripts repeat the same settings on every line: each character's font,
color and position, the usual fade timings, and so on. As in CSS, you can
declare these once and let them cascade:

```yaml
defaults:                 # applied to every text
  fade_in_duration: 0.8
  fade_out_duration: 0.8
  font: {family: Georgia}

styles:                   # named, reusable fragments
  vladimir_voice:
    font: {color: "#1A5490", size: 42}
  vladimir:
    extends: vladimir_voice          # a name or a list of names
    font: {family: Courier}
    position: {mode: relative, x: 0.15, y: 0.25}
  shadow:
    effects:
      drop_shadow: {offset_x: 3, offset_y: 3}

texts:
  - style: vladimir
    content: "VLADIMIR: Nothing to be done."
    start_time: 22.0
  - style: [vladimir, shadow]        # several styles; later ones win
    content: "VLADIMIR: Quite right."
    start_time: 42.8
    font: {size: 48}                 # inline fields win over everything
```

**Precedence** (lowest to highest):

| Level | Where | Notes |
|-------|-------|-------|
| 1 | Built-in defaults | The values in the schema (e.g. `font.size: 72`) |
| 2 | `defaults` | Applied to every text |
| 3 | Styles in `style:` | In the order listed; each style's `extends` chain applies first |
| 4 | Inline text fields | Always win |

**Merge rules:**

- Nested blocks (`font`, `position`, `effects.<name>`) merge key by key, so a
  style can set just `font.color` and keep the family and size from below.
- Plain values and lists replace what's below them.
- There's no way to "unset" a value; override it instead (for example
  `effects: {drop_shadow: {enabled: false}}`).

**Validation:**

- Styles may set any text field, including timings and `content`.
- `extends` is only allowed inside `styles`; `style` is only allowed on texts.
- Unknown keys in `defaults` or a style are errors with a path, e.g.
  `styles.vladimir.font.colour: unknown field`, so a typo can't silently drop a
  setting for every text that uses the style.
- Unknown style names and `extends` cycles (`a -> b -> a`) are reported.
- Use `words-on-paper validate --resolved` (optionally `--text N`) to see the
  computed values for each text, like a browser's "computed styles" panel.

See `examples/waiting_for_godot_full_scene.yaml` for a complete example.

## Examples

The `examples/` directory contains several example configurations:

- **simple_fade.yaml** - Basic fade in/out effect
- **typing_effect.yaml** - Text with typing effect
- **overlapping_phrases.yaml** - Multiple overlapping text sequences
- **complete_demo.yaml** - Comprehensive demo of all features
- **waiting_for_godot_full_scene.yaml** - A full scene written with `defaults` and `styles`

## Architecture

### Modules

- **config**: Configuration loading and validation (Pydantic)
- **rendering**: Text-to-image rendering with PIL
- **background**: Paper texture generation
- **composition**: Frame building, animation timing, z-ordering
- **video**: MoviePy video assembly
- **utils**: Timing and color utilities
- **cli**: Click-based command-line interface

### Workflow

1. **Load Config** → Parse YAML/JSON configuration
2. **Validate** → Ensure configuration is valid
3. **Calculate Duration** → Determine video length from text timings
4. **Generate Frames** → For each frame:
   - Calculate text opacity (fade in/out)
   - Calculate visible characters (typing effect)
   - Render text to image
   - Apply effects (drop shadow)
   - Calculate position
   - Composite layers by z-index
   - Composite on background
5. **Assemble Video** → Combine frames with MoviePy
6. **Output** → Write video file

## API Reference

### Main Functions

#### `load_config(config_path: str | Path) -> VideoConfig`

Load and validate configuration from JSON or YAML file.

```python
from words_on_paper import load_config

config = load_config("config.yaml")
```

#### `generate_video(config: VideoConfig, output_path: str | Path) -> None`

Generate a video from configuration.

```python
from words_on_paper import generate_video, load_config

config = load_config("config.yaml")
generate_video(config, "output.mp4")
```

### Configuration Classes

All configuration classes are Pydantic models that validate input:

- **VideoConfig** - Root configuration (including `defaults` and `styles`)
- **TextSequence** - Text animation configuration
- **Position** - Text positioning
- **Font** - Font configuration
- **Effects** - Animation effects
- **TypingEffect** - Typing animation
- **DropShadow** - Drop shadow effect
- **BackgroundConfig** - Background configuration

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=words_on_paper

# Run specific test file
pytest tests/config/test_schema.py

# Run with verbose output
pytest -v
```

Current test coverage: **80%+**

## Performance

- Frame generation: ~1-3 seconds per 1080p frame (depends on complexity)
- Video assembly: Varies by duration and codec
- For a 10-second video at 30fps: ~5-10 minutes on modern hardware

Tips for faster generation:
- Use lower resolution for previews
- Reduce texture_intensity for faster background rendering
- Minimize number of text sequences and effects

## Troubleshooting

### FFmpeg not found

Install FFmpeg:
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/download.html

### Font not found

The system looks for fonts in standard locations:
- macOS: `/Library/Fonts`, `/System/Library/Fonts`, `~/Library/Fonts`
- Linux: `/usr/share/fonts/truetype`
- Windows: `C:\Windows\Fonts`

Custom font paths are supported in future versions.

### Memory issues

For very long videos or high resolutions:
- Reduce resolution in configuration
- Break video into smaller segments and concatenate
- Use lower texture intensity for backgrounds

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Run quality checks: `black . && ruff check . && mypy words_on_paper`
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Changelog

### 0.1.0 (Initial Release)

- Animated text with fade in/out effects
- Typing effect for character-by-character reveal
- Drop shadow effects
- Horizontal and vertical text orientation
- Multi-layer composition with z-ordering
- Flexible positioning (center, absolute, relative)
- Paper texture background
- YAML and JSON configuration support
- CLI with validate and generate commands
- Comprehensive test coverage

## Future Features

Planned for future releases:

- Custom font file support
- More animation effects (scale, rotate, slide)
- Multi-line text support with line breaking
- Background video support
- Audio synchronization
- Preview mode for quick testing
- Batch processing
- More output formats (GIF, WebP)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review example configurations

---

Made with ❤️ for beautiful text animations
