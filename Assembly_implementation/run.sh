#! /bin/bash
# ./run in terminal: Permission denied, solving: chmod +x ./run.sh, and then for running: ./run

# variable: name of files
file=${1:-ISW_1}     #first argument
project_=${2:-isw_1} #second agument   

#then for running: ./run.sh ISW_1 isw_1

#echo "The current directory is:"
pwd
export SCALE="${PWD}"
cd hw
pwd
ls
printf '\n'
export SCALE_HW="${PWD}"
export TARGET="${SCALE_HW}/target/lpc1313fbd48"
cd ${TARGET}
make --no-builtin-rules clean all
cd ${SCALE_HW}
cd $file
pwd
ls
printf '\n'
sudo make --no-builtin-rules -f ${TARGET}/build/lib/scale.mk BSP="${TARGET}/build" USB="/dev/ttyUSB0" PROJECT="$project_" PROJECT_SOURCES="$project_.c $project_.S" clean all program
