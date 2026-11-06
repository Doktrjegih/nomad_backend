import { readFile, writeFile } from 'node:fs/promises';

// Soften only the scene image, inside a self-contained SVG image document.
// A filter on body::before can trigger iOS standalone compositing problems;
// no live UI element (or its ancestors) needs a CSS blur filter now.
// Dimensions match the source 3-column × 2-row painted location atlas.
const width = 2172, height = 724;
const source = await readFile('public/art/locations.webp');
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
<defs><filter id="soft-scene" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
<feGaussianBlur stdDeviation="2"/><feColorMatrix type="saturate" values="0.8"/>
</filter></defs>
<image width="${width}" height="${height}" preserveAspectRatio="none" filter="url(#soft-scene)" href="data:image/webp;base64,${source.toString('base64')}"/>
</svg>\n`;
await writeFile('public/art/scene-background.svg', svg);
console.log('Prepared isolated scene background (no live CSS blur).');
