# Script de configuración para el proyecto ParqueaderoUAN
# Este script creará la estructura de directorios, configurará el entorno virtual
# e instalará las dependencias necesarias

# Verificar si se está ejecutando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Este script debe ejecutarse como administrador para evitar problemas de permisos." -ForegroundColor Red
    Write-Host "Por favor, reinicie PowerShell como administrador y ejecute el script nuevamente." -ForegroundColor Red
    exit
}

# Crear directorios del proyecto
$projectRoot = "C:\ParqueaderoUAN"
$directories = @(
    "$projectRoot\templates",
    "$projectRoot\static",
    "$projectRoot\static\css",
    "$projectRoot\static\js",
    "$projectRoot\static\img"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        try {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "Directorio creado: $dir" -ForegroundColor Green
        }
        catch {
            Write-Host "Error al crear directorio $dir`: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "El directorio $dir ya existe" -ForegroundColor Yellow
    }
}

# Configurar entorno virtual
try {
    $venvPath = "$projectRoot\venv"
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creando entorno virtual..." -ForegroundColor Cyan
        python -m venv $venvPath
        
        if (-not (Test-Path $venvPath)) {
            throw "Error al crear el entorno virtual"
        }
        
        Write-Host "Entorno virtual creado correctamente" -ForegroundColor Green
    }
    else {
        Write-Host "El entorno virtual ya existe" -ForegroundColor Yellow
    }
    
    # Activar entorno virtual e instalar dependencias
    Write-Host "Activando entorno virtual e instalando dependencias..." -ForegroundColor Cyan
    & "$venvPath\Scripts\Activate.ps1"
    
    # Instalar dependencias desde requirements.txt
    if (Test-Path "$projectRoot\requirements.txt") {
        pip install -r "$projectRoot\requirements.txt"
        Write-Host "Dependencias instaladas correctamente desde requirements.txt" -ForegroundColor Green
    } else {
        Write-Host "No se encontró el archivo requirements.txt, instalando dependencias básicas..." -ForegroundColor Yellow
        pip install flask fastapi uvicorn python-multipart sqlalchemy flask-login flask-wtf python-dotenv flask-bootstrap Flask-HTTPAuth bcrypt
        Write-Host "Dependencias básicas instaladas correctamente" -ForegroundColor Green
    }
    
    # Inicializar la base de datos
    Write-Host "Inicializando la base de datos..." -ForegroundColor Cyan
    python "$projectRoot\init_db.py"
    
    Write-Host "Configuración completada exitosamente" -ForegroundColor Green
    Write-Host "Para iniciar la aplicación, active el entorno virtual con: $venvPath\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "Luego ejecute: python $projectRoot\app.py" -ForegroundColor Cyan
}
catch {
    Write-Host "Error durante la configuración: $_" -ForegroundColor Red
}
