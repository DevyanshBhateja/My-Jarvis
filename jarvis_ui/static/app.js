// J.A.R.V.I.S. Core Interface Canvas & SSE Controller

const canvas = document.getElementById("reactor-canvas");
const ctx = canvas.getContext("2d");

const statePill = document.getElementById("state-pill");
const stateLabel = document.getElementById("state-label");
const stateWatermark = document.getElementById("state-watermark");
const enginePill = document.getElementById("engine-pill");
const engineLabel = document.getElementById("engine-label");
const userSpeechText = document.getElementById("user-speech-text");
const jarvisSpeechText = document.getElementById("jarvis-speech-text");
const actionBanner = document.getElementById("action-banner");
const actionDetail = document.getElementById("action-detail");
const soundwaveContainer = document.getElementById("soundwave-container");

// Generate 36 Soundwave Equalizer Bars
const NUM_EQ_BARS = 36;
const eqBars = [];
for (let i = 0; i < NUM_EQ_BARS; i++) {
  const bar = document.createElement("div");
  bar.className = "eq-bar";
  soundwaveContainer.appendChild(bar);
  eqBars.push(bar);
}

// Global Animation State
let currentState = "idle";
let currentEngine = "local";
let rot1 = 0;
let rot2 = 0;
let rot3 = 0;
let coreEnergy = 0.5;
let audioEnergy = 0.1;
let targetAudioEnergy = 0.1;

// Colors
const COLOR_CYAN = "#00f0ff";
const COLOR_BLUE = "#0066ff";
const COLOR_AMBER = "#ffaa00";

// --- SSE Event Stream Connection ---
function initEventStream() {
  const evtSource = new EventSource("/api/stream");
  let disconnectTimer = null;

  evtSource.onopen = () => {
    if (disconnectTimer) {
      clearTimeout(disconnectTimer);
      disconnectTimer = null;
    }
  };

  evtSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      handleEvent(data);
    } catch (err) {
      console.warn("Malformed SSE payload", err);
    }
  };

  evtSource.onerror = () => {
    stateLabel.innerText = "OFFLINE";
    if (!disconnectTimer) {
      disconnectTimer = setTimeout(() => {
        // Automatically close app window if backend server shuts down
        try { window.close(); } catch (e) {}
      }, 2500);
    }
  };
}

function handleEvent(evt) {
  if (evt.type === "state" || evt.type === "snapshot") {
    setVisualState(evt.state || "idle");
  }

  if (evt.type === "engine" || evt.type === "snapshot") {
    setEngine(evt.engine || "local", evt.model || "");
  }

  if (evt.type === "user_speech") {
    userSpeechText.innerText = `"${evt.text}"`;
  }

  if (evt.type === "jarvis_speech") {
    jarvisSpeechText.innerText = `"${evt.full_text || evt.text}"`;
    // Trigger intense speech audio wave
    targetAudioEnergy = 0.95;
  }

  if (evt.type === "action") {
    if (evt.name) {
      actionBanner.classList.remove("hidden");
      actionDetail.innerText = `${evt.name}: ${evt.description || "In progress..."}`;
      if (evt.status === "done") {
        setTimeout(() => actionBanner.classList.add("hidden"), 4000);
      }
    } else {
      actionBanner.classList.add("hidden");
    }
  }

  if (evt.type === "clear_dialogue") {
    userSpeechText.innerText = `"(Awaiting command...)"`;
    jarvisSpeechText.innerText = `"(Standby)"`;
  }
}

function setVisualState(state) {
  currentState = state.toLowerCase();
  document.body.className = `state-${currentState}`;

  // Reset pill classes
  statePill.className = "pill";
  if (currentState === "listening") {
    statePill.classList.add("state-listening");
    stateLabel.innerText = "LISTENING";
    stateWatermark.innerText = "LISTENING";
    targetAudioEnergy = 0.6;
  } else if (currentState === "thinking") {
    statePill.classList.add("state-thinking");
    stateLabel.innerText = "REASONING";
    stateWatermark.innerText = "THINKING";
    targetAudioEnergy = 0.4;
  } else if (currentState === "speaking") {
    statePill.classList.add("state-speaking");
    stateLabel.innerText = "SPEAKING";
    stateWatermark.innerText = "VOCALIZING";
    targetAudioEnergy = 0.85;
  } else {
    statePill.classList.add("state-idle");
    stateLabel.innerText = "STANDBY";
    stateWatermark.innerText = "READY";
    targetAudioEnergy = 0.15;
  }
}

function setEngine(engine, model) {
  currentEngine = engine.toLowerCase();
  if (currentEngine === "nvidia") {
    enginePill.className = "pill engine-nvidia";
    enginePill.querySelector(".pill-icon").innerText = "☁️";
    engineLabel.innerText = "CLOUD NIM (120B)";
  } else {
    enginePill.className = "pill engine-local";
    enginePill.querySelector(".pill-icon").innerText = "🧠";
    engineLabel.innerText = "LOCAL OLLAMA (3B)";
  }
}

// --- Canvas Arc Reactor Animation Loop ---
function drawReactor() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  // Smoothing audio energy transition
  audioEnergy += (targetAudioEnergy - audioEnergy) * 0.1;
  if (currentState !== "speaking" && targetAudioEnergy > 0.2) {
    targetAudioEnergy *= 0.95;
  }

  // Adjust rotation speeds based on state
  let speedMult = 1.0;
  let activeColor = COLOR_CYAN;

  if (currentState === "thinking") {
    speedMult = 3.5;
    activeColor = COLOR_AMBER;
  } else if (currentState === "speaking") {
    speedMult = 1.8;
    activeColor = COLOR_CYAN;
  } else if (currentState === "listening") {
    speedMult = 0.7;
    activeColor = "#00e5ff";
  }

  rot1 += 0.008 * speedMult;
  rot2 -= 0.012 * speedMult;
  rot3 += 0.018 * speedMult;

  // 1. OUTER STATIC TICK RING (COMPASS)
  ctx.save();
  ctx.translate(cx, cy);
  ctx.strokeStyle = "rgba(0, 240, 255, 0.25)";
  ctx.lineWidth = 1;
  for (let a = 0; a < 360; a += 10) {
    const rad = (a * Math.PI) / 180;
    const len = a % 30 === 0 ? 8 : 4;
    const r1 = 175;
    const r2 = r1 - len;
    ctx.beginPath();
    ctx.moveTo(r1 * Math.cos(rad), r1 * Math.sin(rad));
    ctx.lineTo(r2 * Math.cos(rad), r2 * Math.sin(rad));
    ctx.stroke();
  }
  ctx.restore();

  // 2. CIRCULAR FREQUENCY PINS (AUDIO REACTIVE)
  ctx.save();
  ctx.translate(cx, cy);
  const numPins = 48;
  for (let i = 0; i < numPins; i++) {
    const angle = (i / numPins) * Math.PI * 2 + rot1 * 0.5;
    const wave = Math.sin(angle * 4 + rot3 * 2) * 0.5 + 0.5;
    const pinLen = 4 + wave * 16 * audioEnergy;
    const r1 = 155;
    const r2 = r1 + pinLen;
    ctx.strokeStyle = activeColor;
    ctx.lineWidth = 2;
    ctx.shadowBlur = 6 * audioEnergy;
    ctx.shadowColor = activeColor;
    ctx.beginPath();
    ctx.moveTo(r1 * Math.cos(angle), r1 * Math.sin(angle));
    ctx.lineTo(r2 * Math.cos(angle), r2 * Math.sin(angle));
    ctx.stroke();
  }
  ctx.restore();

  // 3. ROTATING SEGMENTED RING 1 (OUTER)
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rot1);
  ctx.strokeStyle = "rgba(0, 240, 255, 0.5)";
  ctx.lineWidth = 3;
  ctx.setLineDash([18, 12, 6, 12]);
  ctx.beginPath();
  ctx.arc(0, 0, 142, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // 4. COUNTER-ROTATING RING 2 (MIDDLE)
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rot2);
  ctx.strokeStyle = activeColor;
  ctx.lineWidth = 2;
  ctx.shadowBlur = 10;
  ctx.shadowColor = activeColor;
  ctx.setLineDash([35, 20]);
  ctx.beginPath();
  ctx.arc(0, 0, 122, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // 5. TEN ARC REACTOR POWER CELLS (MARK II SEGMENTS)
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(rot3);
  const numCells = 10;
  for (let i = 0; i < numCells; i++) {
    const a = (i / numCells) * Math.PI * 2;
    ctx.save();
    ctx.rotate(a);
    ctx.fillStyle = activeColor;
    ctx.shadowBlur = 12 * audioEnergy + 4;
    ctx.shadowColor = activeColor;
    ctx.fillRect(86, -7, 20, 14);
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1;
    ctx.strokeRect(86, -7, 20, 14);
    ctx.restore();
  }
  ctx.restore();

  // 6. INNER GEOMETRIC CORE RING
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(-rot3 * 1.5);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
  ctx.lineWidth = 2;
  ctx.setLineDash([8, 8]);
  ctx.beginPath();
  ctx.arc(0, 0, 68, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // 7. GLOWING ENERGY CORE
  ctx.save();
  ctx.translate(cx, cy);
  const pulseR = 48 + Math.sin(Date.now() * 0.004) * 4 + audioEnergy * 10;
  const grad = ctx.createRadialGradient(0, 0, 10, 0, 0, pulseR);
  grad.addColorStop(0, "rgba(255, 255, 255, 0.95)");
  grad.addColorStop(0.3, activeColor);
  grad.addColorStop(0.7, "rgba(0, 102, 255, 0.4)");
  grad.addColorStop(1, "transparent");

  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(0, 0, pulseR, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 8. UPDATE EQUALIZER BARS (BOTTOM SOUNDWAVE)
  for (let i = 0; i < NUM_EQ_BARS; i++) {
    const distFromCenter = Math.abs(i - NUM_EQ_BARS / 2) / (NUM_EQ_BARS / 2);
    const wave = Math.sin(Date.now() * 0.008 + i * 0.35) * 0.5 + 0.5;
    const barHeight = Math.max(4, Math.floor(wave * (32 - distFromCenter * 14) * audioEnergy));
    eqBars[i].style.height = `${barHeight}px`;
    eqBars[i].style.background = activeColor;
    eqBars[i].style.boxShadow = `0 0 ${barHeight / 3}px ${activeColor}`;
  }

  requestAnimationFrame(drawReactor);
}

// Start visualizer and event stream on load
window.addEventListener("DOMContentLoaded", () => {
  initEventStream();
  drawReactor();
});
