'use strict';
/* One HTML-to-DOM boundary for templates containing API or imported content.
 * Keep escaping individual values; sanitization is an independent final check.
 * Return nodes so callers never reparse sanitized markup through innerHTML.
 */
(() => {
  function fragment(markup) {
    const purifier = window.DOMPurify;
    if (!purifier?.isSupported) {
      throw new Error('Không thể mở nội dung an toàn. Bạn hãy tải lại trang hoặc cập nhật trình duyệt.');
    }
    return purifier.sanitize(String(markup ?? ''), {
      RETURN_DOM_FRAGMENT: true,
      USE_PROFILES: { html: true, svg: true },
      ADD_ATTR: ['target'],
      FORBID_TAGS: ['style'],
    });
  }
  window.LexiDOM = Object.freeze({ fragment });
})();
