/**
 * Generate test fixtures for Python comparison tests.
 * This script creates JSON files with expected outputs from the JavaScript implementation.
 *
 * Run with: npx tsx tests/generate-fixtures.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Import from TypeScript source files directly (using tsx or ts-node)
import colorHelpers from '../src/dither/functions/color-helpers.ts';
import createBayerMatrix from '../src/dither/functions/bayer-matrix.ts';
import findClosestPaletteColor from '../src/dither/functions/find-closest-palette-color.ts';
import diffusionMaps from '../src/dither/data/diffusion-maps.ts';
import palettes from '../src/dither/data/default-palettes.json';
import deviceColors from '../src/dither/data/default-device-colors.json';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const fixturesDir = path.join(__dirname, '../python/tests/fixtures');

// Ensure fixtures directory exists
if (!fs.existsSync(fixturesDir)) {
    fs.mkdirSync(fixturesDir, { recursive: true });
}

// Test hexToRgb
const hexToRgbTests = [
    '#fff',
    '#FFF',
    '#000',
    '#f00',
    '#00ff00',
    '#0000FF',
    '#123456',
    '#abcdef',
    '#ABCDEF',
    'fff',
    '000',
    '123456',
    '#191E21',
    '#e8e8e8',
    '#2157ba',
    '#0f380f',
];

const hexToRgbResults = hexToRgbTests.map(hex => ({
    input: hex,
    output: colorHelpers.hexToRgb(hex)
}));

fs.writeFileSync(
    path.join(fixturesDir, 'hex_to_rgb.json'),
    JSON.stringify(hexToRgbResults, null, 2)
);
console.log('Generated hex_to_rgb.json');

// Test Bayer matrix
const bayerMatrixTests = [
    [1, 1],
    [2, 2],
    [3, 3],
    [4, 4],
    [5, 5],
    [6, 6],
    [7, 7],
    [8, 8],
    [2, 4],
    [4, 2],
    [3, 5],
];

const bayerMatrixResults = bayerMatrixTests.map(size => ({
    input: size,
    output: createBayerMatrix(size)
}));

fs.writeFileSync(
    path.join(fixturesDir, 'bayer_matrix.json'),
    JSON.stringify(bayerMatrixResults, null, 2)
);
console.log('Generated bayer_matrix.json');

// Test findClosestPaletteColor
const colorPalette = [
    [0, 0, 0],        // Black
    [255, 255, 255],  // White
    [255, 0, 0],      // Red
    [0, 255, 0],      // Green
    [0, 0, 255],      // Blue
];

const findClosestTests = [
    [0, 0, 0, 255],
    [255, 255, 255, 255],
    [128, 128, 128, 255],
    [200, 50, 50, 255],
    [50, 200, 50, 255],
    [50, 50, 200, 255],
    [100, 100, 100, 255],
    [200, 200, 200, 255],
    [255, 128, 0, 255],
    [128, 0, 255, 255],
    [0, 128, 128, 255],
    [64, 64, 64, 255],
    [192, 192, 192, 255],
];

const findClosestResults = findClosestTests.map(pixel => ({
    input: { pixel, palette: colorPalette },
    output: findClosestPaletteColor(pixel, colorPalette)
}));

fs.writeFileSync(
    path.join(fixturesDir, 'find_closest_color.json'),
    JSON.stringify(findClosestResults, null, 2)
);
console.log('Generated find_closest_color.json');

// Test diffusion maps
const diffusionMapNames = [
    'floydSteinberg',
    'falseFloydSteinberg',
    'jarvis',
    'stucki',
    'burkes',
    'sierra3',
    'sierra2',
    'Sierra2-4A',
];

const diffusionMapResults = {};
diffusionMapNames.forEach(name => {
    diffusionMapResults[name] = diffusionMaps[name]();
});

fs.writeFileSync(
    path.join(fixturesDir, 'diffusion_maps.json'),
    JSON.stringify(diffusionMapResults, null, 2)
);
console.log('Generated diffusion_maps.json');

// Test palettes
fs.writeFileSync(
    path.join(fixturesDir, 'palettes.json'),
    JSON.stringify(palettes, null, 2)
);
console.log('Generated palettes.json');

// Test device colors
fs.writeFileSync(
    path.join(fixturesDir, 'device_colors.json'),
    JSON.stringify(deviceColors, null, 2)
);
console.log('Generated device_colors.json');

// Test quant error calculation
const quantErrorTests = [
    { oldPixel: [100, 100, 100, 255], newPixel: [0, 0, 0, 255] },
    { oldPixel: [200, 150, 50, 255], newPixel: [255, 255, 255, 255] },
    { oldPixel: [128, 64, 192, 255], newPixel: [255, 0, 0, 255] },
    { oldPixel: [50, 100, 150, 255], newPixel: [0, 0, 255, 255] },
];

const quantErrorResults = quantErrorTests.map(test => ({
    input: test,
    output: test.oldPixel.map((color, i) => color - test.newPixel[i])
}));

fs.writeFileSync(
    path.join(fixturesDir, 'quant_error.json'),
    JSON.stringify(quantErrorResults, null, 2)
);
console.log('Generated quant_error.json');

// Test add quant error
const addQuantErrorTests = [
    { pixel: [100, 100, 100, 255], quantError: [50, -50, 25, 0], factor: 0.5 },
    { pixel: [0, 0, 0, 255], quantError: [100, 100, 100, 0], factor: 7/16 },
    { pixel: [200, 150, 100, 255], quantError: [-50, 50, -25, 0], factor: 3/16 },
];

const addQuantErrorResults = addQuantErrorTests.map(test => ({
    input: test,
    output: test.pixel.map((color, i) => color + test.quantError[i] * test.factor)
}));

fs.writeFileSync(
    path.join(fixturesDir, 'add_quant_error.json'),
    JSON.stringify(addQuantErrorResults, null, 2)
);
console.log('Generated add_quant_error.json');

// Test pixelXY conversion
const pixelXYTests = [
    { index: 0, width: 10 },
    { index: 5, width: 10 },
    { index: 10, width: 10 },
    { index: 15, width: 10 },
    { index: 99, width: 10 },
    { index: 0, width: 100 },
    { index: 50, width: 100 },
    { index: 150, width: 100 },
];

const pixelXYResults = pixelXYTests.map(test => ({
    input: test,
    output: [test.index % test.width, Math.floor(test.index / test.width)]
}));

fs.writeFileSync(
    path.join(fixturesDir, 'pixel_xy.json'),
    JSON.stringify(pixelXYResults, null, 2)
);
console.log('Generated pixel_xy.json');

// Test ordered dither pixel value
const orderedDitherTests = [
    { pixel: [100, 100, 100, 255], coordinates: [0, 0], matrixSize: [4, 4], threshold: 64 },
    { pixel: [128, 128, 128, 255], coordinates: [1, 1], matrixSize: [4, 4], threshold: 64 },
    { pixel: [200, 100, 50, 255], coordinates: [2, 3], matrixSize: [4, 4], threshold: 64 },
    { pixel: [50, 150, 200, 255], coordinates: [3, 2], matrixSize: [4, 4], threshold: 64 },
];

const orderedDitherResults = orderedDitherTests.map(test => {
    const thresholdMap = createBayerMatrix(test.matrixSize);
    const mapHeight = thresholdMap.length;
    const mapWidth = thresholdMap[0].length;
    const factor = thresholdMap[test.coordinates[1] % mapHeight][test.coordinates[0] % mapWidth] / (mapHeight * mapWidth);
    const output = test.pixel.map(color => color + factor * test.threshold);
    return {
        input: test,
        thresholdMap: thresholdMap,
        factor: factor,
        output: output
    };
});

fs.writeFileSync(
    path.join(fixturesDir, 'ordered_dither.json'),
    JSON.stringify(orderedDitherResults, null, 2)
);
console.log('Generated ordered_dither.json');

console.log('\nAll fixtures generated successfully!');
