FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHALKBOARD_HOST=0.0.0.0 \
    CHALKBOARD_PORT=8765 \
    CHALKBOARD_DATA_DIR=/data

RUN addgroup -S chalkboard \
    && adduser -S -G chalkboard -h /app chalkboard \
    && install -d -o chalkboard -g chalkboard /app /data

COPY --chown=chalkboard:chalkboard src/ /app/

USER chalkboard
WORKDIR /app
VOLUME ["/data"]
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/health', timeout=2).read()"]

ENTRYPOINT ["python", "/app/chalkboard_server.py"]
