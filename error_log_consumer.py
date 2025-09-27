from kafka import KafkaConsumer
import os
import requests
import subprocess
import openai

# Replace 'log-topic' with your topic name
topic_name = "error-logs"

# GitHub authentication (set your token as an environment variable)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "mukulkkumar/Kafka-AI-Log-Agent"
BRANCH_PREFIX = "auto-fix-"

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

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def apply_fix(error_message):
    print("Applying fix for:", error_message)
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    prompt = f"""You are an expert Python developer. The following code has a bug as described in the error message below.
    Error message:
    {error_message}

    Code:
    {code}

    Please provide the corrected code only, with the bug fixed. Do not add explanations or code fences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    fixed_code = response.choices[0].message.content

    # Remove code fences if present
    if fixed_code.startswith("```"):
        fixed_code = fixed_code.strip("` \n")
        # Remove possible language specifier
        fixed_code = "\n".join(line for line in fixed_code.splitlines() if not line.strip().startswith("python"))

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(fixed_code)
    print("Code fixed using OpenAI and overwritten in app.py")
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
    branch_name = BRANCH_PREFIX + str(hash(error_message))
    if apply_fix(error_message):
        print("fix applied")
        create_branch(branch_name)
        commit_and_push(branch_name)
        create_pr(branch_name)
