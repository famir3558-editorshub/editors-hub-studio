# What's new

Shown in the studio after it updates. Each version: `## 1.2.3`, then `### New`, `### Better` or `### Fixed`, with one plain line per change.

## 1.41.0
### New
- Mistakes are found and fixed before the final render, not after it: an edit is first checked on a quick preview (every line listened to, every card checked against the speaker, the sound against the picture), the mistakes are fixed, and only then is the final rendered, once. A final render of an edit that wasn't checked, or changed since, is refused. Live shows what the check found and what was fixed.
- Checks before every render: the studio looks at the finished file first and stops, before a long render, if it's still being written, has no sound, or its sound and picture are different lengths (an old mix after a re-cut). Live says what it found.
- One render at a time: if two edits are ready together, the second waits its turn and Live says so, instead of both fighting over the drive and the graphics card.
- The phone app tells you when a newer version has arrived: tap "New version ready" to reload, instead of opening it twice.
### Fixed
- A slow save could have its lock on a video taken over after 30 seconds while it was still working. Now a lock is only taken over once the program holding it has ended.
- Shared style pictures: several saved at the same moment could lose each other's mark, so a card showed no picture.
- The phone app's sounds now also play on your first tap when the phone held them back, like on the PC.

## 1.40.3
### Better
- The popups that ask you something chime as they open: what's new after an update, render settings and the b-roll picker. A sound that comes before you've clicked anywhere on the page (browsers block those) now plays on your first click instead of being lost.

## 1.40.2
### Better
- Sounds on every studio page, not just the review page: each new notification in the bell plays a sound, and a new draft or an approval gets the party popper, wherever you are in the studio. Switch them off or on in Settings → Sounds.

## 1.40.1
### Better
- The phone's Live tab shows the edit's moving preview like the PC: pictures one after another, the timeline's tracks, and the red line at each picture's place. Until an edit has its own snapshots, frames from the raw clip or the last draft fill in.
- Sounds: a soft tick for Live updates, a chime when the studio asks for render settings or b-roll, and a party popper with a celebration sound when a draft is ready or a video is approved, on the review page and in the phone app. On the phone they can be switched off in Settings.
### Fixed
- Lock-screen notifications on iPhone: the app now reconnects them by itself, including when the service still held the address of an earlier install.

## 1.40.0
### New
- The phone app opens with the Editors.Hub logo on the Aurora sky, and never flashes white.
- The phone's Live tab shows each edit's updates as you'd see them in the studio: what's being done, the step, and the snapshot pictures.
- Share from the phone with the same choices as on the PC: pick the draft, the number your client sees, downloading and commenting, and copy or open the link.
- Choose the render settings from the phone. The notification asking for them opens them straight away.
- Edit and delete chat messages, on the phone and in the studio. Your own messages can be deleted for everyone or just for you; anyone's can be deleted from your side.
- Select several messages at once on the phone and delete them together.
### Better
- The phone app opens in well under a second: it shows what it had last time at once, then refreshes.
- Chats open with their messages straight away, and a message you send shows at once.
- Taps respond instantly, scrolling is smooth, and the chat no longer jumps while you scroll.

## 1.39.1
### New
- Computers without an NVIDIA card get the listening check and the face check too: setup downloads their processor versions once (about 1 GB).
- Every edit now follows the zero-mistake checks: the voice and the busiest section are checked before the rest is built, takes are picked by listening to the raw recording, every pause over 0.4 s and every repeated line is listened to, cards end exactly on their cut, and pictures are never stretched, blurred at the sides or cut through their text.
- A sharper cut-out round the hair, ears and glasses for edits with cards behind the speaker.
### Better
- The listening check lists every pause over 0.4 s and every line said twice, and groups the places it couldn't hear clearly, so there's less to go through.
- If the graphics card can't render a draft, Live says why.
### Fixed
- A render no longer starts on a nearly full drive: it says how much space is free and what it needs (at least 15 GB), and a drive that fills up mid-render is reported as that, not as a graphics card problem.
- With an NVIDIA card, setup's download of the card's tools could fail at Whisper and wait 3 days; it now installs.

## 1.39.0
### New
- Drafts render on your NVIDIA graphics card: about 4-5x faster at the same bitrate and quality. Settings has a switch to keep them on the processor; if the card can't do one, it renders on the processor by itself. Live says which was used.
- With an NVIDIA card on Windows, setup downloads the card's tools once (about 3 GB), then edits use the card for speaker cut-outs, listening checks and in-between video files.
- Before every draft, the voice is listened to again in short slices, so false starts, "ahh"s, throat noises and repeated takes are caught before you see them.
- Before a draft reaches you, a face check looks for cards, pictures or text on the speaker or crowding their head, and cards running into the bottom edge, so they're fixed first.

## 1.38.0
### New
- Voice calls with friends: tap 📞 in a chat, on your phone or in the studio's Chat tab. Answer, decline, mute and hang up; each call shows in the chat with how long it lasted, or as missed.
- A call rings in the app while it's open, and as a notification when it isn't (tap it within about 45 seconds to answer; on Android, Answer and Decline buttons).
### Fixed
- In a chat on iPhone, the keyboard no longer pushes the whole app up: only the messages scroll, and the message box sits on the keyboard.

## 1.37.0
### New
- Your client's review page has the Aurora look: frosted glass over black with a red glow. Every button and comment works as before.
- Chat on the computer: a Chat tab in your studio with the same chats as your phone.
- Chat: voice notes (up to three minutes), reactions (tap a message), and "typing…" when a friend is writing.
- Phone app: send a video from your phone's gallery to a client. It goes to your Google Drive, then your studio adds it as a new video, ready to edit.
- Phone notifications on Android have buttons: Approve a new draft, Reply to a comment or chat, or Mark as read. On iPhone, tapping still opens the right screen.
### Fixed
- The phone app no longer zooms in when you tap a text box or pinch, and long messages at the bottom of the screen show in full.

## 1.36.0
### New
- After an update, this window lists what's new and what's fixed in every version you got. Settings has a What's new button to read them any time.
- Phone app, Clients tab: every client with their videos and where each one is (editing, in review, changes, approved).
- Phone app, Live tab: the edits being made, with their step and running clock, and uploads with their progress.
- Phone app: tap a video to watch it on the client's link, approve a draft, ask for changes, or put the newest draft on the client's link. Your studio does it within a minute.
- Phone app: reply to a client's comment. The reply shows under it on the review link, marked Editor.
- Phone app: pause, resume or stop an upload, and try a failed one again.
- Phone app: a Today card (working now, with clients, changes, news today), plus search and filters in the inbox.
- Phone app settings: quiet hours, an evening digest (one notification a day), which clients can notify you, and your other phones (rename or disconnect them).
- Your phone reminds you when a client hasn't answered on a shared draft for two days.
- The phone app shows your studio's version, and whether an update is waiting.
- Phone app, Chat tab: add other editors as friends (by username or friend code), then chat: messages, photos and your videos' review links. Remove or block anyone at any time.

## 1.35.2
### New
- Whoever writes a comment on a review link can edit or delete it, from the same phone or computer they wrote it on. Everyone still sees all comments.
- Edited or deleted link comments change in the studio too.
### Fixed
- On Android, the phone app installs as its own app (with an Install button) instead of opening in Chrome.

## 1.35.1
### Fixed
- Home stayed blank after the 1.35.0 update.

## 1.35.0
### New
- The phone app: notifications on your phone's lock screen for client comments, client answers, drafts ready, uploads, what needs you and everything in your bell, plus an Inbox. Connect a phone in Settings > Phone notifications. Works on iPhone and Android.
- Clients can tap Approve this draft or Request changes on their review link, and you hear about it at once.
- A comment's time in a link opens the video right at that moment.

## 1.34.2
### Better
- New studio versions reach every computer within about a minute.

## 1.34.1
### New
- Style cards show pictures from the videos made with that style.

## 1.34.0
### New
- Aurora layout: the tabs float as a dock at the bottom, and Home opens with overview tiles (what's in review, the edit on the clock, what needs you, clients, disk space).
- Client cards show pictures from the client's newest videos.

## 1.33.0
### New
- The Aurora look: frosted glass over black with a slow red glow. Switch it, or the moving background, in Settings > Look. Every page and option is still there.
