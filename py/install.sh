#!/usr/bin/env bash
virtualenv -p python3 --system-site-packages sanitypython
./sanitypython/bin/pip install -r requirements.txt
