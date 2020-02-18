#!/usr/bin/env bash

if ! [ -x "$(command -v protoc)" ]; then
	echo "protoc must be installed to generate classes" >$2
	exit 1
fi

protoc \
    --proto_path=statefun-workshop-protocol/src/main/protobuf/ \
	--python_out=statefun-workshop-python/ \
	--java_out=statefun-workshop-protocol/src/main/java/ \
	entities.proto
