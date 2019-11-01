#!/bin/bash

cd ../Downloads/behavioral-model-master/tools
echo "table_modify ipv4_lpm ipv4_forward 2 00:04:00:00:00:02 4" > tmp_file_cmd 
./runtime_CLI.py --thrift-port 9090 < tmp_file_cmd
echo "table_modify ipv4_lpm ipv4_forward 3 00:04:00:00:00:03 4" > tmp_file_cmd 
./runtime_CLI.py --thrift-port 9090 < tmp_file_cmd
echo "table_modify ipv4_lpm ipv4_forward 0 00:04:00:00:00:00 2" > tmp_file_cmd 
./runtime_CLI.py --thrift-port 9091 < tmp_file_cmd
echo "table_modify ipv4_lpm ipv4_forward 1 00:04:00:00:00:01 2" > tmp_file_cmd 
./runtime_CLI.py --thrift-port 9091 < tmp_file_cmd
rm tmp_file_cmd