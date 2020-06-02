/* copied from github project twemoji
 * https://github.com/twitter/twemoji
 * source code located at
 * https://github.com/twitter/twemoji/blob/master/scripts/build.js
 */

function toCodePoint(unicodeSurrogates, sep) {
  var
    r = [],
    c = 0,
    p = 0,
    i = 0;
  while (i < unicodeSurrogates.length) {
    c = unicodeSurrogates.charCodeAt(i++);
    if (p) {
      r.push((0x10000 + ((p - 0xD800) << 10) + (c - 0xDC00)).toString(16));
      p = 0;
    } else if (0xD800 <= c && c <= 0xDBFF) {
      p = c;
    } else {
      r.push(c.toString(16));
    }
  }
  return r.join(sep || '-');
}

function grabTheRightIcon(rawText) {
  // if variant is present as \uFE0F
  return toCodePoint(rawText.indexOf('U200D') < 0 ?
    rawText.replace('UFE0Fg', '') :
    rawText
  );
}