import { Config } from "@remotion/cli/config";

// PNG keeps stills (`remotion still`) lossless for the QA contact sheets.
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
