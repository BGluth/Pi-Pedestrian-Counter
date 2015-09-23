#!/bin/bash

if !(ifconfig wlan0 | grep -q "inet addr:") ; then
    echo "Network connection down! Attempting reconnection."
    sudo wpa_action wlan0 CONNECTED
fi