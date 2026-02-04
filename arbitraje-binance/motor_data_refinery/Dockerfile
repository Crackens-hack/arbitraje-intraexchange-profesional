FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive

# Nueva raíz coherente con tu Compose
WORKDIR /app
RUN mkdir -p /app/motor_data_refinery

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash build-essential default-mysql-client python3-dev libpq-dev \
    libssl-dev libffi-dev libmariadb-dev mycli redis-tools less cron \
    curl ca-certificates coreutils git openssh-client \
  && rm -rf /var/lib/apt/lists/*


# Dependencias Python (copiadas desde tu contexto)
COPY requirements.txt /app/motor_data_refinery/
RUN pip install --no-cache-dir -r /app/motor_data_refinery/requirements.txt

# Scripts de desarrollo de este motor
COPY dev/ /app/motor_data_refinery/dev/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh /app/motor_data_refinery/dev/bootstrap.sh || true

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV SHELL=/bin/bash
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash", "-l", "-c", "tail -f /dev/null"]
