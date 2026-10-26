from fastapi.testclient import TestClient
from app import app
import sys

client = TestClient(app)

print("1. Testing GET /api/presets...")
res = client.get("/api/presets")
assert res.status_code == 200
presets = res.json()["presets"]
print(f"   Success! Found {len(presets)} presets.")

print("2. Testing POST /api/init...")
init_data = {
    "subject": presets[0]["subject"],
    "topic": presets[0]["topic"],
    "notes": presets[0]["notes"],
    "persona_id": "strict_external",
    "total_questions": 2
}
res = client.post("/api/init", data=init_data)
assert res.status_code == 200, f"Init failed: {res.text}"
init_res = res.json()
session_id = init_res["session_id"]
print(f"   Session started! Q1: {init_res['question_text']}")
print(f"   Audio received: {bool(init_res['audio_base64'])}, length: {len(init_res['audio_base64'])}")

print("3. Testing POST /api/answer (Round 1)...")
ans_data = {
    "session_id": session_id,
    "answer_text": "Sir, virtual ground means the potential at the inverting terminal is approximately zero because the open loop gain of op-amp is practically infinite and non-inverting terminal is connected to ground."
}
res = client.post("/api/answer", data=ans_data)
assert res.status_code == 200, f"Answer failed: {res.text}"
ans_res = res.json()
print(f"   Status: {ans_res['status']}")
print(f"   Score: {ans_res.get('score')}/10, Bluff Detected: {ans_res.get('bluff_detected')}")
print(f"   Q2 Followup: {ans_res.get('next_question_text')}")

print("4. Testing POST /api/answer (Round 2 - Final)...")
ans_data_2 = {
    "session_id": session_id,
    "answer_text": "Slew rate is the maximum rate of change of output voltage with time, typically 0.5 V per microsecond for IC 741."
}
res = client.post("/api/answer", data=ans_data_2)
assert res.status_code == 200, f"Answer 2 failed: {res.text}"
final_res = res.json()
print(f"   Final Status: {final_res['status']}")
print(f"   Final Marks: {final_res['final_marks']}/25")
print(f"   Grade: {final_res['report']['grade']}")
print(f"   Verdict: {final_res['report']['examiner_verdict']}")

print("5. Testing POST /api/translate...")
trans_data = {
    "text": final_res['report']['examiner_verdict'],
    "target_lang": "hi-IN"
}
res = client.post("/api/translate", data=trans_data)
assert res.status_code == 200, f"Translate failed: {res.text}"
print("   Translation Success! Hindi text received.")
print("=== ALL FULL-STACK API TESTS PASSED! ===")
