#!/bin/bash

if [ -f "../dist/CloudLogPyCAT" ]; then
	cp ../dist/CloudLogPyCAT ~/.local/bin/
fi

xdg-icon-resource install --size 64 --context apps --mode user k6gte-cloudcat.png k6gte-cloudcat

xdg-desktop-icon install k6gte-CloudLogPyCAT.desktop

xdg-desktop-menu install k6gte-CloudLogPyCAT.desktop

