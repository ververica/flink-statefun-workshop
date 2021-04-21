################################################################################
#  Licensed to the Ververica GmbH under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  'License'); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an 'AS IS' BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################
from statefun import *
from datetime import timedelta
import unittest
from workshop.__main__ import merchant_scorer
from workshop.tests.test_utils import *


async def mock_query_service(_: str) -> int:
    return 1


async def failing_query_service(_: str) -> int:
    raise ValueError('This function should never be called')


class MerchantScoreTestCases(unittest.TestCase):
    """
    Unit tests for the merchant_scorer StatefulFunction
    """
    def test_query_service(self):

        functions = StatefulFunctions()
        functions.register(
            'com.ververica.fn/merchant',
            merchant_scorer(client=mock_query_service),
            [ValueSpec('score', IntType, expire_after_write=timedelta(hours=1))])

        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'merchant', 'abc')\
            .with_invocation('query', StringType, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        response = json_at(result, NTH_OUTGOING_MESSAGE(0))
        self.assertEqual(response['target'],
                         {'namespace': 'com.ververica.fn', 'type': 'transaction-manager', 'id': '0'},
                         'Sending response to wrong function')
        self.assertEqual(response['argument'], as_typed_value(IntType, 1), 'Sending wrong value to manager')

    def test_query_service_cache(self):

        functions = StatefulFunctions()
        functions.register(
            'com.ververica.fn/merchant',
            merchant_scorer(client=failing_query_service),
            [ValueSpec('score', IntType, expire_after_write=timedelta(hours=1))])

        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'merchant', 'abc')\
            .with_state('score', 1, IntType)\
            .with_invocation('query', StringType, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        response = json_at(result, NTH_OUTGOING_MESSAGE(0))
        self.assertEqual(response['target'],
                         {'namespace': 'com.ververica.fn', 'type': 'transaction-manager', 'id': '0'},
                         'Sending response to wrong function')
        self.assertEqual(response['argument'], as_typed_value(IntType, 1), 'Sending wrong value to manager')

