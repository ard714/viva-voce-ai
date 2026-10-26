# 🏛️ 5-Minute Demo Pitch: VivaPrep AI
### *The AI External Examiner for College Practical Vivas*

> **Live Production Demo**: [https://viva-voce-ai.onrender.com/](https://viva-voce-ai.onrender.com/)  
> **GitHub Repository**: [https://github.com/ard714/viva-voce-ai](https://github.com/ard714/viva-voce-ai)

---

## ⏱️ Pitch Timeline Breakdown (5 Minutes)

### [0:00 - 1:00] The Hook & The Real Problem
> *"Raise your hand if you’ve ever sat in an engineering, pharmacy, or B.Sc lab, read your lab manual 10 times, thought you were ready, and then sat in front of the external examiner and completely froze."*

- In India, over **35 million college students** take practical exams every semester. Up to **40% of their final lab grade** depends on a 5-minute oral viva.
- **The Catch:** Nobody ever practices speaking technical concepts out loud. Students read silently, cramming formulas.
- When the external professor asks: *"Why did you connect this capacitor here?"* — the student’s mind races in their mother tongue or Hinglish (*"Actually sir, jab frequency badhti hai..."*), but their mouth locks up trying to formulate formal textbook English.
- The professor detects the hesitation, labels it as a bluff, and marks them down.

---

## [1:00 - 1:45] Why Existing AI Fails & Our Unfair Advantage
- If you search for "AI Mock Interview" today, you will find 500 apps for FAANG coding or behavioral HR questions (*"Tell me about a time you had a conflict"*).
- **None of them work for Indian academia.** Academic vivas are not friendly discussions — they are **adversarial**. Professors probe edge cases, test for rote memorization, and catch hand-waving.
- Furthermore, Indian students think in a mix of Hindi/Tamil/Telugu and English. Standard speech models (Whisper/Siri) hallucinate when technical terms are code-mixed.
- **VivaPrep AI solves this natively by building on Sarvam AI’s purpose-built Indic stack.**

---

## [1:45 - 3:00] The Live Demo (Show, Don't Just Tell)
*(Switch screen to the live production app at https://viva-voce-ai.onrender.com/)*

1. **Step 1: Input the Lab Syllabus**
   - *"Let's select a classic: Analog Electronics — Op-Amp Inverting Gain & Slew Rate. We also choose our examiner: Prof. R.K. Sharma, the Strict External Examiner."*
2. **Step 2: The Grilling Begins**
   - Click *Start Oral Exam*. The examiner speaks aloud with an authoritative Indian professor accent using **Bulbul v4 Flash**:
     > *"Explain the physical significance of virtual ground in an inverting op-amp. Why does this assumption fail if open loop gain is small?"*
3. **Step 3: Answering in Code-Mixed Hinglish**
   - Speak naturally into the mic:
     > *"Sir, virtual ground isiliye banta hai because open loop gain practically infinite hota hai, so inverting terminal ground potential assume karta hai without being physically grounded."*
   - Show how **Saaras v4** transcribes this code-mixed speech with 100% precision.
4. **Step 4: The Bluff-Buster Follow-Up**
   - **Sarvam-105B** evaluates the response in real time, checks if the student dodged formulas, and asks an immediate drill-down follow-up.
5. **Step 5: The Academic Scorecard & Vernacular Feedback**
   - Conclude the exam. Show the **21.5 / 25 Marks Breakdown** (Theory, Practical Intuition, Clarity).
   - Click **"Review in Your Mother Tongue"**: **Sarvam-Translate** converts the professor's feedback into Hindi/Tamil/Telugu so the student actually understands their mistake before tomorrow's exam.

---

## [3:00 - 4:00] Under the Hood: Full Sarvam Indic AI Stack
We didn’t just wrap one LLM — we unified the entire Sarvam AI capability matrix:
1. **Sarvam-105B & 105B-Conversations**: Academic reasoning, viva syllabus comprehension, adversarial question generation, and bluff detection.
2. **Bulbul v4 Flash (TTS)**: Realistic teacher personas (`ratan_hi_documentary`, `shreya`, `kabir`) with natural prosody and classroom authority.
3. **Saaras v4 (ASR)**: Native `mode="codemix"` recognizing student speech across 23 languages without phonetic degradation.
4. **Sarvam-Translate**: High-context translation into 22 Indian languages to democratize lab understanding for tier-2/tier-3 college students.

---

## [4:00 - 4:30] Market & Traction Potential
- **Target Audience:** 10,000+ engineering, polytechnic, pharmacy, and medical colleges across India.
- **The Student Persona:** 2nd and 3rd year students standing outside the lab hallway 20 minutes before their external viva, desperately needing a 5-minute drill.
- **Business Model:** 
  - Free for 3 practice vivas per semester.
  - College B2B licensing: Colleges can upload their proprietary lab manuals to prepare their students for university external audits.

---

## [4:30 - 5:00] Closing & Vision
> *"Viva exams shouldn't be a test of how well you pretend not to be nervous. They should be a test of whether you understand the science.*
> 
> *With VivaPrep AI and Sarvam AI, we are giving every Indian student a private external examiner in their pocket — so they can make their mistakes with an AI professor today, and ace their viva tomorrow.*
> 
> *Thank you. We are now open for questions."*
