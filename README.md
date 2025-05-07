# Sistema de Administración de Parqueadero UAN

Este proyecto implementa un sistema de administración para el parqueadero de la Universidad Antonio Nariño, permitiendo gestionar la entrada y salida de vehículos, calcular tarifas y generar estadísticas.

## Características

- Gestión de 40 puestos de parqueadero numerados
- Registro de entrada y salida de vehículos
- Cálculo automático de tarifas por hora o fracción
- Visualización de puestos disponibles y ocupados
- Informe de ingresos totales
- Control de tarifa por hora
- Avance de reloj para simulaciones
- API RESTful documentada con FastAPI
- Autenticación básica para proteger las rutas

## Requisitos

- Windows 10
- Python 3.8 o superior
- SQLite

## Estructura del Proyecto

```
C:\ParqueaderoUAN\
│
├── app.py              # Aplicación Flask principal
├── api.py              # API con FastAPI
├── init_db.py          # Inicialización de la base de datos
├── models.py           # Modelos de datos
├── routes.py           # Rutas de la aplicación
├── setup.ps1           # Script de configuración
├── parqueadero.db      # Base de datos SQLite
│
├── templates/          # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── puestos.html
│   ├── ingresar_carro.html
│   ├── salida_carro.html
│   ├── avanzar_reloj.html
│   └── cambiar_tarifa.html
│
└── static/             # Archivos estáticos
    ├── css/
    │   └── styles.css
    ├── js/
    │   └── main.js
    └── img/
```

## Instalación

1. Clonar o descargar este repositorio a `C:\ParqueaderoUAN\`
2. Abrir PowerShell como administrador
3. Ejecutar el script de configuración:

```powershell
cd C:\ParqueaderoUAN
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

4. Activar el entorno virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

5. Iniciar la aplicación:

```powershell
python app.py
```

## Uso

1. Abrir un navegador web y dirigirse a `http://localhost:5000`
2. Iniciar sesión con alguno de los siguientes usuarios (todos con contraseña `2025`):
   - Andres
   - Virginia
   - Juliana
   - Jovany
3. Utilizar las funciones del menú para administrar el parqueadero

## API RESTful

La API está disponible en `http://localhost:8000` y su documentación en `http://localhost:8000/docs`

Para acceder a la API, utilice la autenticación básica con los mismos usuarios y contraseña que la interfaz web.

## Desarrollado Por

Universidad Antonio Nariño - 2025
