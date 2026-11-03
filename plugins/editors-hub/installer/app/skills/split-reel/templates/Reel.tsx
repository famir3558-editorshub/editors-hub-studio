/**
 * __TITLE__ : split-screen 9:16 reel panels (1080x960, lower half).
 * One component per scene in reel.json, same order. All cue times are SECONDS ON THE CUT
 * (paste straight from words.json / readable.txt); useT(from) gives that clock per scene.
 * Kit + vocabulary: ../splitReel/kit.tsx. Worked example for structure: the skill's examples/WorkedExample.tsx.
 */
import React from "react";
import { sceneFrames, O, GREY, SF, clamp, easeOut, easeInOut, back, useT, prog, In, Stage, Head, Kicker, glass, hot, Note, Radar, Wave, Bubble, fonts } from "../splitReel/kit";
import reel from "./reel.json";

export const SCENES = sceneFrames(reel);
const startOf = (i: number) => reel.scenes[i].start;

// Scene 1: replace. Pattern: kicker (emphasis font) + CAPS headline with one accent word,
// then ONE diagram that builds on the words the creator says.
const S01: React.FC = () => {
  const t = useT(SCENES[0].from);
  const T0 = startOf(0);
  return (
    <Stage leak={{ x: 540, y: 600 }}>
      <Kicker t={t} at={T0 + 0.1} top={24} size={50} text="kicker line" />
      <Head t={t} at={T0 + 0.2} top={90} size={78} lines={[[{ t: "HEADLINE " }, { t: "WORD", a: true }]]} />
      <In t={t} at={T0 + 0.6} style={{ position: "absolute", left: 190, top: 330, width: 700, height: 460, ...glass }}>
        {/* diagram */}
      </In>
    </Stage>
  );
};

export const __PREFIX___COMPS: React.FC[] = [S01];
