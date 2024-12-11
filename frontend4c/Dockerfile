FROM node:16-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application (with CI=true to ignore warnings)
# RUN CI=true npm run build

# Build the application
RUN npm run build             # Builds from /app/src into /app/build
# Install serve to run the built application
RUN npm install -g serve

EXPOSE 3000

# Serve the built application
CMD ["serve", "-s", "build", "-l", "3000"] 