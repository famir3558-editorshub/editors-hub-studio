# Sourced by the other scripts: where the Remotion project (the kit) and the scratch folder live.
# Override with SPLIT_REEL_KIT / SPLIT_REEL_WORK in the environment.
SK=~/.claude/skills/split-reel
KIT="${SPLIT_REEL_KIT:-@@PROJECTS_ROOT@@/split-reel-kit}"
WORK="${SPLIT_REEL_WORK:-@@WORK_ROOT@@/split-reel}"
case "$KIT" in "~"*) KIT="$HOME${KIT#\~}";; esac
case "$WORK" in "~"*) WORK="$HOME${WORK#\~}";; esac
mkdir -p "$WORK"
