"""python -m llk <preflight|generate|produce|compose|cover|qa>"""

from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python -m llk [preflight|generate|produce|compose|cover|qa|contact]")
        return 2
    cmd = sys.argv[1]
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    if cmd == "preflight":
        from llk.preflight import run_preflight
        import json

        strict = "--before-paid" in sys.argv
        report = run_preflight()
        if strict and report["paid_calls_so_far"] != 0:
            raise SystemExit("paid calls already used")
        print(json.dumps(report, indent=2))
        return 0
    if cmd == "generate":
        from llk.generate import main as gen

        return gen()
    if cmd == "produce":
        from llk.produce import main as produce

        return produce()
    if cmd == "compose":
        from llk.compose import main as compose

        return compose()
    if cmd == "cover":
        from llk.cover import main as cover

        return cover()
    if cmd == "qa":
        from llk.qa import run_qa
        import json

        print(json.dumps(run_qa(), indent=2))
        return 0
    if cmd in {"contact", "contact-sheet"}:
        from llk.contact_sheet import main as contact

        return contact()
    print(f"unknown command {cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
