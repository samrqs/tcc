FROM node:24-alpine AS builder

# Add a work directory
WORKDIR /home/node/app

# Cache and Install dependencies
COPY package.json .
RUN npm i

# Copy app files
COPY . .

# build args (vindos do GitHub Actions)
ARG VITE_OPENAI_API_KEY
ARG VITE_OPENAI_MODEL_NAME
ARG VITE_OPENAI_MODEL_TEMPERATURE
ARG VITE_API_BASE_URL
ARG VITE_WHATSAPP_PHONE_NUMBER

# define envs para o Vite usar no build
ENV VITE_OPENAI_API_KEY=$VITE_OPENAI_API_KEY
ENV VITE_OPENAI_MODEL_NAME=$VITE_OPENAI_MODEL_NAME
ENV VITE_OPENAI_MODEL_TEMPERATURE=$VITE_OPENAI_MODEL_TEMPERATURE
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WHATSAPP_PHONE_NUMBER=$VITE_WHATSAPP_PHONE_NUMBER

# Build the app
RUN npm run build

# Bundle static assets with nginx
FROM nginx:1.29.1-alpine3.22-slim AS production
ENV NODE_ENV production

# Copy built assets from builder
COPY --from=builder /home/node/app/dist /usr/share/nginx/html

# Add your nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 5173

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
