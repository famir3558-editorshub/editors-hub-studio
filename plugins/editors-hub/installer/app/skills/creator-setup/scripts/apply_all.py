#!/usr/bin/env python3
"""Fill every installed skill of the creator pack from the shared profile, in one go.

    python3 scripts/apply_all.py             fill all installed pack skills; report which are ready and which still
                                             need a few answers of their own
    python3 scripts/apply_all.py --status    list every installed pack skill and whether it is configured (changes nothing)

A pack skill is any folder in ~/.claude/skills (or $CREATOR_SKILLS_DIR) that has setup/apply_profile.py.
"""
import json, os, subprocess, sys

ROOT = os.path.expanduser(os.environ.get("CREATOR_SKILLS_DIR", "~/.claude/skills"))
SELF = "creator-setup"


def run(skill, *args):
    p = subprocess.run([sys.executable, f"{ROOT}/{skill}/setup/apply_profile.py", *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    status_only = "--status" in sys.argv[1:]
    skills = sorted(d for d in os.listdir(ROOT)
                    if d != SELF and os.path.exists(f"{ROOT}/{d}/setup/apply_profile.py"))
    if not skills:
        print("No pack skills are installed yet in", ROOT)
        return
    ready, needs = [], []
    for s in skills:
        if status_only:
            _, out = run(s, "--status")
            st = json.loads(out)
        else:
            code, out = run(s)
            _, o2 = run(s, "--status")
            st = json.loads(o2)
            st["detail"] = out
        (ready if st["configured"] else needs).append(st)
    print(f"READY ({len(ready)}): " + (", ".join(x["skill"] for x in ready) or "none"))
    print(f"NEED THEIR OWN ANSWERS ({len(needs)}):")
    for x in needs:
        why = ", ".join(x["missing_answers"]) or "run its setup once"
        print(f"  - {x['skill']}: {why}")
    if needs:
        print("These ask only their own few questions the first time they are used. The brand is not asked again.")


if __name__ == "__main__":
    main()
