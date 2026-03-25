FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/sk3pp3r/ssh-mngr"
LABEL org.opencontainers.image.description="Terminal SSH Connection Manager"
LABEL org.opencontainers.image.licenses="MIT"

RUN pip install --no-cache-dir ssh-mngr==0.1.1

ENTRYPOINT ["ssh-mngr"]
