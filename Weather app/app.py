"""
Weather App (Tkinter + OpenWeatherMap)
--------------------------------------

Requirements:
    pip install requests pillow

Run:
    python weather_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests, json, os, time, threading
from PIL import Image, ImageTk
import io

CONFIG_FILE = "weather_config.json"


# ---------------- Utility ----------------
def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------- Weather App ----------------
class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("600x400")

        self.config_data = load_json(CONFIG_FILE, {})

        self.api_key_var = tk.StringVar(value=self.config_data.get("api", ""))
        self.city_var = tk.StringVar(value=self.config_data.get("city", ""))
        self.units_var = tk.StringVar(value=self.config_data.get("units", "metric"))

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="API Key:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.api_key_var, width=30).grid(row=0, column=1)

        ttk.Label(frame, text="City:").grid(row=1, column=0, sticky="w")
        city_entry = ttk.Entry(frame, textvariable=self.city_var, width=30)
        city_entry.grid(row=1, column=1)
        city_entry.bind("<Return>", lambda e: self.fetch_weather())

        ttk.Label(frame, text="Units:").grid(row=2, column=0, sticky="w")
        units = ttk.Combobox(frame, textvariable=self.units_var, values=("metric", "imperial"))
        units.grid(row=2, column=1)

        self.btn = ttk.Button(frame, text="Get Weather", command=self.fetch_weather)
        self.btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(frame, text="Weather info will appear here",
                                      wraplength=500, justify="left")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.icon_label = ttk.Label(frame)
        self.icon_label.grid(row=5, column=0, columnspan=2)

    def fetch_weather(self):
        api_key = self.api_key_var.get().strip()
        city = self.city_var.get().strip()
        units = self.units_var.get()
        if not api_key or not city:
            messagebox.showwarning("Missing Info", "Please provide API key and city")
            return

        def worker():
            try:
                url = "https://api.openweathermap.org/data/2.5/weather"
                r = requests.get(url, params={"q": city, "appid": api_key, "units": units}, timeout=10)
                data = r.json()
                if data.get("cod") != 200:
                    raise Exception(data.get("message", "Error"))
                self.after(0, lambda: self.show_weather(data))
                self.config_data = {"api": api_key, "city": city, "units": units}
                save_json(CONFIG_FILE, self.config_data)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def show_weather(self, data):
        name = data.get("name")
        weather = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        self.result_label.config(text=f"{name}: {weather}\nTemp: {temp}°\nHumidity: {humidity}%")

        # Load icon
        icon = data["weather"][0]["icon"]
        url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
        r = requests.get(url)
        img = Image.open(io.BytesIO(r.content))
        photo = ImageTk.PhotoImage(img)
        self.icon_label.config(image=photo)
        self.icon_label.image = photo


if __name__ == "__main__":
    WeatherApp().mainloop()
