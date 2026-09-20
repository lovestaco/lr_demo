/**
 * LiveReview — standalone HTML/JS player.
 *
 * Mounts the 19 HyperFrames sub-compositions, nests each frame's own GSAP
 * timeline into one master timeline, applies the injected scene transitions,
 * and keeps the 8 hoisted <video> elements in sync with the master clock.
 *
 * This reimplements the parts of the HyperFrames runtime the film actually
 * needs; the frame HTML is used byte-for-byte as authored.
 */
import spec from "./spec.json";
import transitionSource from "./transitions.js?raw";

const W = 1920;
const H = 1080;

const root = document.getElementById("root");
const scaler = document.getElementById("scaler");
const playBtn = document.getElementById("play");
const scrub = document.getElementById("scrub");
const clock = document.getElementById("clock");
const chapters = document.getElementById("chapters");
const statusEl = document.getElementById("status");

window.__timelines = window.__timelines || {};

const setStatus = (t) => {
  if (statusEl) statusEl.textContent = t;
};

/** Clone a frame's <template> into a scene div and run its inline scripts. */
async function mountFrame(m) {
  const res = await fetch(`frames/${m.id}.html`);
  if (!res.ok) throw new Error(`${m.id}: HTTP ${res.status}`);
  const html = await res.text();

  const holder = document.createElement("div");
  holder.innerHTML = html.trim();
  const tpl = holder.querySelector("template");
  if (!tpl) throw new Error(`${m.id}: no <template>`);

  const scene = document.createElement("div");
  scene.id = `el-${m.id}`;
  scene.className = "scene";
  scene.style.zIndex = String(m.track);
  scene.style.visibility = "hidden";
  scene.appendChild(tpl.content.cloneNode(true));
  root.appendChild(scene);

  // Cloned <script> nodes never execute — re-create them so they do.
  // The GSAP CDN tag in each frame is skipped; GSAP is already global here.
  for (const old of Array.from(scene.querySelectorAll("script"))) {
    if (old.src && /gsap/i.test(old.src)) {
      old.remove();
      continue;
    }
    const s = document.createElement("script");
    s.textContent = old.textContent;
    old.replaceWith(s);
  }

  const tl = window.__timelines[m.id];
  if (!tl) throw new Error(`${m.id}: no timeline registered`);
  return { ...m, el: scene, tl };
}

/** Place the hoisted videos at the root, exactly as the assembler positioned them. */
function mountVideos() {
  return spec.videos.map((v) => {
    const el = document.createElement("video");
    el.src = v.src;
    el.muted = true;
    el.playsInline = true;
    el.preload = "auto";
    el.setAttribute("style", `${v.style};z-index:5;visibility:hidden`);
    root.appendChild(el);
    return { ...v, el };
  });
}

async function build() {
  setStatus("mounting 19 frames…");
  const frames = [];
  for (const m of spec.mounts) {
    frames.push(await mountFrame(m));
    setStatus(`mounting… ${frames.length}/${spec.mounts.length}`);
  }

  const videos = mountVideos();

  const main = gsap.timeline({ paused: true });
  window.__timelines.main = main;

  // Nest each frame's timeline. A PAUSED child never advances inside a parent,
  // so unpause before adding — this is the single easiest thing to get wrong.
  for (const f of frames) {
    f.tl.pause();
    f.tl.paused(false);
    main.add(f.tl, f.start);
  }

  // Gate scene visibility to each frame's window. Kept on `visibility` so it
  // cannot fight the transition tweens, which animate opacity/scale/x/filter.
  for (const f of frames) {
    main.set(f.el, { visibility: "visible" }, f.start);
    if (f.start + f.dur < spec.total) {
      main.set(f.el, { visibility: "hidden" }, f.start + f.dur);
    }
  }

  // The scene transitions, verbatim from the rendered composition.
  try {
    // eslint-disable-next-line no-new-func
    new Function("gsap", "window", transitionSource)(gsap, window);
  } catch (err) {
    console.error("transition injection failed", err);
  }

  main.pause(0);
  return { main, frames, videos };
}

function syncVideos(videos, t, playing) {
  for (const v of videos) {
    const active = t >= v.start && t < v.start + v.dur;
    if (!active) {
      if (!v.el.paused) v.el.pause();
      v.el.style.visibility = "hidden";
      continue;
    }
    v.el.style.visibility = "visible";
    const want = v.mediaStart + (t - v.start);
    if (Math.abs(v.el.currentTime - want) > 0.18) {
      try {
        v.el.currentTime = want;
      } catch {
        /* seek before metadata — ignored, next tick retries */
      }
    }
    if (playing && v.el.paused) v.el.play().catch(() => {});
    if (!playing && !v.el.paused) v.el.pause();
  }
}

function fit() {
  const pad = 40;
  const availW = window.innerWidth - pad;
  const availH = window.innerHeight - 132;
  const s = Math.min(availW / W, availH / H);
  scaler.style.transform = `scale(${s})`;
  scaler.style.width = `${W}px`;
  scaler.style.height = `${H}px`;
  const wrap = scaler.parentElement;
  wrap.style.width = `${W * s}px`;
  wrap.style.height = `${H * s}px`;
}

const fmt = (t) => {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
};

build()
  .then(({ main, frames, videos }) => {
    setStatus("");
    document.body.classList.add("ready");

    // Act markers on the scrubber: frames 1-5 problem, 6-16 solution, 17-19 resolved.
    for (const [i, f] of frames.entries()) {
      const tick = document.createElement("button");
      tick.className = "chapter";
      tick.style.left = `${(f.start / spec.total) * 100}%`;
      tick.title = `${i + 1}. ${f.id}`;
      if (i === 0 || i === 5 || i === 16) tick.classList.add("act");
      tick.onclick = () => seek(f.start + 0.05);
      chapters.appendChild(tick);
    }

    let playing = false;
    let last = performance.now();
    let t = 0;

    function apply(nt) {
      t = Math.max(0, Math.min(spec.total, nt));
      main.time(t);
      scrub.value = String((t / spec.total) * 1000);
      clock.textContent = `${fmt(t)} / ${fmt(spec.total)}`;
      syncVideos(videos, t, playing);
    }
    function seek(nt) {
      apply(nt);
    }

    function loop(now) {
      const dt = (now - last) / 1000;
      last = now;
      if (playing) {
        if (t >= spec.total) {
          playing = false;
          playBtn.textContent = "Replay";
        } else {
          apply(t + dt);
        }
      }
      requestAnimationFrame(loop);
    }
    requestAnimationFrame((n) => {
      last = n;
      loop(n);
    });

    playBtn.onclick = () => {
      if (t >= spec.total) t = 0;
      playing = !playing;
      playBtn.textContent = playing ? "Pause" : "Play";
      syncVideos(videos, t, playing);
    };
    scrub.oninput = () => {
      seek((Number(scrub.value) / 1000) * spec.total);
    };
    document.addEventListener("keydown", (e) => {
      if (e.key === " ") {
        e.preventDefault();
        playBtn.click();
      } else if (e.key === "ArrowRight") seek(t + 5);
      else if (e.key === "ArrowLeft") seek(t - 5);
      else if (e.key === "f" || e.key === "F") {
        if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
        else document.exitFullscreen?.();
      }
    });

    window.addEventListener("resize", fit);
    fit();

    // ?t=<seconds> deep-links a moment; ?play=1 starts immediately.
    const q = new URLSearchParams(location.search);
    const t0 = Number(q.get("t"));
    apply(Number.isFinite(t0) && t0 > 0 ? t0 : 0);
    if (q.get("play") === "1") playBtn.click();

    // exposed for headless verification
    window.__player = { main, seek: apply, total: spec.total, frames };
  })
  .catch((err) => {
    console.error(err);
    setStatus(`failed: ${err.message}`);
  });
