class GameStats:
    """Monitorowanie statystyk gracza."""

    def __init__(self, ai_game):
        """Inicjalizacja statystyk."""
        self.settings = ai_game.settings
        self.reset_stats()

        #Uruchomienie gry.
        self.game_active = False

        #Najlepszy wynik nie jest zerowany.
        self.high_score = 0

    def reset_stats(self):
        """
        Iinicjalizacja statystyk, które ulegają zmianie podczas gry.
        """
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1