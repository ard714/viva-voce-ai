# 🏛️ VivaPrep AI — The AI External Examiner for Practical Vivas

> **Live Production App**: [https://viva-voce-ai.onrender.com/](https://viva-voce-ai.onrender.com/)  
> **Built with Sarvam AI's Full Indic Stack** — Sarvam-105B (Reasoning & Evaluation), Bulbul v4 Flash (TTS), Saaras v4 (Code-mixed ASR), and Sarvam-Translate (22 Languages).

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-00f0ff.svg)](https://viva-voce-ai.onrender.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Sarvam AI](https://img.shields.io/badge/Powered%20by-Sarvam%20AI-00f0ff.svg)](https://docs.sarvam.ai)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 The Problem
In Indian universities (VTU, AKTU, Anna University, Mumbai University, polytechnics, pharmacy, and science colleges), **practical lab vivas carry up to 40% of total lab marks**.

Students memorize notes silently, but **freeze** when an external examiner asks questions aloud. Furthermore, students think in their mother tongue and answer in **code-mixed Hinglish / Tanglish** (e.g., *"Sir, actually jab frequency increase hoti hai, capacitor short behave karta hai"*). Traditional interview bots fail because they only understand corporate English and don't simulate the adversarial grilling of an external university professor.

## 💡 The Solution
**VivaPrep AI** is an adversarial oral examiner powered by Sarvam AI:
1. **Lab Notes / Syllabus Ingestion**: Input any experiment aim, apparatus notes, or formula derivations (or pick a 1-click preset for EE, CS, Mech, or Pharmacy).
2. **Examiner Spoken Questioning**: The examiner speaks aloud with Indian professor voice personas via **Bulbul v4 Flash**.
3. **Student Spoken Answers**: Students speak naturally into the microphone. **Saaras v4** transcribes code-mixed speech with Indian accents without phonetic degradation.
4. **Adversarial Evaluation & Bluff Buster**: Evaluates conceptual depth, catches missing units/formulas, and programmatically detects gibberish or keyboard mashing (scoring 0/10 with zero-credit penalties).
5. **Dynamic Interrogation & Follow-up Grilling**: If the examiner is unsatisfied with a hand-waving or evasive response, they dynamically ask more questions (extending the viva up to 6 rounds) until the student proves understanding or fails.
6. **Scorecard & Regional Translation**: Generates an official score out of 25 (Theory, Intuition, Precision), revision recommendations, and translates the entire feedback into **22 Indian languages** via **Sarvam-Translate**.

---

## 🏗️ Architecture & Sarvam AI Resource Mapping

```
+---------------------------------------------------------------------------------+
|                                 VIVAPREP AI                                     |
+---------------------------------------------------------------------------------+
          |
          | 1. Lab Notes / Syllabus Preset
          v
+-----------------------------+       2. Question Generation
|     FastAPI Backend         | ----------------------------------> [Sarvam-105B]
|                             |
|                             |       3. Professor Speech
|                             | ----------------------------------> [Bulbul v4 Flash]
|                             |                                             |
|                             |                                             v (Audio)
|                             |                                    +-----------------+
|                             |       4. Student Answer (Audio)    | Browser Arena   |
|                             | <----------------------------------| (Web Audio API) |
|                             |                                    +-----------------+
|                             |       5. Code-Mixed Transcription
|                             | ----------------------------------> [Saaras v4]
|                             |
|                             |       6. Evaluation & Bluff Buster
|                             | ----------------------------------> [Sarvam-105B]
|                             |
|                             |       7. Regional Scorecard
|                             | ----------------------------------> [Sarvam-Translate]
+-----------------------------+
```

| Pipeline Step | Sarvam AI Model | Capability Used |
| :--- | :--- | :--- |
| **Examiner Logic & Grilling** | `sarvam-105b` & `sarvam-105b-conversations` | Dynamic adversarial viva questioning and bluff detection |
| **Professor Voice Output** | `bulbul:v4-flash` | Natural Indic professor voices (`ratan_hi_documentary`, `shreya`, `kabir`) |
| **Student Speech-to-Text** | `saaras:v4` | 23-language ASR with `mode="codemix"` |
| **Mother-Tongue Feedback** | `sarvam-translate:v1` | Translation into Hindi, Tamil, Telugu, Marathi, Bengali, etc. |

---

## 👨‍🏫 Examiner Personas
- **Prof. R.K. Sharma (Strict External Examiner)**: Formal, adversarial, catches bluffing, cuts off rambling, demands exact formulas and units.
- **Dr. Ananya Sen (Supportive Internal Guide)**: Patient, constructive, gives hints when you freeze, reinforces core physics intuition.
- **Dr. Kabir Rao (Rapid-Fire Formula Examiner)**: Fast-paced 15-second timer per question testing constants, pinouts, and circuit laws.

---

## 🚀 Quickstart & Local Run

### 1. Clone Repository
```bash
git clone https://github.com/ard714/viva-voce-ai.git
cd viva-voce-ai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```

### 4. Run Development Server
```bash
python -m uvicorn app:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🚢 Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ard714/viva-voce-ai)

### Production URL
The app is live and deployed on Render:
**[https://viva-voce-ai.onrender.com/](https://viva-voce-ai.onrender.com/)**

### Deploy with Docker
```bash
docker build -t vivaprep-ai .
docker run -p 8000:8000 -e SARVAM_API_KEY=your_key vivaprep-ai
```

---

## 📜 License
MIT License. Crafted for Indian Higher Education.
