from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import bcrypt
import math
import secrets
import uvicorn
import os
import sys

# Determinar si estamos ejecutando como un ejecutable de PyInstaller
def is_pyinstaller():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Obtener el directorio base (funciona tanto en desarrollo como empaquetado)
def get_base_dir():
    if is_pyinstaller():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))
    
# Cambiar el directorio de trabajo si es necesario
if is_pyinstaller():
    os.chdir(get_base_dir())

from models import get_db, Puesto, Vehiculo, Tarifa, RegistroParqueo, ConfiguracionParqueadero, Usuario

# Crear la app FastAPI
app = FastAPI(
    title="API Parqueadero UAN",
    description="API para administrar el parqueadero de la Universidad Antonio Nariño",
    version="1.0.0"
)

# Configurar la autenticación básica
security = HTTPBasic()

# Función para verificar credenciales
def get_current_username(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(nombre_usuario=credentials.username).first()
    if not user or not bcrypt.checkpw(credentials.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Modelos Pydantic para la API
class VehiculoBase(BaseModel):
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoResponse(VehiculoBase):
    class Config:
        orm_mode = True

class PuestoBase(BaseModel):
    id_puesto: int
    disponible: bool

class PuestoResponse(PuestoBase):
    class Config:
        orm_mode = True

class RegistroParqueoBase(BaseModel):
    placa: str
    id_puesto: int

class RegistroParqueoCreate(RegistroParqueoBase):
    pass

class RegistroParqueoResponse(BaseModel):
    id_registro: int
    placa: str
    id_puesto: int
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None
    valor_tarifa_aplicada: float
    total_pagado: Optional[float] = None
    
    class Config:
        orm_mode = True

class TarifaBase(BaseModel):
    valor_por_hora: float

class TarifaCreate(TarifaBase):
    pass

class TarifaResponse(TarifaBase):
    id_tarifa: int
    fecha_inicio_vigencia: datetime
    fecha_fin_vigencia: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class ConfiguracionBase(BaseModel):
    hora_actual: datetime
    total_puestos: int

class ConfiguracionResponse(ConfiguracionBase):
    id: int
    
    class Config:
        orm_mode = True

class AvanzarRelojRequest(BaseModel):
    minutos: int = 0
    horas: int = 0

class EstadisticasResponse(BaseModel):
    puestos_disponibles: int
    porcentaje_disponibilidad: float
    ingresos_totales: float

# Rutas de la API

@app.get("/", tags=["Información"])
def read_root():
    return {"mensaje": "API Parqueadero UAN", "version": "1.0.0"}

@app.get("/puestos/", response_model=List[PuestoResponse], tags=["Puestos"])
def listar_puestos(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Listar todos los puestos del parqueadero.
    """
    return db.query(Puesto).order_by(Puesto.id_puesto).all()

@app.get("/puestos/disponibles/", response_model=List[PuestoResponse], tags=["Puestos"])
def listar_puestos_disponibles(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Listar todos los puestos disponibles del parqueadero.
    """
    return db.query(Puesto).filter_by(disponible=True).order_by(Puesto.id_puesto).all()

@app.get("/puestos/{id_puesto}", response_model=PuestoResponse, tags=["Puestos"])
def obtener_puesto(id_puesto: int, username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Obtener información de un puesto específico.
    """
    puesto = db.query(Puesto).filter_by(id_puesto=id_puesto).first()
    if puesto is None:
        raise HTTPException(status_code=404, detail="Puesto no encontrado")
    return puesto

@app.get("/vehiculos/", response_model=List[VehiculoResponse], tags=["Vehículos"])
def listar_vehiculos(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Listar todos los vehículos registrados.
    """
    return db.query(Vehiculo).all()

@app.get("/vehiculos/{placa}", response_model=VehiculoResponse, tags=["Vehículos"])
def obtener_vehiculo(placa: str, username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Obtener información de un vehículo específico.
    """
    vehiculo = db.query(Vehiculo).filter_by(placa=placa).first()
    if vehiculo is None:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@app.post("/ingresar-vehiculo/", response_model=RegistroParqueoResponse, tags=["Operaciones"])
def ingresar_vehiculo(
    vehiculo_data: VehiculoCreate, 
    id_puesto: int,
    username: str = Depends(get_current_username), 
    db: Session = Depends(get_db)
):
    """
    Ingresar un vehículo al parqueadero.
    """
    # Verificar si hay algún registro activo con la misma placa
    registro_existente = db.query(RegistroParqueo).join(Vehiculo).filter(
        Vehiculo.placa == vehiculo_data.placa,
        RegistroParqueo.hora_salida == None
    ).first()
    
    if registro_existente:
        raise HTTPException(
            status_code=400,
            detail=f"El vehículo con placa {vehiculo_data.placa} ya se encuentra en el parqueadero"
        )
    
    # Verificar si el puesto está disponible
    puesto = db.query(Puesto).filter_by(id_puesto=id_puesto).first()
    if not puesto:
        raise HTTPException(status_code=404, detail="Puesto no encontrado")
    
    if not puesto.disponible:
        raise HTTPException(status_code=400, detail="El puesto seleccionado no está disponible")
    
    # Obtener la configuración del parqueadero para la hora actual
    config = db.query(ConfiguracionParqueadero).first()
    
    # Obtener la tarifa vigente
    tarifa_vigente = db.query(Tarifa).filter(Tarifa.fecha_fin_vigencia == None).first()
    
    try:
        # Verificar si el vehículo ya existe
        vehiculo = db.query(Vehiculo).filter_by(placa=vehiculo_data.placa).first()
        if not vehiculo:
            # Crear un nuevo vehículo
            vehiculo = Vehiculo(
                placa=vehiculo_data.placa,
                marca=vehiculo_data.marca,
                modelo=vehiculo_data.modelo
            )
            db.add(vehiculo)
            db.flush()
        
        # Crear un nuevo registro de parqueo
        registro = RegistroParqueo(
            placa=vehiculo_data.placa,
            id_puesto=id_puesto,
            hora_entrada=config.hora_actual,
            valor_tarifa_aplicada=tarifa_vigente.valor_por_hora,
            id_tarifa=tarifa_vigente.id_tarifa
        )
        db.add(registro)
        
        # Actualizar el estado del puesto
        puesto.disponible = False
        
        db.commit()
        
        # Refrescar el objeto para obtener el id generado
        db.refresh(registro)
        
        return registro
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al ingresar el vehículo: {str(e)}")

@app.post("/salida-vehiculo/{id_registro}", response_model=RegistroParqueoResponse, tags=["Operaciones"])
def salida_vehiculo(
    id_registro: int,
    username: str = Depends(get_current_username), 
    db: Session = Depends(get_db)
):
    """
    Dar salida a un vehículo del parqueadero.
    """
    # Verificar si el registro existe
    registro = db.query(RegistroParqueo).filter_by(id_registro=id_registro).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de parqueo no encontrado")
    
    if registro.hora_salida is not None:
        raise HTTPException(status_code=400, detail="Este vehículo ya ha salido del parqueadero")
    
    # Obtener la configuración del parqueadero para la hora actual
    config = db.query(ConfiguracionParqueadero).first()
    
    try:
        # Calcular el tiempo de estancia en horas
        tiempo_estancia = (config.hora_actual - registro.hora_entrada).total_seconds() / 3600
        
        # Redondear hacia arriba para fracciones de hora
        horas_cobrar = math.ceil(tiempo_estancia)
        
        # Calcular el monto a pagar
        monto_pagar = horas_cobrar * registro.valor_tarifa_aplicada
        
        # Actualizar el registro
        registro.hora_salida = config.hora_actual
        registro.total_pagado = monto_pagar
        
        # Liberar el puesto
        puesto = db.query(Puesto).filter_by(id_puesto=registro.id_puesto).first()
        puesto.disponible = True
        
        db.commit()
        
        # Refrescar el objeto para obtener los cambios
        db.refresh(registro)
        
        return registro
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la salida: {str(e)}")

@app.get("/registros/", response_model=List[RegistroParqueoResponse], tags=["Registros"])
def listar_registros(
    activos: bool = False,
    username: str = Depends(get_current_username), 
    db: Session = Depends(get_db)
):
    """
    Listar todos los registros de parqueo. Si activos=true, solo muestra los vehículos actualmente en el parqueadero.
    """
    query = db.query(RegistroParqueo)
    
    if activos:
        query = query.filter(RegistroParqueo.hora_salida == None)
    
    return query.all()

@app.get("/estadisticas/", response_model=EstadisticasResponse, tags=["Estadísticas"])
def obtener_estadisticas(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Obtener estadísticas del parqueadero.
    """
    from sqlalchemy import func
    
    # Obtener la configuración actual del parqueadero
    config = db.query(ConfiguracionParqueadero).first()
    
    # Cantidad de puestos disponibles
    puestos_disponibles = db.query(Puesto).filter_by(disponible=True).count()
    
    # Porcentaje de disponibilidad
    porcentaje_disponibilidad = (puestos_disponibles / config.total_puestos) * 100
    
    # Ingresos totales (suma de total_pagado de todos los registros)
    ingresos_totales = db.query(func.sum(RegistroParqueo.total_pagado)).scalar() or 0
    
    return {
        "puestos_disponibles": puestos_disponibles,
        "porcentaje_disponibilidad": porcentaje_disponibilidad,
        "ingresos_totales": float(ingresos_totales)
    }

@app.get("/configuracion/", response_model=ConfiguracionResponse, tags=["Configuración"])
def obtener_configuracion(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Obtener la configuración actual del parqueadero.
    """
    config = db.query(ConfiguracionParqueadero).first()
    return config

@app.post("/avanzar-reloj/", response_model=ConfiguracionResponse, tags=["Configuración"])
def avanzar_reloj(
    datos: AvanzarRelojRequest,
    username: str = Depends(get_current_username), 
    db: Session = Depends(get_db)
):
    """
    Avanzar el reloj del parqueadero.
    """
    # Obtener la configuración actual
    config = db.query(ConfiguracionParqueadero).first()
    
    if datos.minutos < 0 or datos.horas < 0:
        raise HTTPException(status_code=400, detail="El tiempo a avanzar no puede ser negativo")
    
    # Calcular nueva hora
    nueva_hora = config.hora_actual + timedelta(hours=datos.horas, minutes=datos.minutos)
    
    # Verificar que la nueva hora esté dentro del horario de operación (6:00 - 21:00)
    if nueva_hora.hour < 6 or nueva_hora.hour > 21 or (nueva_hora.hour == 21 and nueva_hora.minute > 0):
        raise HTTPException(
            status_code=400, 
            detail="La nueva hora debe estar dentro del horario de operación (6:00 - 21:00)"
        )
    
    # Actualizar la hora
    config.hora_actual = nueva_hora
    db.commit()
    
    # Refrescar el objeto para obtener los cambios
    db.refresh(config)
    
    return config

@app.get("/tarifas/", response_model=List[TarifaResponse], tags=["Tarifas"])
def listar_tarifas(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Listar todas las tarifas históricas.
    """
    return db.query(Tarifa).order_by(Tarifa.fecha_inicio_vigencia.desc()).all()

@app.get("/tarifas/actual/", response_model=TarifaResponse, tags=["Tarifas"])
def obtener_tarifa_actual(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Obtener la tarifa actual vigente.
    """
    tarifa = db.query(Tarifa).filter(Tarifa.fecha_fin_vigencia == None).first()
    if tarifa is None:
        raise HTTPException(status_code=404, detail="No hay tarifa vigente")
    return tarifa

@app.post("/tarifas/", response_model=TarifaResponse, tags=["Tarifas"])
def crear_tarifa(
    tarifa_data: TarifaCreate,
    username: str = Depends(get_current_username), 
    db: Session = Depends(get_db)
):
    """
    Crear una nueva tarifa.
    """
    if tarifa_data.valor_por_hora <= 0:
        raise HTTPException(status_code=400, detail="El valor de la tarifa debe ser mayor que cero")
    
    # Obtener la configuración del parqueadero para la hora actual
    config = db.query(ConfiguracionParqueadero).first()
    
    # Obtener la tarifa actual
    tarifa_actual = db.query(Tarifa).filter(Tarifa.fecha_fin_vigencia == None).first()
    
    try:
        if tarifa_actual:
            # Finalizar la vigencia de la tarifa actual
            tarifa_actual.fecha_fin_vigencia = config.hora_actual
        
        # Crear nueva tarifa
        nueva_tarifa = Tarifa(
            valor_por_hora=tarifa_data.valor_por_hora,
            fecha_inicio_vigencia=config.hora_actual
        )
        db.add(nueva_tarifa)
        db.commit()
        
        # Refrescar el objeto para obtener el id generado
        db.refresh(nueva_tarifa)
        
        return nueva_tarifa
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la tarifa: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
