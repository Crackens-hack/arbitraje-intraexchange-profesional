FROM golang:1.23
ENV DEBIAN_FRONTEND=noninteractive

# Raíz coherente con tu Compose
WORKDIR /app
RUN mkdir -p /app/motor_reactor_realtime

RUN apt-get update && apt-get install -y --no-install-recommends \
      bash bash-completion git openssh-client ca-certificates curl coreutils \
  && rm -rf /var/lib/apt/lists/*

# 🚫 Eliminamos completamente Codex (ARG + instalación)
# === SIN CODEX CLI ===

# Caches de Go (coinciden con los volumes del compose)
ENV GOMODCACHE=/go/pkg/mod
ENV GOCACHE=/root/.cache/go-build

# Scripts de desarrollo del servicio
COPY dev/ /app/dev/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /app/dev/bootstrap.sh || true

ENV SHELL=/bin/bash
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash", "-l", "-c", "tail -f /dev/null"]
