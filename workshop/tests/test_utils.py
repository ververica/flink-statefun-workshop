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
from google.protobuf.json_format import MessageToDict

from statefun import RequestReplyHandler, StatefulFunctions, Type
from statefun.request_reply_pb2 import ToFunction, FromFunction
from statefun.utils import to_typed_value


class InvocationBuilder(object):
    """Utility class to test Stateful Functions"""

    def __init__(self):
        self.to_function = ToFunction()

    def with_target(self, ns, type, id):
        InvocationBuilder.set_address(ns, type, id, self.to_function.invocation.target)
        return self

    def with_state(self, name, value=None, type=None):
        state = self.to_function.invocation.state.add()
        state.state_name = name
        if value is not None:
            state.state_value.CopyFrom(to_typed_value(type, value))
        return self

    def with_invocation(self, arg, tpe, caller=None):
        invocation = self.to_function.invocation.invocations.add()
        if caller:
            (ns, type, id) = caller
            InvocationBuilder.set_address(ns, type, id, invocation.caller)
        invocation.argument.CopyFrom(to_typed_value(tpe, arg))
        return self

    def serialize_to_string(self):
        return self.to_function.SerializeToString()

    @staticmethod
    def set_address(namespace, type, id, address):
        address.namespace = namespace
        address.type = type
        address.id = id


def round_trip(functions: StatefulFunctions, to: InvocationBuilder) -> dict:
    handler = RequestReplyHandler(functions)

    in_bytes = to.serialize_to_string()
    out_bytes = handler.handle_sync(in_bytes)
    f = FromFunction()
    f.ParseFromString(out_bytes)
    response = MessageToDict(f, preserving_proto_field_name=True)

    if 'incomplete_invocation_context' in response:
        # register missing state values and retrigger execution
        # this can only recurse once
        missing_values = response['incomplete_invocation_context']['missing_values']
        for value in missing_values:
            to.with_state(value['state_name'])

        return round_trip(functions, to)
    else:
        return response


def as_typed_value(type: Type, value=None) -> dict:
    return MessageToDict(to_typed_value(type, value), preserving_proto_field_name=True)


def json_at(nested_structure: dict, path):
    try:
        for next in path:
            nested_structure = next(nested_structure)
        return nested_structure
    except KeyError:
        return None


def key(s: str):
    return lambda dict: dict[s]


def nth(n):
    return lambda list: list[n]


NTH_OUTGOING_MESSAGE = lambda n: [key('invocation_result'), key('outgoing_messages'), nth(n)]
NTH_STATE_MUTATION = lambda n: [key('invocation_result'), key('state_mutations'), nth(n)]
NTH_DELAYED_MESSAGE = lambda n: [key('invocation_result'), key('delayed_invocations'), nth(n)]
NTH_EGRESS = lambda n: [key('invocation_result'), key('outgoing_egresses'), nth(n)]
NTH_MISSING_STATE_SPEC = lambda n: [key('incomplete_invocation_context'), key('missing_values'), nth(n)]