#!/bin/bash

# Script de prueba para verificar que el contenedor construye correctamente el .env
# desde variables de ambiente

echo "🧪 Construyendo imagen Docker..."
docker build -t nexo-backend-test .

echo ""
echo "🚀 Probando contenedor con variables de ambiente personalizadas..."
echo ""

docker run --rm \
  -e MYSQL_HOST=test-mysql-host \
  -e MYSQL_PORT=3307 \
  -e MYSQL_DB=test_database \
  -e MYSQL_USER=test_user \
  -e MYSQL_PASSWORD=test_password \
  -e SECRET_KEY=test-secret-key-123 \
  -e JWT_SECRET=test-jwt-secret-456 \
  -e JWT_EXPIRES_MIN=60 \
  -e CORS_ORIGINS="http://localhost:3000,http://localhost:4200" \
  --entrypoint cat \
  nexo-backend-test \
  .env

echo ""
echo "✅ Si ves las variables arriba, el sistema está funcionando correctamente!"
echo ""
echo "Para ejecutar normalmente (necesitas MySQL corriendo):"
echo "docker run -p 5000:5000 -e MYSQL_HOST=... -e MYSQL_PASSWORD=... nexo-backend-test"
