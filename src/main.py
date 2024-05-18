from pygame import *
from random import randint
import time


#фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# шрифты и надписи
font.init()
font2 = font.SysFont("Arial", 36)
font1 = font.SysFont("Arial", 36)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
reload_text = font1.render('Wait reload...', True, (180, 0, 0))


#нам нужны такие картинки:
img_back = "galaxy.jpg" #фон игры
img_hero = "rocket.png" #герой
img_enemy = "ufo.png" # враг
img_asteroid = "asteroid.png"
img_bullet = "bullet.png"

score = 0 # сбито кораблей
lost = 0 # пропущено кораблей
goal = 10
max_lost = 3
max_lives = 3

#класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
    #конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        #Вызываем конструктор класса (Sprite):
        sprite.Sprite.__init__(self)


        #каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.size_x = size_x
        self.size_y = size_y

        #каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    #метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
#класс главного игрока
class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.bullets_count = 0
        self.buttets_reload_timestamp = 0
    #метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    #метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)
        self.bullets_count += 1
        if self.bullets_count >= 5:
            self.buttets_reload_timestamp = time.time()+3
            self.bullets_count = 0
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width-80)
            self.rect.y = 0
            lost += 1
class Asteroid(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.speed_x = randint(1, 3)*(randint(-10, 10)/10)
    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.speed_x
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width-80)
            self.rect.y = 0
            self.speed_x = randint(1, 3)*(randint(-10, 10)/10)
        if self.rect.x < 0:
            self.speed_x *= -1
        if self.rect.x + self.size_x > win_width:
            self.speed_x *= -1
class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()
#Создаем окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))


#создаем спрайты
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
monsters = sprite.Group()
for i in range(6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(3):
    asteroid = Asteroid(img_asteroid, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    asteroids.add(asteroid)
bullets = sprite.Group()
#переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False
#Основной цикл игры:
run = True #флаг сбрасывается кнопкой закрытия окна
while run:
    #событие нажатия на кнопку Закрыть
    show_reload_text = False
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if time.time() > ship.buttets_reload_timestamp:
                    fire_sound.play()
                    ship.fire()
                else:
                    show_reload_text = True
    if not finish:
        #обновляем фон
        window.blit(background,(0,0))

        
        #производим движения спрайтов
        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update()
        for monster in monsters:
            for bullet in bullets:
                if sprite.collide_rect(monster, bullet):
                    monster.rect.x = randint(80, win_width-80)
                    monster.rect.y = 0
                    bullet.kill()
                    score += 1
        for asteroid in asteroids:
            for bullet in bullets:
                if sprite.collide_rect(asteroid, bullet):
                    bullet.kill()
        bullets.draw(window)
        #обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        monsters.draw(window)
        asteroids.draw(window)
        text = font2.render(f'Счёт: {score}', 1, (255, 255, 255))
        window.blit(text, (10, 20))
        text_lost = font2.render(f"Пропущено: {lost}", 1, (255, 255, 255))
        window.blit(text_lost, (10, 50))
        for mon in monsters:
            if sprite.collide_rect(mon, ship):
                mon.rect.x = randint(80, win_width-80)
                mon.rect.y = 0
                max_lives -= 1
        for asteroid in asteroids:
            if sprite.collide_rect(asteroid, ship):
                asteroid.rect.x = randint(80, win_width-80)
                asteroid.rect.y = 0
                asteroid.speed_x = randint(1, 3)*(randint(-10, 10)/10)
                max_lives -= 1
        lives = font1.render(f"LIVES: {max_lives}", 1, (255, 255, 255))
        window.blit(lives, (win_width-36*3, win_height-36))
        if score >= goal:
            finish = True
            window.blit(win, (win_width//2-36, win_height//2-13))
        elif lost >= max_lost or max_lives <= 0:
            finish = True
            window.blit(lose, (win_width//2-36, win_height//2-13))
        if show_reload_text:
            window.blit(reload_text, (win_width//2-36, win_height//2-13))
        display.update()
    #цикл срабатывает каждые 0.05 секунд
    time.sleep(0.05)
