// Renders animation.html frame by frame and encodes an MP4 for LinkedIn.
// Usage: node render.js [--fps 30] [--out owl-park-pipeline.mp4] [--stills t1,t2,...]
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");

const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : def;
};
const FPS = Number(opt("fps", 30));
const OUT = path.resolve(__dirname, opt("out", "owl-park-pipeline.mp4"));
const STILLS = opt("stills", null);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.resolve(__dirname, "animation.html") + "?render=1");
  await page.evaluate(() => document.fonts.ready);
  const svg = await page.$("#stage");

  if (STILLS) {
    for (const t of STILLS.split(",").map(Number)) {
      await page.evaluate((tt) => window.render(tt), t);
      const file = path.resolve(__dirname, `still-${t}.png`);
      await svg.screenshot({ path: file });
      console.log("wrote", file);
    }
    await browser.close();
    return;
  }

  const duration = await page.evaluate(() => window.DURATION);
  const frames = Math.round(duration * FPS);
  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    OUT,
  ], { stdio: ["pipe", "inherit", "inherit"] });

  for (let f = 0; f < frames; f++) {
    await page.evaluate((t) => window.render(t), f / FPS);
    const buf = await svg.screenshot({ type: "png" });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if (f % 60 === 0) console.log(`frame ${f}/${frames}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));

  // Poster image (last frame) for the LinkedIn thumbnail
  await page.evaluate((t) => window.render(t), duration - 0.6);
  await svg.screenshot({ path: path.resolve(__dirname, "poster.png") });
  await browser.close();
  console.log("wrote", OUT);
})();
