#!/bin/bash

function solve {
  input=$1

  a=$(echo $input | sed -n '/[^0-9A-Fa-f]/p')
  l=$(echo -n $input | wc -c)
  if [ ! -z "$a" ]
  then
    echo "Error: unreconize chars" > /dev/stderr
  elif [ $l -eq 0 ] || [ $(( $l % 2 )) -ne 0 ]
   then
    echo "Error: Non-even length" > /dev/stderr
  else
    echo "$input" | xxd -r -p | base64
  fi
}
