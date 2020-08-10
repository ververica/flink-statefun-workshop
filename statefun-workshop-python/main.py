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

from google.protobuf.any_pb2 import Any

from statefun import StatefulFunctions
from statefun import RequestReplyHandler

from entities_pb2 import FraudScore
from entities_pb2 import FeatureVector

import random

functions = StatefulFunctions()

@functions.bind("ververica/model")
def score(context, message: FeatureVector):
    """
    A complex machine learning model that detects fraudulent transactions
    """

    min_score = min(message.fraud_count, 99)

    result = FraudScore()

    result.score = random.randint(a=min_score, b=100)

    envelope = Any()
    envelope.Pack(result)
    context.reply(envelope)

handler = RequestReplyHandler(functions)

#
# Serve the endpoint
#

from flask import request
from flask import make_response
from flask import Flask

app = Flask(__name__)

@app.route('/statefun', methods=['POST'])
def handle():
    response_data = handler(request.data)
    response = make_response(response_data)
    response.headers.set('Content-Type', 'application/octet-stream')
    return response

if __name__ == "__main__":
    app.run()
