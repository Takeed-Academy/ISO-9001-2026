#!/usr/bin/env python3
"""Stamps a content hash onto the script URLs so a browser cannot serve a
stale copy of the exam.

The symptom this fixes: the files on disk had the shuffle switched off and the
questions in clause order, but the browser kept showing a different question 1
on every load — because it had `app.js` and `data/questions.js` cached from
before the change and never asked for them again. A static site has no server
to send cache headers, so the browser is entitled to do that.

The fix is to change the URL whenever the content changes:

    <script src="app.js?v=8f2c1a04"></script>

A URL the browser has never seen cannot be in its cache. The hash is derived
from the file's own bytes, so it changes exactly when the file does and not
otherwise — re-running this on unchanged files is a no-op.

`index.html` itself still has a fixed URL and can still be cached, so the very
first load after an update may need one refresh. That is one file rather than
all of them, and it is the one the browser revalidates most readily.
"""

import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
INDEX = os.path.join(SITE, "index.html")
ASSETS = ["data/questions.js", "app.js", "styles.css"]


def short_hash(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:8]


def main():
    with open(INDEX, encoding="utf-8") as fh:
        html = fh.read()

    before = html
    for asset in ASSETS:
        full = os.path.join(SITE, asset.replace("/", os.sep))
        if not os.path.exists(full):
            sys.exit("FAIL: %s is missing" % asset)
        digest = short_hash(full)
        # Match the asset with or without an existing ?v=, so re-running
        # replaces the stamp rather than appending a second one.
        pattern = re.compile(r'(src|href)="%s(\?v=[0-9a-f]+)?"' % re.escape(asset))
        if not pattern.search(html):
            sys.exit("FAIL: %s is not referenced by index.html" % asset)
        html = pattern.sub(lambda m: '%s="%s?v=%s"' % (m.group(1), asset, digest),
                           html)
        print("  %-22s v=%s" % (asset, digest))

    if html == before:
        print("  (no change — the stamps already match the files)")
    else:
        with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        print("  stamped index.html")

    # Prove every referenced asset resolves and carries a stamp.
    for asset in ASSETS:
        assert re.search(r'"%s\?v=[0-9a-f]{8}"' % re.escape(asset), html), asset
    assert not re.search(r'\?v=[0-9a-f]+\?v=', html), "double stamp"
    print("  OK  all %d assets are versioned, none double-stamped" % len(ASSETS))


if __name__ == "__main__":
    main()
