from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, CheckConstraint, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, time
import os

# Crear la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "parqueadero.db")
engine = create_engine(f'sqlite:///{db_path}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Modelo para la tabla de Puesto
class Puesto(Base):
    __tablename__ = "puesto"
    
    id_puesto = Column(Integer, primary_key=True)
    disponible = Column(Boolean, default=True)
    
    # Relación con registros de parqueo
    registros = relationship("RegistroParqueo", back_populates="puesto")
    
    def __repr__(self):
        return f"<Puesto(id_puesto={self.id_puesto}, disponible={self.disponible})>"

# Modelo para la tabla de Vehículo
class Vehiculo(Base):
    __tablename__ = "vehiculo"
    
    placa = Column(String(10), primary_key=True)
    marca = Column(String(50), nullable=True)
    modelo = Column(String(50), nullable=True)
    
    # Relación con registros de parqueo
    registros = relationship("RegistroParqueo", back_populates="vehiculo")
    
    def __repr__(self):
        return f"<Vehiculo(placa={self.placa}, marca={self.marca}, modelo={self.modelo})>"

# Modelo para la tabla de Tarifa
class Tarifa(Base):
    __tablename__ = "tarifa"
    
    id_tarifa = Column(Integer, primary_key=True, autoincrement=True)
    valor_por_hora = Column(Float, nullable=False)
    fecha_inicio_vigencia = Column(DateTime, nullable=False, default=datetime.now)
    fecha_fin_vigencia = Column(DateTime, nullable=True)
    
    # Relación con registros de parqueo
    registros = relationship("RegistroParqueo", back_populates="tarifa")
    
    def __repr__(self):
        return f"<Tarifa(id_tarifa={self.id_tarifa}, valor_por_hora={self.valor_por_hora})>"

# Modelo para la tabla de RegistroParqueo
class RegistroParqueo(Base):
    __tablename__ = "registro_parqueo"
    
    id_registro = Column(Integer, primary_key=True, autoincrement=True)
    placa = Column(String(10), ForeignKey("vehiculo.placa"), nullable=False)
    id_puesto = Column(Integer, ForeignKey("puesto.id_puesto"), nullable=False)
    hora_entrada = Column(DateTime, nullable=False)
    hora_salida = Column(DateTime, nullable=True)
    valor_tarifa_aplicada = Column(Float, nullable=False)
    total_pagado = Column(Float, nullable=True)
    id_tarifa = Column(Integer, ForeignKey("tarifa.id_tarifa"), nullable=False)
    
    # Relaciones
    puesto = relationship("Puesto", back_populates="registros")
    vehiculo = relationship("Vehiculo", back_populates="registros")
    tarifa = relationship("Tarifa", back_populates="registros")
    
    # Restricción para horarios de parqueo
    __table_args__ = (
        CheckConstraint('hora_entrada <= hora_salida OR hora_salida IS NULL', name='ck_horarios_parqueo'),
        CheckConstraint('time(hora_entrada) >= time("06:00:00") AND time(hora_entrada) <= time("21:00:00")', name='ck_hora_entrada'),
    )
    
    def __repr__(self):
        return f"<RegistroParqueo(id_registro={self.id_registro}, placa={self.placa}, hora_entrada={self.hora_entrada})>"

# Modelo para la configuración del parqueadero
class ConfiguracionParqueadero(Base):
    __tablename__ = "configuracion_parqueadero"
    
    id = Column(Integer, primary_key=True)
    hora_actual = Column(DateTime, nullable=False, default=datetime.now)
    total_puestos = Column(Integer, nullable=False, default=40)
    
    def __repr__(self):
        return f"<ConfiguracionParqueadero(id={self.id}, hora_actual={self.hora_actual}, total_puestos={self.total_puestos})>"

# Modelo para los usuarios de la aplicación
class Usuario(Base):
    __tablename__ = "usuario"
    
    id = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre_usuario={self.nombre_usuario})>"

# Función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
