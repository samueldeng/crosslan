#!/bin/bash
rm -rf ../bin/
mkdir ../bin/
for i in $(seq 1 200)
do
    declare -i port=$(($i+10000))
    mkdir ../bin/cl_container_$port
    cp cl-container-backup/cow ../bin/cl_container_$port/
done
