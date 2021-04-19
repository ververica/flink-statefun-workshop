################################################################################
# Licensed to Ververica GmbH under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import signal
import sys
import time
import threading
import datetime
import random
import uuid
import json

from kafka.errors import NoBrokersAvailable

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
        yield {
            'account': "0x%08X" % random.randint(0x100000, 0x1000000),
            'merchant': random.choice(PREFIXES).capitalize() + random.choice(WORD_SUFFIXES),
            'amount': random.randint(1, 1000),
            'timestamp': datetime.datetime.now().isoformat()
        }


def random_confirmed_fraud():
    """Generate infinite sequence of random fraud confirmations."""
    while True:
        yield {
            'account': "0x%08X" % random.randint(0x100000, 0x1000000)
        }


def random_threshold():
    """Generate infinite sequence of custom thresholds."""
    while True:
        yield {
            'account': "0x%08X" % random.randint(0x100000, 0x1000000),
            'threshold': random.randint(1, 100)
        }


def produce(topic: str, generator, key_selector, delay: int = 1):
    if len(sys.argv) == 2:
        delay_seconds = int(sys.argv[1]) * delay
    else:
        delay_seconds = 1

    producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])
    for record in generator():
        key = key_selector(record)
        val = json.dumps(record, ensure_ascii=False).encode('utf-8')

        producer.send(topic=topic, key=key, value=val)
        producer.flush()
        time.sleep(delay_seconds)


def consume():
    consumer = KafkaConsumer(
        'alerts',
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        group_id='group-id')
    for message in consumer:
        value = json.loads(message.value)
        print(f"Suspected Fraud for account id {value['account']} at {value['merchant']} for {value['amount']} USD",
              flush=True)


def handler(_number, _frame):
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

    transactions = threading.Thread(target=safe_loop, args=[
        lambda: produce('transactions', random_transaction, lambda _: uuid.uuid4().hex.encode('utf-8'))
    ])
    transactions.start()

    confirmed = threading.Thread(target=safe_loop, args=[
        lambda: produce('confirmed', random_confirmed_fraud, lambda c: c['account'].encode('utf-8'), 10)
    ])
    confirmed.start()

    threshold = threading.Thread(target=safe_loop, args=[
        lambda: produce('thresholds', random_threshold, lambda t: t['account'].encode('utf-8'), 10)
    ])
    threshold.start()

    consumer = threading.Thread(target=safe_loop, args=[consume])
    consumer.start()

    transactions.join()
    confirmed.join()
    threshold.join()
    consumer.join()


if __name__ == "__main__":
    main()
