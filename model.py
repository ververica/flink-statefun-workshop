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

from aiohttp import web
from statefun import *


#####################################################
# `functions` is the `RequestReplyHandler` to which
# all user defined functions are be bound. It
# will proxy all messages between the runtime
# and business logic.
#####################################################
functions = StatefulFunctions()

FeatureVector = make_json_type('com.ververica.types/feature-vector')


@functions.bind('com.ververica.ds/model')
async def scorer(ctx: Context, message: Message):
    """
    A complex machine learning model that detects fraudulent transactions
    """

    min_score = min(message.as_type(FeatureVector)['count'], 99)
    score = random.randint(a=min_score, b=100)

    print(f"Transaction: {ctx.caller.id} Score: {score}")

    ctx.send(message_builder(
        target_typename=ctx.caller.typename,
        target_id=ctx.caller.id,
        int_value=score))


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
    print("Brining model online")
    web.run_app(app, port=8900)
