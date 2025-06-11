import requests

AKEDLY_API_URL = "https://api.akedly.io/api/v1/transactions"
AKEDLY_API_KEY = "4b1f86328e8cf646431f85a8556efe511090d21772dabe693c910b5a488c8113"
AKEDLY_PIPELINE_ID = "6849c2bd476120c9906fd081"

def create_otp_transaction(phone, email):
    payload = {
        "APIKey": AKEDLY_API_KEY,
        "pipelineID": AKEDLY_PIPELINE_ID,
        "verificationAddress": {
            "phoneNumber": phone,
            "email": email,
        }
    }
    response = requests.post(AKEDLY_API_URL, json=payload)
    if response.status_code == 201:
        return response.json()["data"]["transactionID"]
    else:
        raise Exception(f"Akedly OTP error: {response.text}")

def activate_otp_transaction(transactionID):
    res=requests.post(f"{AKEDLY_API_URL}/activate/{transactionID}")
    data = res.json()
    if res.status_code == 201:
        return data["data"]["_id"]
    raise Exception(data.get("message", "Failed to send OTP"))

def verify_otp(request_id, otp):
    res = requests.post(f"{AKEDLY_API_URL}/verify/{request_id}", json={"otp": otp})
    return res.status_code == 200 and res.json()["status"] == "success"