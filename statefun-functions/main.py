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
from datetime import timedelta

from statefun import StatefulFunctions
from statefun import RequestReplyHandler
from statefun import kafka_egress_record

from typing import Union

from entities_pb2 import ConfirmFraud, QueryFraud, ReportedFraud, ExpireFraud
from entities_pb2 import QueryMerchantScore, MerchantScore, ExpireMerchantScore

from entities_pb2 import FraudScore, FeatureVector
from entities_pb2 import Transaction

from workshop_util import internal_query_service

import random

functions = StatefulFunctions()

# The threshold over which we consider fraud
THRESHOLD = 1


@functions.bind("ververica/counter")
def fraud_count(context, message: Union[ConfirmFraud, QueryFraud, ExpireFraud]):
    """
    This function tracks the total number of reported fraudulent transactions made against an account
    on a rolling 30 day period. It supports three message types:

    1) ConfirmFraud: When a customer reports a fraudulent transaction, the function will
    receive this message. It will increment its internal count and set a 30 day expiration timer.

    2) ExpireFraud: After 30 days, the function will receive an expiration message. At this time it
    will decrement its internal count.

    3) QueryFraud: After 30 days, the function will receive an expiration message. At this tme
    it will decrement its internal count by 1.
    """

    if isinstance(message, ConfirmFraud):
        count = context.state("fraud_count").unpack(ReportedFraud)
        if not count:
            count = ReportedFraud()
            count.count = 1
        else:
            count.count += 1

        context.state("fraud_count").pack(count)

    elif isinstance(message, QueryFraud):
        count = context.state("fraud_count").unpack(ReportedFraud)

        if not count:
            count = ReportedFraud()

        context.pack_and_reply(count)

    elif isinstance(message, ExpireFraud):
        raise ValueError("Expire Fraud has not yet been implemented!")


@functions.bind("ververica/merchant")
def merchant_score(context, message: Union[QueryMerchantScore, ExpireMerchantScore]):
    """
    Our application relies on a 3rd party service that returns a trustworthiness score
    for each merchant. This function, when it receives a QueryMerchantScore message will
    query the external service and return a MerchantScore to the caller function. The score
    is stored in local state for 1 hour to avoid excess network calls.
    """

    if isinstance(message, QueryMerchantScore):
        m_score = context.state("merchant_score").unpack(MerchantScore)

        if not m_score:
            m_score = internal_query_service()

        context.pack_and_reply(m_score)
        context.pack_and_send_after(
            timedelta(hours=1),
            context.address.typename(),
            context.address.identity,
            ExpireMerchantScore())

    elif isinstance(message, ExpireMerchantScore):
        del context["merchant_score"]


@functions.bind("ververica/model")
def score(context, message: FeatureVector):
    """
    A complex machine learning model that detects fraudulent transactions
    """

    min_score = min(message.fraud_count, 99)

    result = FraudScore()
    result.score = random.randint(a=min_score, b=100)
    context.pack_and_reply(result)


@functions.bind("ververica/transaction-manager")
def transaction_manager(context, message: Union[Transaction, ReportedFraud, MerchantScore, FraudScore]):
    """
    The transaction manager coordinates all communication between the various functions.
    This includes building up the feature vector, calling into the model, and reporting
    results to the user.
    """

    if isinstance(message, Transaction):
        context.state("transaction").pack(message)

        context.pack_and_send(
            "ververica/counter",
            message.account,
            QueryFraud())

        context.pack_and_send(
            "ververica/merchant",
            message.merchant,
            QueryMerchantScore())

    elif isinstance(message, ReportedFraud):
        m_score = context.state("merchant_score").unpack(MerchantScore)
        if not m_score:
            context.state("fraud_count").pack(message)
        else:
            transaction = context.state("transaction").unpack(Transaction)

            vector = FeatureVector()
            vector.fraud_count = message.count
            vector.merchant_score = m_score.score
            vector.amount = transaction.amount

            context.pack_and_send(
                "ververica/model",
                transaction.account,
                vector)

    elif isinstance(message, MerchantScore):
        count = context.state("fraud_count").unpack(ReportedFraud)
        if not count:
            context.state("merchant_score").pack(message)
        else:
            transaction = context.state("transaction").unpack(Transaction)

            vector = FeatureVector()
            vector.fraud_count = count.count
            vector.merchant_score = message.score
            vector.amount = transaction.amount

            context.pack_and_send(
                "ververica/model",
                transaction.account,
                vector)

    elif isinstance(message, FraudScore):
        if message.score > THRESHOLD:
            transaction = context.state("transaction").unpack(Transaction)
            egress_message = kafka_egress_record(topic="alerts", key=transaction.account, value=transaction)
            context.pack_and_send_egress("ververica/kafka-egress", egress_message)

        del context["transaction"]
        del context["fraud_count"]
        del context["merchant_score"]


#
# Serve the endpoint
#

handler = RequestReplyHandler(functions)

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
