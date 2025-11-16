FROM node:20

WORKDIR /app

# Copy package files
COPY package*.json ./

# Configure npm to use strict-ssl=false (development only!)
RUN npm config set strict-ssl false

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Expose port
EXPOSE 5173

# Start dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
