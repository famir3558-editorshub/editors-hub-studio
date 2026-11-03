/**
 * Worked example from the original style. A reference for structure and API use only: never reuse its wording, names or assets.
 * Two scenes of a split reel: scene 1 = kicker + CAPS headline + counter card, scene 2 = a two-phase scene with a radar,
 * a handwritten note that fades before the next phase, and a pop-in chip row. Times are seconds on the cut.
 */
import React from "react";
import { sceneFrames, O, GREY, clamp, easeOut, easeInOut, back, useT, prog, In, Stage, Head, Kicker, glass, hot, Note, Radar, fonts } from "../splitReel/kit";
import reel from "./reel.json";

export const SCENES = sceneFrames(reel);
const startOf = (i: number) => reel.scenes[i].start;

const Counter: React.FC<{ t: number; at: number; to: number; label: string }> = ({ t, at, to, label }) => (
  <div style={{ textAlign: "center" }}>
    <div style={{ fontWeight: 700, fontSize: 120, letterSpacing: "-0.05em", lineHeight: 1 }}>{Math.round(to * easeOut(prog(t, at, 1.2)))}</div>
    <div style={{ fontSize: 22, letterSpacing: ".2em", color: GREY, marginTop: 8 }}>{label}</div>
  </div>
);

// Scene 1: the hook. Headline words land on the words spoken; one diagram builds under them.
const Hook: React.FC = () => {
  const t = useT(SCENES[0].from);
  const T0 = startOf(0);
  return (
    <Stage leak={{ x: 540, y: 620 }}>
      <Kicker t={t} at={T0 + 0.1} top={24} text="the short version" />
      <Head t={t} at={T0 + 0.25} top={90} lines={[[{ t: "ONE " }, { t: "SIMPLE", a: true, at: T0 + 0.9 }], [{ t: "HABIT" }]]} />
      <In t={t} at={T0 + 1.2} y={30} scale style={{ position: "absolute", left: 270, top: 480, width: 540, height: 330, display: "flex", alignItems: "center", justifyContent: "center", ...glass, ...hot }}>
        <Counter t={t} at={T0 + 1.4} to={52} label="WEEKS IN A ROW" />
      </In>
    </Stage>
  );
};

// Scene 2: two phases (A radar, B chips) cross-faded; the kicker and headline stay as the anchor.
const Framework: React.FC = () => {
  const t = useT(SCENES[1].from);
  const T0 = startOf(1);
  const switchAt = T0 + 5.0; // the second the meaning flips, taken from words.json
  const a = 1 - easeInOut(prog(t, switchAt, 0.5));
  const b = easeInOut(prog(t, switchAt, 0.5));
  const words = ["first", "second", "third"];
  return (
    <Stage leak={{ x: 540, y: 560 }}>
      <Kicker t={t} at={T0 + 0.1} top={24} text={t < switchAt ? "three parts" : "in order"} />
      <Head t={t} at={T0 + 0.2} top={90} lines={[[{ t: "THE " }, { t: "FRAMEWORK", a: true }]]} />
      <div style={{ position: "absolute", left: 290, top: 270, opacity: a }}>
        <Radar t={t} at={T0 + 0.5} size={500} sectors={["ONE", "TWO", "THREE"]} cues={[T0 + 2.0, T0 + 2.6, T0 + 3.2]} active={t > T0 + 3.6 ? 1 : undefined} activeAt={T0 + 3.6} />
      </div>
      <Note t={t} at={T0 + 1.5} until={switchAt - 0.2} text="start here" x={90} y={330} arrow="M0,0 C60,10 120,40 160,90" ax={150} ay={380} aw={200} ah={120} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 380, display: "flex", justifyContent: "center", gap: 24, opacity: b }}>
        {words.map((w, i) => {
          const p = prog(t, switchAt + 0.3 + i * 0.25, 0.4);
          return (
            <div key={w} style={{ padding: "18px 34px", borderRadius: 18, fontWeight: 700, fontSize: 52, letterSpacing: "-0.03em", opacity: easeOut(p), transform: `scale(${0.8 + 0.2 * back(p)})`, ...(i === 2 ? { background: O, color: "#000" } : { border: `2px dashed ${O}` }) }}>
              {w}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 28, textAlign: "center", fontFamily: fonts.serifItalic, fontSize: 30, color: "rgba(255,255,255,.35)", opacity: clamp(easeOut(prog(t, T0 + 0.8, 0.5))) }}>your framework name</div>
    </Stage>
  );
};

export const EXAMPLE_COMPS: React.FC[] = [Hook, Framework];
