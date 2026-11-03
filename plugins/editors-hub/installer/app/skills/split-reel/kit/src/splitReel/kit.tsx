/**
 * Split-screen 9:16 reel kit: shared primitives for the lower-half panels (1080x960 on black) in the diagram style.
 * Used by the `split-reel` skill. Times are seconds on the EDITED timeline;
 * `useT(scene.from)` returns that time for the current frame of a scene comp.
 *
 *   Stage   black canvas + grain + optional accent light leak (also loads the brand fonts)
 *   Head    CAPS headline in the main font, per-word cue, accent-coloured glowing keywords
 *   Kicker  emphasis-font line in the accent colour (above the headline)
 *   In      rise + fade + blur-resolve entrance on a cue
 *   Note    Caveat handwritten note + drawn accent arrow (with `until`)
 *   glass / hot  frosted card + glowing accent-border styles
 *   Radar   three-sector radar: rings, sweep, blips, active sector (labels are yours)
 *   Wave, Bubble  call waveform + comment bubble mocks
 * Figures and currency are always set in the main font, never in the emphasis font.
 *
 * Brand values come from ../brand.js (filled by setup), never from this file.
 */
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";
import { BRAND } from "../brand.js";

export const caveat = loadCaveat("normal", { weights: ["700"], subsets: ["latin"] }).fontFamily;
export const PANEL_W = 1080;
export const PANEL_H = 960;

// ------------------------------------------------------------------ brand

/** accent colour, and its "r,g,b" for glows */
export const O = BRAND.accent;
export const O_RGB = BRAND.accentRgb;
export const ON_O = BRAND.onAccent;
export const PAPER = BRAND.paper;
export const GREY = BRAND.grey;
export const glow = (a: number) => `rgba(${O_RGB},${a})`;

/** SRMain = the creator's main font (bold 700 + regular 400); SRAccent = their emphasis font. */
export const fonts = {
  sans: "SRMain, 'Helvetica Neue', Helvetica, Arial, sans-serif",
  serifItalic: "SRAccent, Georgia, 'Times New Roman', serif",
} as const;
/** system UI stack for iOS / app mock-ups (notes, chat, notifications): not a brand font */
export const SF = "-apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif";

const FACES: [string, string, FontFaceDescriptors][] = [
  ["SRMain", BRAND.fontMainBoldSrc, { weight: "700" }],
  ["SRMain", BRAND.fontMainRegularSrc, { weight: "400" }],
  ["SRAccent", BRAND.fontAccentSrc, {}],
];
const resolveSrc = (s: string) => s.replace(/url\("fonts\/([^"]+)"\)/g, (_m, f) => `url("${staticFile("fonts/" + f)}")`);
/** loads the brand fonts and holds the render until they are in (a face that fails falls back to the CSS stack above) */
const useBrandFonts = () => {
  const [handle] = useState(() => delayRender("brand fonts"));
  useEffect(() => {
    Promise.all(
      FACES.map(async ([family, src, desc]) => {
        try {
          const ff = new FontFace(family, resolveSrc(src), desc);
          await ff.load();
          document.fonts.add(ff);
        } catch (e) {
          console.warn("font not loaded:", family, e);
        }
      }),
    ).then(() => continueRender(handle));
  }, [handle]);
};

// ------------------------------------------------------------------ motion helpers

export const clamp = (x: number) => Math.min(1, Math.max(0, x));
export const easeOut = (x: number) => 1 - Math.pow(1 - clamp(x), 3);
export const easeInOut = (x: number) => { const t = clamp(x); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
export const back = (x: number) => { const t = clamp(x), c = 1.6; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };

/** absolute edited-timeline seconds for the current frame of this scene */
export const useT = (sceneFrom: number) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (f + sceneFrom) / fps;
};
export const prog = (t: number, at: number, dur = 0.45) => clamp((t - at) / dur);

/** standard entrance: rise + fade + blur resolve */
export const In: React.FC<{ t: number; at: number; dur?: number; y?: number; scale?: boolean; style?: React.CSSProperties; children?: React.ReactNode }> = ({ t, at, dur = 0.45, y = 26, scale, style, children }) => {
  const p = prog(t, at, dur);
  const e = easeOut(p);
  return (
    <div style={{ opacity: e, transform: `translateY(${(1 - e) * y}px) scale(${scale ? 0.85 + 0.15 * back(p) : 1})`, filter: `blur(${(1 - e) * 8}px)`, ...style }}>
      {children}
    </div>
  );
};

// ------------------------------------------------------------------ stage

export const Stage: React.FC<{ children: React.ReactNode; leak?: { x: number; y: number; s?: number } }> = ({ children, leak }) => {
  useBrandFonts();
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden", fontFamily: fonts.sans, color: "#fff" }}>
      {leak ? (
        <div style={{ position: "absolute", left: leak.x - 380 * (leak.s ?? 1), top: leak.y - 260 * (leak.s ?? 1), width: 760 * (leak.s ?? 1), height: 520 * (leak.s ?? 1), borderRadius: "50%", filter: "blur(80px)", background: `radial-gradient(closest-side, ${glow(0.26)}, transparent)` }} />
      ) : null}
      {children}
      <AbsoluteFill style={{ pointerEvents: "none", opacity: 0.22, mixBlendMode: "screen", backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .5 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")` }} />
      {/* fade the top edge into the black seam under the camera */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 40, background: "linear-gradient(#000, transparent)" }} />
    </AbsoluteFill>
  );
};

export type Seg = { t: string; a?: boolean; at?: number };
/** CAPS headline; words with `a` glow in the accent colour; optional per-segment cue */
export const Head: React.FC<{ t: number; at: number; lines: Seg[][]; size?: number; top?: number }> = ({ t, at, lines, size = 74, top = 64 }) => (
  <div style={{ position: "absolute", top, left: 0, right: 0, textAlign: "center", zIndex: 5 }}>
    {lines.map((ln, i) => (
      <div key={i} style={{ fontWeight: 700, textTransform: "uppercase", fontSize: size, lineHeight: 0.98, letterSpacing: "-0.045em" }}>
        {ln.map((s, j) => {
          const e = easeOut(prog(t, s.at ?? at + i * 0.08, 0.4));
          return (
            <span key={j} style={{ display: "inline-block", whiteSpace: "pre", opacity: e, transform: `translateY(${(1 - e) * 20}px)`, filter: `blur(${(1 - e) * 6}px)`, color: s.a ? O : "#fff", textShadow: s.a ? `0 0 34px ${glow(0.55)}` : "none" }}>
              {s.t}
            </span>
          );
        })}
      </div>
    ))}
  </div>
);

export const Kicker: React.FC<{ t: number; at: number; text: string; top?: number; size?: number }> = ({ t, at, text, top = 20, size = 52 }) => {
  const e = easeOut(prog(t, at, 0.5));
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, textAlign: "center", fontFamily: fonts.serifItalic, fontSize: size, color: O, letterSpacing: "-0.02em", textShadow: `0 0 30px ${glow(0.35)}`, opacity: e, transform: `translateY(${(1 - e) * 14}px)`, zIndex: 5 }}>
      {text}
    </div>
  );
};

export const glass: React.CSSProperties = {
  borderRadius: 30,
  background: "linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.035))",
  border: "1px solid rgba(255,255,255,.13)",
  boxShadow: "inset 0 1px 0 rgba(255,255,255,.16), 0 30px 70px rgba(0,0,0,.5)",
};
export const hot: React.CSSProperties = { border: `2px solid ${O}`, boxShadow: `0 0 40px ${glow(0.45)}, inset 0 0 20px ${glow(0.15)}` };

/** Caveat note + hand-drawn arrow that draws on */
export const Note: React.FC<{ t: number; at: number; text: string; x: number; y: number; rot?: number; size?: number; arrow?: string; ax?: number; ay?: number; aw?: number; ah?: number; until?: number }> = ({ t, at, text, x, y, rot = -4, size = 50, arrow, ax = 0, ay = 0, aw = 200, ah = 120, until = 1e9 }) => {
  const e = easeOut(prog(t, at, 0.35)) * (1 - easeOut(prog(t, until, 0.3)));
  const d = easeOut(prog(t, at + 0.15, 0.5));
  return (
    <>
      <div style={{ position: "absolute", left: x, top: y, transform: `rotate(${rot}deg) scale(${0.9 + 0.1 * e})`, opacity: e, fontFamily: caveat, fontWeight: 700, fontSize: size, color: "#fff", whiteSpace: "nowrap", zIndex: 6 }}>{text}</div>
      {arrow ? (
        <svg style={{ position: "absolute", left: ax, top: ay, overflow: "visible", zIndex: 6 }} width={aw} height={ah}>
          <path d={arrow} fill="none" stroke={O} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - d} opacity={e} />
        </svg>
      ) : null}
    </>
  );
};

// ------------------------------------------------------------------ radar

/** sector centres in degrees: sector 0 upper left, 1 bottom, 2 upper right */
const SECTOR_ANGLES = [-150, 90, -30];
/**
 * Three-sector radar. `sectors` are the three labels (set them to the creator's own three parts).
 * active: which sector is swept/highlighted (0, 1 or 2); cues: seconds at which a blip appears.
 */
export const Radar: React.FC<{ t: number; at: number; size: number; sectors?: [string, string, string]; cues?: number[]; active?: number; activeAt?: number; sweep?: boolean; labels?: boolean; label?: string }> = ({ t, at, size, sectors = ["ONE", "TWO", "THREE"], cues = [], active, activeAt = 0, sweep = true, labels = true, label }) => {
  const r = size / 2;
  const draw = easeOut(prog(t, at, 0.9));
  const rot = sweep ? ((t - at) * 70) % 360 : 0;
  const rings = [0.33, 0.66, 1];
  const ha = active !== undefined ? easeOut(prog(t, activeAt, 0.5)) : 0;
  const sector = (a0: number, a1: number, rr: number) => {
    const p = (a: number) => [r + rr * Math.cos((a * Math.PI) / 180), r + rr * Math.sin((a * Math.PI) / 180)];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    return `M${r},${r} L${x0},${y0} A${rr},${rr} 0 0 1 ${x1},${y1} Z`;
  };
  return (
    <svg width={size} height={size} style={{ overflow: "visible" }}>
      <defs>
        <radialGradient id="sw" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={O} stopOpacity={0.0} />
          <stop offset="100%" stopColor={O} stopOpacity={0.35} />
        </radialGradient>
      </defs>
      {rings.map((k, i) => (
        <circle key={i} cx={r} cy={r} r={r * k - 2} fill="none" stroke="rgba(255,255,255,.22)" strokeWidth={3} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
      ))}
      {[-90, 30, 150].map((a, i) => (
        <line key={i} x1={r} y1={r} x2={r + (r - 2) * Math.cos((a * Math.PI) / 180) * draw} y2={r + (r - 2) * Math.sin((a * Math.PI) / 180) * draw} stroke="rgba(255,255,255,.18)" strokeWidth={3} />
      ))}
      {active !== undefined ? <path d={sector(SECTOR_ANGLES[active] - 60, SECTOR_ANGLES[active] + 60, r - 2)} fill={O} opacity={0.2 * ha} /> : null}
      {sweep ? (
        <g transform={`rotate(${rot} ${r} ${r})`} opacity={draw}>
          <path d={sector(-40, 0, r - 2)} fill="url(#sw)" />
          <line x1={r} y1={r} x2={size - 2} y2={r} stroke={O} strokeWidth={3} opacity={0.8} />
        </g>
      ) : null}
      {cues.map((c, i) => {
        // blips: alternate sectors
        const a = SECTOR_ANGLES[i % 3] + ((i * 37) % 50) - 25;
        const rr = r * (0.42 + ((i * 29) % 45) / 100);
        const e = back(prog(t, c, 0.35));
        return <circle key={i} cx={r + rr * Math.cos((a * Math.PI) / 180)} cy={r + rr * Math.sin((a * Math.PI) / 180)} r={11 * e} fill={O} style={{ filter: `drop-shadow(0 0 10px ${glow(0.9)})` }} />;
      })}
      <circle cx={r} cy={r} r={r * 0.11} fill="none" stroke={O} strokeWidth={9} opacity={draw} style={{ filter: `drop-shadow(0 0 14px ${glow(0.7)})` }} />
      {label ? (
        <text x={r} y={r + 12} textAnchor="middle" fontFamily={fonts.sans} fontWeight={700} fontSize={30} fill="#fff" opacity={draw}>{label}</text>
      ) : null}
      {labels
        ? sectors.map((k, i) => {
            const e = easeOut(prog(t, at + 0.3 + i * 0.15, 0.4));
            const lr = r * 0.66;
            const a = SECTOR_ANGLES[i];
            const on = active === i ? ha : 0;
            return (
              <text key={k} x={r + lr * Math.cos((a * Math.PI) / 180)} y={r + lr * Math.sin((a * Math.PI) / 180) + 12} textAnchor="middle" fontFamily={fonts.sans} fontWeight={700} fontSize={34} letterSpacing="0.06em" fill={on > 0.5 ? O : "#fff"} opacity={e * (active !== undefined && active !== i ? 0.45 : 1)}>
                {k}
              </text>
            );
          })
        : null}
    </svg>
  );
};

// ------------------------------------------------------------------ mocks

export const Wave: React.FC<{ t: number; w: number; h: number }> = ({ t, w, h }) => (
  <svg width={w} height={h}>
    {Array.from({ length: 28 }).map((_, i) => {
      const a = 0.25 + 0.75 * Math.abs(Math.sin(i * 0.9 + t * 7) * Math.cos(i * 0.37 + t * 3));
      return <rect key={i} x={i * (w / 28)} y={(h - h * a) / 2} width={w / 28 - 5} height={h * a} rx={3} fill={i % 5 === 0 ? O : "rgba(255,255,255,.65)"} />;
    })}
  </svg>
);

export const Bubble: React.FC<{ t: number; at: number; name: string; text: string; hotText?: boolean; w?: number }> = ({ t, at, name, text, hotText, w = 430 }) => (
  <In t={t} at={at} dur={0.35} y={18}>
    <div style={{ display: "flex", gap: 14, alignItems: "flex-start", width: w }}>
      <div style={{ width: 40, height: 40, borderRadius: 20, flex: "none", background: "linear-gradient(180deg,#8e8e93,#48484a)" }} />
      <div style={{ fontFamily: SF }}>
        <div style={{ fontSize: 19, fontWeight: 600, color: "#cfcfcf" }}>{name}</div>
        <div style={{ fontSize: 24, lineHeight: 1.25, color: hotText ? "#fff" : "#e8e8e8", marginTop: 2 }}>{text}</div>
      </div>
    </div>
  </In>
);

// ------------------------------------------------------------------ reel.json plumbing
/** reel.json (shared with the skill's composite.py):
 *  { fps: "24000/1001", scenes: [{ id: "01-Hook", start: 0, end: 3.71 }], fullscreen: [[a,b]], ... } */
export type ReelScene = { id: string; start: number; end: number };
export type ReelJson = { fps: string; scenes: ReelScene[]; fullscreen?: number[][] };
export const fpsOf = (s: string) => { const [a, b] = s.split("/").map(Number); return b ? a / b : a; };
/** scene windows in frames of the edited timeline */
export const sceneFrames = (reel: ReelJson) => {
  const fps = fpsOf(reel.fps);
  return reel.scenes.map((s) => ({ id: s.id, from: Math.round(s.start * fps), to: Math.round(s.end * fps) }));
};
