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
from workshop.__main__ import functions
from workshop.models import *
from workshop.tests.test_utils import *

transaction = Transaction('abc', 'foo', 10, '2021-01-01')


class TransactionManagerTestCases(unittest.TestCase):
    """
    Unit tests for the transaction manager StatefulFunction
    """
    def test_initial_transaction(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'transaction-manager', '0x123')\
            .with_invocation(transaction, Transaction.TYPE)

        result = round_trip(functions, invocation)

        mutation = json_at(result, NTH_STATE_MUTATION(0))
        self.assertEqual(mutation['mutation_type'], 'MODIFY', 'Failed to modify function state')
        self.assertEqual(mutation['state_name'], 'transaction', 'Modified incorrect state value')
        self.assertEqual(mutation['state_value'],
                         as_typed_value(Transaction.TYPE, transaction),
                         'transaction should be set')

        outgoing = json_at(result, NTH_OUTGOING_MESSAGE(0))
        self.assertEqual(outgoing['target'],
                         {'namespace': 'com.ververica.fn', 'type': 'counter', 'id': 'abc'},
                         'Sending query to wrong function')

        self.assertEqual(outgoing['argument'], as_typed_value(StringType, 'query'), 'Sending wrong value to counter')

        outgoing = json_at(result, NTH_OUTGOING_MESSAGE(1))
        self.assertEqual(outgoing['target'],
                         {'namespace': 'com.ververica.fn', 'type': 'merchant', 'id': 'foo'},
                         'Sending query to wrong function')

        self.assertEqual(outgoing['argument'], as_typed_value(StringType, 'query'), 'Sending wrong value to counter')

    def test_counter_responds_first(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'transaction-manager', '0x123')\
            .with_state('transaction', transaction, Transaction.TYPE)\
            .with_invocation(1, IntType, ('com.ververica.fn', 'counter', 'abc'))

        result = round_trip(functions, invocation)

        mutation = json_at(result, NTH_STATE_MUTATION(0))
        self.assertEqual(mutation['mutation_type'], 'MODIFY', 'Failed to modify function state')
        self.assertEqual(mutation['state_name'], 'fraud_count', 'Modified incorrect state value')
        self.assertEqual(mutation['state_value'],
                         as_typed_value(IntType, 1),
                         'fraud_count should be set')

    def test_counter_responds_second(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'transaction-manager', '0x123')\
            .with_state('transaction', transaction, Transaction.TYPE)\
            .with_state('merchant_score', 1, IntType)\
            .with_invocation(1, IntType, ('com.ververica.fn', 'counter', 'abc'))

        result = round_trip(functions, invocation)

        outgoing = json_at(result, NTH_OUTGOING_MESSAGE(0))
        self.assertEqual(outgoing['target'],
                         {'namespace': 'com.ververica.ds', 'type': 'model', 'id': 'abc'},
                         'Sending query to wrong function')

        self.assertEqual(outgoing['argument'],
                         as_typed_value(FeatureVector.TYPE, FeatureVector(1, 1, 10)),
                         'Sending wrong value to model')

    def test_merchant_responds_first(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'transaction-manager', '0x123')\
            .with_state('transaction', transaction, Transaction.TYPE)\
            .with_invocation(1, IntType, ('com.ververica.fn', 'merchant', 'foo'))

        result = round_trip(functions, invocation)

        mutation = json_at(result, NTH_STATE_MUTATION(0))
        self.assertEqual(mutation['mutation_type'], 'MODIFY', 'Failed to modify function state')
        self.assertEqual(mutation['state_name'], 'merchant_score', 'Modified incorrect state value')
        self.assertEqual(mutation['state_value'],
                         as_typed_value(IntType, 1),
                         'merchant_score should be set')

    def test_merchant_responds_second(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'transaction-manager', '0x123')\
            .with_state('transaction', transaction, Transaction.TYPE)\
            .with_state('fraud_count', 1, IntType)\
            .with_invocation(1, IntType, ('com.ververica.fn', 'merchant', 'foo'))

        result = round_trip(functions, invocation)

        outgoing = json_at(result, NTH_OUTGOING_MESSAGE(0))
        self.assertEqual(outgoing['target'],
                         {'namespace': 'com.ververica.ds', 'type': 'model', 'id': 'abc'},
                         'Sending query to wrong function')

        self.assertEqual(outgoing['argument'],
                         as_typed_value(FeatureVector.TYPE, FeatureVector(1, 1, 10)),
                         'Sending wrong value to model')

    def test_score_above_threshold(self):
        invocation = InvocationBuilder()\
            .with_target('com.ververica.fn', 'transaction-manager', '0x123')\
            .with_state('transaction', transaction, Transaction.TYPE)\
            .with_state('fraud_count', 1, IntType)\
            .with_state('merchant_score', 1, IntType)\
            .with_invocation(100, IntType, ('com.ververica.ds', 'model', 'abc'))

        result = round_trip(functions, invocation)

        outgoing = json_at(result, NTH_EGRESS(0))
        self.assertEqual(outgoing['egress_namespace'], 'com.ververica.egress')
        self.assertEqual(outgoing['egress_type'], 'alerts')

        mutation_0 = json_at(result, NTH_STATE_MUTATION(0))
        self.assertTrue(
            'mutation_type' not in mutation_0,
            'Failed to delete {} state'.format(mutation_0['state_name']))

        mutation_1 = json_at(result, NTH_STATE_MUTATION(1))
        self.assertTrue(
            'mutation_type' not in mutation_1,
            'Failed to delete {} state'.format(mutation_1['state_name']))

        mutation_2 = json_at(result, NTH_STATE_MUTATION(2))
        self.assertTrue(
            'mutation_type' not in mutation_2,
            'Failed to delete {} state'.format(mutation_2['state_name']))