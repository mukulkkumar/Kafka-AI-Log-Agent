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

