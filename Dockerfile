# --- STAGE 1: Build the React/TypeScript Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Use the command that works locally: npm run build
RUN npm run build

# --- STAGE 2: Spin Up the Fast API Data Engine Container ---
FROM python:3.10-slim
WORKDIR /workspace

# Install server packages
RUN pip install --no-cache-dir fastapi uvicorn pandas python-multipart openai

# Copy the core backend application logic
COPY main.py .

# IMPORTANT: Copy from the correct .output folder
COPY --from=frontend-builder /app/.output ./.output

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]