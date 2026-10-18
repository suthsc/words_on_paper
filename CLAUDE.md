# CLAUDE.md - Words on Paper Development Guide

This file provides guidance to Claude Code when working with this project.

## Project Overview

**Words on Paper** is a Python video generation system that creates animated text on paper-like backgrounds using MoviePy and PIL. It transforms configuration files (YAML/JSON) into HD videos with smooth animations, typing effects, and layered text.

## Development Environment

This is a Python 3.10+ project managed with `uv` (fast Python package installer), using a `src/` layout (package lives under `src/words_on_paper/`).

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
mypy src/words_on_paper                   # Type check (src/ layout — `mypy words_on_paper` will fail)
isort .                                   # Sort imports

# Run all checks (pre-commit style)
black --check . && ruff check . && mypy src/words_on_paper && pytest
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
├── src/
│   └── words_on_paper/       # Main package (src layout)
│       ├── __init__.py      # Public API exports
│       ├── __main__.py      # Entry point for -m
│       ├── main.py          # Entry point helper
│       ├── cli.py           # Click CLI implementation
│       ├── config/          # Configuration handling
│       │   ├── schema.py    # Pydantic models
│       │   └── loader.py    # Load/parse YAML/JSON
│       ├── rendering/       # Text rendering
│       │   ├── text_renderer.py # PIL text-to-image
│       │   └── fonts.py     # Font loading
│       ├── background/      # Background generation
│       │   └── paper_texture.py # Paper texture with noise
│       ├── composition/     # Frame building
│       │   ├── frame_builder.py # Assemble frames
│       │   ├── animator.py  # Calculate opacity/typing/effects
│       │   └── layer_manager.py # Z-ordering & compositing
│       ├── video/           # Video output
│       │   └── assembler.py # MoviePy video generation (streamed parallel frame batches)
│       └── utils/           # Utilities
│           ├── color.py     # Color parsing/conversion
│           ├── image.py     # RGBA conversion helpers
│           └── timing.py    # Frame/time conversions
├── tests/                   # Unit tests (mirror src/words_on_paper structure)
├── examples/                # Example configurations
├── docs/                    # Additional docs (requirements.md)
├── pyproject.toml          # Project configuration
├── CLAUDE.md               # This file
├── AGENTS.md                # Agent-facing notes
└── README.md               # User documentation
```

Note: `cli.py` and `main.py` live directly under `src/words_on_paper/`, not in a separate `cli/` subpackage.

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
  - `calculate_scale_factor()`, `calculate_letter_spacing()` / `calculate_letter_spacing_centered()`, `calculate_depth_of_field()`: scale, letter-spacing (incl. centered/perspective), and depth-of-field effect curves
- **frame_builder.py**: Build complete frames
  - Compose background + text layers
  - Apply effects (typing, drop shadow, scale, letter spacing, depth of field, opacity)
  - Calculate positioning
- **layer_manager.py**: Z-order and composite layers
  - Sort by z_index
  - Handle alpha compositing

Key design: Stateless frame generation from config + time — each frame is built fresh. The only cross-frame caching is of pure lookups: `load_font()` and `generate_background()` are wrapped in `@lru_cache` (per worker process). The cached background is shared, so callers must copy it before mutating it (`ensure_rgba()` and `composite_layers()` both do).

#### video/ - Video Assembly
- **assembler.py**: MoviePy integration
  - `_stream_frames()` generates frames in parallel chunks via `ProcessPoolExecutor` (`MAX_WORKERS = 8`, `CHUNK_SIZE = 100`) and yields them in order, keeping at most `MAX_WORKERS` chunks in flight
  - `_SequentialFrameFeeder` adapts that iterator to MoviePy's `make_frame(t)`, relying on `write_videofile` requesting `t` in non-decreasing order
  - `generate_video()` builds a `VideoClip(make_frame=...)` sized to exactly `total_frames` and writes it with a per-chunk tqdm progress bar

Key design: Encapsulates MoviePy complexity; peak memory is bounded at ~`MAX_WORKERS * CHUNK_SIZE` frames regardless of video length.

#### utils/ - Utilities
- **color.py**: Hex/RGB/RGBA color parsing
- **image.py**: `ensure_rgba()` and other RGBA conversion helpers
- **timing.py**: Frame ↔ time conversions

Key design: Simple utilities, thoroughly tested.

#### Command-Line Interface
- **cli.py**: Click commands (generate, validate) — lives directly under `src/words_on_paper/`, not a `cli/` subpackage
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
- Effects (`effects`): `typing` (reveal animation), `drop_shadow`, `scale` (scale/depth during fades), `letter_spacing` (sequential or `center_spacing` perspective illusion, clamped to a minimum readable spacing), `depth_of_field` (focal-plane blur/alpha)
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

- **video**: `tests/video/test_assembler.py` covers frame ordering, the in-flight bound in `_stream_frames()`, `_SequentialFrameFeeder` stepping, and an end-to-end `generate_video()` frame-count check (~94% coverage of `assembler.py`)

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
- `video/assembler.py` parallelizes frame generation across an 8-worker `ProcessPoolExecutor` in 100-frame chunks
- Background generation and font loading are cached (`@lru_cache`), so their cost is paid once per worker process rather than per frame

### Memory
Frames are streamed to the encoder rather than materialized up front, so memory stays roughly constant (~`MAX_WORKERS * CHUNK_SIZE` frames, i.e. ~800 frames) regardless of video length. Lower `MAX_WORKERS` or `CHUNK_SIZE` in `video/assembler.py` if that is still too much at high resolutions.

### Optimization Tips
- Use lower resolution for previews
- Reduce texture_intensity (affects background generation)
- Minimize text sequences and effects

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
- Moved package to a `src/` layout (`src/words_on_paper/`)
- Added all core modules with comprehensive testing (213 tests, 91% coverage)
- Streamed video frames through `VideoClip(make_frame=...)` instead of materializing them all, fixing OOM on long videos; cached font loading and background generation
- Clamped absolute/relative text positions to frame bounds; fixed typing-effect position drift
- Added scale, letter-spacing (sequential, centered, perspective), and depth-of-field effects
- Grew example configurations to 11 (including letter-spacing and multi-scene examples like `waiting_for_godot_full_scene.yaml`)
- Parallelized frame generation in `video/assembler.py` via `ProcessPoolExecutor`
- Implemented CLI with validate and generate commands
- Updated dependencies to include MoviePy, Pillow, Pydantic, PyYAML, Click, NumPy, tqdm

## Dependencies

**Production**:
- `moviepy>=1.0.3` - Video composition
- `pillow>=12.1.0` - Image/text rendering
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
| Type checking fails | Run `mypy src/words_on_paper` and fix issues |
| Formatting inconsistencies | Run `black . && isort .` |
| FFmpeg not found | Install FFmpeg for your system |
| Font not found | Check system font paths (macOS: ~/Library/Fonts) |

## Next Steps / Future Work

- [ ] Custom font file support via config
- [x] Scale effect (done — see `effects.scale`)
- [ ] Additional animation effects (rotate, slide)
- [ ] Multi-line text with line breaking
- [ ] Background video support
- [ ] Audio synchronization
- [ ] Performance profiling and optimization
- [ ] Additional output formats (GIF, WebP)
- [x] Streaming/bounded-memory video rendering for long videos (done — `words_on_paper-4eh`)

Full backlog and in-progress work is tracked in beads (`bd ready`, `bd list`), not this list — treat this section as a high-level, occasionally-stale wishlist.

---

**Last Updated**: 2026-10-18
**Current Version**: 0.1.0


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
