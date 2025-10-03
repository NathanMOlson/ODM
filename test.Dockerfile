FROM ubuntu:24.04 AS builder

# Env variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH="$PYTHONPATH:/code/SuperBuild/install/lib/python3.12/dist-packages:/code/SuperBuild/install/bin/opensfm" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/code/SuperBuild/install/lib"

# Prepare directories
WORKDIR /code

# Copy everything
COPY . ./

# Entry point
ENTRYPOINT ["/bin/bash"]
