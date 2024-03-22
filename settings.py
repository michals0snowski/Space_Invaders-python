class Settings:
    """
    Klasa przeznaczona do przechowania wszystkich ustawień.
    """
    def __init__(self):
        """Inicjalizacja ustawień gry."""
        #Ustawienia ekranu
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        #Ustawienia dotyczące statku
        self.ship_limit = 3

        #Ustawienia dotyczące pocisku
        self.bullet_width = 7
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5

        #Ustawienia dotyczące obcego.
        self.fleet_drop_speed = 10

        #Zmiana szybkości gry.
        self.speedup_scale = 1.1

        #Zmiana punktów za zestrzelenie obcego.
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Inicjzalizacja zmiennych ustawień."""
        self.ship_speed = 1.5
        self.bullet_speed = 1.5
        self.alien_speed = 0.9

        #Wartość fleet_direction wynosząca 1 oznacza prawo, natomiast -1 lewo.
        self.fleet_direction = 1

        #Punktacja.
        self.alien_points = 50

    def increase_speed(self):
        """Zmiana ustawień szybkości gry i punktacji."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)