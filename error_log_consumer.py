from kafka import KafkaConsumer
import os
import requests
import subprocess

# Replace 'log-topic' with your topic name
topic_name = "error-logs"

# GitHub authentication (set your token as an environment variable)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "mukulkkumar/Kafka-AI-Log-Agent"
BRANCH_NAME = "auto-fix"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Create consumer
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=["localhost:9092"],  # Kafka broker
    auto_offset_reset="earliest",          # Read from beginning if no offset
    enable_auto_commit=True,
    group_id="error-log-consumer-group"           # Consumer group
)

print(f"Listening to topic: {topic_name} ...")

def apply_fix(error_message):
    print("Applying fix for:", error_message)
    # Add a comment line to app.py
    with open("app.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Insert comment at the top
    lines.insert(0, "# This is an auto-fix comment added by apply_fix\n")
    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Added auto-fix comment to app.py")
    return True

def create_branch(branch_name):
    subprocess.run(["git", "checkout", "-b", branch_name])

def commit_and_push(branch_name):
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Auto-fix: error detected and fixed"])
    subprocess.run(["git", "push", "origin", branch_name])

def create_pr(branch_name):
    url = f"https://api.github.com/repos/{REPO}/pulls"
    data = {
        "title": "Auto-fix: error detected and fixed",
        "head": branch_name,
        "base": "main",
        "body": "This PR was created automatically after error detection."
    }
    response = requests.post(url, headers=headers, json=data)
    print("PR created:", response.json().get("html_url"))

# Poll messages
for message in consumer:
    error_message = message.value.decode('utf-8')
    print(f"Received: {error_message}")
    # branch_name = BRANCH_PREFIX + str(hash(error_message))
    if apply_fix(error_message):
        create_branch(BRANCH_NAME)
        commit_and_push(BRANCH_NAME)
        create_pr(BRANCH_NAME)
