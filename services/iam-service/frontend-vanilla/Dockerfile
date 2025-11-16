# Dockerfile - IAM Frontend (Eventos Perú)
#
# Build:
#   docker build -t emeday/eventos-iam-frontend:1.0.0 .
#
# Run (local test):
#   docker run --rm -p 8080:80 emeday/eventos-iam-frontend:1.0.0
#
FROM nginx:1.27-alpine

# Remove default Nginx static content
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend static files into Nginx web root
# Asume que el Dockerfile está en la raíz del frontend (donde está index.html)
COPY . /usr/share/nginx/html/

# Custom Nginx config (SPA + gzip)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
