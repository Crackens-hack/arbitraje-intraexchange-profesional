FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive

# Raíz coherente con tu Compose limpio
WORKDIR /app
RUN mkdir -p /app/motor_sentinel

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl ca-certificates coreutils git openssh-client \
  && rm -rf /var/lib/apt/lists/*

# 🚫 SIN Codex (borramos todos los ARG y la instalación del CLI)
# === Codex eliminado ===

# Zona horaria
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Scripts de desarrollo del servicio
COPY dev/ /app/dev/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /app/dev/bootstrap.sh || true

ENV SHELL=/bin/bash
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash", "-l", "-c", "tail -f /dev/null"]
