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

`index.html` itself still has a fixed URL and can still be cached, so the
stamps it carries can themselves be yesterday's. Nothing written inside an
HTML file can prevent that — only a response header can, and a static host
sends its own. So this script also writes a build id two places:

    index.html   <meta name="build" content="e6ff3b4b">
    version.json {"build": "e6ff3b4b"}

and the page fetches version.json with cache:"no-store" on load. Equal means
the page is current; different means the page is the stale one, and it
reloads once. The id is a hash of the three asset hashes, so it changes
exactly when something shipped changes.
"""

import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
INDEX = os.path.join(SITE, "index.html")
VERSION = os.path.join(SITE, "version.json")
ASSETS = ["data/questions.js", "app.js", "styles.css"]


def short_hash(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:8]


def main():
    with open(INDEX, encoding="utf-8") as fh:
        html = fh.read()

    before = html
    digests = []
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
        digests.append(digest)
        print("  %-22s v=%s" % (asset, digest))

    # One id for the whole build, derived from the parts rather than invented,
    # so it cannot be bumped by hand and cannot stay still when a file moves.
    build = hashlib.sha256(" ".join(digests).encode("ascii")).hexdigest()[:8]
    meta = re.compile(r'(<meta name="build" content=")[0-9a-f]*(">)')
    if not meta.search(html):
        sys.exit("FAIL: index.html has no <meta name=\"build\"> to stamp")
    html = meta.sub(lambda m: m.group(1) + build + m.group(2), html)
    print("  %-22s %s" % ("build", build))

    with open(VERSION, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{"build": "%s"}\n' % build)

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
    # The whole scheme rests on these three agreeing, so check, don't assume.
    assert ('<meta name="build" content="%s">' % build) in html, "meta build"
    assert io.open(VERSION, encoding="utf-8").read().strip() == \
        '{"build": "%s"}' % build, "version.json"
    assert 'version.json?t=' in html, \
        "index.html does not fetch version.json — the freshness check is gone"
    print("  OK  all %d assets are versioned, none double-stamped" % len(ASSETS))
    print("  OK  build %s matches in index.html, version.json and the check"
          % build)


if __name__ == "__main__":
    main()
