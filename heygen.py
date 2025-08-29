import requests
import json
import time

API_KEY = ""

# Step 1: Generate video
generate_url = "https://api.heygen.com/v2/video/generate"
headers = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "video_inputs": [
        {
            "character": {
                "type": "avatar",
                "avatar_id": "Daisy-inskirt-20220818",
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "input_text": "I love arnab",
                "voice_id": "2d5b0e6cf36f460aa7fc47e3eee4ba54"
            },
            "background": {
                "type": "color",
                "value": "#FFFFFF"
            }
        }
    ],
    "dimension": {
        "width": 1280,
        "height": 720
    }
}

response = requests.post(generate_url, headers=headers, data=json.dumps(payload))
result = response.json()
print("Generate response:", result)

video_id = result.get("data", {}).get("video_id")
if not video_id:
    raise Exception("Failed to get video_id from generate response")

# Step 2: Poll video status
status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

print(f"Checking status for video_id: {video_id}")
while True:
    status_response = requests.get(status_url, headers={"X-Api-Key": API_KEY})
    status_data = status_response.json()
    print("Status response:", status_data)

    status = status_data.get("data", {}).get("status")
    if status == "completed":
        video_url = status_data["data"]["video_url"]
        print("Video ready at:", video_url)
        break
    elif status == "failed":
        raise Exception("Video generation failed!")
    else:
        print("Video still processing... waiting 10s")
        time.sleep(10)

# Step 3: Download video
video_response = requests.get(video_url, stream=True)
with open("first_video.mp4", "wb") as f:
    for chunk in video_response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)

print("✅ Video downloaded as first_video.mp4")
