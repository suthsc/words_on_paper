# CLAUDE.md - Words on Paper Development Guide

This file provides guidance to Claude Code when working with this project.

## Project Overview

**Words on Paper** is a Python video generation system that creates animated text on paper-like backgrounds using MoviePy and PIL. It transforms configuration files (YAML/JSON) into HD videos with smooth animations, typing effects, and layered text.

## Development Environment

This is a Python 3.9+ project managed with `uv` (fast Python package installer).

### Quick Setup

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install in development mode with all dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Common Development Commands

**Testing:**
```bash
pytest                                    # Run all tests
pytest tests/config/test_schema.py       # Run specific test file
pytest -v                                 # Verbose output
pytest --cov=words_on_paper              # With coverage report
pytest --cov=words_on_paper --cov-report=html  # HTML coverage report
```

**Code Quality:**
```bash
black .                                   # Format code
black --check .                           # Check formatting
ruff check .                              # Lint code
ruff check --fix .                        # Auto-fix issues
mypy words_on_paper                       # Type check
isort .                                   # Sort imports

# Run all checks (pre-commit style)
black --check . && ruff check . && mypy words_on_paper && pytest
```

**CLI Testing:**
```bash
words-on-paper --help                    # Show help
words-on-paper validate examples/simple_fade.yaml  # Validate config
words-on-paper generate examples/simple_fade.yaml -o test.mp4  # Generate video
```

## Project Architecture

### Directory Structure

```
words_on_paper/
├── words_on_paper/           # Main package
│   ├── __init__.py          # Public API exports
│   ├── __main__.py          # Entry point for -m
│   ├── cli.py               # Click CLI implementation
│   ├── config/              # Configuration handling
│   │   ├── schema.py        # Pydantic models
│   │   └── loader.py        # Load/parse YAML/JSON
│   ├── rendering/           # Text rendering
│   │   ├── text_renderer.py # PIL text-to-image
│   │   └── fonts.py         # Font loading
│   ├── background/          # Background generation
│   │   └── paper_texture.py # Paper texture with noise
│   ├── composition/         # Frame building
│   │   ├── frame_builder.py # Assemble frames
│   │   ├── animator.py      # Calculate opacity/typing
│   │   └── layer_manager.py # Z-ordering & compositing
│   ├── video/               # Video output
│   │   └── assembler.py     # MoviePy video generation
│   └── utils/               # Utilities
│       ├── color.py         # Color parsing/conversion
│       └── timing.py        # Frame/time conversions
├── tests/                   # Unit tests (mirror package structure)
├── examples/                # Example configurations
├── pyproject.toml          # Project configuration
├── CLAUDE.md               # This file
└── README.md               # User documentation
```

### Module Overview

#### config/ - Configuration Management
- **schema.py**: Pydantic models for type validation
  - `VideoConfig`: Root configuration
  - `TextSequence`: Individual text animation
  - `Position`, `Font`, `Effects`: Sub-configurations
- **loader.py**: Load YAML/JSON files, validate against schema

Key design: Pydantic models provide runtime validation with clear error messages.

#### rendering/ - Text Rendering
- **text_renderer.py**: Convert text to PIL images
  - Supports horizontal and vertical orientations
  - Hex color parsing and RGB conversion
- **fonts.py**: Font loading with fallback support

Key design: Simple PIL-based rendering, returns RGBA images for compositing.

#### background/ - Background Generation
- **paper_texture.py**: Generate white/textured backgrounds
  - Solid color backgrounds
  - Perlin-like noise for paper texture effect
  - Configurable intensity

Key design: NumPy-based noise generation for performance.

#### composition/ - Frame Assembly
- **animator.py**: Calculate animation properties per frame
  - `calculate_text_opacity()`: Fade in/out curves
  - `calculate_visible_chars()`: Typing effect progress
- **frame_builder.py**: Build complete frames
  - Compose background + text layers
  - Apply effects (drop shadow, opacity)
  - Calculate positioning
- **layer_manager.py**: Z-order and composite layers
  - Sort by z_index
  - Handle alpha compositing

Key design: Stateless frame generation from config + time.

#### video/ - Video Assembly
- **assembler.py**: MoviePy integration
  - Generate frame sequence
  - Create ImageSequenceClip
  - Write video file with progress bar

Key design: Encapsulates MoviePy complexity, uses tqdm for progress.

#### utils/ - Utilities
- **color.py**: Hex/RGB/RGBA color parsing
- **timing.py**: Frame ↔ time conversions

Key design: Simple utilities, thoroughly tested.

#### cli/ - Command-Line Interface
- **cli.py**: Click commands (generate, validate)
- **__main__.py**: Entry point

Key design: Simple, user-friendly error messages.

## Code Quality Standards

### Type Checking
- **mypy** with `check_untyped_defs` enabled (strict)
- All functions should have type hints
- Use `from __future__ import annotations` for forward references

### Formatting
- **Black**: 88-character line length
- **Ruff**: PEP 8, import sorting, comprehension style, bug detection
- **isort**: Import organization

### Testing
- **pytest**: Framework
- Target: >80% coverage
- Each module has corresponding `tests/module_name/test_file.py`
- Use descriptive test names: `test_<function>_<scenario>`
- Include docstrings explaining the test

### Pre-commit Hooks
Pre-commit automatically runs:
- Black formatting
- Ruff linting (with --fix)
- mypy type checking

## Configuration Schema

### Key Concepts

**Video Config**: Root configuration object
- `video`: Resolution (width, height) and FPS
- `background`: Background type and color
- `texts`: List of text sequences

**Text Sequence**: Individual animated text
- Timing: `start_time`, `fade_in_duration`, `display_duration`, `fade_out_duration`
- Content: `content`, `orientation` (horizontal/vertical)
- Positioning: `position.mode` (center/absolute/relative)
- Appearance: `font` (family, size, color)
- Effects: `effects.typing` (for typing animation), `effects.drop_shadow`
- Layering: `z_index` (higher = on top)

### Validation

Pydantic models in `config/schema.py` validate:
- Positive dimensions and durations
- Valid color hex format
- Position coordinates non-negative
- Valid orientation/positioning modes

## Testing Strategy

### Unit Tests
Each module has comprehensive unit tests:
- **config**: Valid/invalid configs, edge cases
- **rendering**: Different fonts, sizes, colors, orientations
- **background**: Different dimensions and texture levels
- **composition**: Animation calculations, frame building, positioning
- **utils**: Color conversions, timing calculations

### Integration Tests
- `test_frame_builder.py`: End-to-end frame generation
- Load config → Build frames → Verify output

### Manual Testing
- Run `words-on-paper validate` on example configs
- Generate test videos with small resolution/duration
- Visual inspection of output

## Performance Considerations

### Frame Generation
- Text rendering: ~100-500ms per frame (PIL)
- Background generation: ~50-100ms per frame (NumPy)
- Compositing: ~50-200ms per frame (PIL)
- Total: ~1-3 seconds per 1080p frame

### Optimization Tips
- Use lower resolution for previews
- Reduce texture_intensity (affects background generation)
- Minimize text sequences and effects
- Cache fonts if needed in future

## Extending the System

### Adding New Effects
1. Add effect configuration to `schema.py`
2. Add calculation method to `composition/animator.py`
3. Apply effect in `composition/frame_builder.py`
4. Add tests in `tests/composition/`

### Adding New Positioning Modes
1. Add mode to `Position.mode` Literal in `schema.py`
2. Implement in `_calculate_position()` in `frame_builder.py`
3. Add tests in `tests/composition/test_frame_builder.py`

### Adding New Background Types
1. Add type to `BackgroundConfig.type` in `schema.py`
2. Implement in `background/paper_texture.py`
3. Add tests in `tests/background/`

## Debugging Tips

### Configuration Issues
- Use `words-on-paper validate config.yaml` for schema validation
- Check color hex format: must be #RRGGBB or #RRGGBBAA
- Verify timing values are non-negative

### Frame Issues
- Enable logging in `composition/frame_builder.py`
- Test with single text sequence first
- Check positioning mode and coordinates

### Video Output
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check output path is writable
- Use lower resolution for quick testing

## Recent Changes

- Renamed package from `my_python_project` to `words_on_paper`
- Added all core modules with comprehensive testing (121 tests, 80% coverage)
- Created 4 example configurations (simple_fade, typing_effect, overlapping_phrases, complete_demo)
- Implemented CLI with validate and generate commands
- Updated dependencies to include MoviePy, Pillow, Pydantic, PyYAML, Click, NumPy, tqdm

## Dependencies

**Production**:
- `moviepy>=1.0.3` - Video composition
- `pillow>=10.0.0` - Image/text rendering
- `pydantic>=2.0.0` - Configuration validation
- `pyyaml>=6.0` - YAML support
- `click>=8.0.0` - CLI framework
- `numpy>=1.24.0` - Array operations for noise
- `tqdm>=4.65.0` - Progress bars

**Development**:
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reporting
- `black>=23.0` - Code formatting
- `ruff>=0.1.0` - Linting
- `mypy>=1.0` - Type checking
- `isort>=5.0` - Import sorting
- `pre-commit>=3.0` - Git hooks

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `uv pip install -e ".[dev]"` |
| Tests fail with coverage | Run `pytest --cov=words_on_paper` |
| Type checking fails | Run `mypy words_on_paper` and fix issues |
| Formatting inconsistencies | Run `black . && isort .` |
| FFmpeg not found | Install FFmpeg for your system |
| Font not found | Check system font paths (macOS: ~/Library/Fonts) |

## Next Steps / Future Work

- [ ] Custom font file support via config
- [ ] Additional animation effects (scale, rotate, slide)
- [ ] Multi-line text with line breaking
- [ ] Background video support
- [ ] Audio synchronization
- [ ] Performance profiling and optimization
- [ ] Additional output formats (GIF, WebP)

---

**Last Updated**: 2026-02-01
**Current Version**: 0.1.0
