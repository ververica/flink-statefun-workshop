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
ModelType = 'com.ververica.ds/model'


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
    raise ValueError('Implement Me')


def merchant_scorer(client=third_party_api_client):
    """
    This function queries a 3rd party API to retrieve a trustworthiness
    score for the merchant. The score will be stored in state, as a sort of
    cache, to reduce expensive API calls. The state is set to expire 1 hour
    after write to prevent the use of stale data.

    Unlike other stateful functions, this returns a function that is manually
    registered with the RequestReply handler. Doing so allows supporting dependency
    injection of the API client.
    """
    async def call(ctx: Context, message: Message):
        raise ValueError('Implement Me')

    return call


#####################################################
# Manually register the function with the handler
# supplied with the production API client.
#####################################################
functions.register('com.ververica.fn/merchant',
                   merchant_scorer(),
                   [ValueSpec('score', IntType, expire_after_write=timedelta(hours=1))])


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
        raise ValueError('Implement Me')

    elif ctx.caller.typename == 'com.ververica.fn/counter':
        raise ValueError('Implement Me')

    elif ctx.caller.typename == 'com.ververica.fn/merchant':
        raise ValueError('Implement Me')

    elif ctx.caller.typename == ModelType:
        raise ValueError('Implement Me')


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
