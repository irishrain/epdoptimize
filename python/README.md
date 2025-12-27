# epdoptimize (Python)

A Python library for optimizing and dithering images for electronic paper (e-paper) displays.

This is a Python port of the [epdoptimize](https://github.com/irishrain/epdoptimize) Node.js library.

## Installation

```bash
pip install epdoptimize
```

Or install from source:

```bash
cd python
pip install -e .
```

## Usage

```python
from PIL import Image
from epdoptimize import dither_image, replace_colors, get_default_palettes, get_device_colors

# Load an image
image = Image.open("photo.jpg")

# Get the palette for your e-paper display
palette = get_default_palettes("spectra6")
device_colors = get_device_colors("spectra6")

# Dither the image using Floyd-Steinberg error diffusion
dithered = dither_image(image, {
    "ditheringType": "errorDiffusion",
    "errorDiffusionMatrix": "floydSteinberg",
    "palette": palette
})

# Map the dithered colors to device colors for display
final = replace_colors(dithered, palette, device_colors)

# Save the result
final.save("output.png")
```

## Dithering Options

### Dithering Types

- `errorDiffusion` - Error diffusion dithering (default)
- `ordered` - Ordered/Bayer dithering
- `random` - Random dithering
- `quantizationOnly` - No dithering, just color quantization

### Error Diffusion Matrices

- `floydSteinberg` - Classic Floyd-Steinberg (default)
- `falseFloydSteinberg` - Simplified version
- `jarvis` - Jarvis-Judice-Ninke
- `stucki` - Stucki
- `burkes` - Burkes
- `sierra3` - Sierra-3
- `sierra2` - Sierra-2
- `Sierra2-4A` - Sierra-2-4A (lightweight)

### Available Palettes

- `default` - Black and white
- `gameboy` - Game Boy green palette
- `spectra6` - E Ink Spectra 6 colors
- `acep` - E Ink Advanced Color ePaper (7 colors)

## License

MIT
