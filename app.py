from flask import Flask, redirect, url_for
from flask_bootstrap import Bootstrap
from routes import routes
import os
import sys
import subprocess
from models import get_db, ConfiguracionParqueadero
import atexit
import signal

# Determinar si estamos ejecutando como un ejecutable de PyInstaller
def is_pyinstaller():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Obtener el directorio base (funciona tanto en desarrollo como empaquetado)
def get_base_dir():
    if is_pyinstaller():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

# Configurar Flask para que funcione con PyInstaller
if is_pyinstaller():
    template_folder = os.path.join(get_base_dir(), 'templates')
    static_folder = os.path.join(get_base_dir(), 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

Bootstrap(app)

# Configuración de la app
app.config['SECRET_KEY'] = 'clavesecretaparqueaderouan2025'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# Registrar blueprint de rutas
app.register_blueprint(routes)

@app.route('/api-docs')
def api_docs():
    return redirect('http://localhost:8000/docs')

# Variable global para el proceso de FastAPI
api_process = None

def iniciar_fastapi():
    global api_process
    # Iniciar el servidor FastAPI en un subproceso
    if is_pyinstaller():
        # Si es un ejecutable, usar la ruta del ejecutable
        api_script = os.path.join(get_base_dir(), 'api.py')
    else:
        # En desarrollo, usar la ruta relativa
        api_script = 'api.py'
    
    api_process = subprocess.Popen(
        [sys.executable, api_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Registrar función para cerrar el proceso al salir
    atexit.register(detener_fastapi)
    
    # Manejar señales para cierre limpio
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, handle_exit)

def detener_fastapi():
    global api_process
    if api_process:
        print("Deteniendo el servidor FastAPI...")
        api_process.terminate()
        api_process = None

def handle_exit(signum, frame):
    detener_fastapi()
    sys.exit(0)

if __name__ == '__main__':
    iniciar_fastapi()
    app.run(debug=True, port=5000)
