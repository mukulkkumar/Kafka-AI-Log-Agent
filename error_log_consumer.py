from kafka import KafkaConsumer

# Replace 'log-topic' with your topic name
topic_name = "error-logs"

# Create consumer
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=["localhost:9092"],  # Kafka broker
    auto_offset_reset="earliest",          # Read from beginning if no offset
    enable_auto_commit=True,
    group_id="error-log-consumer-group"           # Consumer group
)

print(f"Listening to topic: {topic_name} ...")

# Poll messages
for message in consumer:
    print(f"Received: {message.value.decode('utf-8')}")
