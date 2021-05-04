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
import random
import logging

from aiohttp import web
from datetime import timedelta
from statefun import *
from util import third_party_api_client

logger = logging.getLogger('merchant-scorer')


#####################################################
# `functions` is the `RequestReplyHandler` to which
# all user defined functions are be bound. It
# will proxy all messages between the runtime
# and business logic.
#####################################################
functions = StatefulFunctions()

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
        operation = message.as_string()
        print(f"ctx.caller.id: {ctx.caller.id}; ctx.address.id: {ctx.address.id}", flush=True)
        if operation == 'query':
            logger.debug(f"Retrieving merchant score for transaction: {ctx.caller.id}")
            if not ctx.storage.score:
                logger.debug(f"Score for merchant {ctx.address.id} is not in state, querying external service")
                score = await client(ctx.address.id)
                ctx.storage.score = score

            ctx.send(message_builder(
                target_typename=ctx.caller.typename,
                target_id=ctx.caller.id,
                int_value=ctx.storage.score))

    return call


#####################################################
# Manually register the function with the handler
# supplied with the production API client.
#####################################################
functions.register('com.ververica.fn/merchant',
                   merchant_scorer(),
                   [ValueSpec('score', IntType, expire_after_write=timedelta(hours=1))])


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
    print("Bringing up merchant score service", flush=True)
    web.run_app(app, port=8800)
