# Despliegue con Docker

Este proyecto está configurado para construir el archivo `.env` dinámicamente a partir de variables de ambiente, ideal para despliegues en Caprover u otros orquestadores.

## Cómo funciona

1. El contenedor lee el archivo `.env.example` como plantilla
2. Al iniciar, el script `docker-entrypoint.sh` construye el archivo `.env` usando:
   - Variables de ambiente pasadas con `-e` (tienen prioridad)
   - Valores por defecto del `.env.example` (si la variable no se pasa)
3. Ejecuta las migraciones de Alembic
4. Inicia la aplicación con Gunicorn

## Uso con docker run

### Ejemplo básico (usando valores por defecto)
```bash
docker build -t nexo-backend .
docker run -p 5000:5000 nexo-backend
```

### Ejemplo con variables personalizadas
```bash
docker run -p 5000:5000 \
  -e MYSQL_HOST=my-mysql-server.com \
  -e MYSQL_PORT=3306 \
  -e MYSQL_DB=production_db \
  -e MYSQL_USER=prod_user \
  -e MYSQL_PASSWORD=super_secret_password \
  -e SECRET_KEY=my-super-secret-key-123 \
  -e JWT_SECRET=my-jwt-secret-456 \
  -e JWT_EXPIRES_MIN=30 \
  -e CORS_ORIGINS="https://myapp.com,https://www.myapp.com" \
  nexo-backend
```

## Uso en Caprover

En Caprover, simplemente configura las variables de ambiente en la interfaz web:

1. Ve a tu aplicación en Caprover
2. Navega a "App Configs" → "Environment Variables"
3. Agrega las variables necesarias:

```
MYSQL_HOST=srv-captain--mysql-db
MYSQL_PORT=3306
MYSQL_DB=nexo_production
MYSQL_USER=nexo_prod
MYSQL_PASSWORD=******************
SECRET_KEY=******************
JWT_SECRET=******************
JWT_EXPIRES_MIN=30
CORS_ORIGINS=https://tudominio.com
UPLOAD_ROOT=uploads
MAX_AVATAR_MB=2
```

4. Haz push de tu código o deploy desde el repo
5. El contenedor construirá automáticamente el `.env` con estos valores

## Variables de ambiente disponibles

Consulta el archivo `.env.example` para ver todas las variables disponibles:

- **Base de datos**: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`
- **Seguridad**: `SECRET_KEY`, `JWT_SECRET`, `JWT_EXPIRES_MIN`
- **CORS**: `CORS_ORIGINS`
- **Uploads**: `UPLOAD_ROOT`, `MAX_AVATAR_MB`
- **Aplicación**: `APP_PORT`

## Notas importantes

- **NO** necesitas crear un archivo `.env` manualmente
- Las variables de ambiente tienen **prioridad** sobre los valores del `.env.example`
- Si no pasas una variable, se usará el valor por defecto del `.env.example`
- El script espera automáticamente a que MySQL esté listo antes de ejecutar migraciones
- Las migraciones se ejecutan automáticamente al iniciar el contenedor
