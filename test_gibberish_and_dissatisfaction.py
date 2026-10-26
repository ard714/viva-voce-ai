import sys
sys.stdout.reconfigure(encoding='utf-8')
import sys
from fastapi.testclient import TestClient
from app import app, is_gibberish

client = TestClient(app)

print("=== VIVAPREP AI: RIGOROUS VERIFICATION SUITE ===")

# --- 1. Unit Testing `is_gibberish` Heuristics ---
print("\n[Test 1] Testing `is_gibberish` function heuristics...")
assert is_gibberish("asdfghjkl zxcvbnm") == True, "Failed on keyboard mash"
assert is_gibberish("aaaaaaa") == True, "Failed on repeated chars"
assert is_gibberish("blah blah blah") == True, "Failed on repeated word"
assert is_gibberish("idk lol") == True, "Failed on slang dismissal"
assert is_gibberish("pass") == True, "Failed on single pass word"
assert is_gibberish("") == True, "Failed on empty"
assert is_gibberish("   ") == True, "Failed on spaces"
assert is_gibberish("(Student was silent or unable to speak an answer)") == True, "Failed on silence"
# Valid answers must NOT be marked gibberish
assert is_gibberish("Virtual ground means inverting terminal is at 0V") == False, "False positive on technical answer"
assert is_gibberish("Slew rate is 0.5 V per microsecond for IC 741") == False, "False positive on formula"
print("✓ [PASS] All gibberish detection heuristics verified!")

# --- 2. Live API Testing: Gibberish Scoring & No 15/25 Bug ---
print("\n[Test 2] Testing Gibberish Scoring via Live Viva Session...")
init_data = {
    "subject": "Analog Electronics Lab (EE/ECE)",
    "topic": "Operational Amplifiers (Op-Amp 741)",
    "notes": "Virtual ground concept: A_v is infinite, inverting terminal is at 0V. Gain = -Rf/Rin.",
    "persona_id": "strict_external",
    "total_questions": 2
}
res = client.post("/api/init", data=init_data)
assert res.status_code == 200, f"Init failed: {res.text}"
session_id = res.json()["session_id"]
print(f"   Session started! ID: {session_id}")

# Submit gibberish for Question 1
ans_gibberish = {
    "session_id": session_id,
    "answer_text": "asdfghjkl zxcvbnm qwertyuiop"
}
res1 = client.post("/api/answer", data=ans_gibberish)
assert res1.status_code == 200, f"Answer 1 failed: {res1.text}"
ans1 = res1.json()

print(f"   Q1 Answer: '{ans_gibberish['answer_text']}'")
print(f"   Q1 Score: {ans1.get('score')}/10 (Expected: 0)")
print(f"   Q1 Bluff Detected: {ans1.get('bluff_detected')} (Expected: True)")
print(f"   Q1 Examiner Satisfied: {ans1.get('is_satisfied')} (Expected: False)")

assert ans1.get("score") == 0, f"CRITICAL: Gibberish score must be 0, got {ans1.get('score')}"
assert ans1.get("bluff_detected") == True, "Bluff must be detected for gibberish"
assert ans1.get("is_satisfied") == False, "Examiner must NOT be satisfied with gibberish"
print("✓ [PASS] Gibberish Q1 awarded 0/10 with bluff flag!")

# --- 3. Dynamic Question Continuation: Examiner Unsatisfied Grills Deeper ---
print("\n[Test 3] Testing Dynamic Interrogation Continuation when Examiner is Unsatisfied...")
# Note: Initial total_questions was 2.
# We answer Question 2 with more gibberish/slang.
# In the old code, this would have abruptly ended the exam.
# In the new code, the examiner is NOT satisfied, so total_questions increases to 3 and status remains 'ongoing'!

ans_evasive = {
    "session_id": session_id,
    "answer_text": "idk lol nothing"
}
res2 = client.post("/api/answer", data=ans_evasive)
assert res2.status_code == 200, f"Answer 2 failed: {res2.text}"
ans2 = res2.json()

print(f"   Q2 Answer: '{ans_evasive['answer_text']}'")
print(f"   Q2 Score: {ans2.get('score')}/10 (Expected: 0)")
print(f"   Status after Q2: {ans2.get('status')} (Expected: 'ongoing' because examiner is unsatisfied)")
print(f"   Total Questions count: {ans2.get('total_questions')} (Expected: 3, extended from 2)")
print(f"   Next Question: '{ans2.get('next_question_text')}'")

assert ans2.get("status") == "ongoing", f"Expected exam to continue, got {ans2.get('status')}"
assert ans2.get("total_questions") == 3, f"Expected total_questions extended to 3, got {ans2.get('total_questions')}"
assert ans2.get("is_satisfied") == False, "Examiner must be unsatisfied"
print("✓ [PASS] Examiner did not end exam; dynamically added Question 3 to drill deeper!")

# Now answer Question 3 (still unsatisfied)
ans3_res = client.post("/api/answer", data={
    "session_id": session_id,
    "answer_text": "blah blah blah nope"
})
assert ans3_res.status_code == 200
ans3 = ans3_res.json()
print(f"   Q3 Score: {ans3.get('score')}/10")
print(f"   Status after Q3: {ans3.get('status')} (Total questions: {ans3.get('total_questions')})")

# Submit until concluding or answer with a valid answer to test completion
ans_valid = {
    "session_id": session_id,
    "answer_text": "Sir, virtual ground is at inverting terminal, and slew rate for 741 is 0.5 V per microsecond."
}
res_final = client.post("/api/answer", data=ans_valid)
assert res_final.status_code == 200
data_final = res_final.json()

# If still ongoing, submit until completed
while data_final.get("status") == "ongoing":
    print(f"   Grilling deeper on Q{data_final.get('question_number')}: {data_final.get('next_question_text')}")
    res_final = client.post("/api/answer", data=ans_valid)
    data_final = res_final.json()

print(f"\nExam Completed!")
print(f"   Final Marks: {data_final.get('final_marks')} / 25")
print(f"   Report Grade: {data_final.get('report', {}).get('grade')}")
print(f"   Report Verdict: {data_final.get('report', {}).get('examiner_verdict')}")

# Verify that gibberish answers dragged down the score and it is NOT 15.0
assert data_final.get("final_marks") != 15.0, "FAIL: Score is still 15.0!"
print("✓ [PASS] Final marks is NOT 15.0!")

print("\n=== ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY ===")
