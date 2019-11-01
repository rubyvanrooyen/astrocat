#! /bin/bash

## Standard checks to run after new development to ensure typical conversion are still successful

RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW='\033[0;33m'
NOCOLOR="\033[0m"

CMD="./astrokat-catalogue2observation.py"

echo
$CMD --csv test_convert/targets.csv --target-duration 10
ret=$?
if [ "0" -eq "$ret" ]
then
    echo -e "${GREEN} Success ${NOCOLOR}"
else
    echo -e "${RED} Failure ${NOCOLOR}"
    exit
fi


echo
$CMD --csv test_convert/two_calib.csv --integration-period 4 --primary-cal-duration 300 --horizon 17 --show
ret=$?
if [ "0" -eq "$ret" ]
then
    echo -e "${GREEN} Success ${NOCOLOR}"
else
    echo -e "${RED} Failure ${NOCOLOR}"
    exit
fi


echo
$CMD --csv test_convert/image.csv --target-duration 180 --primary-cal-duration 300 --secondary-cal-duration 65 --primary-cal-cadence 1800 --max-duration 3600
ret=$?
if [ "0" -eq "$ret" ]
then
    echo -e "${GREEN} Success ${NOCOLOR}"
else
    echo -e "${RED} Failure ${NOCOLOR}"
    exit
fi


echo
$CMD --csv test_convert/OH_periodic_masers.csv --target-duration 600 --primary-cal-duration 300 --secondary-cal-duration 60 --product c856M32k --show
ret=$?
if [ "0" -eq "$ret" ]
then
    echo -e "${GREEN} Success ${NOCOLOR}"
else
    echo -e "${RED} Failure ${NOCOLOR}"
    exit
fi


# -fin-

