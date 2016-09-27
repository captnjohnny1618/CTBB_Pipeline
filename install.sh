#!/bin/bash

INSTALL_DIR=/usr/bin
CTBB_PATH=$INSTALL_DIR/ctbb_pipeline_scripts

if [[ $EUID -ne 0 ]]; then
    echo "Please run as root"
    exit 1
else
    mkdir -p $CTBB_PATH
    cp ctbb_pipeline* $CTBB_PATH

    touch $INSTALL_DIR/ctbb_pipeline
    echo "#!/bin/bash" > $INSTALL_DIR/ctbb_pipeline
    echo "$CTBB_PATH/ctbb_pipeline.py" >> $INSTALL_DIR/ctbb_pipeline
    chmod +x /usr/bin/ctbb_pipeline  
fi

