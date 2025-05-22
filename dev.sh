#!/bin/bash

docker build -t dropspy-dev .

docker run --rm -it -v $(pwd):/app --env-file .env dropspy-dev /bin/bash