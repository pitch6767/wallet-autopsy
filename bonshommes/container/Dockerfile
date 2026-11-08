FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fontconfig ca-certificates && rm -rf /var/lib/apt/lists/*
COPY fonts/ /usr/share/fonts/truetype/stickman/
RUN fc-cache -f
WORKDIR /app
COPY server.mjs .
EXPOSE 8080
CMD ["node", "server.mjs"]
