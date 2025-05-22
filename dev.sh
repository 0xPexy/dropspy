#!/bin/bash

docker build -t dropspy-dev .

docker run --rm -it -v $(pwd):/app dropspy-dev /bin/bash