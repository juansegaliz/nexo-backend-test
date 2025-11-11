# Guía: Ejecutar con Docker Run

Esta guía explica cómo ejecutar los contenedores usando `docker run` directamente (sin docker-compose).

## ⚠️ Problema Común

Si ejecutas los contenedores sin una red compartida, **NO podrán comunicarse entre sí**.

```bash
# ❌ ESTO NO FUNCIONA (sin red compartida)
docker run -d --name nexo-mysql -e MYSQL_DATABASE=nexo_db -p 3307:3306 mysql:8.0
docker run -d --name nexo-backend -e MYSQL_HOST=nexo-mysql nexo-backend  # ERROR!
```

## ✅ Solución: Usar una Red Docker

### Paso 1: Crear una red Docker

```bash
docker network create nexo-network
```

### Paso 2: Ejecutar MySQL en la red

```bash
docker run -d \
  --name nexo-mysql \
  --network nexo-network \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=nexo_db \
  -e MYSQL_USER=nexo_user \
  -e MYSQL_PASSWORD=nexo_password \
  -p 3307:3306 \
  mysql:8.0
```

**Espera 15-20 segundos** para que MySQL esté completamente listo.

### Paso 3: Ejecutar el Backend en la misma red

```bash
docker run -d \
  --name nexo-backend \
  --network nexo-network \
  -p 5000:5000 \
  -e MYSQL_HOST=nexo-mysql \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DB=nexo_db \
  -e MYSQL_USER=nexo_user \
  -e MYSQL_PASSWORD=nexo_password \
  -e SECRET_KEY=my-secret-key-for-testing \
  -e JWT_SECRET=my-jwt-secret-for-testing \
  nexo-backend
```

### Notas Importantes:

1. **MYSQL_HOST**: Usa el **nombre del contenedor** (`nexo-mysql`), NO `localhost` ni `host.docker.internal`
2. **MYSQL_PORT**: Usa `3306` (puerto interno), NO `3307` (que es solo para el host)
3. **--network**: Ambos contenedores deben estar en la **misma red**
4. El puerto `3307:3306` significa:
   - `3307` = puerto en tu máquina (host)
   - `3306` = puerto dentro de Docker

## Verificar que funciona

```bash
# Ver logs del backend
docker logs nexo-backend

# Verificar que la API responde
curl http://localhost:5000/health
# Debe devolver: {"status":"ok"}

# Ver ambos contenedores corriendo
docker ps --filter "name=nexo"
```

## Detener y Limpiar

```bash
# Detener contenedores
docker stop nexo-backend nexo-mysql

# Eliminar contenedores
docker rm nexo-backend nexo-mysql

# Eliminar red (opcional)
docker network rm nexo-network
```

## Script Completo (Todo en Uno)

```bash
#!/bin/bash

# Crear red
docker network create nexo-network 2>/dev/null || echo "Red ya existe"

# Ejecutar MySQL
docker run -d \
  --name nexo-mysql \
  --network nexo-network \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=nexo_db \
  -e MYSQL_USER=nexo_user \
  -e MYSQL_PASSWORD=nexo_password \
  -p 3307:3306 \
  mysql:8.0

echo "Esperando 20 segundos a que MySQL esté listo..."
sleep 20

# Ejecutar Backend
docker run -d \
  --name nexo-backend \
  --network nexo-network \
  -p 5000:5000 \
  -e MYSQL_HOST=nexo-mysql \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DB=nexo_db \
  -e MYSQL_USER=nexo_user \
  -e MYSQL_PASSWORD=nexo_password \
  -e SECRET_KEY=my-production-secret-key \
  -e JWT_SECRET=my-production-jwt-secret \
  -e JWT_EXPIRES_MIN=30 \
  -e CORS_ORIGINS=https://tudominio.com \
  nexo-backend

echo ""
echo "✅ Contenedores ejecutándose!"
echo "API: http://localhost:5000"
echo ""
echo "Ver logs: docker logs nexo-backend"
```

## Para Caprover

En Caprover no necesitas preocuparte por las redes, ya que Caprover maneja la comunicación entre servicios automáticamente. Solo necesitas:

1. Crear un servicio para MySQL (o usar uno existente)
2. Crear tu aplicación nexo-backend
3. Configurar las variables de ambiente en la UI
4. Usar el hostname del servicio MySQL (ejemplo: `srv-captain--mysql-db`)
