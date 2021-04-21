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
import unittest
from workshop.__main__ import functions, ConfirmFraud
from workshop.tests.test_utils import *


class FraudCountTestCases(unittest.TestCase):
    """
    Unit tests for the fraud_count StatefulFunction
    """
    def test_confirm_fraud(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'counter', 'abc')\
            .with_invocation({'account': 'abc'}, ConfirmFraud, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        mutation = json_at(result, NTH_STATE_MUTATION(0))
        self.assertEqual(mutation['mutation_type'], 'MODIFY', 'Failed to modify function state')
        self.assertEqual(mutation['state_name'], 'fraud_count', 'Modified incorrect state value')
        self.assertEqual(mutation['state_value'], as_typed_value(IntType, 1), 'fraud_count should be set')

    def test_expiration_sent(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'counter', 'abc')\
            .with_invocation({'account': 'abc'}, ConfirmFraud, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        delayed = json_at(result, NTH_DELAYED_MESSAGE(0))
        self.assertEqual(delayed['delay_in_ms'], '1800000', 'Wrong delay for expiration')
        self.assertEqual(delayed['target'],
                         {'namespace': 'com.ververica.fn', 'type': 'counter', 'id': 'abc'},
                         'Sending expiration to wrong function')
        self.assertEqual(delayed['argument'], as_typed_value(StringType, 'expire'), 'Sending wrong value for expire')

    def test_query_fraud(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'counter', 'abc')\
            .with_state('fraud_count', 1, IntType)\
            .with_invocation('query', StringType, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        response = json_at(result, NTH_OUTGOING_MESSAGE(0))
        self.assertEqual(response['target'],
                         {'namespace': 'com.ververica.fn', 'type': 'transaction-manager', 'id': '0'},
                         'Sending response to wrong function')
        self.assertEqual(response['argument'], as_typed_value(IntType, 1), 'Sending wrong value to manager')

    def test_expire_fraud(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'counter', 'abc')\
            .with_state('fraud_count', 2, IntType)\
            .with_invocation('expire', StringType, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        mutation = json_at(result, NTH_STATE_MUTATION(0))
        self.assertEqual(mutation['state_name'], 'fraud_count', 'Modified incorrect state value')
        self.assertEqual(mutation['mutation_type'], 'MODIFY', 'Failed to modify function state')
        self.assertEqual(mutation['state_value'], as_typed_value(IntType, 1), 'fraud_count should be set')

        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'counter', 'abc')\
            .with_state('fraud_count', 1, IntType)\
            .with_invocation('expire', StringType, ('com.ververica.fn', 'transaction-manager', '0'))

        result = round_trip(functions, invocation)

        mutation = json_at(result, NTH_STATE_MUTATION(0))
        self.assertEqual(mutation['state_name'], 'fraud_count', 'Modified incorrect state value')
        self.assertFalse('mutation_type' in mutation, 'Failed to delete function state')