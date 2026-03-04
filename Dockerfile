FROM node:20-bookworm-slim
RUN apt-get update && apt-get install -y python3
RUN npm install -g n8n
CMD ["n8n", "start"]