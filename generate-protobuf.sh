#!/usr/bin/env bash

if ! [ -x "$(command -v protoc)" ]; then
	echo "protoc must be installed to generate classes" >$2
	exit 1
fi

protoc \
	--java_out=statefun-workshop-protocol/src/main/java/ \
	statefun-workshop-protocol/src/main/protobuf/entities.proto
