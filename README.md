# F4BY - Sistema de Renta de Coches

F4BY es una aplicación web para la renta de coches desarrollada con Python (Flask) y HTML/CSS.

## Características

- Registro y autenticación de usuarios
- Catálogo de coches con filtros por categoría y precio
- Sistema de reservas con verificación de disponibilidad
- Diferentes opciones de seguro
- Sistema de puntos "Millas F4BY"
- Descuentos por rentas de última hora
- Penalizaciones por daños o entrega tardía

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/f4by.git
cd f4by
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

1. Activar el entorno virtual (si no está activado):
```bash
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Iniciar la aplicación:
```bash
python app.py
```

3. Abrir el navegador y visitar:
```
http://localhost:5000
```

## Estructura del Proyecto

```
f4by/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── static/            # Archivos estáticos
│   └── css/
│       └── style.css
└── templates/         # Plantillas HTML
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── cars.html
    ├── car_detail.html
    └── rent.html
```

## Tecnologías Utilizadas

- Flask: Framework web de Python
- SQLAlchemy: ORM para la base de datos
- Flask-Login: Manejo de autenticación
- Bootstrap 5: Framework CSS
- SQLite: Base de datos

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.