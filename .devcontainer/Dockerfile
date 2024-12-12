# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.11-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:1-${VARIANT}

# Adding redis to sources list
RUN curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" \
    | sudo tee /etc/apt/sources.list.d/redis.list

# Install deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    protobuf-compiler>=3.12.4 \
    libprotobuf-dev>=3.12.4 \
    redis>=7.4.0 \
    libmagic-dev>=5.39 \
    pandoc>=2.9.2.1 \
    libreoffice>=7.0.4 \
    && rm -rf /var/lib/apt/lists/*


# Install/upgrade pip, build, twine
RUN python -m pip install --upgrade \
    # Use latest version
    pip \
    build>=1.2.0 \
    twine>=5.1.1 \
    grpcio-tools>=1.65.4 \
    betterproto[compiler]==2.0.0b6 \
    ruff>=0.5.7 \
    pre-commit>=3.8.0


# Install grpcurl version 1.8.9
RUN if [ ! -e grpcurl_1.9.1_linux_amd64.deb -a  x"$(arch)" = "xx86_64" ] ; \
    then wget https://github.com/fullstorydev/grpcurl/releases/download/v1.9.1/grpcurl_1.9.1_linux_amd64.deb ; \
    sudo dpkg -i grpcurl_1.9.1_linux_amd64.deb; fi
RUN if [ ! -e grpcurl_1.9.1_linux_arm64.deb -a  x"$(arch)" = "xaarch64" ] ; \
    then wget https://github.com/fullstorydev/grpcurl/releases/download/v1.9.1/grpcurl_1.9.1_linux_arm64.deb ; \
    sudo dpkg -i grpcurl_1.9.1_linux_arm64.deb; fi


# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1
