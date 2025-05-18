from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///f4by.db')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)
    rentals = db.relationship('Rental', backref='user', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False, index=True)
    model = db.Column(db.String(50), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    price_per_hour = db.Column(db.Float, nullable=False, index=True)
    available = db.Column(db.Boolean, default=True, index=True)
    rentals = db.relationship('Rental', backref='car', lazy=True)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    insurance_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    cars = Car.query.all()
    return render_template('index.html', cars=cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo electrónico o contraseña incorrectos', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/cars')
def cars():
    category = request.args.get('category')
    price_range = request.args.get('price_range')
    
    query = Car.query
    
    if category:
        query = query.filter_by(category=category)
    
    if price_range:
        if price_range == '0-50':
            query = query.filter(Car.price_per_hour <= 50)
        elif price_range == '50-100':
            query = query.filter(Car.price_per_hour > 50, Car.price_per_hour <= 100)
        elif price_range == '100+':
            query = query.filter(Car.price_per_hour > 100)
    
    cars = query.all()
    return render_template('cars.html', cars=cars)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template('car_detail.html', car=car)

@app.route('/rent/<int:car_id>', methods=['GET', 'POST'])
@login_required
def rent_car(car_id):
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
            insurance_type = request.form.get('insurance')
            
            # Validar fechas
            if start_time < datetime.now():
                flash('La fecha de inicio debe ser en el futuro', 'danger')
                return redirect(url_for('rent_car', car_id=car_id))
            
            if end_time <= start_time:
                flash('La fecha de fin debe ser posterior a la fecha de inicio', 'danger')
                return redirect(url_for('rent_car', car_id=car_id))
            
            # Verificar disponibilidad
            existing_rentals = Rental.query.filter(
                Rental.car_id == car_id,
                Rental.status != 'cancelled',
                (
                    (Rental.start_time <= start_time) & (Rental.end_time >= start_time) |
                    (Rental.start_time <= end_time) & (Rental.end_time >= end_time) |
                    (Rental.start_time >= start_time) & (Rental.end_time <= end_time)
                )
            ).all()
            
            if existing_rentals:
                flash('El coche no está disponible en el horario seleccionado', 'danger')
                return redirect(url_for('rent_car', car_id=car_id))
            
            # Crear la reserva
            rental = Rental(
                user_id=current_user.id,
                car_id=car_id,
                start_time=start_time,
                end_time=end_time,
                insurance_type=insurance_type
            )
            
            db.session.add(rental)
            
            # Calcular y otorgar puntos
            hours = (end_time - start_time).total_seconds() / 3600
            points = int(hours * 10)  # 10 puntos por hora
            current_user.points += points
            
            db.session.commit()
            
            flash(f'Reserva exitosa. Has ganado {points} puntos!', 'success')
            return redirect(url_for('car_detail', car_id=car_id))
            
        except ValueError:
            flash('Formato de fecha inválido', 'danger')
            return redirect(url_for('rent_car', car_id=car_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error al procesar la reserva. Por favor, intente nuevamente.', 'danger')
            app.logger.error(f'Error en la base de datos: {str(e)}')
            return redirect(url_for('rent_car', car_id=car_id))
    
    return render_template('rent.html', car=car)

@app.route('/my-rentals')
@login_required
def my_rentals():
    rentals = Rental.query.filter_by(user_id=current_user.id).order_by(Rental.start_time.desc()).all()
    return render_template('my_rentals.html', rentals=rentals)

# Inicializar la base de datos con algunos datos de ejemplo
def init_db():
    with app.app_context():
        db.create_all()
        
        # Agregar coches de ejemplo si no existen
        if not Car.query.first():
            cars = [
                Car(brand='Toyota', model='Corolla', category='económico', price_per_hour=25.0),
                Car(brand='Honda', model='Civic', category='compacto', price_per_hour=30.0),
                Car(brand='BMW', model='320i', category='sedan', price_per_hour=45.0),
                Car(brand='Mercedes', model='GLC', category='suv', price_per_hour=60.0),
                Car(brand='Audi', model='A6', category='lujo', price_per_hour=80.0)
            ]
            db.session.add_all(cars)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 