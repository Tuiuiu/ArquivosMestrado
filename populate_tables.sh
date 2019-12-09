#!/bin/bash

cd ../Downloads/behavioral-model-master/tools
./runtime_CLI.py --thrift-port 9090 < ~/P4\ Tests\ Mestrado/commandss1_test.txt
./runtime_CLI.py --thrift-port 9091 < ~/P4\ Tests\ Mestrado/commandss2_test.txt
./runtime_CLI.py --thrift-port 9092 < ~/P4\ Tests\ Mestrado/commandss3_test.txt
./runtime_CLI.py --thrift-port 9093 < ~/P4\ Tests\ Mestrado/commandss4_test.txt