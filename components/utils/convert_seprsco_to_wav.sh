#!/bin/bash
# Converts files from seprsco (saved as .pkl) format to wav
# using conversion script from the original NESMDB dataset.

# Parse input parameters
INPUT="original"
OUTPUT="original"
while getopts ":i:o" opt; do
  case $opt in
    i) INPUT="$OPTARG";;
    o) OUTPUT="$OPTARG";;
    \?) echo "Invalid option -$OPTARG" >&2;;
  esac
done

# Convert original
if [ "${INPUT}" == "original" ] && [ "${OUTPUT}" == "original" ]; then
  INPUT="./../../data/nesmdb24_seprsco/train"
  OUTPUT="./../../data/nesmdb24_seprsco_wav/train"
fi

# Run command
trap "exit" INT
for file in "${INPUT}"/*; do
  python2 -m nesmdb.convert seprsco_to_wav ${file} --out_dir ${OUTPUT} || exit 1
done
