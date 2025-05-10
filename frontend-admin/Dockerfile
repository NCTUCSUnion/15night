FROM node:18-alpine

WORKDIR /app

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package*.json ./

RUN npm install

COPY . .

RUN echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}" > .env

EXPOSE 8082

RUN npm run build

CMD ["npm", "run", "preview", "--", "--host"]