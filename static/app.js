// Viva Voce AI - Client Application Logic

let currentSessionId = null;
let currentPersona = null;
let currentAudioBase64 = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let recordedAudioBlob = null;
let audioContext = null;
let analyser = null;
let animFrameId = null;

// DOM Elements
const setupStage = document.getElementById("setup-stage");
const arenaStage = document.getElementById("arena-stage");
const scorecardStage = document.getElementById("scorecard-stage");

const presetContainer = document.getElementById("preset-buttons");
const personaGrid = document.getElementById("persona-grid");
const vivaSetupForm = document.getElementById("viva-setup-form");
const subjectInput = document.getElementById("subject-input");
const topicInput = document.getElementById("topic-input");
const notesInput = document.getElementById("notes-input");
const startVivaBtn = document.getElementById("start-viva-btn");

const currentQNum = document.getElementById("current-q-num");
const totalQNum = document.getElementById("total-q-num");
const vivaProgressFill = document.getElementById("viva-progress-fill");
const activePersonaTitle = document.getElementById("active-persona-title");
const examinerAvatar = document.getElementById("examiner-avatar");
const examinerName = document.getElementById("examiner-name");
const examinerStatusPill = document.getElementById("examiner-status-pill");
const questionText = document.getElementById("question-text");
const replayAudioBtn = document.getElementById("replay-audio-btn");
const abortVivaBtn = document.getElementById("abort-viva-btn");

const micToggleBtn = document.getElementById("mic-toggle-btn");
const micStatusLabel = document.getElementById("mic-status-label");
const answerTextFallback = document.getElementById("answer-text-fallback");
const submitAnswerBtn = document.getElementById("submit-answer-btn");
const audioVisualizerCanvas = document.getElementById("audio-visualizer");
const vivaAudioPlayer = document.getElementById("viva-audio-player");

const intermediateFeedback = document.getElementById("intermediate-feedback");
const feedbackBadge = document.getElementById("feedback-badge");
const feedbackText = document.getElementById("feedback-text");
const bluffChip = document.getElementById("bluff-chip");

// Scorecard elements
const finalMarksDisplay = document.getElementById("final-marks-display");
const gradeDisplay = document.getElementById("grade-display");
const examinerVerdictText = document.getElementById("examiner-verdict-text");
const overallBluffText = document.getElementById("overall-bluff-text");
const strengthsList = document.getElementById("strengths-list");
const revisionList = document.getElementById("revision-list");
const roundHistoryList = document.getElementById("round-history-list");
const targetLangSelect = document.getElementById("target-lang-select");
const translateReportBtn = document.getElementById("translate-report-btn");
const translatedBox = document.getElementById("translated-box");
const translatedTextDisplay = document.getElementById("translated-text-display");
const restartVivaBtn = document.getElementById("restart-viva-btn");

let allPresets = [];
let allPersonas = {};
let selectedPersonaId = "strict_external";

// Initialize application
document.addEventListener("DOMContentLoaded", async () => {
  await loadPresetsAndPersonas();
  setupEventListeners();
  drawIdleWaveform();
});

async function loadPresetsAndPersonas() {
  try {
    const res = await fetch("/api/presets");
    const data = await res.json();
    allPresets = data.presets || [];
    allPersonas = data.personas || {};

    renderPresets();
    renderPersonas();
  } catch (err) {
    console.error("Error loading presets:", err);
  }
}

function renderPresets() {
  presetContainer.innerHTML = "";
  allPresets.forEach((p, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `preset-btn ${idx === 0 ? "active" : ""}`;
    btn.innerHTML = `<span>??</span> <span>${p.subject.split("(")[0].trim()}</span>`;
    btn.onclick = () => selectPreset(p, btn);
    presetContainer.appendChild(btn);
  });

  if (allPresets.length > 0) {
    applyPresetData(allPresets[0]);
  }
}

function selectPreset(preset, btnElem) {
  document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
  btnElem.classList.add("active");
  applyPresetData(preset);
}

function applyPresetData(p) {
  subjectInput.value = p.subject;
  topicInput.value = p.topic;
  notesInput.value = p.notes;
}

function renderPersonas() {
  personaGrid.innerHTML = "";
  Object.entries(allPersonas).forEach(([id, p]) => {
    const card = document.createElement("div");
    card.className = `persona-card ${id === selectedPersonaId ? "selected" : ""}`;
    card.innerHTML = `
      <div class="persona-header">
        <div class="persona-avatar">${p.avatar}</div>
        <div>
          <div class="persona-title">${p.name}</div>
          <div class="persona-subtitle">${p.title}</div>
        </div>
      </div>
      <p class="persona-desc">${p.tone}</p>
    `;
    card.onclick = () => {
      document.querySelectorAll(".persona-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      selectedPersonaId = id;
    };
    personaGrid.appendChild(card);
  });
}

function setupEventListeners() {
  // Setup Form Submit
  vivaSetupForm.onsubmit = async (e) => {
    e.preventDefault();
    await startVivaSession();
  };

  // Mic Toggle
  micToggleBtn.onclick = toggleRecording;

  // Textarea input activates submit button
  answerTextFallback.addEventListener("input", () => {
    if (answerTextFallback.value.trim().length > 0) {
      submitAnswerBtn.disabled = false;
    } else if (!recordedAudioBlob) {
      submitAnswerBtn.disabled = true;
    }
  });

  // Submit Answer Button
  submitAnswerBtn.onclick = submitAnswer;

  // Replay Audio
  replayAudioBtn.onclick = () => {
    if (currentAudioBase64) {
      playBase64Audio(currentAudioBase64);
    }
  };

  // Abort / Exit
  abortVivaBtn.onclick = () => {
    if (confirm("Are you sure you want to exit this viva session?")) {
      resetToSetup();
    }
  };

  // Restart / Retake
  restartVivaBtn.onclick = resetToSetup;

  // Translate Report
  translateReportBtn.onclick = handleTranslateReport;
}

async function startVivaSession() {
  startVivaBtn.disabled = true;
  startVivaBtn.innerHTML = `<span>?</span> <span>Generating Examiner & First Question...</span>`;

  const formData = new FormData();
  formData.append("subject", subjectInput.value.trim());
  formData.append("topic", topicInput.value.trim());
  formData.append("notes", notesInput.value.trim());
  formData.append("persona_id", selectedPersonaId);
  formData.append("total_questions", 3);

  try {
    const res = await fetch("/api/init", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to initialize viva session.");
    }

    const data = await res.json();
    currentSessionId = data.session_id;
    currentPersona = data.persona;
    currentAudioBase64 = data.audio_base64;

    // Transition to Arena
    setupStage.classList.remove("active");
    scorecardStage.classList.remove("active");
    arenaStage.classList.add("active");

    // Populate Arena Info
    currentQNum.textContent = data.question_number;
    totalQNum.textContent = data.total_questions;
    updateProgressBar(data.question_number, data.total_questions);

    examinerAvatar.textContent = currentPersona.avatar;
    examinerName.textContent = currentPersona.name;
    activePersonaTitle.textContent = `${currentPersona.name} (${currentPersona.title})`;

    questionText.textContent = data.question_text;

    // Play Audio
    if (currentAudioBase64) {
      playBase64Audio(currentAudioBase64);
    }

    // Reset Answer Inputs
    resetAnswerConsole();

  } catch (err) {
    alert("Viva initialization failed: " + err.message);
  } finally {
    startVivaBtn.disabled = false;
    startVivaBtn.innerHTML = `<span class="btn-icon">?</span><span>Start Oral Examination</span>`;
  }
}

function updateProgressBar(cur, total) {
  const pct = Math.round((cur / total) * 100);
  vivaProgressFill.style.width = `${pct}%`;
}

function playBase64Audio(b64) {
  try {
    vivaAudioPlayer.src = `data:audio/mp3;base64,${b64}`;
    examinerStatusPill.classList.add("speaking");
    vivaAudioPlayer.play().catch(e => console.log("Audio autoplay prevented by browser:", e));

    vivaAudioPlayer.onended = () => {
      examinerStatusPill.classList.remove("speaking");
    };
  } catch (e) {
    console.error("Audio playback error:", e);
  }
}

// Microphone Recording Management
async function toggleRecording() {
  if (isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // Web Audio Visualizer Setup
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyser.fftSize = 64;

    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        audioChunks.push(e.data);
      }
    };

    mediaRecorder.onstop = () => {
      recordedAudioBlob = new Blob(audioChunks, { type: "audio/webm" });
      micStatusLabel.textContent = "Audio recorded! Click submit or re-record.";
      submitAnswerBtn.disabled = false;
      stream.getTracks().forEach(track => track.stop());
      cancelAnimationFrame(animFrameId);
      drawIdleWaveform();
    };

    mediaRecorder.start();
    isRecording = true;
    micToggleBtn.classList.add("recording");
    micStatusLabel.textContent = "Recording answer... Click again to finish speaking.";
    drawLiveWaveform();

  } catch (err) {
    alert("Microphone access denied or unavailable: " + err.message + ". You can type your answer below.");
    micStatusLabel.textContent = "Microphone unavailable. Please type your answer.";
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    micToggleBtn.classList.remove("recording");
  }
}

function drawLiveWaveform() {
  const canvas = audioVisualizerCanvas;
  const ctx = canvas.getContext("2d");
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  function render() {
    animFrameId = requestAnimationFrame(render);
    analyser.getByteFrequencyData(dataArray);

    ctx.fillStyle = "rgba(7, 9, 14, 0.4)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 1.8;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * canvas.height * 0.9;
      
      const grad = ctx.createLinearGradient(0, canvas.height, 0, 0);
      grad.addColorStop(0, "#00f0ff");
      grad.addColorStop(1, "#8b5cf6");
      ctx.fillStyle = grad;

      ctx.fillRect(x, (canvas.height - barHeight) / 2, barWidth - 2, barHeight);
      x += barWidth;
    }
  }
  render();
}

function drawIdleWaveform() {
  const canvas = audioVisualizerCanvas;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "rgba(7, 9, 14, 0.9)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "rgba(0, 240, 255, 0.25)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(0, canvas.height / 2);
  ctx.lineTo(canvas.width, canvas.height / 2);
  ctx.stroke();
}

function resetAnswerConsole() {
  recordedAudioBlob = null;
  audioChunks = [];
  answerTextFallback.value = "";
  submitAnswerBtn.disabled = true;
  micToggleBtn.classList.remove("recording");
  micStatusLabel.textContent = "Click microphone to speak your answer";
  drawIdleWaveform();
}

async function submitAnswer() {
  if (!currentSessionId) return;

  submitAnswerBtn.disabled = true;
  submitAnswerBtn.innerHTML = `<span>?</span> <span>Examiner Evaluating Response (Sarvam AI)...</span>`;

  const formData = new FormData();
  formData.append("session_id", currentSessionId);

  if (recordedAudioBlob) {
    formData.append("audio_file", recordedAudioBlob, "student_answer.webm");
  }
  if (answerTextFallback.value.trim()) {
    formData.append("answer_text", answerTextFallback.value.trim());
  }

  try {
    const res = await fetch("/api/answer", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Evaluation failed.");
    }

    const data = await res.json();

    if (data.status === "ongoing") {
      // Show intermediate feedback
      showIntermediateFeedback(data);

      // Update question
      currentQNum.textContent = data.question_number;
      updateProgressBar(data.question_number, data.total_questions);
      questionText.textContent = data.next_question_text;
      currentAudioBase64 = data.audio_base64;

      if (currentAudioBase64) {
        playBase64Audio(currentAudioBase64);
      }

      resetAnswerConsole();

    } else if (data.status === "completed") {
      // Transition to Scorecard Stage
      renderScorecard(data);
    }

  } catch (err) {
    alert("Error submitting answer: " + err.message);
  } finally {
    submitAnswerBtn.disabled = false;
    submitAnswerBtn.innerHTML = `<span class="btn-icon">?</span><span>Submit Answer to Examiner</span>`;
  }
}

function showIntermediateFeedback(data) {
  feedbackBadge.textContent = `Round Score: ${data.score}/10`;
  feedbackText.textContent = data.last_feedback;

  if (data.bluff_detected) {
    bluffChip.textContent = "?? Hand-waving / Bluff Detected";
    bluffChip.classList.add("warning");
  } else {
    bluffChip.textContent = "? Direct Answer";
    bluffChip.classList.remove("warning");
  }

  intermediateFeedback.classList.remove("hidden");
}

function renderScorecard(data) {
  arenaStage.classList.remove("active");
  scorecardStage.classList.add("active");

  finalMarksDisplay.textContent = data.final_marks;
  gradeDisplay.textContent = `Grade ${data.report.grade || 'A'}`;
  examinerVerdictText.textContent = data.report.examiner_verdict;
  overallBluffText.textContent = data.report.bluff_analysis || "Direct answers with good clarity.";

  // Strengths
  strengthsList.innerHTML = "";
  (data.report.strengths || []).forEach(s => {
    const li = document.createElement("li");
    li.textContent = s;
    strengthsList.appendChild(li);
  });

  // Revision Topics
  revisionList.innerHTML = "";
  (data.report.revision_topics || []).forEach(t => {
    const li = document.createElement("li");
    li.textContent = t;
    revisionList.appendChild(li);
  });

  // Round History
  roundHistoryList.innerHTML = "";
  (data.evaluations || []).forEach(ev => {
    const item = document.createElement("div");
    item.className = "round-item";
    item.innerHTML = `
      <div class="round-head">
        <span>Question ${ev.question_number}</span>
        <span class="round-score">Score: ${ev.score}/10</span>
      </div>
      <div class="round-q">Q: ${ev.question}</div>
      <div class="round-ans">Student: "${ev.student_answer}"</div>
      <div class="round-feed">Feedback: ${ev.feedback}</div>
    `;
    roundHistoryList.appendChild(item);
  });

  // Play concluding audio
  if (data.concluding_audio) {
    playBase64Audio(data.concluding_audio);
  }
}

async function handleTranslateReport() {
  const targetLang = targetLangSelect.value;
  const originalText = examinerVerdictText.textContent.trim();

  translateReportBtn.disabled = true;
  translateReportBtn.textContent = "Translating with Sarvam-Translate...";

  try {
    const formData = new FormData();
    formData.append("text", originalText);
    formData.append("target_lang", targetLang);

    const res = await fetch("/api/translate", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Translation failed.");

    const data = await res.json();
    translatedTextDisplay.textContent = data.translated_text;
    translatedBox.classList.remove("hidden");

  } catch (err) {
    alert("Translation failed: " + err.message);
  } finally {
    translateReportBtn.disabled = false;
    translateReportBtn.textContent = "Translate Feedback";
  }
}

function resetToSetup() {
  currentSessionId = null;
  currentAudioBase64 = null;
  intermediateFeedback.classList.add("hidden");
  translatedBox.classList.add("hidden");
  scorecardStage.classList.remove("active");
  arenaStage.classList.remove("active");
  setupStage.classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}
