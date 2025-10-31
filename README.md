# Sistema de Gestión y Enrutamiento de Órdenes Multiárea

MVP de aplicación web para gestión de órdenes de trabajo con asignación multiárea, 
temporizador SLA y trazabilidad completa.

## 🔧 Requisitos Previos

- Python 3.10 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)

## ⚡ Instalación y Ejecución (5 pasos)

### 1. Clonar el repositorio
```bash
git clone <url-repositorio>
cd enrutador-ordenes-multiarea
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
copy .env.example .env
# Editar .env con tus credenciales de MySQL
```

### 5. Inicializar base de datos y ejecutar
```bash
# Crear base de datos y tablas
mysql -u root -p < db/migrations/001_initial_schema.sql
mysql -u root -p < db/seeds/seed_data.sql

# Ejecutar aplicación
python src/main.py
```

La aplicación estará disponible en: `http://localhost:8000`
Documentación interactiva en: `http://localhost:8000/docs`

## 🎯 Ejecución Rápida (Windows)

Alternativamente, usa el script batch:
```bash
run.bat
```

## 🧪 Ejecutar Pruebas
```bash
pytest tests/ -v
```

## 📊 Variables de Entorno

Ver archivo `.env.example` para todas las variables requeridas.

Variables críticas:
- `DATABASE_URL`: Conexión a MySQL
- `N_SEG`: Intervalo del temporizador (segundos)
- `SLA_SEG`: Límite SLA (segundos)
- `ESTADO_TIMEOUT`: Estado al superar SLA

## 📚 Estructura del Proyecto

- `src/`: Código fuente de la aplicación
- `db/`: Scripts de base de datos (migrations y seeds)
- `tests/`: Pruebas unitarias y de integración
- `docs/`: Documentación y evidencia

## 📝 Licencia

MIT License - Ver archivo LICENSE