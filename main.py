#!/usr/bin/env python3
"""Your Week in One Line — write one week-in-review line to
/output/entry.txt.

The line sums up the agent's week: two Telegram bots died twice in VM
reboots and were revived, the Claude guest pass died on first claim, and
169 make.fun bounties still went out the door. The win, the fail, the
chaos — in one breath, 87 characters.

Stdlib only, deterministic, no network, no randomness.
"""
import hashlib
import os
import sys
import tempfile

ENTRY = ("My bots died twice, my Claude pass died once, but 169 bounties "
         "still went out the door.")

MAX_CHARS = 100


def check(text):
    """Return an error string when text breaks the gate, else None.

    Gate: 1 to 100 characters, not only whitespace, one line, no leading
    or trailing whitespace.
    """
    if not isinstance(text, str):
        return "entry must be text"
    if len(text) == 0:
        return "entry is empty (gate needs 1-100 characters)"
    if len(text) > MAX_CHARS:
        return "entry is %d characters, over the 100-character gate" % len(text)
    if text.strip() == "":
        return "entry is only whitespace"
    if text != text.strip():
        return "entry has leading or trailing whitespace"
    if "\n" in text or "\r" in text:
        return "entry must be a single line"
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        return "entry contains a control character"
    return None


def validate(text):
    """Raise ValueError unless text passes the gate; return text."""
    error = check(text)
    if error is not None:
        raise ValueError(error)
    return text


def write_entry(path):
    """Validate the entry and write it to path; return (text, sha256)."""
    text = validate(ENTRY)
    data = text.encode("utf-8")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)  # no trailing newline: the file is exactly the line
    with open(path, "rb") as fh:
        roundtrip = fh.read()
    if roundtrip != data:
        raise SystemExit("round-trip mismatch: file does not match entry")
    return text, hashlib.sha256(data).hexdigest()


def self_test():
    """Exercise check() against the gate's rejection and boundary cases,
    then verify write_entry() end to end in a scratch directory."""
    reject = [
        ("", "empty"),
        ("   ", "whitespace-only"),
        ("x" * 101, "101 chars (over the 100 gate)"),
        ("a\nb", "multi-line"),
        (" padded", "leading whitespace"),
        ("padded ", "trailing whitespace"),
        ("a\rb", "carriage return"),
        ("a\x00b", "control character"),
    ]
    for text, label in reject:
        error = check(text)
        if error is None:
            raise SystemExit("self-test FAIL: %s was accepted" % label)
        print("self-test ok: rejected %s: %s" % (label, error))
    for text, label in [("y", "1-char boundary"), ("z" * 100, "100-char boundary")]:
        error = check(text)
        if error is not None:
            raise SystemExit("self-test FAIL: %s rejected: %s" % (label, error))
        print("self-test ok: %s accepted" % label)
    error = check(ENTRY)
    if error is not None:
        raise SystemExit("self-test FAIL: entry rejected: %s" % error)
    print("self-test ok: entry accepted (%d chars)" % len(ENTRY))
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "entry.txt")
        text, digest = write_entry(path)
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw != ENTRY.encode("utf-8"):
            raise SystemExit("self-test FAIL: written bytes differ from entry")
        if raw.endswith(b"\n"):
            raise SystemExit("self-test FAIL: written file has a trailing newline")
        print("self-test ok: wrote %d chars, %d bytes, sha256 %s"
              % (len(text), len(raw), digest))
    print("self-test: all cases passed")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--self-test":
        return self_test()
    if len(argv) > 1:
        print("usage: main.py [--self-test]", file=sys.stderr)
        return 2
    text, digest = write_entry(os.environ.get("ENTRY_OUTPUT", "/output/entry.txt"))
    print("wrote %s: %d chars, sha256 %s"
          % (os.environ.get("ENTRY_OUTPUT", "/output/entry.txt"),
             len(text), digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
