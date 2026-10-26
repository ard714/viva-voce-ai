# 🏛️ VivaPrep AI: Complete Architectural Guide & Testing Manual

> **Live Production App**: [https://viva-voce-ai.onrender.com/](https://viva-voce-ai.onrender.com/)  
> **GitHub Repository**: [https://github.com/ard714/viva-voce-ai](https://github.com/ard714/viva-voce-ai)

---

## 1. What This Project Is Supposed to Do vs What It Does

### What It Is Supposed to Do
In Indian higher education (engineering, pharmacy, polytechnics, science colleges), up to **40% of practical marks** are determined in a 5-minute oral examination (*viva voce*). Students read notes silently in the library, but freeze when an external examiner asks questions out loud. Furthermore, students naturally think and formulate answers in **code-mixed speech (Hinglish/Tanglish)**, which standard US-centric mock interview tools flag as errors.

**VivaPrep AI is designed to:**
1. Ingest any college lab manual or custom notes.
2. Interrogate the student out loud with an authentic Indian professor persona.
3. Listen to the student's spoken answer in English or code-mixed Hinglish.
4. Detect **bluffing** (hand-waving without explaining principles) and drill into weak spots.
5. Provide an official scorecard (/25 marks) with feedback translated into **22 Indian languages**.

### What It Is Actually Doing Right Now
- **Live in Production**: Deployed on Render (`https://viva-voce-ai.onrender.com/`) and running locally (`http://localhost:8000`).
- **Full Indic AI Stack**:
  - `sarvam-105b` & `sarvam-105b-conversations` for reasoning, adversarial follow-ups, and bluff scoring.
  - `bulbul:v4-flash` for high-speed voice synthesis across 3 distinct teacher personas.
  - `saaras:v4` (`mode="codemix"`) transcribing student audio with heavy Indian accents and mixed Hinglish.
  - `sarvam-translate:v1` translating full scorecards into Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, and Punjabi.
- **Pre-loaded Syllabi**: 4 ready-to-test lab presets (Analog Electronics, DSA Trees, Fluid Mechanics, Pharmaceutical Chemistry).

---

## 2. Detailed Technical Architecture: How It Works

```
                                  [ STUDENT ]
                                       |
                1. Selects Lab Preset OR Pastes Custom Notes
                2. Picks Examiner Persona (Sharma / Sen / Rao)
                                       |
                                       v
                             +-------------------+
                             |  Browser Frontend |
                             |   (HTML/CSS/JS)   |
                             +-------------------+
                               |               ^
     3. POST /api/init         |               |  4. Returns Q1 Text +
        (Notes + Persona)      |               |     Base64 MP3 Audio
                               v               |
                     +-----------------------------------+
                     |          FastAPI Backend          |
                     +-----------------------------------+
                       |              |               ^
                       |              v               |
                       |       [Bulbul v4 Flash]      |
                       |       Synthesizes audio      |
                       v                              |
               [Sarvam-105B]                          |
               Generates Q1 tailored to notes --------+
```

### The Student Response Loop

```
  [ Student speaks via Mic ]
              |
              v (Web Audio API: WebM Audio Blob)
    POST /api/answer
              |
              v
       [Saaras v4 ASR]  --> Transcribes code-mixed Hinglish with technical accuracy
              |
              v
       [Sarvam-105B]    --> Evaluates correctness (0-10), checks Bluff Meter,
              |             generates adversarial drill-down follow-up
              v
     [Bulbul v4 Flash]  --> Synthesizes next question audio
              |
              v
     Browser updates waveform, plays professor voice, shows live score chip
```

---

## 3. Rigorous Testing Guide (What You Should Check)

To ensure every component is functioning with 100% reliability, test these 5 dimensions:

### Test 1: Examiner Voice Generation (`Bulbul v4 Flash`)
- **What to do**: Click any preset (e.g. *Analog Electronics*) and click **Start Oral Examination**.
- **What to check**:
  1. The examiner podium lights up with animated sound wave bars.
  2. The question text appears in the bubble.
  3. The speaker icon button (🔊) allows replaying the audio at any time.
  4. Audio should play clearly with the professor's accent without stutter.

### Test 2: Code-Mixed Speech Transcription (`Saaras v4`)
- **What to do**: Click the microphone icon (🎤) and speak in Hinglish:
  > *"Sir, virtual ground isiliye form hota hai because open loop gain practically infinite hota hai, so inverting terminal ground potential assume karta hai."*
- **What to check**:
  1. Click the mic again to stop recording.
  2. Click **Submit Answer to Examiner**.
  3. Look at the recognized transcript: Saaras v4 should accurately capture technical terms (`virtual ground`, `open loop gain`, `inverting terminal`) alongside Hindi verbs (`form hota hai`, `assume karta hai`).

### Test 3: The Bluff Buster & Zero-Tolerance Gibberish Detection
- **What to do**: Submit pure gibberish (e.g. `"asdfghjkl zxcvbnm qwertyuiop"`, `"idk lol"`, or repeated words).
- **What to verify**:
  - Round score is strictly **0/10** (never 15/25).
  - The UI highlights `⚠️ Hand-waving / Gibberish Detected`.
  - Examiner status shows `❌ Examiner Unsatisfied — Drills Deeper`.
  - Final scorecard caps marks at $\le 2.0/25$ with Grade **F**.

### Test 3B: Dynamic Examiner Grilling (Unsatisfied Follow-ups)
- **What to do**: Provide evasive, partial, or weak answers at the nominal last question (Question 3).
- **What to verify**:
  - The examiner does **not** terminate prematurely!
  - The examiner says *"I am not satisfied with your explanation. Let me drill deeper:"* and asks Question 4, Question 5, etc. (up to 6 questions).
  - The question counter updates dynamically (e.g. `Question 4 of 4`).
- **What to do**: Intentionally give a vague, evasive answer without formulas or principles:
  > *"Sir, this experiment is very important in modern electronics and we use it everywhere in industry to amplify signals nicely."*
- **What to check**:
  1. The intermediate feedback chip should show **⚠️ Hand-waving / Bluff Detected**.
  2. The score for that question will drop to 2-4 / 10.
  3. The examiner will immediately challenge your evasion: *"You gave a generic description. Explain the mathematical formula for gain."*

### Test 4: All 3 Examiner Personas
- **Prof. R.K. Sharma (Strict External)**: Voice `ratan_hi_documentary` — Demands derivations, cuts off buzzwords.
- **Dr. Ananya Sen (Supportive Guide)**: Voice `shreya_hi_conversational` — Constructive, patient hints.
- **Dr. Kabir Rao (Rapid-Fire Formula)**: Voice `kabir_hi_conversational` — Direct, fast-paced formula interrogation.

### Test 5: Mother-Tongue Scorecard Translation (`Sarvam-Translate`)
- **What to do**: Complete all 3 questions to reach the **VivaPrep AI Scorecard**.
- **What to check**:
  1. Overall score out of 25 marks is calculated.
  2. Strengths and High-Yield Revision bullet points are rendered.
  3. Select **Hindi (हिन्दी)**, **Tamil (தமிழ்)**, or **Telugu (తెలుగు)** and click **Translate Feedback**.
  4. The translated advice appears in the purple banner with accurate technical translation.

---

## 4. How an Independent User Can Use It with Their Own Data

Any student, professor, or independent user can use this tool for **any academic subject** without touching a line of code:

### Method A: Direct Web UI (Zero Coding)
1. Open **[https://viva-voce-ai.onrender.com/](https://viva-voce-ai.onrender.com/)**.
2. In **Lab Course / Department**, type your subject (e.g., *Biochemistry Lab - MBBS 1st Year*).
3. In **Experiment Title / Topic**, type your experiment (e.g., *Estimation of Serum Creatinine by Jaffe's Reaction*).
4. In **Lab Manual Key Concepts & Formulas**, paste:
   - Your lab manual procedure notes.
   - Key formulas (e.g. Beer-Lambert's law, standard concentration values).
   - Expected clinical significance or common viva questions.
5. Select your preferred Examiner Persona and click **Start Oral Examination**.
6. The AI examiner will dynamically calibrate questions **exclusively from your pasted notes**.

### Method B: Self-Hosting with Own API Key
1. Clone the repository:
   ```bash
   git clone https://github.com/ard714/viva-voce-ai.git
   cd viva-voce-ai
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your own Sarvam API key in `.env`:
   ```env
   SARVAM_API_KEY=your_key_here
   ```
4. Start the server:
   ```bash
   python -m uvicorn app:app --port 8000
   ```
5. Open `http://localhost:8000`. All student transcripts, audio recordings, and evaluations stay completely private on your local machine.
