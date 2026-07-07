FROM node:20-slim

WORKDIR /app

# Copy package files first
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

EXPOSE 5173

# Run the dev server with host exposed so it can be accessed outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
