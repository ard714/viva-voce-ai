import os
import uuid
import json
import base64
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from sarvamai import SarvamAI

API_KEY = os.getenv("SARVAM_API_KEY")
if not API_KEY:
    raise RuntimeError("SARVAM_API_KEY environment variable is missing.")

client = SarvamAI(api_subscription_key=API_KEY)

app = FastAPI(title="Viva Voce AI", description="Academic Oral Examination AI Powered by Sarvam AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: Dict[str, Dict[str, Any]] = {}

# Personas with voice mappings
PERSONAS = {
    "strict_external": {
        "name": "Prof. R.K. Sharma",
        "title": "Strict External Examiner",
        "voice": "ratan_hi_documentary",
        "tone": "adversarial, precise, catches bluffing, demands physical intuition and exact formulas, intolerant of vague theory recitation.",
        "avatar": "?????"
    },
    "friendly_guide": {
        "name": "Dr. Ananya Sen",
        "title": "Supportive Internal Guide",
        "voice": "shreya",
        "tone": "encouraging, patient, breaks down complex doubts, offers hints when the student struggles, checks core concepts.",
        "avatar": "?????"
    },
    "rapid_fire": {
        "name": "Dr. Kabir Rao",
        "title": "Rapid-Fire Formula Examiner",
        "voice": "kabir_hi_conversational",
        "tone": "fast-paced, direct, quizzes on units, pin diagrams, constants, and circuit laws without preamble.",
        "avatar": "?"
    }
}

PRESETS = [
    {
        "id": "electronics_opamp",
        "subject": "Analog Electronics Lab (EE/ECE)",
        "topic": "Operational Amplifiers (Op-Amp 741): Inverting, Non-Inverting, and Slew Rate",
        "notes": """Experiment: Study of Inverting & Non-Inverting Amplifiers using IC 741.
Key Concepts:
- Virtual Ground concept: In an inverting op-amp with high open-loop gain (A ~ 10^5), the potential difference between inverting (-) and non-inverting (+) terminals is approximately zero. Since (+) is at ground, (-) is virtually at ground.
- Inverting Gain formula: A_v = - (R_f / R_in). Negative sign denotes 180 degree phase shift.
- Non-Inverting Gain formula: A_v = 1 + (R_f / R_1). Zero phase shift.
- Slew Rate: Maximum rate of change of output voltage per unit time, SR = (dV_out / dt)_max, typically 0.5 V/microsecond for IC 741. Caused by internal compensation capacitor charging limits.
- Common Mode Rejection Ratio (CMRR): Ratio of differential gain to common-mode gain, CMRR = A_d / A_cm, ideally infinite, practically ~90dB."""
    },
    {
        "id": "cs_trees",
        "subject": "Data Structures & Algorithms Lab (CSE/IT)",
        "topic": "Binary Search Trees (BST) & AVL Balancing",
        "notes": """Experiment: Implementation and Verification of Binary Search Trees (BST) & AVL Self-Balancing.
Key Concepts:
- BST Property: For every node N, all keys in left subtree < N.key, and all keys in right subtree > N.key.
- Inorder traversal of BST yields keys in strictly ascending sorted order.
- Time Complexity: O(h) for search, insert, and delete, where h is tree height. Best case h = O(log n), worst case (skewed tree) h = O(n).
- AVL Trees maintain strict balance factor: Balance Factor BF = height(left) - height(right) must be in {-1, 0, +1}.
- Rotations: Single (LL, RR) and Double (LR, RL) rotations restore balance upon insertion/deletion in O(1) time per node."""
    },
    {
        "id": "mech_bernoulli",
        "subject": "Fluid Mechanics Lab (Mechanical/Civil)",
        "topic": "Verification of Bernoulli's Theorem using Venturimeter",
        "notes": """Experiment: Verification of Bernoulli's Principle along a Converging-Diverging Venturimeter.
Key Concepts:
- Bernoulli's Equation: P/rho*g + v^2/(2g) + z = Constant along a streamline for steady, incompressible, inviscid fluid flow.
- Pressure head (P/rho*g), Velocity head (v^2/2g), Datum head (z).
- Venturimeter: Flow measurement device based on Bernoulli. Consists of converging cone (21 deg), throat, and diverging cone (5-7 deg).
- Why diverging cone angle is smaller: To prevent boundary layer separation and flow eddies (cavitation and head loss).
- Coefficient of discharge C_d: Actual discharge / Theoretical discharge, typically 0.96 to 0.98 due to viscous friction."""
    },
    {
        "id": "pharm_titration",
        "subject": "Pharmaceutical Chemistry Lab (B.Pharm/B.Sc)",
        "topic": "Acid-Base Neutralization Titration & pH Indicators",
        "notes": """Experiment: Assay of Sodium Hydroxide using standard Oxalic Acid solution with Phenolphthalein.
Key Concepts:
- Primary Standard vs Secondary Standard: Oxalic acid is a primary standard (pure, stable, known stoichiometry). NaOH is secondary (hygroscopic, absorbs atmospheric CO2).
- Equivalence point vs End point: Equivalence point is theoretical stoichiometric neutrality. End point is the experimental observation marked by indicator color change.
- Phenolphthalein pH range: 8.2 to 10.0 (colorless in acid, deep pink in alkaline medium due to quinonoid structure formation).
- Buffer solution: Resists pH changes upon addition of small amounts of acid or base; governed by Henderson-Hasselbalch equation."""
    }
]

def synthesize_speech(text: str, voice_name: str = "ratan_hi_documentary", lang: str = "en-IN") -> str:
    """Generate audio via Sarvam Bulbul v4 Flash and return base64 string."""
    try:
        # Normalize text to keep it concise and audio-friendly
        clean_text = text.replace("*", "").replace("#", "").strip()
        if len(clean_text) > 450:
            clean_text = clean_text[:450] + "."

        res = client.text_to_speech.convert(
            text=clean_text,
            language_code=lang,
            model="bulbul:v4-flash",
            speaker=voice_name,
            output_audio_codec="mp3"
        )
        if res.audios and len(res.audios) > 0:
            return res.audios[0]
    except Exception as e:
        print(f"TTS generation error: {e}")
    return ""

@app.get("/api/presets")
def get_presets():
    return {"presets": PRESETS, "personas": PERSONAS}

@app.post("/api/init")
def init_viva(
    subject: str = Form(...),
    topic: str = Form(...),
    notes: str = Form(...),
    persona_id: str = Form("strict_external"),
    total_questions: int = Form(3)
):
    persona = PERSONAS.get(persona_id, PERSONAS["strict_external"])
    session_id = str(uuid.uuid4())

    system_prompt = f"""You are {persona['name']}, {persona['title']} conducting a formal oral viva exam in an Indian university.
Your examination style is {persona['tone']}.
Subject: {subject}
Topic: {topic}

The student has submitted the following lab notes:
---
{notes}
---

Your task:
1. Greet the student briefly in 1 authoritative sentence.
2. Ask your FIRST viva question based on the notes. Focus on foundational principles, working formulas, or experimental significance.
Keep your response short (max 2-3 sentences total) because this will be spoken out loud by TTS. Do not include markdown headers or bullet points."""

    try:
        response = client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
            max_tokens=150
        )
        first_q = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sarvam LLM Error: {str(e)}")

    audio_b64 = synthesize_speech(first_q, voice_name=persona["voice"], lang="en-IN")

    sessions[session_id] = {
        "session_id": session_id,
        "subject": subject,
        "topic": topic,
        "notes": notes,
        "persona_id": persona_id,
        "total_questions": total_questions,
        "current_question_index": 1,
        "history": [
            {"role": "assistant", "content": first_q}
        ],
        "evaluations": []
    }

    return {
        "session_id": session_id,
        "question_number": 1,
        "total_questions": total_questions,
        "question_text": first_q,
        "audio_base64": audio_b64,
        "persona": persona
    }

@app.post("/api/answer")
async def submit_answer(
    session_id: str = Form(...),
    answer_text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None)
):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Viva session not found.")

    session = sessions[session_id]
    persona = PERSONAS.get(session["persona_id"], PERSONAS["strict_external"])
    
    # Process spoken audio if provided
    transcribed_text = ""
    if audio_file is not None:
        try:
            audio_bytes = await audio_file.read()
            if len(audio_bytes) > 0:
                filename = audio_file.filename or "student_audio.webm"
                res = client.speech_to_text.transcribe(
                    file=(filename, audio_bytes, audio_file.content_type or "audio/webm"),
                    model="saaras:v4",
                    mode="codemix"
                )
                transcribed_text = res.transcript.strip()
        except Exception as e:
            print(f"Speech transcription error: {e}")

    student_answer = transcribed_text if transcribed_text else (answer_text or "").strip()
    if not student_answer:
        student_answer = "(Student was silent or unable to speak an answer)"

    session["history"].append({"role": "user", "content": student_answer})

    last_question = session["history"][-2]["content"]
    q_idx = session["current_question_index"]
    total_q = session["total_questions"]
    is_last = (q_idx >= total_q)

    # Evaluation & Next Step Prompt
    eval_prompt = f"""You are {persona['name']}, evaluating a student's oral answer in a viva exam.
Notes context:
{session['notes']}

Question Asked: {last_question}
Student's Spoken Answer (transcribed, may be Hinglish or English): "{student_answer}"

Evaluate this answer rigorously:
1. 'score': integer from 0 to 10 (10 = fully accurate physical intuition + formula, 5 = partial/vague, 0-2 = wrong or pure bluff).
2. 'bluff_detected': boolean (true if student used buzzwords or hand-waving without explaining actual concepts).
3. 'feedback': 1-2 concise sentences on what was correct and what key fact was missing.
4. 'next_action': {"'finish'" if is_last else "'follow_up'"}.
5. 'next_question': {"''" if is_last else "your next viva question. If the student gave a weak/bluffing answer, interrogate that specific flaw. If strong, advance to the next critical lab concept. Keep it 2 sentences max for spoken audio."}

Respond ONLY with valid JSON in this exact structure:
{{
  "score": 7,
  "bluff_detected": false,
  "bluff_comment": "Student answered accurately without dodging.",
  "feedback": "Correct definition of slew rate, but missed stating the typical value for IC 741.",
  "next_question": "What happens to the output waveform if the input frequency exceeds the slew rate limit?"
}}"""

    try:
        response = client.chat.completions(
            model="sarvam-105b",
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.3,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        eval_data = json.loads(content.strip())
    except Exception as e:
        # Fallback evaluation
        eval_data = {
            "score": 6,
            "bluff_detected": False,
            "bluff_comment": "Evaluated based on student input.",
            "feedback": "Concept addressed. Practice stating the exact formulas and units.",
            "next_question": "Explain the practical sources of error in this experiment."
        }

    session["evaluations"].append({
        "question_number": q_idx,
        "question": last_question,
        "student_answer": student_answer,
        "score": eval_data.get("score", 5),
        "bluff_detected": eval_data.get("bluff_detected", False),
        "bluff_comment": eval_data.get("bluff_comment", ""),
        "feedback": eval_data.get("feedback", "")
    })

    if not is_last:
        next_q = eval_data.get("next_question", "Explain the sources of experimental error in this setup.")
        session["current_question_index"] += 1
        session["history"].append({"role": "assistant", "content": next_q})

        audio_b64 = synthesize_speech(next_q, voice_name=persona["voice"], lang="en-IN")

        return {
            "status": "ongoing",
            "session_id": session_id,
            "question_number": session["current_question_index"],
            "total_questions": total_q,
            "transcribed_text": student_answer,
            "last_feedback": eval_data.get("feedback", ""),
            "bluff_detected": eval_data.get("bluff_detected", False),
            "score": eval_data.get("score", 5),
            "next_question_text": next_q,
            "audio_base64": audio_b64
        }
    else:
        # Generate Final Viva Scorecard
        scores = [e["score"] for e in session["evaluations"]]
        avg_score = sum(scores) / len(scores) if scores else 5
        # Total out of 25 (Standard Indian practical exam scale)
        final_marks = round((avg_score / 10.0) * 25, 1)

        summary_prompt = f"""You are {persona['name']}. The viva exam for {session['subject']} has concluded.
Student's performance record:
{json.dumps(session['evaluations'], indent=2)}

Generate a final Academic Viva Report:
1. 'grade': Letter grade (A+, A, B, C, F)
2. 'examiner_verdict': 2 sentences in character summarizing readiness for external practical exam.
3. 'strengths': list of 2 key strengths.
4. 'revision_topics': list of 3 high-yield topics the student MUST revise before facing the external professor.
5. 'bluff_analysis': 1 sentence on the student's communication clarity vs hand-waving.

Respond ONLY with valid JSON in this exact structure:
{{
  "grade": "A",
  "examiner_verdict": "Demonstrated sound understanding of core formulas, but needs to be faster on derivations.",
  "strengths": ["Clear understanding of virtual ground", "Accurately recalled gain equation"],
  "revision_topics": ["Slew rate distortion graph", "CMRR calculation steps", "Frequency response curve"],
  "bluff_analysis": "Direct answers with minimal dodging."
}}"""

        try:
            report_res = client.chat.completions(
                model="sarvam-105b",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3,
                max_tokens=400
            )
            raw = report_res.choices[0].message.content.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            report = json.loads(raw.strip())
        except Exception:
            report = {
                "grade": "B+",
                "examiner_verdict": "Satisfactory conceptual baseline. Work on numerical parameters and derivation steps.",
                "strengths": ["Answered with confidence", "Good grasp of primary law"],
                "revision_topics": ["Key formula derivations", "Practical apparatus limitations", "Unit conversions"],
                "bluff_analysis": "Fair clarity."
            }

        concluding_audio_text = f"That concludes your viva. Your total score is {final_marks} out of 25. Check your detailed feedback sheet."
        audio_b64 = synthesize_speech(concluding_audio_text, voice_name=persona["voice"], lang="en-IN")

        return {
            "status": "completed",
            "session_id": session_id,
            "transcribed_text": student_answer,
            "final_marks": final_marks,
            "total_possible": 25,
            "report": report,
            "evaluations": session["evaluations"],
            "concluding_audio": audio_b64
        }

@app.post("/api/translate")
def translate_report(
    text: str = Form(...),
    target_lang: str = Form("hi-IN")
):
    try:
        res = client.text.translate(
            input=text,
            source_language_code="en-IN",
            target_language_code=target_lang,
            model="sarvam-translate:v1"
        )
        return {"translated_text": res.translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

# Mount static folder
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
