from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Sucursal, Repartidor, Paquete, Transporte
from datetime import datetime

app = Flask(__name__)

# Configurar la base de datos
app.config.from_object('config')

# Inicializar sqlAlchemy
db.init_app(app)

# FUNCIONALIDAD #1: Acceso del despachante a la aplicación
@app.route('/', methods=['GET', 'POST'])
def accesoDespachante():
    if request.method == 'POST':
        idSucursalSeleccionada = request.form.get('sucursal')
        if idSucursalSeleccionada:
            return redirect(url_for('panelDespachante', idSucursal=idSucursalSeleccionada))
        
    sucursales = Sucursal.query.order_by(Sucursal.numero).all()
    print(f"Numero de sucursales: {len(sucursales)}")
    return render_template('despachantes.html', sucursales=sucursales)

@app.route('/sucursal/<int:idSucursal>')
def panelDespachante(idSucursal):
    sucursal = Sucursal.query.get_or_404(idSucursal)
    return render_template('panel_despachante.html', sucursal=sucursal)

# FUNCIONALIDAD #2: Registrar la recepción de un paquete 
def generarNumeroEnvio():
    ultimoPaquete = Paquete.query.order_by(Paquete.numeroenvio.desc()).first()
    if ultimoPaquete:
        print(ultimoPaquete.numeroenvio)
        ultimoNumero = ultimoPaquete.numeroenvio
        nuevoNumero = ultimoNumero + 20
    else:
        nuevoNumero = 1000  
    return nuevoNumero

@app.route('/registrar_paquete/<int:idSucursal>', methods=['GET', 'POST'])
def registrarPaquete(idSucursal):
    sucursal = Sucursal.query.get_or_404(idSucursal)    
    if request.method == 'POST':
        try:
            nuevoPaquete = Paquete(
                numeroenvio=generarNumeroEnvio(),
                peso=float(request.form['peso']),
                nomdestinatario=request.form['nomdestinatario'], 
                dirdestinatario=request.form['dirdestinatario'],  
                idsucursal=idSucursal,
                entregado=False
            )
            db.session.add(nuevoPaquete)
            db.session.commit()
            flash(f'Paquete registrado en la sucursal {idSucursal}', 'success')
            return redirect(url_for('panelDespachante', idSucursal=idSucursal))
        except KeyError as e:
            db.session.rollback()
            flash(f'Error: Campo faltante en el formulario - {str(e)}', 'error')
        except ValueError as e:
            db.session.rollback()
            flash(f'Error: El valor no es valido - {str(e)}', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el paquete: {str(e)}', 'error')
    
    return render_template('registrar_paquete.html', sucursal=sucursal)

# FUNCIONALIDAD #3: Registrar salida de transporte 
def generarNumeroTransporte():
    ultimoTransporte = Transporte.query.order_by(Transporte.numerotransporte.desc()).first()
    if ultimoTransporte:
        print(ultimoTransporte.numerotransporte)
        ultimoNumero = ultimoTransporte.numerotransporte
        nuevoNumero = ultimoNumero + 1
        print(f"el ultimo numero fue: {ultimoNumero} y el nuevo: {nuevoNumero}")
    else:
        nuevoNumero = 1000  
    return nuevoNumero

@app.route('/registrar_salida/<int:idSucursal>', methods=['GET', 'POST'])
def registrarSalida(idSucursal):
    sucursal = Sucursal.query.get_or_404(idSucursal)
    sucursalActual = str(sucursal).split()
    sucursalActual = sucursalActual[-1].replace(">", "")
    print(f" la sucursal actual es {sucursalActual}")
    if request.method == 'POST':
        idSucursal = request.form.get('sucursal_destino')
        print(f" la sucursal destino es {idSucursal}")
        paquetesSeleccionados = request.form.getlist('paquetes')
        if idSucursal and paquetesSeleccionados:
            try:
                transporte = Transporte(
                    numerotransporte=generarNumeroTransporte(),
                    fechahorasalida=datetime.now(),
                    idsucursal=idSucursal,
                )
                db.session.add(transporte)
                for paqueteId in paquetesSeleccionados:
                    paquete = Paquete.query.get(paqueteId)
                    paquete.idtransporte = transporte.id
                db.session.commit()
                flash('Salida de transporte registrada', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al registrar el transporte: {str(e)}', 'error')
        else:
            if not idSucursal:
                flash('Seleccione una sucursal de destino', 'warning')
            if not paquetesSeleccionados:
                flash('Seleccione al menos un paquete para el transporte', 'warning')
        return redirect(url_for('panelDespachante', idSucursal=sucursalActual))
    
    sucursales = Sucursal.query.filter(Sucursal.id != sucursalActual).order_by(Sucursal.numero).all()
    paquetes = Paquete.query.filter_by(idsucursal=sucursalActual, entregado=False, idrepartidor=None, idtransporte=None).all()
    
    return render_template('registrar_salida.html', sucursal=sucursal, sucursales=sucursales, paquetes=paquetes)

# FUNCIONALIDAD #4: Registrar la llegada de un transporte
@app.route('/registrar_llegada/<int:idSucursal>', methods=['GET', 'POST'])
def registrarLlegada(idSucursal):
    sucursal = Sucursal.query.get_or_404(idSucursal)
    
    if request.method == 'POST':
        transporteId = request.form.get('transporte')
        if transporteId:
            try:
                transporte = Transporte.query.get(transporteId)
                transporte.fechahorallegada = datetime.now()
                db.session.commit()
                flash('Llegada de transporte registrada', 'success')
                return redirect(url_for('panelDespachante', idSucursal=idSucursal))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al registrar la llegada: {str(e)}', 'error')
    
    transportesPendientes = Transporte.query.filter_by(fechahorallegada=None, idsucursal=idSucursal).all()
    return render_template('registrar_llegada.html', sucursal=sucursal, transportes=transportesPendientes)

@app.route('/test_db')
def testDb():
    try:
        sucursales = Sucursal.query.all()
        return f"Se conecto a la base de datos. Numero de sucursales: {len(sucursales)}"
    except Exception as e:
        return f"Error de conexion con la base de datos: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)