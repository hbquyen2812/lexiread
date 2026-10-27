/* Copy the exact lockfile dependency. Runtime pages never load it from a CDN. */
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'node_modules/dompurify');
const target = path.join(root, 'static/vendor');
fs.mkdirSync(target, { recursive: true });
for (const [from, to] of [['dist/purify.min.js', 'purify.min.js'], ['LICENSE', 'DOMPurify-LICENSE']]) {
  fs.copyFileSync(path.join(source, from), path.join(target, to));
}
console.log('Vendored DOMPurify ' + require(path.join(source, 'package.json')).version);
