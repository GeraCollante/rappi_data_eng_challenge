#!/usr/bin/bash

docker build -t rappi-challenge .
docker run -ti rappi-challenge /bin/bash