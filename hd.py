import subprocess
import sys
import importlib
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

def install_and_import(package):
    try:
        return importlib.import_module(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(package)

requests = install_and_import('requests')
geonamescache = install_and_import('geonamescache')

API_KEY = 'YOUR_API_KEY_HERE'

root = tk.Tk()
root.title("Hava Durumu Uygulaması")
root.geometry("1280x720")

gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
country_names = sorted([country['name'] for country in countries.values()])

country_label = tk.Label(root, text="Ülke Seçiniz:")
country_label.pack()
country_var = tk.StringVar()
country_combobox = ttk.Combobox(root, textvariable=country_var, values=country_names)
country_combobox.pack()

city_label = tk.Label(root, text="Şehir Seçiniz:")
city_label.pack()
city_var = tk.StringVar()
city_combobox = ttk.Combobox(root, textvariable=city_var)
city_combobox.pack()

def update_cities(*args):
    selected_country = country_var.get()
    if selected_country:
        country_code = next(code for code, country in countries.items() if country['name'] == selected_country)
        all_cities = gc.get_cities()
        selected_cities = [city for city in all_cities.values() if city['countrycode'] == country_code]
        city_names = sorted([city['name'] for city in selected_cities])
        city_combobox['values'] = city_names
    else:
        city_combobox['values'] = []

country_var.trace('w', update_cities)

def get_weather_time():
    selected_city = city_var.get()
    selected_country = country_var.get()
    if selected_city and selected_country:
        country_code = next(code for code, country in countries.items() if country['name'] == selected_country)
        city_with_country = f"{selected_city},{country_code}"
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_with_country}&appid={API_KEY}&units=metric'
        try:
            response = requests.get(url)
            data = response.json()
            if data['cod'] == 200:
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                timezone_offset = data['timezone']
                utc_time = datetime.utcnow()
                local_time = utc_time + timedelta(seconds=timezone_offset)
                local_time_str = local_time.strftime("%Y-%m-%d %H:%M:%S")
                result = f"Şehir: {selected_city}\nSaat: {local_time_str}\nSıcaklık: {temp} °C\nAçıklama: {description}"
                result_label.config(text=result)
            else:
                result_label.config(text="Şehir bulunamadı veya API hatası")
        except Exception as e:
            result_label.config(text=f"Hata: {str(e)}")
    else:
        result_label.config(text="Lütfen bir şehir seçin")

get_button = tk.Button(root, text="Hava Durumu ve Saati Al", command=get_weather_time)
get_button.pack()

result_label = tk.Label(root, text="", justify='left')
result_label.pack()

root.mainloop()
