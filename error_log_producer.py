from kafka import KafkaProducer
import time

log_file = "excel_to_sqlite.log"   # change path if needed
producer = KafkaProducer(bootstrap_servers="localhost:9092")

with open(log_file, "r") as f:
    # go to end of file
    f.seek(0, 2)

    while True:
        line = f.readline()
        if not line:
            time.sleep(1)
            continue
        if "ERROR" in line:
            producer.send("error-logs", value=line.strip().encode("utf-8"))
            print(f"Sent: {line.strip()}")
