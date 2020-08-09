#!/usr/bin/env bash
# Copyright 2020 Ververica GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if ! [ -x "$(command -v protoc)" ]; then
	echo "protoc must be installed to generate classes" >$2
	exit 1
fi

protoc \
    --proto_path=statefun-workshop-protocol/src/main/protobuf/ \
	--python_out=statefun-workshop-python/ \
	--java_out=statefun-workshop-protocol/src/main/java/ \
	entities.proto
