import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key' 

db = SQLAlchemy(app)


class City(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def get_weather_data(city):

    url = f'https://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=31711e4776520f7cce0f2f4e47b7ae24'
    
    req = requests.get(url).json()
    return req


@app.route('/')
def index_get():

    cities = City.query.all()

    weather_data =[]
    
    for city in cities:

        r = get_weather_data(city.name)

        weather = {
            'city' : city.name,
            'temperature' : str(round(int(r['main']['temp']))),
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'country' : r['sys']['country'],
            'feels_like' : str(round(int(r['main']['feels_like']))),
            'speed' : r['wind']['speed'],
        }

        weather_data.append(weather)

    return render_template('weatherapp.html', weather_data=reversed(weather_data))


@app.route('/', methods=['POST'])
def index_post():

    error_message = ''

    new_city = request.form.get('city')
    
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()

            else:
                error_message = 'City does not exist.'
        else:
            error_message = 'City already exists below.'

        if error_message:
            flash(error_message, 'error')

        else:
            flash('City added successfully.')
    
    return redirect(url_for('index_get')) 


@app.route('/delete/<name>')
def delete_city(name):

    city = City.query.filter_by(name=name).first()
    
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }.', 'success')

    return redirect(url_for('index_get'))
