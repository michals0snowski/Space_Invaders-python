import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """
    Ogólna klasa przeznaczona do zarzadzania zasobami i sposobem działania gry.
    """

    def __init__(self):
        """Inicjalizacja gry i tworzenie jej zasobów."""
        pygame.init()
        #
        self.settings = Settings()
        #
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        
        pygame.display.set_caption("Inwazja obcych")

        #Utworzenie egzemplarza przechowującego dane statystyczne dot. gry i egzemplarza Scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Utworzenie przycisku Game.
        self.play_button = Button(self.settings, self.screen, "Game")

    def run_game(self):
        """Rozpoczecie petli glownej gry."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
                    
    def _check_events(self):
        """Reakcja na zdarzenia generowane przez klawiaturę i mysz."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Rozpoczęcie gry po kliknięciu przycisku Game."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Wyzerowanie statsów gry.
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            #Usunięcie zawartości list aliens i bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Utworzenie nowej kohorty i wyśrodkowanie gracza.
            self._create_fleet()
            self.ship.center_ship()

            #Ukrycie kursora podczas gry.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
            """Reakcja na wciśnięcie klawisza."""                
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_q:
                sys.exit()
            elif event.key == pygame.K_SPACE:
                self._fire_bullet()

    def _check_keyup_events(self, event):
            """Reakcja na zwolnienie klawisza."""
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = False
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = False

    def _fire_bullet(self):
        """Utworzenie nowego pocisku i dodanie go do grupy pocisków."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet) 

    def _update_bullets(self):
        """Uaktualnienie położenia pocisków i usunięcie tych niewidocznych na ekranie."""
        #Uaktualnienie położenia pocisków.
        self.bullets.update()

        #Usunięcie pocisków znajdujących się poza ekranem
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        #print(len(self.bullets))

        self._check_bullet_alien_collision()
        
    def _check_bullet_alien_collision(self):
        """Reakcja na kolizję między pociskiem i obcym."""
        #Usunięcie obcych i trafiających w nich pocisków.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #Pozbycie się pocisków z ekranu, przyspieszenie i utworzenie nowych obcych.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #Inkrementacja poziomu
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Reakcja na uderzenie obcego w statek."""
        if self.stats.ships_left > 0:
            #Zmniejszenie wartości przechowywanej w ships_left.
            #Aktualizacja wyników.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Usunięcie zawartości list aliens i bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Utworzenie nowej floty i wyśrodkowanie statku.
            self._create_fleet()
           #self.ship.center_ship()
        
            #Pauza
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Sprawdzenie czy obcy dotarł do dolnej krawędzi ekranu."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Jak przy zderzeniu ze statkiem.
                self._ship_hit()
                break

    def _update_aliens(self):
        """Uaktualnienie położenia wszystkich obcyh we flocie."""
        self._check_fleet_edges()
        self.aliens.update()

        #Wykrywanie kolizji między obcym a statkiem
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Wyszukiwanie obcych docierających do dolnej krawędzi ekranu.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Utworzenie pełnej floty obcych."""
        #Utworzenie obcego.
        #Odstęp między obcymi jest równy szerokości 1 obcego.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        #Ustalenie, ile rzędów obcych zmieści się na ekranie.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (4 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #Utworzenie floty obcych.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
            
    def _create_alien(self, alien_number, row_number):
            """Utworzenie obcego i umieszczenie go w rzędzie."""
            alien = Alien(self)
            alien_width, alien_height = alien.rect.size
            alien.x = alien_width + 2 * alien_width * alien_number
            alien.rect.x = alien.x
            alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
            self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Odbicie po dotarciu obcego do krawędzi ekranu."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Przesunięcie floty w dół i zmiana kierunku."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
            """Uaktualnianie obrazów na ekranie i przejście do nowgo ekranu"""
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            
            self.aliens.draw(self.screen)

            #Wyświetlanie punktacji.
            self.sb.show_score()

            #Wyświetlanie buttona kiedy gra nie jest aktywna.
            if not self.stats.game_active:
                self.play_button.draw_button()

            pygame.display.flip()

if __name__ == '__main__':
    #Utworzenie egzemplarza gry i jej uruchomienie
    ai = AlienInvasion()
    ai.run_game()