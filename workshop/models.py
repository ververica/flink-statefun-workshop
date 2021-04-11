################################################################################
#  Licensed to the Ververica GmbH under one
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

import statefun
import json

#####################################################
# Custom type definitions that convert between
# JSON serialized representation and python
# classes. `simple_type` defines the serializer,
# deserializer, and type name for the corresponding
# python classes.
#####################################################


class Transaction:
    """
    A Transaction event which triggers the pipeline and is tested authenticity.
    """
    TYPE: statefun.Type = statefun.simple_type(
        typename='com.ververica.types/transaction',
        serialize_fn=lambda transaction: json.dumps(transaction.__dict__, default=str).encode(),
        deserialize_fn=lambda data: Transaction(**json.loads(data)))

    def __init__(self, account: str, merchant: str, amount: int, timestamp):
        self.account = account
        self.merchant = merchant
        self.amount = amount
        self.timestamp = timestamp


class FeatureVector:
    """
    A feature vector contains all the requisite data points
    to be sent to the model for scoring.
    """
    TYPE: statefun.Type = statefun.simple_type(
        typename='com.ververica.types/feature-vector',
        serialize_fn=lambda vector: json.dumps(vector.__dict__).encode(),
        deserialize_fn=lambda data: FeatureVector(**json.loads(data)))

    def __init__(self, count: int, score: int, amount: int):
        self.count = count
        self.score = score
        self.amount = amount
