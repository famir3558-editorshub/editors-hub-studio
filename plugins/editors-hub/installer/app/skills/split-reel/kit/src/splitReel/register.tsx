import React from "react";
import { Composition } from "remotion";
import { fpsOf, sceneFrames, PANEL_W, PANEL_H, ReelJson } from "./kit";

/** Registers one 1080x960 composition per scene: id `${prefix}-${scene.id}` */
export const SplitReelComps: React.FC<{ prefix: string; reel: ReelJson; comps: React.FC[] }> = ({ prefix, reel, comps }) => (
  <>
    {sceneFrames(reel).map((s, i) => (
      <Composition key={s.id} id={`${prefix}-${s.id}`} component={comps[i]} durationInFrames={s.to - s.from} fps={fpsOf(reel.fps)} width={PANEL_W} height={PANEL_H} />
    ))}
  </>
);
