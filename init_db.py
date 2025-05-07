import os
import bcrypt
from sqlalchemy import create_engine
from models import Base, Puesto, Tarifa, Usuario, ConfiguracionParqueadero
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Crear la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "parqueadero.db")
engine = create_engine(f'sqlite:///{db_path}')

# Crear todas las tablas
Base.metadata.create_all(engine)

# Crear una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Verificar si ya existen registros en las tablas
def inicializar_base_datos():
    try:
        # Verificar si ya existen puestos
        puestos_count = db.query(Puesto).count()
        if puestos_count == 0:
            print("Inicializando los puestos de parqueo...")
            # Crear los 40 puestos de parqueo
            for i in range(1, 41):
                puesto = Puesto(id_puesto=i, disponible=True)
                db.add(puesto)
            
            db.commit()
            print(f"Se han creado 40 puestos de parqueo")
        else:
            print(f"Los puestos ya están inicializados, hay {puestos_count} puestos")
        
        # Verificar si ya existe una tarifa por defecto
        tarifa_count = db.query(Tarifa).count()
        if tarifa_count == 0:
            print("Inicializando la tarifa por defecto...")
            # Crear tarifa por defecto
            tarifa_default = Tarifa(
                id_tarifa=1,
                valor_por_hora=5000.0,  # 5000 pesos por hora
                fecha_inicio_vigencia=datetime.now()
            )
            db.add(tarifa_default)
            db.commit()
            print("Tarifa por defecto creada")
        else:
            print("La tarifa ya está inicializada")
        
        # Verificar si ya existe la configuración del parqueadero
        config_count = db.query(ConfiguracionParqueadero).count()
        if config_count == 0:
            print("Inicializando la configuración del parqueadero...")
            # Crear configuración inicial
            # Usar la hora actual del sistema en lugar de fijar 8:00 AM
            hora_actual = datetime.now()
            # Asegurar que la hora está dentro del horario permitido (6:00 - 21:00)
            if hora_actual.hour < 6:
                hora_actual = hora_actual.replace(hour=6, minute=0, second=0, microsecond=0)
            elif hora_actual.hour >= 21:
                hora_actual = hora_actual.replace(hour=20, minute=59, second=0, microsecond=0)
                
            config = ConfiguracionParqueadero(
                id=1,
                hora_actual=hora_actual,
                total_puestos=40
            )
            db.add(config)
            db.commit()
            print("Configuración del parqueadero creada")
        else:
            print("La configuración del parqueadero ya está inicializada")
        
        # Crear usuarios por defecto si no existen
        usuario_count = db.query(Usuario).count()
        if usuario_count == 0:
            print("Creando usuarios por defecto...")
            # Usuarios requeridos: Andres, Virginia, Juliana y Jovany con contraseña 2025
            usuarios = ["Andres", "Virginia", "Juliana", "Jovany"]
            password = "2025"
            
            for nombre in usuarios:
                # Generar hash de la contraseña
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                usuario = Usuario(
                    nombre_usuario=nombre,
                    password_hash=password_hash
                )
                db.add(usuario)
            
            db.commit()
            print(f"Se han creado {len(usuarios)} usuarios por defecto")
        else:
            print(f"Ya existen {usuario_count} usuarios en la base de datos")
            
        print("Base de datos inicializada correctamente")
    
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    inicializar_base_datos()
