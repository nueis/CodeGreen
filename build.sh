#!/bin/bash
git config --global url."https://$GH_TOKEN@github.com/".insteadOf "https://github.com/"
git submodule update --init --recursive