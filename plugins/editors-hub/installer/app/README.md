# Editors.Hub

Your own studio for video edits: a **Home** page (styles, videos, settings) and a **review page** for each video
(play the draft, leave notes on exact moments, compare versions, approve). It runs only on your computer, at
`http://127.0.0.1:48100`, and works on **Mac and Windows**. Nothing is sent anywhere.

## Start it

- **Mac:** double-click `Editors.Hub.command` (first time: right-click > Open).
- **Windows:** install Python 3 from python.org (tick "Add python.exe to PATH"), copy this folder to
  `C:\Users\<you>\editors-hub`, then double-click `Editors.Hub.bat`.

Optional: install ffmpeg for video thumbnails on Home (`brew install ffmpeg` / `winget install ffmpeg`).

## How it's organised

```
library/
  styles/<style>/
    style.json  STYLE.md        the style's rules (fonts, colours, captions, pacing...)
    references/                 reference videos, fonts, LUTs, project files
    videos/<video>/
      video.json  VIDEO.md      status, drafts, review notes / the brief
      raw/  drafts/  exports/   footage / v1, v2... for review / final files
```

Change where the library lives in **Settings** (an external drive is a good idea for big footage).

## Workflow

0. A style can start with its format (short-form or long-form), reference videos, reference links and editing project files such as XML.
1. **New project** for each client: their details, brandbook and brand guidelines.
2. **New style** for each editing look. A style has no client in it, so any client can use it.
3. **New video**: pick the project and the style, then add the brief and raw footage.
3. Edit it (yourself or with Claude), then **upload the draft** on the review page (or drop it on the page).
4. On the review page, pause on a moment and type a note; red marks on the timeline show each note.
5. Tick notes as fixed, upload v2, and **Approve** when it's done.

## Skills that come with the studio

`skills/` holds the Claude skills that travel with Editors.Hub (the Creator Skill Pack, the HyperFrames skills and
the Editors.Hub skill). Every time Home starts, on any computer, it copies the missing ones into Claude's skills
folder (`~/.claude/skills`, on Windows `C:\Users\<you>\.claude\skills`) and updates the ones nobody has changed.
A skill that's been set up (creator-setup fills in your brand) or that came from somewhere else is never
overwritten. **Settings > Skills** on Home shows each one's state.

- Pack a new skill in: `studio.py skills add <skill folder or folder of skills>`
- Don't install some on one computer: `studio.py skills skip <name>...` (undo with `skills install <name>`)
- The pack's editing scripts are written for macOS, so on Windows some skills may need tools or steps they don't
  describe yet. With a creator profile packed (see below) the skills come filled in; without one, run
  **creator-setup** once on the new computer.

## First start on a new computer

Copy the whole `editors-hub` folder over and double-click the launcher. On every start Editors.Hub:

1. **Installs the tools** the skills need, if missing: Node.js 22+, ffmpeg, yt-dlp, HyperFrames and the Python
   packages (numpy, soundfile, requests, pillow, fonttools). Mac uses Homebrew, Windows uses winget. Homebrew itself
   has to be installed by you once (https://brew.sh, it asks for your password); Home tells you if it's missing.
2. **Puts your creator profile in place** (`profile/`: brand, colours, fonts, notes) if that computer has none.
3. **Installs the packed skills** and **fills them from the profile**, so they're ready without running
   creator-setup again. Skills that need a few answers of their own (how you film, where your B-roll is) ask them
   the first time they're used.

Home shows the progress at the top, and **Settings** lists every tool and skill. By hand:
`studio.py setup`, `studio.py profile pack` (after changing your brand with creator-setup), `studio.py skills install`.

## Projects (clients)

Each client lives in `projects/<project>/`: `project.json` (their details), `BRAND.md` (brand guidelines), `brandbook/`,
`logos/`, `fonts/`, `files/` and `videos/`. Their videos stay here, so sharing or saving a style never carries a client's
footage with it. Home's Videos tab lists these under **Client videos**. A video made only to train a style has no client:
it lives in the style, shows under **Style videos** and on the style's page, and travels with the style. Everyone who makes videos sees every project; only its maker or the owner can change it. The client's
brand decides colours, fonts, logos and tone; the style decides pacing, captions, motion and sound.

A project page has **Download (.zip)** and **Save to a drive**, and **Projects → Import a project** brings one back. Every file
is checked. Styles travel separately: saving names the ones the videos use, and importing says if any aren't here yet.
Commands: `studio.py export-project <project> <folder>`, `studio.py import-project <folder or .zip>`.

## Who can use it

A new person asks for access on their own computer, and the code goes only to the studio's owner. Once they have it, they own the copy on their computer. The owner sees and
removes people on the approval service's `/admin` page. A computer that's been let in works offline for up to 30 days. If the owner removes someone, it stops the next time it checks in.

## Updates

The studio updates itself: `updater.py` checks a public repository (no GitHub account needed), checks every file against the release's list, and leaves
`data/`, `library/` and `profile/` alone. Home restarts onto the new version once nothing is being copied or uploaded. To turn it off on a computer, set
`"auto_update": false` in `data/settings.json`. Notes are in `data/update.log`.

## Choosing the b-roll

When an edit or next draft starts, a popup asks: **Pick manually** or **Claude picks automatically** (`studio.py broll-ask`). Manually, Claude finds every
place b-roll can go and the picker shows 3 or 4 options for each, with the words spoken there (`studio.py broll-plan`). After a draft, tick any to change
and you get new options for just those, or say **All b-roll is good**, and it won't ask again until a note mentions b-roll. The B-roll tab shows what's used.

Options come from your own footage, free sites such as Pexels, Pixabay and Mixkit, and Envato if you've signed in to your own account in the Claude app's
built-in browser. No account comes with the studio: each person signs in with their own.

## Following an edit, and choosing the render

The review page's **Live** tab, beside Notes, shows what Claude is doing in plain words, with snapshots
(`studio.py update`). Before each draft, a popup asks for the resolution, frame rate, bitrate (low, medium, high, higher),
format and audio quality (`studio.py ask-render`). `studio.py finish-render` encodes the edit with those settings and adds it as the
next draft. **Later** closes the popup; the choice waits in the Live tab, and Home shows a reminder.

## Style pages

Click a style to open its page: stills from its videos, its colours and description, and tabs for Overview, Videos,
Brief, References, Guide, Learned rules, B-roll, Graphics, Effects, Transitions, Colour grading, Sound effects, Music,
Project files and Files. Drop files on the page to add them: on a section tab they go into that section; on the
Overview each file is sorted by type. Only the style's maker, or the owner, can add files or edit the guide and brief.


## Adding a style, and the online Shared folder

**My styles → + Add a style** has two options:

1. **From a folder:** a style saved on another computer comes in whole, with its videos; any other folder of
   references, B-roll, LUTs, music, fonts or project files becomes a new style, each file sorted into its section.
2. **From the online Shared folder:** the styles listed on the **Shared** tab, shared by anyone with **⋯ → Share online**.

## The Effects tab

Everyone who makes videos can see it. It's mainly for Claude: it reads the library before each edit, for ideas, so the studio knows more with every style added. The video's style and the client's brand still decide the look. It mixes the effects, transitions and techniques from your styles and the online Shared folder, with search and a filter by style. **Collect them** downloads the online styles not in it yet and keeps only their effects and guide. A style someone keeps private stays on their computer, so nobody else sees it until they share it online.
Only the owner can remove something, and that removes it for everyone, for Claude too. **Bring them all back** undoes it. The style it came from keeps it.

## Video cards

Videos show as tall 9:16 cards on Home, client pages and style pages; a sideways video fits inside its card with black above and below. Hold the mouse on a card to play it silently: the latest draft, or the raw clip until there is a draft.

## Make video starts the edit, in its own session

Each client and each style has one parent Claude session, and each video gets its own subsession of it. When you make a client or style, the page gives you one line to paste into a new Claude session (the page can't create sessions itself; it's also under **Copy a prompt for Claude**). That session then only listens. **Make video** puts the video in a queue on this computer, and the client's parent session starts a subsession that edits it. A client's video goes only to that client's parent, and a style's training video only to that style's. If the parent session isn't open, the video waits, and the Live page says which session it needs. Only the parent has to stay open for new videos to start. Depending on the Claude app, it may show a card for you to click to start the subsession.

## The Live tab

While Claude edits, the Live tab shows, from the top:

- **The video:** its name, how long Claude has worked on this draft, the draft number, client, style, start time and raw clip length. The counter stops while Claude waits for your answer, and when the draft is ready. If there's no update for 30 minutes, it stops and says so, as the session may have stopped.
- **The timeline:** the newest frame with what Claude is doing, and tracks for the video, b-roll, animation, captions and sound that fill in as the edit builds. Until Claude reports each clip, a track can show a solid block for the whole length, and animation stays empty.
- **The preview:** the newest snapshot shows beside the timeline, and the red line moves to where Claude says it's working. The line only moves when Claude reports, so it jumps from place to place and doesn't run like a playhead. Click or drag on the tracks to look back at any snapshot, then **Back to live**.
- **The steps:** the progress bar and each step. The percentage and time left are estimates from the steps. Only the steps this edit uses show, so a video with no b-roll has no B-roll step or track.
- **Updates:** the latest update, then the earlier ones with their frames.

## Seeing and stopping long jobs

Uploads, downloads, Save to a drive, Duplicate and Add a style run in the background: a bar shows how far they've
got on the style's card, its page, the Shared tab (uploads) and the panel at the bottom right, with the size done,
the speed and the time left. **Stop** ends any of them and cleans up: a stopped upload removes the unfinished copy
from the online folder, a stopped copy or import leaves nothing half done, and the style itself is never touched.

## Managing a style

The **⋯** button on a style's card or page: **Share online**, **Rename**, **Duplicate** (a private copy for you), **Download (.zip)**, **Save to a drive**, **Open
folder** and **Delete**. Delete moves the style and its videos to the **Recently deleted** tab, with deleted clients, where **Delete forever** erases them for good;
**Restore** puts it back. Only the person who made a style, or the owner, can share, rename or delete it.

## Taking a style to another computer (Mac or Windows)

On a style's page: **Download (.zip)** saves it to the device you're using; **Save to a drive** copies it onto a USB
drive or cloud folder (fast, any size). On the other computer: **My styles → Import a style**, pick it (Editors.Hub
finds saved styles on drives, Desktop, Downloads and cloud folders, or upload the .zip).
It comes into My styles. Every file is checked. Commands:
`studio.py export-style <style> <folder>`, `studio.py import-style <folder or .zip>`.

## Private styles, and sharing online

- Everyone who makes videos (the owner and editors) can make their own styles. A style is **private**: only the
  person who made it sees it and its videos (`library/private/<username>/`).
- **⋯ → Share online** is the only way to share one. It appears on the **Shared** tab of everyone using Editors.Hub,
  and a download becomes that person's own private copy. Only the person who shared it, or the owner, can remove it. Sharing inside one studio no longer exists: a style older
  studios shared that way goes back to its maker the next time Home starts.
- **Clients (reviewers)** see no styles at all: only the videos they're invited to under "Who can review" on the
  review page.

## Accounts and sign-in

Everyone signs in with a **username, an email and a 6-digit code**. There are no passwords.

- **Every code goes to the owner**, whoever set up this computer's studio first: the owner's own, and everyone else's. A new person signs up,
  the owner gets their code by email and on the **Team** page, and gives it to them only if they want them in.
- **Only the owner can do admin things:** Settings, Team, tools, skills and email.
  **Editors** make styles and videos, upload drafts and leave notes. **Reviewers** (clients) watch, leave notes,
  approve or ask for changes. The owner picks each person's role on the Team page.
- **Email:** on the Team page, add a Gmail address and a Gmail *app password* so codes reach your inbox. Until then
  they show on the Team page and with `studio.py codes` on this computer.
- **Sharing styles online:** on any style, ⋯ → Share online. Everyone using Editors.Hub can download it from their Shared tab right away. What goes online is a lighter copy, at most 3 GB (7 GB for a long-form style), with large videos made smaller. Your own style doesn't change.
- **Something wrong, or need help?** "Report to owner" sends it to the studio's owner, and their answer shows up there. The
  owner gets it by email and answers from their approvals page (the Reports tab links to it).
- **Other devices:** turn on "Let people on your Wi-Fi in" on the Team page, then restart Editors.Hub. Only the owner's
  studios can do this: on anyone else's, the studio is theirs alone, and each person asks for approval on their own computer.
- Accounts are kept in `data/` on each computer (not online). Sessions last 30 days.

## Install it on another computer

Editors.Hub is also a Claude Code plugin. `python3 make_release.py --repo <github-user>/<repo>` builds it in
`~/editors-hub-release` (a clean copy: no accounts, sign-ins, settings, email login, keys or videos); push that
folder to GitHub, then on any computer:

```
claude plugin marketplace add <github-user>/<repo>
claude plugin install editors-hub@editors-hub
```

and say "set up Editors.Hub" in a new Claude session.

## Commands (for Claude or a terminal)

Mac: `python3 ~/editors-hub/studio.py ...`  ·  Windows: `py %USERPROFILE%\editors-hub\studio.py ...`

```
studio.py open [<video>]                 start Home if needed, print the address
studio.py status                         styles, videos and where each stands
studio.py new-style "<name>" --client "..."
studio.py new-video <style> "<name>" --raw <file> --brief "..."
studio.py add-draft <video> <file>       a new version for review
studio.py notes <video>                  open notes on the latest draft
studio.py done <video> <id>...           mark notes fixed
studio.py set-status <video> <status>    editing | in review | changes | approved | delivered
studio.py skills [install|add <folder>|skip <name>]   the packed Claude skills
studio.py stop                           stop Home
```

Settings and the access key are in `data/settings.json`; the address printed by `open` carries the key, so only
your browser can open the pages.
