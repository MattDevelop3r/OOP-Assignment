from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sucursal(db.Model):
    __tablename__ = 'Sucursal'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    provincia = db.Column(db.String(50), nullable=False)
    localidad = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)

class Repartidor(db.Model):
    __tablename__ = 'Repartidor'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('Sucursal.id'), nullable=False)
    sucursal = db.relationship('Sucursal', backref=db.backref('repartidores', lazy=True))

class Paquete(db.Model):
    __tablename__ = 'Paquete'
    id = db.Column(db.Integer, primary_key=True)
    numeroenvio = db.Column(db.Integer, unique=True, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    nomdestinatario = db.Column(db.String(100), nullable=False)
    dirdestinatario = db.Column(db.String(200), nullable=False)
    entregado = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    idsucursal = db.Column(db.Integer, db.ForeignKey('Sucursal.id'), nullable=False)
    idtransporte = db.Column(db.Integer, db.ForeignKey('Transporte.id'))
    idrepartidor = db.Column(db.Integer, db.ForeignKey('Repartidor.id'))
    sucursal = db.relationship('Sucursal', backref=db.backref('paquetes', lazy=True))
    transporte = db.relationship('Transporte', backref=db.backref('paquetes', lazy=True))
    repartidor = db.relationship('Repartidor', backref=db.backref('paquetes', lazy=True))

class Transporte(db.Model):
    __tablename__ = 'Transporte'
    id = db.Column(db.Integer, primary_key=True)
    numerotransporte = db.Column(db.Integer, unique=True, nullable=False)
    fechahorasalida = db.Column(db.DateTime, nullable=False)
    fechahorallegada = db.Column(db.DateTime)
    idsucursal = db.Column(db.Integer, db.ForeignKey('Sucursal.id'), nullable=False)