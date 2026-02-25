FROM ubuntu:22.04

# Set non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install OpenSSH server (older vulnerable version for demonstration)
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir /var/run/sshd && \
    mkdir -p /root/.ssh

# Create a test user
RUN useradd -m -s /bin/bash testuser && \
    echo 'testuser:password123' | chpasswd && \
    echo 'root:rootpassword' | chpasswd

# Copy vulnerable SSH configuration
COPY sshd_config /etc/ssh/sshd_config

# Generate host keys
RUN ssh-keygen -A

# Setup script
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh

# Expose SSH port
EXPOSE 22

# Run setup and start SSH
CMD ["/setup.sh"]
