# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para PyMySQL y cryptography
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requirements
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instala gunicorn para producción
RUN pip install --no-cache-dir gunicorn

# Copia el .env.example (se usará como template)
COPY .env.example .

# Copia el script de entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh && chmod +x /usr/local/bin/docker-entrypoint.sh

# Copia el código de la aplicación
COPY . .

# Crea el directorio para uploads
RUN mkdir -p uploads

# Expone el puerto 5000
EXPOSE 5000

# Variable de entorno para Python
ENV PYTHONUNBUFFERED=1

# Configura el entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Comando para ejecutar la aplicación con gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
