"""Layer composition and z-ordering."""

from PIL import Image


def composite_layers(
    background: Image.Image,
    layers: list[tuple[Image.Image, int, int, int]],
) -> Image.Image:
    """
    Composite multiple layers on top of a background.

    Args:
        background: Background image
        layers: List of (image, x, y, z_index) tuples

    Returns:
        Composited image
    """
    result = background.copy()

    # Sort layers by z_index
    sorted_layers = sorted(layers, key=lambda x: x[3])

    for layer_img, x, y, _ in sorted_layers:
        _paste_with_alpha(result, layer_img, (x, y))

    return result


def _paste_with_alpha(
    background: Image.Image, layer: Image.Image, pos: tuple[int, int]
) -> None:
    """
    Paste a layer onto background, respecting alpha channel.

    Args:
        background: Background image (must be RGB or RGBA)
        layer: Layer to paste (must be RGBA)
        pos: (x, y) position
    """
    # Convert background to RGBA if needed
    if background.mode != "RGBA":
        background = background.convert("RGBA")

    # Ensure layer is RGBA
    if layer.mode != "RGBA":
        layer = layer.convert("RGBA")

    # Paste with alpha
    background.paste(layer, pos, layer)
