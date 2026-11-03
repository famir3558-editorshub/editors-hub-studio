// Filled by setup/apply_profile.py from the creator profile (~/.claude/creator-profile/profile.json).
// Never edit by hand: change the answer and run apply_profile.py again, then new.sh refreshes the kit.
export const BRAND = {
  creator: String.raw`@@CREATOR_NAME@@`,
  brand: String.raw`@@BRAND_NAME@@`,
  accent: "@@ACCENT@@",
  accentRgb: "@@ACCENT_RGB@@",
  onAccent: "@@ON_ACCENT@@",
  paper: "@@PAPER@@",
  grey: "@@GREY@@",
  // CSS `src` strings: url("fonts/<file>") is resolved against the kit's public/fonts folder; local("Name") uses an installed font
  fontMainBoldSrc: String.raw`@@FONT_MAIN_BOLD_SRC_CSS@@`,
  fontMainRegularSrc: String.raw`@@FONT_MAIN_REGULAR_SRC_CSS@@`,
  fontAccentSrc: String.raw`@@FONT_ACCENT_SRC_CSS@@`,
};
