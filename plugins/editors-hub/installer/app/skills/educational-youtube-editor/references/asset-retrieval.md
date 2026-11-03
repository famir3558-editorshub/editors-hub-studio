# Real-world examples: finding and presenting assets

When the creator references something that can be shown, show the real thing. The viewer should often think "that is exactly what they are talking about". An unrelated image that loosely matches a keyword is worse than nothing.

## The ladder (record the tier with every asset)

| Tier | What | Example |
|---|---|---|
| 1 | The exact real-world example the creator means | The actual thumbnails of the channel they name; the client's real award; the post they quote |
| 2 | A relevant screenshot | The company's homepage; the app's real interface; the search result |
| 3 | An authentic photograph | A real photo of the person, product or place |
| 4 | A high-quality illustration | A clean kit illustration or metaphor |
| 5 | A custom graphic | A diagram or UI recreation you build |
| 6 | Stock imagery | Only when nothing specific exists. The audit flags every use |

Start at 1 and step down only when a tier truly has nothing. A specific mention ("Apple", "Netflix", a well-known author's book) almost always has a tier 1-3 answer.

## What to show for each kind of mention

| The creator mentions | Show |
|---|---|
| A company | The product, the interface or the store that matters to their point. Not just a logo, unless the logo is the point |
| A named channel's thumbnails, another creator's content | Their actual thumbnails or covers (`get_asset.py ytthumb`), several, in a `collage` |
| A website | The site, in `K.browser`, scrolled to and highlighting the part the creator means |
| An app | Its real interface. Record or screenshot it; recreate it only if it cannot be captured |
| A person | Their real photo or footage, whole, with their name (`K.person`) |
| A social post | The post itself (`K.social` with the real wording and avatar, or a screenshot in `K.frame`) |
| A product | The product, clean, on its own |
| A book | The real cover |
| A study or statistic | The paper's title page or the chart, plus the figure as a `K.stat` |
| A place | A real photograph; a map if location is the point |
| A comment or DM | The real notification style, real wording where the creator has it |
| YouTube / Instagram / TikTok themselves | The real interface (search, feed, channel page) with real thumbnails |
| The creator's own results, clients, testimonials | The creator's real screenshots and footage, from the proof folder |

## Where to look, in order

1. **The creator's computer and drives.** `python3 scripts/find_assets.py <terms> [--image|--video]` searches this skill's assets, the creator profile's assets, the proof folder and the other asset folders named at setup (see "Your setup" in `SKILL.md`), the other skills of this pack if they are installed, earlier projects, Desktop, Downloads and Pictures, then Spotlight across the machine and every mounted drive. Clients, testimonials and the creator's own results are nearly always here. If their footage drive is not plugged in, say so rather than concluding the asset does not exist.
2. **The source itself.** A website: `get_asset.py <slug> site "<url>" --as <name> --tier 2 --for "..."` (`--tall 2400` for a long page to scroll, `--dark` for dark mode). A YouTube video: `get_asset.py <slug> ytthumb "<url or id>"`. Find a channel's real videos in the browser, then fetch their thumbnails.
3. **The web**, when "Real assets from the web" in "Your setup" allows it (the pack default is yes, with every source listed in the report; rights to third-party images are the creator's to manage). If their answer is no, skip to step 4. Search for the exact thing (web search or the built-in browser), open the candidate, take the direct image URL: `get_asset.py <slug> url "<image url>" ...`. For a post or a logged-in page, screenshot it in the browser and bring the saved file in with `get_asset.py <slug> file`.
4. **Build it** (tier 5): a simple, honest recreation with the kit. For YouTube, a simple channel or video card you build yourself beats a messy screenshot.
5. **Stock** (tier 6), last, and say so in the report.

Every `get_asset.py` call copies the file into `<project>/assets/media/` and logs file, source, tier and what it shows in `<project>/assets.json`. `get_asset.py <slug> list` prints the ledger for the report. Pass the tier to the scene (`tier=2`) so the audit can count real-world assets and flag stock.

## Check every asset before using it

**Open each file with Read.** Reject: cookie walls and consent banners, blank or half-loaded pages, the wrong person with the same name, watermarks, tiny or blurry images (under about 800 px on the long side for anything shown large), images with baked-in text that fights the point, and anything on the creator's "Never show" line (check the background of photos and the edges of screenshots too). A wrong image damages trust more than a missing one.

Sensitive cases: a private individual who is not a client or a public figure (use a generic profile with their name instead); a client the creator has not confirmed is happy to be named (ask in the report, do not publish around it); figures in a screenshot that contradict what the creator says (use the spoken figure in text and a neutral image).

## Protect faces when cropping

Never carelessly crop someone's face. Before an image's crop is decided:

1. Detect where the faces are (`E.faces(src)`, Apple Vision). Every kit component does this for you.
2. Decide the important subject of the photograph. Usually the people; sometimes the plaque, the screen or the product they are holding, in which case pass `pos="50% 70%"` or choose a frame shape that keeps both.
3. Choose the crop around the subject, with headroom.
4. Keep faces completely visible whenever reasonably possible.
5. Reposition or resize instead of cutting through anyone.

How the kit applies it:

- `K.frame` and `K.person` take **the image's own shape** by default, so nothing is cropped at all.
- When a layout needs another shape (a collage of 16:9 tiles, a square polaroid), `E.img` moves the crop window so every detected face, with room for hair and chin, is inside it.
- If the faces cannot all fit a filling crop, the whole image is shown on a blurred extension of itself. The audit notes it, because a different layout usually looks better.
- If an image still does not sit well: scale it down, reposition it, change the frame's aspect, use another layout, or find a better source image. **Protecting the subject is more important than fitting a predetermined template.**

Verify it: `09_review.py` writes `crops-*.jpg`, each image with the shown area boxed in green (red when a face is cut) and each detected face in yellow. Detection misses faces that are small, in profile, covered or in drawings, and knows nothing about hands holding a product or text that matters. Look at every crop yourself.

## Presentation: never dump a raw image

Raw images are rarely just placed on screen. Present them as designed elements in the composition:

- **Rounded corners** (28 px), a subtle 1 px light border where the image edge is dark, a **soft black drop shadow**, clean spacing from the frame edge and from the creator.
- **Depth and layering** (when depth is on in "Your setup"; with it off the engine keeps these flat): a slight 3D rest angle (`frame` `tilt`), overlapping layers at different depths (`collage` `scatter`), a floating browser window for a site.
- **Gentle life:** a slow 4-5% scale drift over the time it is on screen, a smooth focus-pull entrance and a soft fade exit. No Ken Burns sweeps, no bounce.
- **Masks and crops** that direct attention: scroll the page to the part the creator means, box it with `hl`, or crop to the relevant region rather than showing a whole busy screenshot.
- **Match the frame to the image:** portrait footage in a portrait frame, a phone screenshot in a phone-shaped frame, a person never cropped through.

All of this is built into `K.frame`, `K.browser`, `K.collage`, `K.person`, so presentation stays consistent: the same corner radius and shadow on every image in the video. Avoid stacking effects; premium here means calm.

## Report

At delivery, list every asset: what it shows, its source, its tier, and anything you could not find or had to mock up. The creator can swap in better ones quickly when they can see the list, and can decide about rights with the sources in front of them.
