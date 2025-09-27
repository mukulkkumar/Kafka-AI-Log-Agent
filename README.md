# Apache Kafka (KRaft Mode) Setup Guide

This guide explains how to set up and run Apache Kafka in **KRaft mode** (without ZooKeeper).

---

## 🚀 Prerequisites
- Java 11 or higher installed (`java -version`)
- Kafka downloaded and extracted (e.g., `~/kafka`)

Download latest Kafka:  
👉 [https://kafka.apache.org/downloads](https://kafka.apache.org/downloads)

---

## ⚙️ Configuration

Edit `config/kraft/server.properties` and ensure the following settings exist:

```properties
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@localhost:9093
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
log.dirs=/tmp/kraft-combined-logs
```

## Setup Steps

### 1. Navigate to Kafka directory
```
cd ~/kafka
```

### 2. Clean old logs (if any)
```
rm -rf /tmp/kraft-combined-logs/*
```

### 3. Generate a Cluster ID
```
CLUSTER_ID=$(bin/kafka-storage.sh random-uuid)
echo "Generated Cluster ID: $CLUSTER_ID"
```

### 4. Format the storage
```
bin/kafka-storage.sh format \
  --config config/kraft/server.properties \
  --cluster-id $CLUSTER_ID
```

### 5. Start Kafka broker
```
bin/kafka-server-start.sh config/kraft/server.properties
```
(Optional: run in background)
```
nohup bin/kafka-server-start.sh config/kraft/server.properties > kafka.log 2>&1 &
```

## Verification

### Create a topic

```
bin/kafka-topics.sh --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 --replication-factor 1
```

### List topics
```
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Produce messages
```
bin/kafka-console-producer.sh --topic test-topic --bootstrap-server localhost:9092
```

### Consume messages
```
bin/kafka-console-consumer.sh --topic test-topic --bootstrap-server localhost:9092 --from-beginning
```

---

## 🛠️ Auto-Fixing Code with AI

This project supports **automatic code fixing** using AI (OpenAI GPT-4) in response to error logs detected by the Kafka consumer. When an error block is received:

- The error message and relevant code are sent to the OpenAI API for analysis and correction.
- The AI returns the fixed code, which is then automatically written back to the affected file (e.g., `app.py`).
- No code fences or extra formatting are included—only the corrected code is saved.
- This enables self-healing code workflows, reducing manual intervention for common errors.

**Requirements:**
- Set your OpenAI API key in the environment variable `OPENAI_API_KEY`.
- Install Python package (`pip install -r requirements.txt`).

**Example Workflow:**
1. Error is detected and sent to the consumer via Kafka.
2. The consumer's `apply_fix` function uses OpenAI to generate a fix.
3. The code is updated in place, and optionally a pull request can be created for review.

---

