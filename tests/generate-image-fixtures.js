/**
 * Generate image processing fixtures for back-to-back comparison with Python.
 *
 * This script creates test images as raw pixel arrays and processes them
 * with the JavaScript implementation using a mock canvas.
 *
 * Run with: npx tsx tests/generate-image-fixtures.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Import from TypeScript source files
import dither from '../src/dither/dither.ts';
import palettes from '../src/dither/data/default-palettes.json';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const fixturesDir = path.join(__dirname, '../python/tests/fixtures');

// Create a mock canvas with ImageData
class MockImageData {
    constructor(width, height, data = null) {
        this.width = width;
        this.height = height;
        this.data = data || new Uint8ClampedArray(width * height * 4);
    }
}

class MockCanvas {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this._imageData = new MockImageData(width, height);
    }

    getContext(type) {
        const canvas = this;
        return {
            getImageData(x, y, width, height) {
                return canvas._imageData;
            },
            putImageData(imageData, x, y) {
                canvas._imageData = imageData;
            }
        };
    }
}

// Create a test image with a specific pattern
function createTestImageData(width, height, pattern) {
    const data = new Uint8ClampedArray(width * height * 4);

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const idx = (y * width + x) * 4;

            if (pattern === 'gradient') {
                // Grayscale gradient
                const gray = Math.floor((x / width) * 255);
                data[idx] = gray;
                data[idx + 1] = gray;
                data[idx + 2] = gray;
                data[idx + 3] = 255;
            } else if (pattern === 'color_gradient') {
                // Color gradient
                data[idx] = Math.floor((x / width) * 255);
                data[idx + 1] = Math.floor((y / height) * 255);
                data[idx + 2] = Math.floor(((width - x) / width) * 255);
                data[idx + 3] = 255;
            } else if (pattern === 'solid_gray') {
                data[idx] = 128;
                data[idx + 1] = 128;
                data[idx + 2] = 128;
                data[idx + 3] = 255;
            }
        }
    }

    return data;
}

async function generateImageFixtures() {
    console.log('Generating image processing fixtures...\n');

    const testCases = [
        {
            name: 'gradient_10x10_quantization',
            width: 10,
            height: 10,
            pattern: 'gradient',
            options: {
                ditheringType: 'quantizationOnly',
                palette: 'default'
            }
        },
        {
            name: 'gradient_10x10_floyd_steinberg',
            width: 10,
            height: 10,
            pattern: 'gradient',
            options: {
                ditheringType: 'errorDiffusion',
                errorDiffusionMatrix: 'floydSteinberg',
                palette: 'default'
            }
        },
        {
            name: 'gradient_10x10_ordered',
            width: 10,
            height: 10,
            pattern: 'gradient',
            options: {
                ditheringType: 'ordered',
                orderedDitheringMatrix: [4, 4],
                palette: 'default'
            }
        },
        {
            name: 'color_gradient_10x10_spectra6',
            width: 10,
            height: 10,
            pattern: 'color_gradient',
            options: {
                ditheringType: 'errorDiffusion',
                errorDiffusionMatrix: 'floydSteinberg',
                palette: palettes.spectra6
            }
        },
        {
            name: 'gradient_20x20_jarvis',
            width: 20,
            height: 20,
            pattern: 'gradient',
            options: {
                ditheringType: 'errorDiffusion',
                errorDiffusionMatrix: 'jarvis',
                palette: 'default'
            }
        },
    ];

    const results = [];

    for (const testCase of testCases) {
        console.log(`Processing: ${testCase.name}`);

        // Create source canvas with test pattern
        const sourceCanvas = new MockCanvas(testCase.width, testCase.height);
        sourceCanvas._imageData = new MockImageData(
            testCase.width,
            testCase.height,
            createTestImageData(testCase.width, testCase.height, testCase.pattern)
        );

        // Create destination canvas
        const destCanvas = new MockCanvas(testCase.width, testCase.height);

        // Get source pixel data (before processing)
        const sourcePixels = Array.from(sourceCanvas._imageData.data);

        // Apply dithering
        await dither(sourceCanvas, destCanvas, testCase.options);

        // Get result pixel data
        const resultPixels = Array.from(destCanvas._imageData.data);

        results.push({
            name: testCase.name,
            width: testCase.width,
            height: testCase.height,
            pattern: testCase.pattern,
            options: testCase.options,
            sourcePixels: sourcePixels,
            resultPixels: resultPixels
        });

        console.log(`  - Source pixels: ${sourcePixels.length}`);
        console.log(`  - Result pixels: ${resultPixels.length}`);
    }

    // Save results
    fs.writeFileSync(
        path.join(fixturesDir, 'image_processing.json'),
        JSON.stringify(results, null, 2)
    );

    console.log('\nGenerated image_processing.json');
}

generateImageFixtures().catch(console.error);
