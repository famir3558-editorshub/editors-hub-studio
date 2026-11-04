---
name: editors-hub-setup
description: Installs, opens and updates Editors.Hub, the owner's own video studio (Home, review pages, sign-in, setup) on this computer. Use when the user has just installed the editors-hub plugin, says "set up Editors.Hub", "install my studio", "open Editors.Hub", "open Home", "update Editors.Hub", or when a session-start note says Editors.Hub was installed or updated. For editing videos in the studio, use the editors-hub skill.
---

# Editors.Hub setup

The plugin carries the studio app; a session-start hook copies it to `~/editors-hub` (Windows:
`C:\Users\<you>\editors-hub`) and updates it later, never touching that computer's accounts, settings, videos or keys.

1. Make sure the app is in place:
   `python3 "${CLAUDE_PLUGIN_ROOT}/installer/check.py" --install` (Windows: `py` instead of `python3`).
2. Start Home and get its address: `python3 ~/editors-hub/studio.py open`. Open that address in the Claude app's
   built-in browser beside the chat, never the system browser.
3. First time on a computer: the owner creates their account there (username and email; the first account on a computer is its owner). The sign-in page asks once for their Gmail app password (Google Account > Security > App passwords,
   one called "Editors.Hub") and then emails the code; they type it in and they're in. If they skip that,
   `python3 ~/editors-hub/studio.py codes` shows it. Give a code only to the owner.
4. The setup page then installs what edits need, in order (folder, Apple's tools, Homebrew, FFmpeg/Node/yt-dlp/uv,
   HyperFrames, Python tools, models, skills, API keys). Steps marked as needing the user: say plainly what to do
   (Homebrew asks for the Mac password in a Terminal window it opens; keys are pasted on the page, never in the chat).
   `python3 ~/editors-hub/studio.py setup --check` shows the same list in text.
5. When it says Ready, editing work goes through the `editors-hub` skill.
