#!/bin/bash
set -e

echo "🔧 Construyendo archivo .env desde variables de ambiente..."

# Crear archivo .env vacío
> .env

# Leer cada línea del .env.example
while IFS= read -r line || [ -n "$line" ]; do
    # Remover posibles caracteres de retorno de carro
    line=$(echo "$line" | tr -d '\r')

    # Ignorar líneas vacías y comentarios
    if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
        echo "$line" >> .env
        continue
    fi

    # Verificar que la línea contiene un '='
    if [[ ! "$line" =~ = ]]; then
        echo "$line" >> .env
        continue
    fi

    # Extraer el nombre de la variable (antes del =)
    var_name=$(echo "$line" | cut -d'=' -f1 | xargs)

    # Saltar si var_name está vacío
    if [[ -z "$var_name" ]]; then
        echo "$line" >> .env
        continue
    fi

    # Si la variable existe en el ambiente, usar ese valor
    if [ -n "${!var_name:-}" ]; then
        echo "$var_name=${!var_name}" >> .env
        echo "  ✓ $var_name (desde ambiente)"
    else
        # Si no existe, usar el valor por defecto del .env.example
        echo "$line" >> .env
        echo "  ℹ $var_name (valor por defecto)"
    fi
done < .env.example

echo ""
echo "✅ Archivo .env construido exitosamente"
echo ""

# Ejecutar migraciones (con reintentos)
echo "🔄 Ejecutando migraciones de base de datos..."
max_attempts=5
attempt=0

until alembic upgrade head || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    if [ $attempt -lt $max_attempts ]; then
        echo "   ⚠️  Intento $attempt falló, reintentando en 5 segundos..."
        sleep 5
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  No se pudieron ejecutar las migraciones después de $max_attempts intentos"
    echo "   Continuando de todas formas (las migraciones pueden ejecutarse manualmente)"
fi

echo "✅ Migraciones completadas (o saltadas)"
echo ""

# Iniciar la aplicación
echo "🚀 Iniciando aplicación..."
exec "$@"
