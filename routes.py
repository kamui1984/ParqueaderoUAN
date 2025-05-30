from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, session
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import Session
from models import Puesto, Vehiculo, Tarifa, RegistroParqueo, ConfiguracionParqueadero, Usuario, get_db
from datetime import datetime, timedelta, date
import bcrypt
import math
from functools import wraps

# Crear un Blueprint para las rutas
routes = Blueprint('routes', __name__)

# Configurar autenticación básica
auth = HTTPBasicAuth()

# Verificar contraseña
@auth.verify_password
def verify_password(username, password):
    db = next(get_db())
    user = db.query(Usuario).filter_by(nombre_usuario=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return username
    return None

# Decorador para rutas protegidas con autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth.current_user():
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta para la página principal
@routes.route('/')
def index():
    return render_template('index.html')

# Ruta para el login
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_password(username, password):
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Credenciales inválidas. Intente nuevamente.', 'danger')
    
    return render_template('login.html')

# Ruta para el dashboard
@routes.route('/dashboard')
@auth.login_required
def dashboard():
    db = next(get_db())
    
    # Obtener la configuración actual del parqueadero
    config = db.query(ConfiguracionParqueadero).first()
    
    # Cantidad de puestos disponibles
    puestos_disponibles = db.query(Puesto).filter_by(disponible=True).count()
    
    # Porcentaje de disponibilidad
    porcentaje_disponibilidad = (puestos_disponibles / config.total_puestos) * 100
    
    # Ingresos totales (suma de total_pagado de todos los registros)
    ingresos_totales = db.query(RegistroParqueo).filter(RegistroParqueo.total_pagado != None).with_entities(
        func.sum(RegistroParqueo.total_pagado)
    ).scalar() or 0
    
    # Carros actualmente en el parqueadero
    carros_actuales = db.query(RegistroParqueo).filter(RegistroParqueo.hora_salida == None).all()
    
    # Tarifa actual
    tarifa_actual = db.query(Tarifa).filter(
        Tarifa.fecha_fin_vigencia == None
    ).first()
    
    return render_template(
        'dashboard.html', 
        config=config,
        puestos_disponibles=puestos_disponibles,
        porcentaje_disponibilidad=porcentaje_disponibilidad,
        ingresos_totales=ingresos_totales,
        carros_actuales=carros_actuales,
        tarifa_actual=tarifa_actual,
        hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    )

# Ruta para ver todos los puestos
@routes.route('/puestos')
@auth.login_required
def puestos():
    db = next(get_db())
    puestos = db.query(Puesto).order_by(Puesto.id_puesto).all()
    
    # Para cada puesto, obtener el registro de parqueo activo si existe
    puestos_info = []
    for puesto in puestos:
        registro = db.query(RegistroParqueo).filter(
            RegistroParqueo.id_puesto == puesto.id_puesto,
            RegistroParqueo.hora_salida == None
        ).first()
        
        info = {
            'puesto': puesto,
            'registro': registro,
            'vehiculo': registro.vehiculo if registro else None
        }
        puestos_info.append(info)
    
    return render_template('puestos.html', puestos_info=puestos_info)

# Ruta para ingresar un carro
@routes.route('/ingresar-carro', methods=['GET', 'POST'])
@auth.login_required
def ingresar_carro():
    db = next(get_db())
    
    # Obtener los puestos disponibles
    puestos_disponibles = db.query(Puesto).filter_by(disponible=True).order_by(Puesto.id_puesto).all()
    
    # Si no hay puestos disponibles, mostrar mensaje emergente
    if len(puestos_disponibles) == 0:
        flash('No hay puestos disponibles en el parqueadero', 'danger')
        return redirect(url_for('routes.dashboard'))
    
    # Obtener la tarifa vigente
    tarifa_vigente = db.query(Tarifa).filter(Tarifa.fecha_fin_vigencia == None).first()
    
    # Obtener la configuración del parqueadero para la hora actual
    config = db.query(ConfiguracionParqueadero).first()
    
    if request.method == 'POST':
        placa = request.form.get('placa').upper()
        id_puesto = int(request.form.get('id_puesto'))
        marca = request.form.get('marca', '')
        modelo = request.form.get('modelo', '')
        
        # Verificar si hay algún registro activo con la misma placa
        registro_existente = db.query(RegistroParqueo).join(Vehiculo).filter(
            Vehiculo.placa == placa,
            RegistroParqueo.hora_salida == None
        ).first()
        
        if registro_existente:
            flash(f'El vehículo con placa {placa} ya se encuentra en el parqueadero', 'danger')
            return redirect(url_for('routes.ingresar_carro'))
        
        # Verificar si el puesto está disponible
        puesto = db.query(Puesto).filter_by(id_puesto=id_puesto).first()
        if not puesto or not puesto.disponible:
            flash('El puesto seleccionado no está disponible', 'danger')
            return redirect(url_for('routes.ingresar_carro'))
        
        try:
            # Verificar si el vehículo ya existe
            vehiculo = db.query(Vehiculo).filter_by(placa=placa).first()
            if not vehiculo:
                # Crear un nuevo vehículo
                vehiculo = Vehiculo(placa=placa, marca=marca, modelo=modelo)
                db.add(vehiculo)
                db.flush()
            
            # Crear un nuevo registro de parqueo
            registro = RegistroParqueo(
                placa=placa,
                id_puesto=id_puesto,
                hora_entrada=config.hora_actual,
                valor_tarifa_aplicada=tarifa_vigente.valor_por_hora,
                id_tarifa=tarifa_vigente.id_tarifa
            )
            db.add(registro)
            
            # Actualizar el estado del puesto
            puesto.disponible = False
            
            db.commit()
            flash(f'Vehículo con placa {placa} ingresado exitosamente en el puesto {id_puesto}', 'success')
            return redirect(url_for('routes.dashboard'))
            
        except Exception as e:
            db.rollback()
            flash(f'Error al ingresar el vehículo: {str(e)}', 'danger')
            return redirect(url_for('routes.ingresar_carro'))
    
    return render_template('ingresar_carro.html', puestos_disponibles=puestos_disponibles, config=config, hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S'))

# Ruta para dar salida a un carro
@routes.route('/salida-carro', methods=['GET', 'POST'])
@auth.login_required
def salida_carro():
    db = next(get_db())
    
    # Obtener la configuración del parqueadero para la hora actual
    config = db.query(ConfiguracionParqueadero).first()
    
    # Obtener todos los registros activos (sin hora de salida)
    registros_activos = db.query(RegistroParqueo).filter(
        RegistroParqueo.hora_salida == None
    ).all()
    
    if request.method == 'POST':
        id_registro = request.form.get('id_registro')
        
        # Verificar si el registro existe
        registro = db.query(RegistroParqueo).filter_by(id_registro=id_registro).first()
        if not registro:
            flash('Registro de parqueo no encontrado', 'danger')
            return redirect(url_for('routes.salida_carro'))
        
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
            
            flash(f'Salida exitosa del vehículo con placa {registro.placa}. Total pagado: ${monto_pagar:.2f}', 'success')
            return redirect(url_for('routes.dashboard'))
            
        except Exception as e:
            db.rollback()
            flash(f'Error al procesar la salida: {str(e)}', 'danger')
            return redirect(url_for('routes.salida_carro'))
    
    return render_template('salida_carro.html', registros_activos=registros_activos, config=config, hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S'))

# Ruta para avanzar el reloj
@routes.route('/avanzar-reloj', methods=['GET', 'POST'])
@auth.login_required
def avanzar_reloj():
    db = next(get_db())
    
    # Obtener la configuración actual
    config = db.query(ConfiguracionParqueadero).first()
    
    if request.method == 'POST':
        # Verificar si se solicitó sincronizar con la hora del sistema
        usar_hora_sistema = request.form.get('usar_hora_sistema')
        
        if usar_hora_sistema:
            # Usar la hora actual del sistema
            hora_sistema = datetime.now()
            
            # Verificar que la hora esté dentro del horario de operación (6:00 - 21:00)
            if hora_sistema.hour < 6:
                nueva_hora = hora_sistema.replace(hour=6, minute=0, second=0, microsecond=0)
                flash('La hora del sistema está fuera del horario de operación. Se ajustó a las 6:00 AM.', 'warning')
            elif hora_sistema.hour > 21:
                nueva_hora = hora_sistema.replace(hour=21, minute=0, second=0, microsecond=0)
                flash('La hora del sistema está fuera del horario de operación. Se ajustó a las 9:00 PM.', 'warning')
            else:
                nueva_hora = hora_sistema
                
            # Actualizar la hora
            config.hora_actual = nueva_hora
            db.commit()
            
            flash(f'Reloj sincronizado exitosamente con la hora del sistema: {nueva_hora.strftime("%Y-%m-%d %H:%M:%S")}', 'success')
            return redirect(url_for('routes.dashboard'))
        else:
            # Modo tradicional - avanzar manualmente
            minutos = int(request.form.get('minutos', 0))
            horas = int(request.form.get('horas', 0))
            
            if minutos < 0 or horas < 0:
                flash('El tiempo a avanzar no puede ser negativo', 'danger')
                return redirect(url_for('routes.avanzar_reloj'))
            
            # Calcular nueva hora
            nueva_hora = config.hora_actual + timedelta(hours=horas, minutes=minutos)
            
            # Verificar que la nueva hora esté dentro del horario de operación (6:00 - 21:00)
            if nueva_hora.hour < 6 or nueva_hora.hour > 21 or (nueva_hora.hour == 21 and nueva_hora.minute > 0):
                flash('La nueva hora debe estar dentro del horario de operación (6:00 - 21:00)', 'danger')
                return redirect(url_for('routes.avanzar_reloj'))
            
            # Actualizar la hora
            config.hora_actual = nueva_hora
            db.commit()
            
            flash(f'Reloj avanzado exitosamente. Nueva hora: {nueva_hora.strftime("%Y-%m-%d %H:%M:%S")}', 'success')
            return redirect(url_for('routes.dashboard'))
    
    return render_template('avanzar_reloj.html', config=config, hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S'))

# Ruta para cambiar la tarifa
@routes.route('/cambiar-tarifa', methods=['GET', 'POST'])
@auth.login_required
def cambiar_tarifa():
    db = next(get_db())
    
    # Obtener la tarifa actual
    tarifa_actual = db.query(Tarifa).filter(Tarifa.fecha_fin_vigencia == None).first()
    
    # Obtener la configuración del parqueadero para la hora actual
    config = db.query(ConfiguracionParqueadero).first()
    
    # Obtener historial de tarifas
    historial_tarifas = db.query(Tarifa).order_by(Tarifa.fecha_inicio_vigencia.desc()).all()
    
    if request.method == 'POST':
        nuevo_valor = float(request.form.get('valor_por_hora'))
        
        if nuevo_valor <= 0:
            flash('El valor de la tarifa debe ser mayor que cero', 'danger')
            return redirect(url_for('routes.cambiar_tarifa'))
        
        try:
            # Finalizar la vigencia de la tarifa actual
            tarifa_actual.fecha_fin_vigencia = config.hora_actual
            
            # Crear nueva tarifa
            nueva_tarifa = Tarifa(
                valor_por_hora=nuevo_valor,
                fecha_inicio_vigencia=config.hora_actual
            )
            db.add(nueva_tarifa)
            db.commit()
            
            flash(f'Tarifa actualizada exitosamente a ${nuevo_valor:.2f} por hora', 'success')
            return redirect(url_for('routes.dashboard'))
            
        except Exception as e:
            db.rollback()
            flash(f'Error al actualizar la tarifa: {str(e)}', 'danger')
            return redirect(url_for('routes.cambiar_tarifa'))
    
    return render_template('cambiar_tarifa.html', tarifa_actual=tarifa_actual, historial_tarifas=historial_tarifas, config=config, hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S'))

# Importar func para las operaciones de suma
from sqlalchemy import func, desc, and_, or_

# Ruta para mostrar el histórico de ingresos
@routes.route('/historico-ingresos')
@auth.login_required
def historico_ingresos():
    db = next(get_db())
    
    # Obtener la configuración del parqueadero
    config = db.query(ConfiguracionParqueadero).first()
    
    # Obtener registros completados (con hora de salida y pago)
    registros_completados = db.query(RegistroParqueo).filter(
        RegistroParqueo.hora_salida != None,
        RegistroParqueo.total_pagado != None
    ).order_by(RegistroParqueo.hora_salida.desc()).all()
    
    # Calcular ingresos totales
    ingresos_totales = db.query(func.sum(RegistroParqueo.total_pagado)).scalar() or 0
    
    # Agrupar por día para gráfico (opcional)
    # Esta implementación básica muestra los últimos registros
    # Para un análisis más detallado se podría agregar agrupación por día/mes
    
    return render_template(
        'historico_ingresos.html',
        registros=registros_completados,
        ingresos_totales=ingresos_totales,
        config=config,
        hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    )

# Ruta para buscar vehículos por placa
@routes.route('/buscar-carro', methods=['GET', 'POST'])
@auth.login_required
def buscar_carro():
    db = next(get_db())
    config = db.query(ConfiguracionParqueadero).first()
    
    placa_buscada = None
    resultado = None
    
    if request.method == 'POST':
        placa_buscada = request.form.get('placa').upper()
        
        # Buscar el vehículo
        vehiculo = db.query(Vehiculo).filter_by(placa=placa_buscada).first()
        
        if vehiculo:
            # Buscar si tiene un registro activo (está en el parqueadero)
            registro_activo = db.query(RegistroParqueo).filter(
                RegistroParqueo.placa == placa_buscada,
                RegistroParqueo.hora_salida == None
            ).first()
            
            resultado = {
                'vehiculo': vehiculo,
                'registro': registro_activo
            }
        else:
            # Mostrar mensaje de que la placa no se encuentra registrada
            flash(f'La placa {placa_buscada} no se encuentra registrada en el parqueadero', 'warning')
    
    return render_template(
        'buscar_carro.html',
        placa_buscada=placa_buscada,
        resultado=resultado,
        config=config,
        hora_actual=config.hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    )

# Ruta para mostrar el resumen diario
@routes.route('/resumen-diario', methods=['GET', 'POST'])
@auth.login_required
def resumen_diario():
    db = next(get_db())
    config = db.query(ConfiguracionParqueadero).first()
    
    # Fecha actual del sistema (la del parqueadero)
    fecha_actual = config.hora_actual.date()
    fecha_seleccionada = fecha_actual
    
    if request.method == 'POST' and request.form.get('fecha'):
        fecha_seleccionada = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d').date()
    
    # Obtener inicio y fin del día seleccionado
    inicio_dia = datetime.combine(fecha_seleccionada, datetime.min.time())
    fin_dia = datetime.combine(fecha_seleccionada, datetime.max.time())
    
    # Vehículos ingresados ese día
    vehiculos_ingresados = db.query(RegistroParqueo).join(Vehiculo).filter(
        RegistroParqueo.hora_entrada >= inicio_dia,
        RegistroParqueo.hora_entrada <= fin_dia
    ).order_by(RegistroParqueo.hora_entrada).all()
    
    # Vehículos que salieron ese día
    vehiculos_salidos = db.query(RegistroParqueo).join(Vehiculo).filter(
        RegistroParqueo.hora_salida >= inicio_dia,
        RegistroParqueo.hora_salida <= fin_dia
    ).order_by(RegistroParqueo.hora_salida).all()
    
    # Contadores
    total_ingresados = len(vehiculos_ingresados)
    total_salidos = len(vehiculos_salidos)
    
    # Ingresos del día
    ingresos_totales = db.query(func.sum(RegistroParqueo.total_pagado)).filter(
        RegistroParqueo.hora_salida >= inicio_dia,
        RegistroParqueo.hora_salida <= fin_dia
    ).scalar() or 0
    
    # Calcular porcentaje máximo de ocupación del día
    total_puestos = config.total_puestos
    
    # Máxima ocupación durante el día (calculando por cada hora)
    max_ocupacion = 0
    for hora in range(6, 22):  # Horario de 6am a 9pm
        hora_punto = datetime.combine(fecha_seleccionada, datetime.min.time().replace(hour=hora))
        
        # Contar carros presentes a esa hora (entraron antes y salieron después o no han salido)
        ocupacion = db.query(RegistroParqueo).filter(
            RegistroParqueo.hora_entrada <= hora_punto,
            or_(
                RegistroParqueo.hora_salida > hora_punto,
                RegistroParqueo.hora_salida == None
            )
        ).count()
        
        if ocupacion > max_ocupacion:
            max_ocupacion = ocupacion
    
    porcentaje_ocupacion = (max_ocupacion / total_puestos) * 100 if total_puestos > 0 else 0
    
    return render_template(
        'resumen_diario.html',
        fecha_actual=fecha_actual.strftime('%d/%m/%Y'),
        fecha_seleccionada=fecha_seleccionada.strftime('%Y-%m-%d'),
        vehiculos_ingresados=vehiculos_ingresados,
        vehiculos_salidos=vehiculos_salidos,
        total_ingresados=total_ingresados,
        total_salidos=total_salidos,
        ingresos_totales=ingresos_totales,
        porcentaje_ocupacion=porcentaje_ocupacion,
        config=config
    )
