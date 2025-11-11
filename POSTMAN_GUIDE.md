# Guía de Postman - Nexo Backend API

Esta guía explica cómo importar y usar la colección de Postman para probar la API de Nexo Backend.

## 📥 Importar en Postman

### Paso 1: Importar la Colección

1. Abre Postman
2. Haz clic en **Import** (botón en la parte superior izquierda)
3. Arrastra el archivo `Nexo_Backend_API.postman_collection.json` o haz clic en **Upload Files**
4. Confirma la importación

### Paso 2: Importar el Environment (Opcional pero Recomendado)

1. Haz clic en **Import** nuevamente
2. Arrastra el archivo `Nexo_Backend_Environments.postman_environment.json`
3. Confirma la importación
4. Selecciona el environment "Nexo - Local" en el dropdown superior derecho

## 🚀 Comenzar a Usar

### 1. Health Check

Primero verifica que el servidor esté funcionando:

```
GET http://localhost:5000/health
```

Debe responder: `{"status": "ok"}`

### 2. Registrar un Usuario

Usa el endpoint **Auth > Register** para crear un nuevo usuario:

```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan.perez@example.com",
  "fecha_nacimiento": "1990-05-15",
  "username": "juanperez",
  "password": "MiPassword123!"
}
```

**Nota:** La colección automáticamente guardará el `user_uuid` en las variables.

### 3. Iniciar Sesión

Usa el endpoint **Auth > Login**:

```json
{
  "email": "juan.perez@example.com",
  "password": "MiPassword123!"
}
```

**Importante:** La colección automáticamente:
- Guarda el `access_token` en las variables de colección
- Guarda el `user_uuid` del usuario

### 4. Endpoints Protegidos

Todos los endpoints que requieren autenticación ya tienen configurado el header:

```
Authorization: Bearer {{access_token}}
```

El token se añade automáticamente después del login.

## 📋 Variables de Colección

La colección usa estas variables:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `base_url` | URL base de la API | `http://localhost:5000` |
| `access_token` | Token JWT (se guarda automáticamente al hacer login) | `eyJ0eXAiOiJKV1QiLCJhbGc...` |
| `user_uuid` | UUID del usuario autenticado | `550e8400-e29b-41d4-a716-446655440000` |

### Ver/Editar Variables

1. Haz clic en la colección "Nexo Backend API"
2. Ve a la pestaña **Variables**
3. Ahí puedes ver y editar los valores

## 📚 Estructura de la Colección

### 1. Health
- **Health Check**: Verifica el estado del servidor

### 2. Auth (Autenticación)
- **Register**: Crear nuevo usuario
- **Login**: Iniciar sesión (guarda token automáticamente)
- **Logout**: Cerrar sesión

### 3. Users (Usuarios)
- **Get My Profile**: Ver mi perfil completo
- **Update My Profile**: Actualizar mi información
- **Upload Avatar**: Subir foto de perfil
- **Get User by UUID**: Ver perfil público de un usuario
- **Search Users**: Buscar usuarios por nombre, apellido, username o email

### 4. Friends (Amistades)
- **List Friends**: Listar mis amigos (filtrable por estado)
- **Send Friend Request**: Enviar solicitud de amistad
- **Accept Friend Request**: Aceptar solicitud
- **Reject Friend Request**: Rechazar solicitud
- **Unfriend**: Eliminar amistad

## 🔄 Flujo de Trabajo Típico

### Escenario 1: Nuevo Usuario

1. **Register** → Crea cuenta
2. **Login** → Obtiene token
3. **Get My Profile** → Ve su información
4. **Upload Avatar** → Sube foto
5. **Search Users** → Busca otros usuarios
6. **Send Friend Request** → Envía solicitud

### Escenario 2: Usuario Existente

1. **Login** → Inicia sesión
2. **List Friends** → Ve sus amigos
3. **Accept/Reject Friend Request** → Gestiona solicitudes pendientes

## 🧪 Tests Automáticos

La colección incluye tests automáticos que:

- **Register**: Guarda el `user_uuid` del usuario creado
- **Login**: Guarda el `access_token` y `user_uuid` automáticamente

Estos scripts están en la pestaña **Tests** de cada request.

## 🌍 Cambiar de Entorno

Para usar diferentes entornos (local, staging, production):

1. Crea un nuevo environment en Postman
2. Define las variables:
   - `base_url`: URL de tu API
   - `access_token`: (vacío inicialmente)
   - `user_uuid`: (vacío inicialmente)
3. Selecciona el environment en el dropdown

Ejemplo para producción:

```json
{
  "base_url": "https://api.tudominio.com",
  "access_token": "",
  "user_uuid": ""
}
```

## 📝 Notas Importantes

### Políticas de Contraseña

Las contraseñas deben cumplir:
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Al menos un carácter especial (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

### Validación de Edad

Los usuarios deben ser mayores de 18 años.

### Formatos de Fecha

Usa el formato `YYYY-MM-DD` para fechas:
```
"fecha_nacimiento": "1990-05-15"
```

### Subida de Avatar

- Formatos permitidos: JPG, JPEG, PNG, GIF, WEBP
- Tamaño máximo: 2MB (configurable en `.env`)
- Se envía como `multipart/form-data`

### Estados de Amistad

- `pending`: Solicitud enviada pero no aceptada
- `accepted`: Amistad confirmada
- `rejected`: Solicitud rechazada
- `removed`: Amistad eliminada

## 🐛 Troubleshooting

### Error: "No such container"

Asegúrate de que el servidor esté corriendo:

```bash
docker-compose up
```

O con docker run:

```bash
docker ps --filter "name=nexo"
```

### Token Expirado

Si recibes `401 Unauthorized`, vuelve a hacer login:

1. Ve a **Auth > Login**
2. Envía el request
3. El nuevo token se guardará automáticamente

### Variables No Se Guardan

1. Verifica que estés usando la colección correctamente
2. Ve a **Variables** y confirma que `access_token` y `user_uuid` están definidas
3. Los scripts de tests deben estar habilitados

## 📖 Ejemplos de Uso

### Buscar y Agregar Amigo

```javascript
// 1. Buscar usuarios
GET /users/search?q=maria

// 2. Copiar el user_uuid del resultado
// 3. Enviar solicitud de amistad
POST /friends/request
{
  "to_user_uuid": "UUID_DE_MARIA"
}
```

### Actualizar Perfil Completo

```javascript
PATCH /users/me
{
  "nombre": "Juan Carlos",
  "apellido": "Pérez García",
  "username": "juancarlos",
  "email": "nuevo@email.com",
  "password": "NuevoPass123!",
  "fecha_nacimiento": "1990-06-20"
}
```

### Ver Solicitudes Pendientes

```javascript
GET /friends?status=pending

// El campo "requested_by_me" indica si yo envié la solicitud
// Si es false, puedo aceptar/rechazar
```

## 📱 Exportar para Compartir

Para compartir la colección con tu equipo:

1. Haz clic derecho en la colección
2. **Export**
3. Elige formato **Collection v2.1**
4. Guarda el archivo JSON
5. Compártelo con tu equipo

¡Listo para usar! 🚀
