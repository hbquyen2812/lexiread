/* Real renderer/event-path regressions in a Node VM; not browser or layout QA. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const rootPath = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(rootPath, name), 'utf8');
const guides = JSON.parse(read('data/strategy_guides.json')).guides;

class NodeStub {
  constructor(attributes = {}, root = null) {
    this.attributes = {...attributes}; this.root = root; this.dataset = {};
    for (const [name, value] of Object.entries(attributes)) if (name.startsWith('data-')) this.dataset[name.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = value;
    this.textContent = ''; this.innerHTML = ''; this.value = ''; this.hidden = false;
    this.classes = new Set();
    this.classList = {add: value => this.classes.add(value), toggle: (value, on) => on ? this.classes.add(value) : this.classes.delete(value)};
  }
  matches(selector) { return selector.split(',').some(part => this.hasAttribute(part.trim().slice(1, -1))); }
  closest(selector) {
    if (selector === '#main') return this.inMain ? this : null;
    if (selector === '.skip-link') return null;
    if (this.matches(selector)) return this;
    return this.root?.matches(selector) ? this.root : null;
  }
  hasAttribute(name) { return Object.hasOwn(this.attributes, name); }
  setAttribute(name, value) { this.attributes[name] = value; }
  focus() { this.focused = true; }
  scrollIntoView(options) { this.scrolled = options; }
}
class RootStub extends NodeStub {
  constructor(attributes = {}) { super(attributes); this.nodes = new Map(); this.groups = new Map(); }
  querySelector(selector) {
    if (!this.nodes.has(selector)) this.nodes.set(selector, new NodeStub({[selector.slice(1, -1)]: ''}, this));
    return this.nodes.get(selector);
  }
  querySelectorAll(selector) { return this.groups.get(selector) || []; }
}
function environment(items = guides) {
  const handlers = new Map(), elements = new Map(), groups = new Map(), storage = new Map(), intervals = new Map();
  const env = {now: 1000, failRead: false, failWrite: false, items, handlers, elements, groups, storage, intervals, messages: []};
  const document = {
    getElementById: id => id === 'strategy-guides-data' ? {textContent: JSON.stringify(env.items)} : elements.get('#' + id),
    querySelector: selector => elements.get(selector) || null,
    querySelectorAll: selector => groups.get(selector) || [],
    addEventListener: (event, fn) => { if (!handlers.has(event)) handlers.set(event, []); handlers.get(event).push(fn); }
  };
  const scope = {
    document, localStorage: {getItem: key => { if (env.failRead) throw Error('denied'); return storage.get(key) ?? null; }, setItem: (key, value) => { if (env.failWrite) throw Error('quota'); storage.set(key, value); }},
    window: {addEventListener() {}, scrollTo() {}}, location: {hash: ''},
    Date: class extends Date {static now() {return env.now;}},
    FormData: class {constructor(form) {this.form = form;} get(name) {return this.form.values?.[name] ?? null;}},
    setInterval: fn => {const id = intervals.size + 1; intervals.set(id, fn); return id;},
    clearInterval: id => intervals.delete(id), queueMicrotask: fn => fn(),
    state: {}, toast: message => env.messages.push(message), lexicalDetails: () => '', lexicalContext: () => ''
  };
  vm.createContext(scope);
  vm.runInContext(read('static/learning_hub.js'), scope);
  const app = read('static/app.js');
  vm.runInContext(app.slice(app.indexOf('const $ ='), app.indexOf('const uid =')), scope);
  vm.runInContext(app.split('\n').find(line => line.startsWith('function heading(')), scope);
  vm.runInContext(read('static/practice_tools.js'), scope);
  env.scope = scope; env.hub = scope.window.LexiHub;
  env.fire = (event, target) => {for (const fn of handlers.get(event) || []) fn({target, preventDefault() {}});};
  return env;
}

function planData() {
  return {general: [{slug: 'first', title: 'A quiet walk', status: 'new'}, {slug: 'second', title: 'Another day', status: 'new'}],
    ielts: [{slug: 'academic', title: 'A changing city', status: 'new'}],
    toeic: [{slug: 'office', title: 'Office requests', attempt_count: 0}], due: 3};
}
function testPlans() {
  const env = environment();
  for (const corrupt of ['{broken', 'null', '17', '"a string"', '[]', '{"goal":"__proto__","minutes":"45"}']) {
    env.storage.set('lexiread.plan.v1', corrupt);
    const root = new RootStub({'data-daily-plan': ''});
    assert.doesNotThrow(() => env.hub.plan(root, planData()));
    assert.match(root.innerHTML, /value="general" selected/);
    assert.match(root.innerHTML, /value="15" selected/);
  }
  env.failRead = true;
  assert.doesNotThrow(() => env.hub.plan(new RootStub(), null));
  env.failRead = false;
  const root = new RootStub({'data-daily-plan': ''});
  env.hub.plan(root, planData());
  root.querySelector('[data-plan-goal]').value = 'toeic';
  root.querySelector('[data-plan-time]').value = '30';
  env.failWrite = true;
  env.fire('change', root.querySelector('[data-plan-goal]'));
  assert.match(root.innerHTML, /value="toeic" selected/);
  assert.match(root.innerHTML, /value="30" selected/);
  assert.match(root.innerHTML, /Office requests/);
  assert.match(root.querySelector('[data-plan-save-note]').textContent, /không cho lưu/);
  assert.match(root.innerHTML, /aria-label="Mục tiêu"/);
  assert.match(root.innerHTML, /aria-label="Thời gian hôm nay"/);
  env.hub.plan(root, {...planData(), due: '<img src=x onerror=alert(1)>'});
  assert.doesNotMatch(root.innerHTML, /<img/);

  // A daily recommendation changes at Vietnam midnight, not UTC midnight.
  env.storage.clear(); env.failWrite = false;
  env.now = Date.UTC(2026, 9, 25, 16, 59, 59); env.hub.plan(root, planData()); const before = root.innerHTML;
  env.now += 1000; env.hub.plan(root, planData()); assert.notEqual(root.innerHTML, before);
  env.now = Date.UTC(2026, 9, 25, 23, 59, 59); env.hub.plan(root, planData()); const evening = root.innerHTML;
  env.now += 1000; env.hub.plan(root, planData()); assert.equal(root.innerHTML, evening);
  console.log('PASS malformed/blocked plan storage, temporary selections, accessible labels and Vietnam day boundary');
}

function testGuideRenderingAndSearch() {
  const altered = structuredClone(guides); altered[0].title = '<img src=x onerror=alert(1)>';
  const env = environment(altered), root = new RootStub({'data-guide-root': ''});
  for (const raw of ['{}', '[null,{},12]', '"not-an-array"']) {
    env.storage.set('lexiread.guides.read', raw);
    assert.doesNotThrow(() => env.hub.guidePage(root));
  }
  const results = root.querySelector('[data-guide-results]');
  assert.doesNotMatch(results.innerHTML, /<img/); assert.match(results.innerHTML, /&lt;img/);
  env.hub.guidePage(root, 'toeic');
  assert.equal(root.querySelector('[data-guide-count]').textContent, '6 hướng dẫn');
  const search = root.querySelector('[data-guide-search]'); search.value = 'ngu phap'; env.fire('input', search);
  assert.equal(root.querySelector('[data-guide-count]').textContent, '1 hướng dẫn');
  search.value = 'Part 7'; env.fire('input', search);
  assert.equal(root.querySelector('[data-guide-count]').textContent, '2 hướng dẫn');
  env.hub.guidePage(root, 'ielts-tfng'); assert.doesNotMatch(root.innerHTML, /<img/);
  assert.match(root.innerHTML, /&lt;img/); assert.match(root.innerHTML, /#ielts\/tfng/);
  const detail = new RootStub({'data-guide-id': 'ielts-short-answers'}), form = new RootStub({'data-guide-example': ''});
  form.root = detail; form.values = {example: ' Courtyard '};
  const disclosure = new NodeStub(); form.parentElement = {querySelector: () => disclosure};
  env.fire('submit', form);
  assert.match(form.querySelector('[data-guide-feedback]').textContent, /^✓ Đúng/);
  assert.equal(disclosure.open, true);
  form.values.example = 'old kitchen'; env.fire('submit', form);
  assert.match(form.querySelector('[data-guide-feedback]').textContent, /^Chưa đúng/);
  console.log('PASS guide escaping, malformed read markers and accent-insensitive exam/type search');
}

function toeicFixture(overrides = {}) {
  return {slug: 'a', title: 'Grammar practice', description: 'Ngữ pháp công việc', mode_label: 'Part 5', level: 'B1', parts: [5], duration_minutes: 12, question_count: 3, attempt_count: 0, best_score: 0, ...overrides};
}
function testToeicFilters() {
  const env = environment(), root = new RootStub({'data-toeic-library': ''});
  const items = [toeicFixture({title: '<img src=x onerror=alert(1)>'}),
    toeicFixture({slug: 'b', title: 'Message cohesion', description: 'Nối câu', parts: [6], duration_minutes: 20, question_count: 4, attempt_count: 2}),
    toeicFixture({slug: 'c', title: 'Multiple passages', description: 'Đọc nhiều văn bản', parts: [7], duration_minutes: 25, question_count: 6}),
    toeicFixture({slug: 'd', title: 'Mixed review', description: 'Ôn hỗn hợp', parts: [5, 6, 7], duration_minutes: 45, question_count: 7, attempt_count: 1})];
  env.hub.toeicCatalog(root, items, '6');
  assert.equal(root.querySelector('[data-toeic-count]').textContent, '2 bộ luyện · 11 câu hỏi');
  function change(name, value) {const input = root.querySelector('[data-toeic-' + name + ']'); input.value = value; env.fire('change', input);}
  change('status', 'new'); assert.match(root.querySelector('[data-toeic-count]').textContent, /^0 bộ/);
  change('part', '7'); assert.equal(root.querySelector('[data-toeic-count]').textContent, '1 bộ luyện · 6 câu hỏi');
  change('duration', '15'); assert.match(root.querySelector('[data-toeic-count]').textContent, /^0 bộ/);
  change('part', ''); change('status', ''); change('duration', '');
  const search = root.querySelector('[data-toeic-search]'); search.value = 'ngu phap'; env.fire('input', search);
  const results = root.querySelector('[data-toeic-results]');
  assert.equal(root.querySelector('[data-toeic-count]').textContent, '1 bộ luyện · 3 câu hỏi');
  assert.doesNotMatch(results.innerHTML, /<img/); assert.match(results.innerHTML, /&lt;img/);
  env.hub.toeicCatalog(root, Array.from({length: 12}, (_, i) => toeicFixture({slug: 'set-' + i})));
  assert.equal((results.innerHTML.match(/<article/g) || []).length, 9);
  env.fire('click', root.querySelector('[data-toeic-more]'));
  assert.equal((results.innerHTML.match(/<article/g) || []).length, 12);
  assert.equal(root.querySelector('[data-toeic-more]').hidden, true);
  console.log('PASS combined TOEIC part/status/duration/search filters, count totals, escaping and pagination');
}

function testPracticeTools() {
  const env = environment(), {scope} = env;
  const question = (id, part) => ({id, part, prompt: '<img src=x onerror=alert(1)>', options: ['A < B', 'B', 'C', 'D'], document_ids: ['doc']});
  scope.state.toeicSet = {title: 'Practice', mode_label: 'Reading', level: 'B1', duration_minutes: 15, question_count: 3, instructions: 'Read carefully',
    parts: [7], questions: [question('q1', 7), question('q2', 7), question('q3', 7)],
    documents: [{id: 'doc', kind: 'email', heading: 'A message', body: '<script>alert(1)</script>'}], focus_vocabulary: []};
  scope.state.toeicSession = {answers: {q1: 0, q2: -1, q3: 4}, elapsedMs: 0, clockStartedAt: 1000, result: null, flags: 'malformed'};
  for (const name of ['progress', 'count', 'clock', 'pause']) env.elements.set('[data-practice-' + name + ']', new NodeStub());
  env.elements.set('#main', new RootStub());
  const jumps = ['q1', 'q2', 'q3'].map((id, i) => {const n = new NodeStub({'data-practice-jump': id}); n.textContent = String(i + 1); return n;});
  env.groups.set('[data-practice-jump]', jumps);
  for (const id of ['q1', 'q2', 'q3']) env.elements.set('#practice-question-' + id, new NodeStub());
  scope.updatePracticeProgress();
  assert.equal(env.elements.get('[data-practice-count]').textContent, '1 / 3 câu đã trả lời');
  assert.equal(jumps[0].classes.has('is-answered'), true); assert.equal(jumps[1].classes.has('is-answered'), false);
  env.fire('click', new NodeStub({'data-practice-unanswered': ''}));
  assert.equal(env.elements.get('#practice-question-q2').focused, true);
  scope.state.toeicSession.answers.q2 = 2;
  env.fire('click', new NodeStub({'data-practice-unanswered': ''}));
  assert.equal(env.elements.get('#practice-question-q3').focused, true);
  scope.state.toeicSession.answers.q3 = 1;
  env.fire('click', new NodeStub({'data-practice-unanswered': ''})); assert.equal(env.messages.length, 1);
  const flag = new NodeStub({'data-practice-flag': 'q1'}); env.fire('click', flag);
  assert.equal(flag.attributes['aria-pressed'], 'true'); env.fire('click', flag); assert.equal(flag.attributes['aria-pressed'], 'false');

  env.now = 6000; const pause = new NodeStub({'data-practice-pause': ''}); env.fire('click', pause);
  assert.equal(scope.practiceElapsed(scope.state.toeicSession), 5000);
  env.now = 16000; scope.updatePracticeProgress(); assert.equal(env.elements.get('[data-practice-clock]').textContent, '00:05');
  env.fire('click', pause); env.now = 18500; assert.equal(scope.practiceElapsed(scope.state.toeicSession), 7500);
  scope.pausePracticeClock(); env.now = 30000; assert.equal(scope.practiceElapsed(scope.state.toeicSession), 7500);
  assert.equal(scope.practiceElapsed({elapsedMs: 'broken', clockStartedAt: null}), 0);
  assert.equal(scope.practiceElapsed({elapsedMs: 2000, clockStartedAt: 40000}), 2000);
  scope.renderToeicPractice();
  const rendered = env.elements.get('#main').innerHTML;
  assert.doesNotMatch(rendered, /<img|<script>/); assert.match(rendered, /&lt;script&gt;/); assert.match(rendered, /&lt;img/);
  assert.equal(scope.practiceElapsed(scope.state.toeicSession), 7500);
  scope.state.toeicSession.result = {score: 2, total: 3, percentage: 67, by_part: {7: {score: 2, total: 3}}, results: []};
  scope.renderToeicPractice(); assert.equal(env.intervals.size, 0);
  const correct = new NodeStub({'data-practice-correct': 'true'}), wrong = new NodeStub({'data-practice-correct': 'false'});
  env.groups.set('[data-practice-correct]', [correct, wrong]);
  const wrongOnly = new NodeStub({'data-practice-wrong': ''}); wrongOnly.checked = true; env.fire('change', wrongOnly);
  assert.equal(correct.hidden, true); assert.equal(wrong.hidden, false);
  console.log('PASS valid-answer navigation, flags, timer pause/resume, rendering escapes and wrong-answer filter');
}

function testReaderVisibility() {
  const env = environment(), {scope} = env, app = read('static/app.js');
  vm.runInContext(read('static/library.js'), scope);
  // Execute the production renderer and its text helper, without booting the SPA.
  vm.runInContext(app.slice(app.indexOf('function escapeRegex('), app.indexOf('async function readerPage(')), scope);
  vm.runInContext(app.slice(app.indexOf('function renderReader('), app.indexOf('async function vocabPage(')), scope);
  const main = new RootStub(), content = new RootStub(), extraTabs = [];
  env.elements.set('#main', main); env.elements.set('#reader-content', content);
  scope.readingExtraTab = (_box, reading) => extraTabs.push([scope.state.readingTab, reading.id]);
  const fixture = () => ({id: 'reader-1', title: 'A short reading', catalog_slug: 'short-reading', word_count: 12,
    paragraphs: ['A quiet courtyard welcomes visitors.'], progress: {},
    analysis: {vocabulary: [], grammar: [], translations: []},
    lesson: {track: 'ielts', level: 'B1', topic: 'Places', revision: 1, faqs: [],
      provenance: '<img src=x onerror=alert(1)>', level_note: '<script>alert(1)</script>'}});
  const reset = () => Object.assign(scope.state, {reading: fixture(), readingTab: 'text', boot: {ai_enabled: false}, qaHistory: [], readerWords: [], translation: false});
  const tabs = () => [...main.innerHTML.matchAll(/data-action="reader-tab" data-tab="([^"]+)"/g)].map(match => match[1]);

  reset(); scope.renderReader();
  assert.deepEqual(tabs(), ['text', 'quiz']);
  assert.doesNotMatch(content.innerHTML, /data-action="ask-paragraph"/);
  assert.match(content.innerHTML, /A quiet courtyard welcomes visitors\./);
  assert.match(main.innerHTML, /data-action="study-reading"/);
  assert.doesNotMatch(main.innerHTML, /id="translation-toggle"/);
  const about = main.innerHTML.match(/<details\b([^>]*)class="lesson-about"[^>]*>([\s\S]*?)<\/details>/);
  assert.ok(about, 'the source note remains available as a disclosure');
  assert.doesNotMatch(about[0].split('>')[0], /\bopen\b/);
  assert.doesNotMatch(about[2], /<img|<script>/);
  assert.match(about[2], /&lt;img/); assert.match(about[2], /&lt;script&gt;/);

  // A stale selection must return to the passage when its data is unavailable.
  for (const missingTab of ['words', 'grammar']) {
    scope.state.readingTab = missingTab; scope.renderReader();
    assert.equal(scope.state.readingTab, 'text');
    assert.deepEqual(tabs(), ['text', 'quiz']);
  }
  reset(); scope.state.reading.catalog_slug = ''; scope.renderReader();
  assert.deepEqual(tabs(), ['text']);
  assert.match(main.innerHTML, /data-action="edit-reading"/);
  assert.match(main.innerHTML, /data-action="reading-prompt"/);

  // Each real source of explanations independently keeps Help discoverable.
  for (const enable of [
    () => {scope.state.reading.lesson.faqs = [{question: 'Why?', answer_vi: 'Vì vậy.'}];},
    () => {scope.state.qaHistory = [{id: 'saved-answer'}];},
    () => {scope.state.boot.ai_enabled = true;}
  ]) {
    reset(); enable(); scope.renderReader(); assert.ok(tabs().includes('help'));
    scope.state.readingTab = 'help'; scope.renderReader();
    assert.deepEqual(extraTabs.at(-1), ['help', 'reader-1']);
  }

  // Hiding empty tabs must not remove the normal vocabulary-saving path.
  reset();
  scope.state.reading.analysis.vocabulary = [{word: 'courtyard', pos: 'noun', meaning_vi: '<img src=x onerror=alert(1)>'}];
  scope.state.readingTab = 'words'; scope.renderReader();
  assert.deepEqual(tabs(), ['text', 'words', 'quiz']);
  assert.match(content.innerHTML, /data-action="save-candidates"/);
  assert.match(content.innerHTML, /id="select-all-candidates"/);
  assert.match(content.innerHTML, /aria-label="Chọn courtyard"/);
  assert.match(content.innerHTML, /&lt;img/); assert.doesNotMatch(content.innerHTML, /<img/);
  scope.state.reading.analysis.grammar = [{pattern: 'can + verb', evidence: 'can visit', explanation_vi: 'Có thể làm gì', example: 'We can visit.', example_vi: 'Chúng ta có thể ghé thăm.'}];
  scope.state.readingTab = 'grammar'; scope.renderReader();
  assert.ok(tabs().includes('grammar')); assert.match(content.innerHTML, /can \+ verb/);
  console.log('PASS reader hides empty tabs, retains available explanations and vocabulary save, and collapses escaped provenance');
}

testPlans(); testGuideRenderingAndSearch(); testToeicFilters(); testPracticeTools(); testReaderVisibility();
