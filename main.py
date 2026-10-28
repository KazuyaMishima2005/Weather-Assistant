# Главный файл


from datetime import date
from threading import Thread

from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle
from kivy.core.window import Window

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from weather_api import get_city_weather
from recommendations import describe_weather, get_recommendations


#Цветовая палитра
BG = (0.045, 0.065, 0.075, 1)
CARD = (0.09, 0.13, 0.14, 1)
GREEN = (0.22, 0.741, 0.973, 1)
WHITE = (0.95, 0.97, 0.96, 1)
GRAY = (0.68, 0.73, 0.72, 1)

#Вспомогательные элементы интерфейса

def label(text, size=15, color=WHITE, height=38):
    widget = Label(
        text=text,
        font_size=sp(size),
        color=color,
        size_hint_y=None,
        height=dp(height),
        halign="left",
        valign="middle",
    )
    widget.bind(
        width=lambda instance, value:
            setattr(instance, "text_size", (value, None))
    )
    return widget


def button(text, callback):
    widget = Button(
        text=text,
        size_hint_y=None,
        height=dp(48),
        background_normal="",
        background_color=GREEN,
        color=BG,
        font_size=sp(16),
    )
    widget.bind(on_release=callback)
    return widget


#Карточка прогноза
def forecast_card(day, description, low, high, rain):
    card = BoxLayout(
        orientation="vertical",
        padding=dp(12),
        spacing=dp(3),
        size_hint_y=None,
        height=dp(105),
    )

    with card.canvas.before:
        Color(*CARD)
        shape = RoundedRectangle(
            pos=card.pos,
            size=card.size,
            radius=[dp(12)],
        )

    card.bind(
        pos=lambda obj, value: setattr(shape, "pos", value),
        size=lambda obj, value: setattr(shape, "size", value),
    )

    card.add_widget(label(
        f"{day}  •  {description}", 15, WHITE, 30
    ))
    card.add_widget(label(
        f"Мин. {low:.1f}°C    Макс. {high:.1f}°C",
        14, GREEN, 28
    ))
    rain_text = (
        f"Вероятность осадков: {rain}%"
        if rain is not None
        else "Вероятность осадков: нет данных"
    )
    card.add_widget(label(rain_text, 12, GRAY, 24))

    return card


# Основной класс приложения
class WeatherAssistant(App):

    # Главный экран приложения
    def build(self):
        self.title = "Weather Assistant"
        Window.clearcolor = BG

        # Путь к папке проекта и картинке
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent
        background_path = base_dir / "assets" / "background.png"

        # Главный контейнер
        root = FloatLayout()

        # Фон: картинка и затемнение
        with root.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(
                source=str(background_path),
                pos=root.pos,
                size=root.size
            )

            self.dark_color = Color(0, 0, 0, 0.45)
            self.dark_rect = Rectangle(
                pos=root.pos,
                size=root.size
            )

        # Подгоняем фон под размеры окна
        def update_background(instance, value):
            self.bg_rect.pos = root.pos
            self.bg_rect.size = root.size
            self.dark_rect.pos = root.pos
            self.dark_rect.size = root.size

        root.bind(pos=update_background, size=update_background)

        # Контейнер с элементами поверх фона
        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(8),
            size_hint=(1, 1)
        )
        root.add_widget(layout)

        # Заголовок
        layout.add_widget(label(
            "Прогноз погоды", 23, GREEN, 42
        ))
        layout.add_widget(label(
            "Погода • Прогноз • Советы", 13, GRAY, 28
        ))

        # Поле ввода города
        self.city_input = TextInput(
            hint_text="Введите город",
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size=sp(16),
            foreground_color=WHITE,
            background_color=CARD,
            cursor_color=GREEN,
            padding=dp(12),
        )
        layout.add_widget(self.city_input)

        # Кнопка поиска
        layout.add_widget(button(
            "Найти погоду", self.search_weather
        ))

        # Область прогноза с прокруткой
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(9),
            size_hint_y=None,
            padding=[0, dp(4)],
        )
        self.content.bind(
            minimum_height=self.content.setter("height")
        )

        scroll.add_widget(self.content)
        layout.add_widget(scroll)

        # Начальное сообщение
        self.show_message("Введите город для загрузки прогноза.")

        # Загружаем погоду для Якутска при запуске
        self.city_input.text = "Yakutsk"
        Clock.schedule_once(
            lambda dt: self.search_weather(), 0.5
        )

        return root

        return root

    # Вывод статуса
    def show_message(self, message):
        self.content.clear_widgets()
        self.content.add_widget(label(message, 14, GRAY, 90))

    # Запрос погоды
    def search_weather(self, *args):
        city = self.city_input.text.strip()

        if not city:
            self.show_message("Введите название города.")
            return

        self.show_message("Загрузка...")

        Thread(
            target=self.load_weather,
            args=(city,),
            daemon=True,
        ).start()

    def load_weather(self, city):
        try:
            data = get_city_weather(city)
            Clock.schedule_once(
                lambda dt: self.display_weather(data), 0
            )
        except Exception:
            # Ошибка.
            Clock.schedule_once(
                lambda dt: self.show_message(
                    "Не удалось загрузить погоду.\n"
                    "Проверьте интернет и название города."
                ),
                0,
            )

    # Отображение погоды и рекомендаций
    def display_weather(self, data):
        self.content.clear_widgets()

        city = data["city"]
        forecast = data["forecast"]
        current = forecast["current"]
        daily = forecast["daily"]

        self.content.add_widget(label(
            f"{city['name']}, {city['country']}",
            20, GREEN, 42
        ))
        self.content.add_widget(label(
            f"{current['temperature_2m']:.1f} °C",
            40, WHITE, 64
        ))
        self.content.add_widget(label(
            describe_weather(current["weather_code"]),
            18, WHITE, 36
        ))

        # Основные погодные показатели
        details = (
            f"Ощущается как: {current['apparent_temperature']} °C\n"
            f"Влажность: {current['relative_humidity_2m']}%\n"
            f"Ветер: {current['wind_speed_10m']} км/ч\n"
            f"Осадки сейчас: {current['precipitation']} мм"
        )
        self.content.add_widget(label(details, 14, GRAY, 105))

        # Советы по погоде
        self.content.add_widget(label(
            "РЕКОМЕНДАЦИИ", 17, GREEN, 38
        ))

        rain = daily["precipitation_probability_max"][0] or 0
        tips = get_recommendations(
            temperature=current["temperature_2m"],
            precipitation=current["precipitation"],
            wind_speed=current["wind_speed_10m"],
            rain_probability=rain,
        )

        for tip in tips:
            self.content.add_widget(label(
                f"• {tip}", 14, WHITE, 42
            ))

        # Прогноз на 7 дней
        self.content.add_widget(label(
            "ПРОГНОЗ НА 7 ДНЕЙ", 17, GREEN, 44
        ))

        for i, day in enumerate(daily["time"]):
            day_text = date.fromisoformat(day).strftime("%d.%m")
            code = daily["weather_code"][i]
            low = daily["temperature_2m_min"][i]
            high = daily["temperature_2m_max"][i]
            probability = daily["precipitation_probability_max"][i]

            self.content.add_widget(forecast_card(
                day_text,
                describe_weather(code),
                low,
                high,
                probability,
            ))

if __name__ == "__main__":
    WeatherAssistant().run()
