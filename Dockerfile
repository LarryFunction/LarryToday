FROM python:3.13-slim
WORKDIR /app
COPY server.py ./
COPY scripts ./scripts
COPY config ./config
COPY public ./public
COPY srcs/sources.json ./srcs/sources.json
RUN useradd --uid 10001 --create-home reader && mkdir data && chown reader:reader data
USER reader
ENV HOST=0.0.0.0 PORT=8000 PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "server.py"]
