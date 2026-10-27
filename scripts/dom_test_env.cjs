const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const createDOMPurify = require('../static/vendor/purify.min.js');

function installSafeDOM(window) {
  const scope = { window: { DOMPurify: createDOMPurify(window) } };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/safe_dom.js'), 'utf8'), scope);
  return scope.window.LexiDOM;
}

function environment() {
  const dom = new JSDOM('<!doctype html><html><body><main id="main"></main></body></html>', {url:'https://lexiread.test/'});
  dom.window.LexiDOM = installSafeDOM(dom.window);
  // Layout methods are outside jsdom's remit, not security substitutes.
  dom.window.HTMLElement.prototype.scrollIntoView = function () {};
  return dom;
}
module.exports = { environment, installSafeDOM };
