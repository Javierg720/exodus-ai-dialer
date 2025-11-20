FROM node:20-alpine

# Install edge-tts (Python package)
RUN apk add --no-cache python3 py3-pip ffmpeg && \
    pip3 install edge-tts --break-system-packages

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY index.js ./

EXPOSE 6011

CMD ["node", "index.js"]
