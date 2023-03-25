#!/bin/bash

liveDir=./live
myDATE=$(date)

# Build CVE Translation Map
./gen_cve_map.sh 2>&1 > cve_log.txt &

# Build IP Rep. Translation Map
./gen_iprep_map.sh 2>&1 > iprep_log.txt &

# Wait for background jobs to finish
wait

# Sanity Check
myCVE=$(grep -c "CVE\|CAN" < $liveDir/cve.yaml)
myIPREP=$(grep -c -P "\b(?:\d{1,3}\.){3}\d{1,3}\b" < $liveDir/iprep.yaml)

if [ $myCVE -gt 5000 ] && [ $myIPREP -gt 200000 ];
  then
    myMESSAGE="$myDATE: $myCVE IDs, $myIPREP reps - OK."
    echo "$myMESSAGE" >> $liveDir/run.log
    #cp *.yaml ./live/
    
  else
    myMESSAGE="$myDATE: $myCVE IDs, $myIPREP reps - ERROR."
    echo "$myMESSAGE" >> $liveDir/error.log
fi

echo


