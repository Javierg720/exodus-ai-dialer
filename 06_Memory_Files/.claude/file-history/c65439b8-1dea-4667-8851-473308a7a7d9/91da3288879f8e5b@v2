FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY index.js ./

EXPOSE 6002

CMD ["node", "index.js"]
