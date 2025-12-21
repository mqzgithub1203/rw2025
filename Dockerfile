FROM node:alpine

WORKDIR /app

ARG PORT=3000
ENV PORT=$PORT
EXPOSE $PORT

COPY package.json ./
RUN apk update && \
    apk add --no-cache bash wget curl procps && \
    npm install

COPY index.js start.sh ./
RUN chmod +x start.sh

ENTRYPOINT [ "node", "index.js" ]
