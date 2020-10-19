################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import signal
import sys
import time
import threading

import random
import uuid

from kafka.errors import NoBrokersAvailable

from entities_pb2 import Transaction, ConfirmFraud, CustomThreshold

from kafka import KafkaProducer
from kafka import KafkaConsumer

KAFKA_BROKER = "kafka-broker:9092"
PREFIXES = [
    "active", "arc", "auto", "app", "avi", "base", "co", "con", "core", "clear", "en", "echo",
    "even", "ever", "fair", "go", "high", "hyper", "in", "inter", "iso", "jump", "live", "make",
    "mass", "meta", "matter", "omni", "on", "one", "open", "over", "out", "re", "real", "peak",
    "pure", "shift", "silver", "solid", "spark", "start", "true", "up", "vibe"
]

WORD_SUFFIXES = [
    "arc", "atlas", "base", "bay", "boost", "capsule", "case", "center", "cast", "click", "dash",
    "deck", "dock", "dot", "drop", "engine", "flow", "glow", "grid", "gram", "graph", "hub",
    "focus", "kit", "lab", "level", "layer", "light", "line", "logic", "load", "loop", "ment",
    "method", "mode", "mark", "ness", "now", "pass", "port", "post", "press", "prime", "push",
    "rise", "scape", "scale", "scan", "scout", "sense", "set", "shift", "ship", "side", "signal",
    "snap", "scope", "space", "span", "spark", "spot", "start", "storm", "stripe", "sync", "tap",
    "tilt", "ture", "type", "view", "verge", "vibe", "ware", "yard", "up"
]


def random_transaction():
    """Generate infinite sequence of random Transactions."""
    while True:
        transaction = Transaction()
        transaction.account = "0x%08X" % random.randint(0x100000, 0x1000000)
        transaction.merchant = random.choice(PREFIXES).capitalize() + random.choice(WORD_SUFFIXES)
        transaction.amount = random.randint(1, 1000)
        transaction.timestamp.seconds = int(time.time())

        yield transaction


def produce():
    if len(sys.argv) == 2:
        delay_seconds = int(sys.argv[1])
    else:
        delay_seconds = 1
    producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])
    for transaction in random_transaction():
        key = uuid.uuid4().hex.encode('utf-8')
        val = transaction.SerializeToString()
        producer.send(topic='transactions', key=key, value=val)
        producer.flush()
        time.sleep(delay_seconds)


def random_confirmed_fraud():
    """Generate infinite sequence of random fraud confirmations."""
    while True:
        confirm_fraud = ConfirmFraud()
        confirm_fraud.account = "0x%08X" % random.randint(0x100000, 0x1000000)

        yield confirm_fraud


def produce_confirmed():
    if len(sys.argv) == 2:
        delay_seconds = int(sys.argv[1]) * 10
    else:
        delay_seconds = 10
    producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])
    for confirmed in random_confirmed_fraud():
        key = confirmed.account.encode('utf-8')
        val = confirmed.SerializeToString()
        producer.send(topic='confirmed', key=key, value=val)
        producer.flush()
        time.sleep(delay_seconds)


def random_threshold():
    """Generate infinite sequence of custom thresholds."""
    while True:
        threshold = CustomThreshold()
        threshold.account = "0x%08X" % random.randint(0x100000, 0x1000000)
        threshold.threshold = random.randint(1, 100)

        yield threshold


def produce_threshold():
    if len(sys.argv) == 2:
        delay_seconds = int(sys.argv[1]) * 10
    else:
        delay_seconds = 10
    producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])
    for threshold in random_confirmed_fraud():
        key = threshold.account.encode('utf-8')
        val = threshold.SerializeToString()
        producer.send(topic='thresholds', key=key, value=val)
        producer.flush()
        time.sleep(delay_seconds)


def consume():
    consumer = KafkaConsumer(
        'alerts',
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        group_id='group-id')
    for message in consumer:
        value = Transaction()
        try:
            value.ParseFromString(message.value)
            print(f"Suspected Fraud for account id {value.account} at {value.merchant} for {value.amount:d} USD", flush=True)
        except Exception:
            continue


def handler(number, frame):
    sys.exit(0)


def safe_loop(fn):
    while True:
        try:
            fn()
        except SystemExit:
            print("Good bye!")
            return
        except NoBrokersAvailable:
            time.sleep(2)
            continue
        except Exception as e:
            print(e, flush=True)
            return


def main():
    signal.signal(signal.SIGTERM, handler)

    producer = threading.Thread(target=safe_loop, args=[produce])
    producer.start()

    confirmed = threading.Thread(target=safe_loop, args=[produce_confirmed])
    confirmed.start()

    threshold = threading.Thread(target=safe_loop, args=[produce_threshold])
    threshold.start()

    consumer = threading.Thread(target=safe_loop, args=[consume])
    consumer.start()

    producer.join()
    confirmed.join()
    threshold.join()
    consumer.join()


if __name__ == "__main__":
    main()
