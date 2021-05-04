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

import logging

from workshop.util import third_party_api_client
from workshop.models import *

from aiohttp import web
from statefun import *

THRESHOLD = 1

logger = logging.getLogger('workshop')

#####################################################
# `functions` is the `RequestReplyHandler` to which
# all user defined functions are bound. It
# will proxy all messages between the runtime
# and business logic.
#####################################################
functions = StatefulFunctions()

#####################################################
# Custom type definitions that convert between
# JSON serialized representation and python
# dictionaries. See 'models.py' for an example
# of deserializing into a custom type.
#####################################################

ConfirmFraud = make_json_type('com.ververica.types/confirm-fraud')

#####################################################
# The logical typename of the model as supplied
# by the Data Science team. It accepts a
# FeatureVector and returns an integer score.
#####################################################
ModelType = 'com.ververica.fn/model'


@functions.bind(
    'com.ververica.fn/counter',
    [ValueSpec(name='fraud_count', type=IntType)])
async def fraud_count(ctx: Context, message: Message):
    """
    This function tracks the total number of reported fraudulent transactions made against an account
    on a rolling 30 minute period. It supports three message types:

    1) ConfirmFraud: When a customer reports a fraudulent transaction, the function will
    receive this message. It will increment its internal count and schedule an 'expire' message.

    2) 'expire': After 30 minutes, the function will receive an expiration message. At this time it
    will decrement its internal count.

    3) 'query': The message sent by the transaction manager when requesting the curent count.
    """
    if message.is_type(ConfirmFraud):
        logger.info(f"Confirming fraud for account {ctx.address.id}")
        count = ctx.storage.fraud_count or 0
        ctx.storage.fraud_count = count + 1
        ctx.send_after(timedelta(minutes=30),
                       message_builder(
                           target_typename=ctx.address.typename,
                           target_id=ctx.address.id,
                           str_value='expire'))

    elif message.is_string() and message.as_string() == 'query':
        logger.debug(f"Retrieving fraud count for transaction: {ctx.caller.id}")
        storage = ctx.storage
        ctx.send(message_builder(
            target_typename=ctx.caller.typename,
            target_id=ctx.caller.id,
            int_value=storage.fraud_count or 0))

    elif message.is_string() and message.as_string() == 'expire':
        updated_count = ctx.storage.fraud_count - 1
        if updated_count == 0:
            del ctx.storage.fraud_count
        else:
            ctx.storage.fraud_count = updated_count
    else:
        logger.warning(f"Unknown {message.value_typename()}")


@functions.bind(
    'com.ververica.fn/transaction-manager',
    [ValueSpec('transaction', Transaction.TYPE),
     ValueSpec('fraud_count', IntType),
     ValueSpec('merchant_score', IntType)])
async def transaction_manager(ctx: Context, message: Message):
    """
    The transaction manager coordinates the processes of building
    feature vectors and scoring them based on incoming transactions.

    Each time a transaction is received, it is stored in state
    and the various feature functions are queried for their
    relevant data points. Once all functions have replied, the
    completed feature vector is sent to the model for scoring.

    If the final score is greater than the specified fraud
    threshold, the transaction is sent to the alerts Kafka
    topic.
    """
    if message.is_type(Transaction.TYPE):
        logger.info(f"Processing transaction: {ctx.address.id}")
        transaction = message.as_type(Transaction.TYPE)
        ctx.storage.transaction = transaction

        ctx.send(message_builder(
            target_typename='com.ververica.fn/counter',
            target_id=transaction.account,
            str_value='query'))

        ctx.send(message_builder(
            target_typename='com.ververica.fn/merchant',
            target_id=transaction.merchant,
            str_value='query'))

    elif ctx.caller.typename == 'com.ververica.fn/counter':
        if ctx.storage.merchant_score is None:
            # The merchant score has not yet been received.
            # Store the count in state for latter.
            logger.debug(f"Waiting on merchant score for transaction: {ctx.address.id}")
            ctx.storage.fraud_count = message.as_int()
        else:
            # All features are available. Send the
            # feature vector to the model.
            logger.debug(f"Sending feature vector for transaction: {ctx.address.id} to model")
            ctx.send(message_builder(
                target_typename=ModelType,
                target_id=ctx.storage.transaction.account,
                value=FeatureVector(
                    message.as_int(),
                    ctx.storage.merchant_score,
                    ctx.storage.transaction.amount),
                value_type=FeatureVector.TYPE))

    elif ctx.caller.typename == 'com.ververica.fn/merchant':
        if ctx.storage.fraud_count is None:
            logger.debug(f"Waiting on fraud count for transaction: {ctx.address.id}")
            # The fraud count has not yet been received.
            # Store the score in state for latter.
            ctx.storage.merchant_score = message.as_int()
        else:
            # All features are available. Send the
            # feature vector to the model.
            logger.debug(f"Sending feature vector for transaction: {ctx.address.id} to model")
            ctx.send(message_builder(
                target_typename=ModelType,
                target_id=ctx.storage.transaction.account,
                value=FeatureVector(
                    ctx.storage.fraud_count,
                    message.as_int(),
                    ctx.storage.transaction.amount),
                value_type=FeatureVector.TYPE))

    elif ctx.caller.typename == ModelType:
        # Check the result of the model
        # if it is above a threshold then
        # send the transaction to the alerts
        # Kafka topic
        logger.debug(f"Received score {message.as_int()} for transaction {ctx.address.id}")
        if message.as_int() > THRESHOLD:
            logger.info(f"Score for transaction {ctx.address.id} is above threshold, sending alert")
            ctx.send_egress(kafka_egress_message(
                typename='com.ververica.egress/alerts',
                topic='alerts',
                key=ctx.storage.transaction.account,
                value=ctx.storage.transaction,
                value_type=Transaction.TYPE))

        del ctx.storage.transaction
        del ctx.storage.fraud_count
        del ctx.storage.merchant_score


####################
# Serve the endpoint
####################

handler = RequestReplyHandler(functions)


async def handle(request):
    req = await request.read()
    res = await handler.handle_async(req)
    return web.Response(body=res, content_type='application/octet-stream')


app = web.Application()
app.add_routes([web.post('/statefun', handle)])

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s')
    logger.setLevel(logging.DEBUG)
    web.run_app(app, port=8100)
