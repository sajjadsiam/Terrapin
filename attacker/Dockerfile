FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary tools
RUN apt-get update && \
    echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections && \
    apt-get install -y \
    python3 \
    python3-pip \
    tcpdump \
    wireshark-common \
    tshark \
    net-tools \
    iproute2 \
    iptables \
    nftables \
    openssh-client \
    netcat-traditional \
    vim \
    curl \
    git && \
    rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /attack

# Copy POC exploit code
COPY poc_exploit /attack/poc_exploit

# Install Python dependencies
RUN pip3 install -r /attack/poc_exploit/requirements.txt

# Copy manual attack demo
COPY manual_attack_demo.py /attack/manual_attack_demo.py

# Copy attacker tools
COPY attacker/tools /attack/tools
COPY attacker/mitm_setup.sh /attack/mitm_setup.sh
RUN chmod +x /attack/mitm_setup.sh
RUN chmod +x /attack/tools/*.sh 2>/dev/null || true
RUN chmod +x /attack/manual_attack_demo.py

# Create directories for captures
RUN mkdir -p /attack/captures /attack/logs

# Set environment
ENV PYTHONUNBUFFERED=1

CMD ["/bin/bash"]
