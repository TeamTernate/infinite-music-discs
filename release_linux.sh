#!/bin/bash
./build_linux.sh "$@"
./build/release_wrapper_linux.sh "$@"
