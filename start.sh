#!/bin/bash

export FW_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

SPECIAL_SOURCE=${FW_PATH}/special_start.sh
if [ -f "$SPECIAL_SOURCE" ]; then
    source $SPECIAL_SOURCE
fi

source $FW_PATH/spritz-env/bin/activate

export PYTHONPATH=${FW_PATH}:$PYTHONPATH

chmod +x ${FW_PATH}/scripts/*.py
export PATH=${FW_PATH}/scripts/:$PATH