# Viva Voce: AI Oral Examiner
### Project Plan & Technical Specification

> **Mission**: Build an AI-powered adversarial oral examiner that helps Indian college students prepare for practical and laboratory viva exams by testing spoken understanding, probing weak answers, and handling code-mixed (Hinglish/regional) speech.

---

## 1. Problem Statement & Opportunity

### The Indian Academic Viva Problem
In Indian universities (VTU, AKTU, Anna University, Mumbai University, polytechnics, pharmacy, and medical colleges):
- **Up to 40% of practical marks** come from the viva voce conducted by an external examiner.
- Students practice by silently memorizing formulas, definitions, and theory notes.
- When facing an examiner, students **freeze** or stammer when translating technical concepts into spoken English.
- Students naturally explain concepts in **code-mixed Hinglish / Tanglish** (e.g., *"Sir, jab frequency increase karte hain, reactance decrease hoti hai"*). Most interview prep software marks this as gibberish.
- **Examiners are adversarial**: They detect when a student is bluffing, ask "why" follow-ups, and interrupt memorized rote answers.

### Why Existing Tools Fail
- **Job interview bots (LeetCode / STAR behavioral)** focus on corporate HR questions, not physics derivations, circuit laws, chemical titrations, or pharmacology mechanisms.
- Standard ASR models (Whisper/Google) struggle with heavy Indian regional accents and code-mixed technical jargon.
- Sarvam AI's Indic models provide an unfair advantage in solving this exact problem.

---

## 2. Sarvam AI API & Model Architecture

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion Phase"]
        A[Lab Manual / Notes / Syllabus] --> B[Sarvam Vision OCR]
        B --> C[Topic & Experiment Summary]
    end

    subgraph ExamLoop["2. Viva Interrogation Loop (3-5 Rounds)"]
        C --> D[sarvam-105b: Generate Conceptual Question]
        D --> E[Bulbul v4 Flash: Synthesize Examiner Speech]
        E --> F[Student Speaks Answer via Web Audio]
        F --> G[Saaras v4: Code-Mixed Speech-to-Text]
        G --> H[sarvam-105b-conversations: Evaluate & Bluff Detection]
        H -->|Weak / Incomplete Answer| I[Adversarial Follow-up Drill]
        H -->|Strong Answer| J[Advance to Next Experiment Aspect]
        I --> E
        J --> E
    end

    subgraph Evaluation["3. Feedback & Scorecard"]
        H --> K[Viva Scorecard: Marks out of 25]
        K --> L[High-Yield Revision Points]
        L --> M[Sarvam-Translate: Mother-Tongue Explanation]
    end
```

### Exact Model Specifications

| Component | Sarvam Model ID | Modality | Role |
| :--- | :--- | :--- | :--- |
| **Notes / PDF Ingestion** | `Sarvam Vision` | Image/PDF $\to$ Text | Reads xeroxed notes, handwritten lab journals, and textbook diagrams in 23 languages. |
| **Examiner Logic & Grading** | `sarvam-105b` | Text $\to$ Text | Deep reasoning, fact-checking against syllabus notes, detecting student bluffing. |
| **Conversational Flow** | `sarvam-105b-conversations` | Text $\to$ Text | Real-time, responsive multi-turn dialogue with low latency. |
| **Examiner Voice** | `Bulbul v4 Flash` | Text $\to$ Audio | High-speed, natural prosody with realistic Indian English and Hindi-accented teacher voices. |
| **Student Speech-to-Text** | `Saaras v4` | Audio $\to$ Text | 23-language ASR with `mode="codemix"` to accurately transcribe Hinglish, Tanglish, etc. |
| **Regional Explanations** | `Sarvam-Translate` | Text $\to$ Text | Translates complex feedback and model answers into student's home language (22 Indian languages). |

---

## 3. Product Features & User Experience

### A. Examiner Personas
- **Prof. Sharma (The Strict External)**:
  - Highly critical, demands precise units, cuts off rambling, asks *"Don't recite book lines, explain the physical intuition."*
- **Dr. Ananya (The Supportive Guide)**:
  - Patient, gives hints when the student freezes, asks guided step-by-step questions.
- **The Rapid-Fire Formula Grill**:
  - Fast-paced 15-second timer per question testing constants, pin diagrams, and unit conversions.

### B. The Viva Interaction Loop
1. **Prompt**: The examiner speaks a targeted question aloud via audio.
2. **Response**: Student speaks into the microphone (hands-free VAD or push-to-talk).
3. **Transcription**: Saaras v4 transcribes code-mixed speech, preserving technical keywords.
4. **Adversarial Follow-Up**: If an answer is vague, the examiner immediately challenges it:
   - *"You mentioned reactance decreases, but what happens at resonance? What is the impedance then?"*

### C. The Comprehensive Viva Scorecard
- **Viva Grade**: Scored on the official Indian practical scale (e.g. `/25` marks).
- **Bluff Meter**: Highlights answers where buzzwords were used without explaining underlying principles.
- **Caught Out Points**: Specific concepts where the external examiner would have deducted marks.
- **Cheat Sheet**: 3 bullet-point model answers for missed questions.
- **Audio Replay & Pronunciation**: Audio breakdown of difficult technical terms.

---

## 4. Technical Stack

- **Backend**: Python 3.13 + FastAPI + Uvicorn.
  - SDK: `sarvamai` (Chat, Speech-to-Text, Text-to-Speech, Vision).
  - Environment: Managed through `.env` (`SARVAM_API_KEY`).
  - Session Store: In-memory dictionary / SQLite session cache (no complex DB needed for MVP).
- **Frontend**: Clean Vanilla HTML5 / Modern CSS / Vanilla JavaScript.
  - Audio capture: Native `MediaRecorder` API (recording in 16kHz PCM/WAV or WebM).
  - Audio playback: Native HTML5 Audio element.
  - Glassmorphic, dark-mode academic terminal theme.

---

## 5. Development Roadmap & Milestones

### Phase 1: MVP Core Voice Loop (1-2 Days)
- [x] Environment & SDK configured with active API key.
- [x] Verified chat completion with `sarvam-105b-conversations`.
- [ ] Implement backend endpoint `/api/start-viva` (generates question 1 from pasted notes).
- [ ] Implement backend endpoint `/api/submit-answer` (transcribes student audio with `Saaras v4`, evaluates with `sarvam-105b`, generates next question and audio with `Bulbul v4 Flash`).
- [ ] Simple web UI with mic button and audio player.

### Phase 2: Examiner Personas & Scoring Engine (2-3 Days)
- [ ] Add system prompts for "Strict External", "Helpful Guide", and "Rapid Fire".
- [ ] Add structured JSON evaluation schema (Score, Factuality, Bluffing Detected, Follow-up Strategy).
- [ ] Generate downloadable Markdown Viva Scorecard.

### Phase 3: Lab Manual OCR & Regional Translation (3-4 Days)
- [ ] Add PDF / Image drag-and-drop for lab manuals using `Sarvam Vision`.
- [ ] Add "Explain in My Language" button using `Sarvam-Translate`.

### Phase 4: Phone Call Mode (Stretch / Future)
- [ ] Connect with Sarvam Voice Agents (`Samvaad`) for phone-dial-in viva drills.

---

## 6. Success Metrics
- **End-to-End Latency**: Under 2.5 seconds from student stopping speech to examiner speaking.
- **Code-Mix Accuracy**: Accurate transcription of Hinglish technical explanations without phonetic corruption.
- **Viva Readiness**: Measurable improvement in student confidence and elimination of vague "filler" answers.
