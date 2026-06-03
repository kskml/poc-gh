Structure & Simpler Implementation

To make this easy to maintain, we strip away the over-engineering (no iptables, no SSH, no complex entrypoints) and rely on Podman's native isolation plus rbash and Squid. 
Directory Structure
sandbox/
├── Containerfile          # Single-stage, simple build
├── allowed-commands.list  # What commands the user can run
├── allowed-urls.list      # What URLs the proxy allows
├── squid.conf             # Proxy configuration
└── bashrc                 # Restricted bash configuration

1. Containerfile (Simplified)

We use a single stage. We install packages, create the user, set up the restricted bin directory, and drop in the configs.
dockerfile
FROM ubuntu:22.04

# 1. Install all required OS packages + code-server
RUN apt-get update && apt-get install -y \
        bash git squid curl wget vim python3 nodejs npm \
        supervisor ca-certificates \
    && curl -fsSL https://code-server.dev/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 2. Install opencode (adjust URL to the actual binary release)
RUN curl -fsSL "https://github.com/sst/opencode/releases/latest/download/opencode-linux-amd64" \
         -o /usr/local/bin/opencode && chmod +x /usr/local/bin/opencode

# 3. Create sandbox user with rbash as the default shell
RUN useradd -m -s /bin/rbash sandbox

# 4. Setup Restricted PATH (Whitelisted Commands)
RUN mkdir -p /opt/sandbox/bin
COPY allowed-commands.list /tmp/allowed-commands.list
RUN while read cmd; do \
        [[ "$cmd" =~ ^#.*$ || -z "$cmd" ]] && continue; \
        if command -v "$cmd" &>/dev/null; then \
            ln -s "$(command -v "$cmd")" "/opt/sandbox/bin/$cmd"; \
        fi; \
    done < /tmp/allowed-commands.list && \
    # Explicitly link opencode since it's in /usr/local/bin
    ln -s /usr/local/bin/opencode /opt/sandbox/bin/opencode && \
    chown -R root:root /opt/sandbox/bin

# 5. Configure User Environment
COPY bashrc /home/sandbox/.bashrc
RUN chown sandbox:sandbox /home/sandbox/.bashrc

# 6. Configure Network Whitelisting (Squid Proxy)
COPY allowed-urls.list /etc/squid/allowed-urls.list
COPY squid.conf /etc/squid/squid.conf
RUN mkdir -p /var/spool/squid && squid -z

# 7. Configure Supervisor (to run Squisk & Code-Server)
COPY supervisord.conf /etc/supervisord.conf

# 8. Setup Workspace
RUN mkdir -p /home/sandbox/workspace && chown sandbox:sandbox /home/sandbox/workspace
WORKDIR /home/sandbox/workspace

EXPOSE 8080
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]

2. allowed-commands.list
   # Dev tools
git
opencode
python3
pip3
node
npm
npx

# File utilities
ls
cat
head
tail
mkdir
touch
cp
mv

# Text
grep
sed
awk
vim

# Network (forced through proxy by env vars)
curl
wget

# Shell built-ins we want to allow
echo
clear
exit

3. allowed-urls.list
.github.com
.gitlab.com
.pypi.org
.files.pythonhosted.org
.registry.npmjs.org
.npmjs.org
.api.openai.com

4. squid.conf
A bare-minimum Squid configuration that denies everything except what matches the URL list.
http_port 127.0.0.1:3128
cache deny all

# Define ACLs
acl allowed_urls dstdomain "/etc/squid/allowed-urls.list"
acl SSL_ports port 443
acl Safe_ports port 80 443
acl CONNECT method CONNECT

# Rules
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow allowed_urls
http_access deny all

5. bashrc

This forces all network traffic from the user's tools through the local Squid proxy.
export PATH=/opt/sandbox/bin
export http_proxy=http://127.0.0.1:3128
export https_proxy=http://127.0.0.1:3128
export GIT_PROXY_COMMAND="curl --proxy http://127.0.0.1:3128 %h %p"

PS1='[sandbox] \$ '

# Audit every command
trap 'echo "$(date +%FT%T) | $USER | $BASH_COMMAND" >> /var/log/sandbox-audit.log' DEBUG

6. supervisord.conf
[supervisord]
nodaemon=true

[program:squid]
command=/usr/sbin/squid -N -d 1
autostart=true

[program:code-server]
command=/usr/bin/code-server --bind-addr 0.0.0.0:8080 --auth none /home/sandbox/workspace
user=sandbox
environment=HOME="/home/sandbox",PATH="/opt/sandbox/bin:/usr/local/bin:/usr/bin",http_proxy="http://127.0.0.1:3128",https_proxy="http://127.0.0.1:3128"
autostart=true

Running and Logging In via Podman

Because we rely on supervisord to start Squid and the IDE, and rbash to restrict the user, the Podman run command is very simple. 

1. Build the image:
   podman build -t dev-sandbox .

2. Run container
podman run -d \
  --name my-sandbox \
  -p 8080:8080 \
  --memory=2g \
  --pids-limit=256 \
  dev-sandbox

3. Access the IDE:
Open your browser and navigate to http://localhost:8080. The code-server IDE is running as the sandbox user. The integrated terminal inside the IDE will automatically be an rbash shell with restricted commands and proxied network.

4. Login to the container via Podman (CLI):
To get a shell in the container, you use podman exec. Because the sandbox user's default shell is rbash, you drop straight into the restricted environment:
# Standard user login (restricted bash)
podman exec -it -u sandbox my-sandbox bash

# If you need to do admin tasks (unrestricted)
podman exec -it -u root my-sandbox bash

Test the restrictions:
# Inside the sandbox rbash:
[sandbox] $ cd /tmp
rbash: cd: restricted

[sandbox] $ ping google.com
rbash: ping: command not found

[sandbox] $ curl -I https://api.openai.com
HTTP/2 200  <-- ALLOWED by Squid

[sandbox] $ curl -I https://reddit.com
HTTP/1.1 403 Forbidden  <-- BLOCKED by Squid
