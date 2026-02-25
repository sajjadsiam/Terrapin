FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install SSH client and tools
RUN apt-get update && \
    apt-get install -y \
    openssh-client \
    python3 \
    python3-pip \
    net-tools \
    iproute2 \
    curl \
    vim && \
    rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /client

# Copy test client script
COPY test_client.py /client/test_client.py
RUN chmod +x /client/test_client.py

# Install Python dependencies
RUN pip3 install paramiko

CMD ["/bin/bash"]
