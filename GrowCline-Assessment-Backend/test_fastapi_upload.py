"""
FastAPI Recording Endpoint Integration Test
Tests POST /api/recordings/upload with real OAuth Google Drive upload & MongoDB metadata persistence.
"""

import sys
import os
import io
import json
import logging

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app import app
from app.config.database import Database

def test_recording_endpoint():
    print("\n==========================================")
    print("STEP 12 & 13 — TEST FASTAPI RECORDING ENDPOINT & MONGODB")
    print("==========================================")

    from app.utils.jwt_utils import generate_token

    db = Database.get_db()
    
    # 1. Get or create candidate user
    candidate_user = db.users.find_one({"role": "candidate"})
    if not candidate_user:
        res = db.users.insert_one({
            "email": "candidate@growcline.com",
            "name": "Test Candidate",
            "role": "candidate",
        })
        user_id = str(res.inserted_id)
    else:
        user_id = str(candidate_user["_id"])

    token = generate_token({"id": user_id, "role": "candidate"})

    from datetime import datetime
    from bson import ObjectId

    # 2. Create interview owned by this user
    res_int = db.interviews.insert_one({
        "userId": ObjectId(user_id),
        "candidateId": user_id,
        "title": "Test AI Interview",
        "interviewType": "TECHNICAL",
        "status": "IN_PROGRESS",
        "durationMinutes": 30,
        "maxQuestions": 5,
        "currentQuestionIndex": 0,
        "startedAt": datetime.utcnow(),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    })
    interview_id = str(res_int.inserted_id)

    print(f"[FASTAPI] Candidate User ID: {user_id}")
    print(f"[FASTAPI] Target interview_id: {interview_id}")

    client = TestClient(app)

    webm_content = b"\x1a\x45\xdf\xa3\x99\x42\x86\x81\x01\x42\xf7\x81\x01\x42\xf2\x81\x04\x42\xf3\x81\x08\x42\x82\x84webm\x42\x87\x81\x02\x42\x85\x81\x02"
    webm_file = ("candidate_interview.webm", io.BytesIO(webm_content), "video/webm")

    print("[FASTAPI] Sending POST /api/recordings/upload...")
    response = client.post(
        "/api/recordings/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "interview_id": interview_id,
            "duration": "12.5",
        },
        files={
            "video_file": webm_file
        }
    )

    print(f"[FASTAPI] Status Code: {response.status_code}")
    res_json = response.json()
    print(f"[FASTAPI] Response JSON: {json.dumps(res_json, indent=2)}")

    if response.status_code == 201 and res_json.get("success"):
        rec_data = res_json.get("data", {})
        drive_file_id = rec_data.get("driveFileId") or rec_data.get("drive_file_id")
        rec_id = rec_data.get("id") or rec_data.get("_id")

        print(f"[FASTAPI] Google Drive File ID: {drive_file_id}")
        print(f"[FASTAPI] MongoDB Recording ID: {rec_id}")

        # Step 13: Verify MongoDB document
        mongo_doc = db.video_recordings.find_one({"_id": ObjectId(rec_id)})
        if mongo_doc:
            print("[MONGODB] Metadata verification: PASS")
            print(f"[MONGODB] Document: driveFileId={mongo_doc.get('driveFileId')}, status={mongo_doc.get('status')}, storageProvider={mongo_doc.get('storageProvider')}")
            print("\n✅ FASTAPI RECORDING ENDPOINT & MONGODB INTEGRATION TEST PASSED!")
        else:
            print("[MONGODB] Metadata verification: FAIL — Document not found in DB")
    else:
        print("[FASTAPI] Upload test: FAIL")

if __name__ == "__main__":
    test_recording_endpoint()
