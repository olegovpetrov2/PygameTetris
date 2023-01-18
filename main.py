import os
import random
import sqlite3
import sys
from copy import deepcopy
from random import randint
import pygame_gui

import pygame

WIDTH = 10
HEIGHT = 20
CELL_SIZE = 45
size = WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE
pygame.init()
game_screen = pygame.Surface(size)
screen = pygame.display.set_mode((1500, 900))
game_screen_rect = (500, 0, WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE)
next_fig_screen = pygame.Surface((400, 400), pygame.SRCALPHA)
score_screen = pygame.Surface((500, 200), pygame.SRCALPHA)
high_score_screen = pygame.Surface((500, 200), pygame.SRCALPHA)
lines_screen = pygame.Surface((400, 250), pygame.SRCALPHA)
start_game_screen = pygame.Surface((1500, 900), pygame.SRCALPHA)
rules_screen = pygame.Surface((500, 250), pygame.SRCALPHA)
clock = pygame.time.Clock()
FPS = 60
# переменные для регулировки скорости падения фигурок
level_time = 0
fall_time = 60
fall_time_limit = 2000
GRAVITY = 0.2
all_sprites = pygame.sprite.Group()
CURR_USER = "default"
all_liness = 0
curr_score = 0
lines = 0
LINES_AND_SCORES = {
    0: 0,
    1: 3000,
    2: 6000,
    3: 8000,
    4: 10000
}

game_text_font = pygame.font.Font('fonts/tetrisfont.ttf', 90)
game_text_font2 = pygame.font.Font('fonts/tetrisfont.ttf', 50)
game_text_font3 = pygame.font.Font('fonts/tetrisfont.ttf', 120)
game_text_font4 = pygame.font.Font('fonts/tetrisfont.ttf', 30)
game_text_font5 = pygame.font.Font('fonts/tetrisfont.ttf', 23)

game_name = game_text_font.render("TETRIS", True, pygame.Color("red"))
end_game_text = game_text_font4.render("ESC - экстренно окончить игру",
                                       True, pygame.Color("red"))
next_figure_img = game_text_font2.render("NEXT FIGURE", True,
                                         pygame.Color("red"))
curr_score_label = game_text_font.render("SCORE", True, pygame.Color("red"))
high_score_label = game_text_font2.render("PREV HIGH SCORE", True,
                                          pygame.Color("red"))
lines_label = game_text_font2.render("LINES", True, pygame.Color("red"))
input_name_label = game_text_font.render("INPUT YOUR NAME", True,
                                         pygame.Color("red"))

block_sound = pygame.mixer.Sound("sounds/block_sound.wav")
game_ended_sound = pygame.mixer.Sound("sounds/game_ended_sound.wav")
tetris_collected_sound = pygame.mixer.Sound("sounds/tetris_collected_sound.wav")
start_game_sound = pygame.mixer.Sound("sounds/start_game_sound.wav")


def load_image(name, colorkey=None):
    fullname = os.path.join('imgs', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Particle(pygame.sprite.Sprite):
    fire = [pygame.transform.scale(load_image("pngegg.png"), (32, 32))]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = GRAVITY

    def update(self):

        self.velocity[1] += self.gravity

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect(game_screen_rect):
            self.kill()


def create_particles(position):
    particle_count = 40

    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def start_screen():
    fig_numi = randint(0, 6)
    start_fig = TetrisFigure(fig_numi)

    while True:
        screen.blit(start_game_screen, (0, 0))
        start_game_screen.fill((0, 0, 0))
        start_screen_text = game_text_font3.render("TETRIS",
                                                   True, pygame.Color("red"))
        start_screen_text_rect = start_screen_text.get_rect(center=(1500 // 2,
                                                                    900 // 2))
        screen.blit(start_screen_text, start_screen_text_rect)
        RULES_TEXT = ["ПРАВИЛА ИГРЫ",
                      "R - поворот фигуры",
                      "D - моментальный сброс фигуры",
                      "DOWN - сдвинуть на 1 клетку вниз фигуру",
                      "RIGHT - двигать фигуру вправа",
                      "LEFT - двигать фигуру влево",
                      "ESC - экстренно окончить игру",
                      "S - начать игру",
                      "L - таблица лидеров"
                      ]
        text_coord = 10
        for line in RULES_TEXT:
            string_rendered = game_text_font4.render(line,
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 500
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        for i in range(10):
            start_fig = TetrisFigure(randint(0, 6))
            start_fig.draw_figure_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    start_game_sound.play()
                    login_screen()
                    return
                elif event.key == pygame.K_l:
                    start_game_sound.play()
                    leaderboard_screen()
                    return
        start_fig.move_figure_y_start_screen()
        pygame.time.wait(300)
        pygame.display.flip()
        clock.tick(FPS)


def end_screen():
    game_ended_sound.play()

    game_ended_text = game_text_font3.render("GAME ENDED!",
                                             True, pygame.Color("red"))
    game_ended_text_rect = game_ended_text.get_rect(center=(1500 // 2,
                                                            900 // 2))
    screen.blit(game_ended_text, game_ended_text_rect)

    while True:
        screen.blit(start_game_screen, (0, 0))
        start_game_screen.fill((0, 0, 0))
        screen.blit(game_ended_text, (350, 400))
        RULES_TEXT = ["ПРАВИЛА ИГРЫ",
                      "R - поворот фигуры",
                      "D - моментальный сброс фигуры",
                      "DOWN - сдвинуть на 1 клетку вниз фигуру",
                      "RIGHT - двигать фигуру вправа",
                      "LEFT - двигать фигуру влево",
                      "ESC - экстренно окончить игру",
                      "S - начать игру снова",
                      "L - таблица лидеров"
                      ]
        text_coord = 10
        for line in RULES_TEXT:
            string_rendered = game_text_font4.render(line,
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 500
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        for i in range(10):
            start_fig = TetrisFigure(randint(0, 6))
            start_fig.draw_figure_start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    start_game_sound.play()
                    game()
                    return
                elif event.key == pygame.K_l:
                    start_game_sound.play()
                    leaderboard_screen()
                    return
        pygame.display.flip()
        clock.tick(FPS)


manager = pygame_gui.UIManager((1500, 900))
text_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(
    (0, 0), (900, 50)), manager=manager,
    object_id='#main_text_entry',
    anchors={'center': 'center'})


def login_screen():
    global CURR_USER
    while True:
        ui_refresh_rate = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                    event.ui_object_id == '#main_text_entry'):
                con = sqlite3.connect("users.db")
                cur = con.cursor()
                if event.text:
                    cur.execute(
                        """INSERT OR IGNORE INTO User(name) VALUES(?)""",
                        [str(event.text)],
                    )
                    CURR_USER = str(event.text)
                else:
                    cur.execute(
                        """INSERT OR IGNORE INTO User(name) VALUES(?)""",
                        ["default"],
                    )
                con.commit()
                con.close()
                # event.text -- > имя юсера
                start_game_sound.play()
                game()

            manager.process_events(event)

        manager.update(ui_refresh_rate)

        screen.fill((0, 0, 0))
        input_name_label_rect = input_name_label.get_rect(
            center=(1500 // 2,
                    900 // 2 - 150))
        screen.blit(input_name_label, input_name_label_rect)
        manager.draw_ui(screen)

        pygame.display.flip()


def leaderboard_screen():
    fig_numi = randint(0, 6)
    start_fig = TetrisFigure(fig_numi)

    while True:
        screen.blit(start_game_screen, (0, 0))
        start_game_screen.fill((0, 0, 0))
        leader_screen_text = game_text_font3.render("LEADERS",
                                                    True, pygame.Color("red"))
        leader_screen_text_rect = leader_screen_text.get_rect(center=(1500 // 2,
                                                                      70))
        screen.blit(leader_screen_text, leader_screen_text_rect)
        RULES_TEXT = [
            "S - на главный экран",
        ]
        text_coord = 50
        for line in RULES_TEXT:
            string_rendered = game_text_font4.render(line,
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 100
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        users_data = select_all_users_records()
        text_coord = 200
        for line in users_data:
            string_rendered = game_text_font4.render(line[0],
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 440
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        text_coord = 200
        for line in users_data:
            string_rendered = game_text_font4.render(str(line[1]),
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 750
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        text_coord = 200
        for line in users_data:
            string_rendered = game_text_font4.render(str(line[2]),
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 1000
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        COL_NAMES = ["NAME", "HIGH SCORE", "LINES"]
        text_coord = 150
        c = 450
        for line in COL_NAMES:
            string_rendered = game_text_font4.render(line,
                                                     True,
                                                     pygame.Color("white"))
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord
            intro_rect.x = c
            screen.blit(string_rendered, intro_rect)
            c += 270
        for i in range(10):
            start_fig = TetrisFigure(randint(0, 6))
            start_fig.draw_figure_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    start_game_sound.play()
                    start_screen()
                    return
        start_fig.move_figure_y_start_screen()
        pygame.time.wait(300)
        pygame.display.flip()
        clock.tick(FPS)


class TetrisField:
    # создание поля
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.board = []
        for i in range(self.height):
            c = []
            for j in range(self.width):
                c.append(0)
            self.board.append(c)

    # ф-ия отрисовки игрового поля
    def render(self, screen):
        pygame.init()
        for i in range(0, self.width):
            for j in range(0, self.height):
                pygame.draw.rect(screen, (255, 255, 255), (i * self.cell_size,
                                                           j * self.cell_size,
                                                           self.cell_size,
                                                           self.cell_size), 1)
        pygame.display.set_caption("Tetris")

    def check_field_lines(self):
        global lines, fall_time, curr_score, all_liness
        line = HEIGHT - 1
        lines = 0
        for row in range(HEIGHT - 1, -1, -1):
            count = 0
            for i in range(WIDTH):
                if self.board[row][i]:
                    count += 1
                self.board[line][i] = self.board[row][i]
            if count < WIDTH:
                line -= 1
            else:
                tetris_collected_sound.play()
                lines += 1
                all_liness += 1
                fall_time += 10
        curr_score += LINES_AND_SCORES[lines]

    def bloody_game_screen(self):
        pygame.draw.rect(game_screen, pygame.Color("red"),
                         (0, 0,
                          WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE))
        screen.blit(game_screen, (500, 0))
        pygame.display.flip()

    def check_game_over(self):
        global curr_score, level_time, fall_time_limit, fall_time
        for i in range(WIDTH):
            if self.board[0][i]:
                self.game_over()
                break

    def game_over(self):
        global curr_score, level_time, \
            fall_time_limit, \
            fall_time, fig, fig_num, tetris_field, next_fig, all_liness
        self.board = []
        for xo in range(self.height):
            c = []
            for j in range(self.width):
                c.append(0)
            self.board.append(c)
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        curr_high_score = int(
            cur.execute(
                f"""SELECT high_score FROM User
             WHERE name = '{CURR_USER}'""").fetchall()[0][0])
        if curr_score > curr_high_score:
            cur.execute(
                """UPDATE USER
                    SET high_score = ?, lines = ?
                    WHERE name = ? """,
                [curr_score, all_liness, str(CURR_USER)],
            )
            con.commit()
            con.close()
        curr_score = 0
        all_liness = 0
        level_time = 0
        fall_time = 60
        fall_time_limit = 2000
        self.bloody_game_screen()
        fig_num = randint(0, 6)
        fig = TetrisFigure(fig_num)
        next_fig = TetrisFigure(fig.next_fig_num, fig.next_figure_color)
        tetris_field = TetrisField(WIDTH, HEIGHT, CELL_SIZE)
        pygame.time.wait(1000)
        end_screen()

    def to_main_screen(self):
        global curr_score, level_time, \
            fall_time_limit, fall_time, \
            fig, tetris_field, next_fig, fig_num, all_liness
        self.board = []
        for xo in range(self.height):
            c = []
            for j in range(self.width):
                c.append(0)
            self.board.append(c)
        curr_score = 0
        all_liness = 0
        level_time = 0
        fall_time = 60
        fall_time_limit = 2000
        self.bloody_game_screen()
        fig_num = randint(0, 6)
        fig = TetrisFigure(fig_num)
        next_fig = TetrisFigure(fig.next_fig_num, fig.next_figure_color)
        tetris_field = TetrisField(WIDTH, HEIGHT, CELL_SIZE)
        start_game_sound.play()
        pygame.time.wait(1000)
        start_screen()


# 6 фигур
FIGURES = [
    [(-1, 1), (-2, 1), (0, 1), (1, 1)],
    [(0, 0), (-1, 0), (-1, 1), (0, 1)],
    [(-1, 1), (-1, 2), (0, 1), (0, 0)],
    [(0, 1), (-1, 1), (0, 2), (-1, 0)],
    [(0, 1), (0, 0), (0, 2), (-1, 0)],
    [(0, 1), (0, 0), (0, 2), (1, 0)],
    [(0, 1), (0, 0), (0, 2), (-1, 1)]
]


def get_curr_high_score():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    curr_high_score = int(cur.execute(
        f"""SELECT high_score FROM User
         WHERE name = '{CURR_USER}'""").fetchall()[0][0])
    con.close()
    return curr_high_score


def select_all_users_records():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    users_data = cur.execute(
        f"""SELECT * FROM User
         ORDER BY high_score""").fetchall()[:10][::-1]
    con.close()
    return users_data


def generate_color():
    return randint(110, 255), randint(110, 255), randint(110, 255)


class TetrisFigure:
    def __init__(self, fig_num, color=None):
        if color:
            self.color = color
        else:
            self.color = generate_color()
        self.fig_num = fig_num
        self.figure = [pygame.Rect(x + WIDTH // 2, y, 1, 1)
                       for x, y in FIGURES[self.fig_num]]
        self.next_fig_num = randint(0, 6)
        self.next_figure_color = generate_color()
        self.add_x = 0
        self.add_y = 1
        self.figure_rect = pygame.Rect(0, 0, CELL_SIZE - 2, CELL_SIZE - 2)
        self.rotation = False

    # ф-ия отрисовки фигурки
    def draw_figure(self):
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * CELL_SIZE
            self.figure_rect.y = self.figure[i].y * CELL_SIZE
            pygame.draw.rect(game_screen, self.color, self.figure_rect)

    # ф-ия для передвижения фигуры по Ox
    def move_figure_x(self):
        fig_old = deepcopy(self.figure)
        for i in range(4):
            self.figure[i].x += self.add_x
            if self.check_x_borders():
                pass
            else:
                self.figure = fig_old
                break

    def move_figure_y(self):
        global level_time, fall_time, fall_time_limit, fig, fig_num, next_fig
        level_time += fall_time
        if level_time > fall_time_limit:
            level_time = 0
            fig_old = deepcopy(self.figure)
            for i in range(4):
                self.figure[i].y += 1
                if not self.check_y_borders():
                    block_sound.play()
                    for j in range(4):
                        tetris_field.board[fig_old[j].y][fig_old[j].x] = \
                            self.color
                    fig = TetrisFigure(self.next_fig_num,
                                       self.next_figure_color)
                    next_fig = TetrisFigure(fig.next_fig_num,
                                            fig.next_figure_color)
                    fall_time_limit = 2000
                    break

    def draw_figure_start_screen(self):
        for i in range(4):
            self.figure_rect.x = randint(0, 1600)
            self.figure_rect.y = randint(0, 1600)
            pygame.draw.rect(start_game_screen, self.color, self.figure_rect)

    def move_figure_y_start_screen(self):
        global level_time, fall_time, fall_time_limit, fig, fig_num, next_fig
        level_time += fall_time
        if level_time > fall_time_limit:
            level_time = 0
            for i in range(4):
                self.figure[i].y += 1
                if not self.check_y_borders():
                    fig = TetrisFigure(self.next_fig_num,
                                       self.next_figure_color)
                    next_fig = TetrisFigure(fig.next_fig_num,
                                            fig.next_figure_color)
                    fall_time_limit = 2000
                    break

    def move_figure_on_press(self):
        global fig, fig_num, next_fig
        fig_old = deepcopy(self.figure)
        for i in range(4):
            self.figure[i].y += 1
            if not self.check_y_borders():
                block_sound.play()
                for j in range(4):
                    print(self.figure[j].y, self.figure[j].x,
                          fig_old[j].y, fig_old[j].x)
                    tetris_field.board[fig_old[j].y][fig_old[j].x] = self.color
                fig = TetrisFigure(self.next_fig_num, self.next_figure_color)
                next_fig = TetrisFigure(fig.next_fig_num, fig.next_figure_color)
                break

    def rotate_figure(self):
        if self.rotation and self.fig_num != 1:
            c = self.figure[0]
            fig_old = deepcopy(self.figure)
            for i in range(4):
                x = self.figure[i].y - c.y
                y = self.figure[i].x - c.x
                self.figure[i].x = c.x - x
                self.figure[i].y = c.y + y
                if not self.check_x_borders() or not self.check_y_borders():
                    self.figure = fig_old
                    break

    def check_x_borders(self):
        for i in range(4):
            if self.figure[i].x < 0 or self.figure[i].x > WIDTH - 1 or \
                    tetris_field.board[self.figure[i].y][self.figure[i].x]:
                return False
        return True

    def check_y_borders(self):
        for i in range(4):
            if self.figure[i].y > HEIGHT - 1 or \
                    tetris_field.board[self.figure[i].y][self.figure[i].x]:
                for j in range(4):
                    create_particles((self.figure[j].x * CELL_SIZE + 500,
                                      self.figure[j].y * CELL_SIZE))
                return False
        return True


fig_num = randint(0, 6)
fig = TetrisFigure(fig_num)
next_fig = TetrisFigure(fig.next_fig_num, fig.next_figure_color)
tetris_field = TetrisField(WIDTH, HEIGHT, CELL_SIZE)


def draw_next_figure():
    if fig.next_fig_num != 5:
        for ki in range(4):
            next_fig.figure_rect.x = next_fig.figure[ki].x * CELL_SIZE - 25
            next_fig.figure_rect.y = next_fig.figure[ki].y * CELL_SIZE + 80

            pygame.draw.rect(next_fig_screen,
                             fig.next_figure_color, next_fig.figure_rect)
    else:
        for ki in range(4):
            next_fig.figure_rect.x = next_fig.figure[ki].x * CELL_SIZE - 50
            next_fig.figure_rect.y = next_fig.figure[ki].y * CELL_SIZE + 80

            pygame.draw.rect(next_fig_screen,
                             fig.next_figure_color, next_fig.figure_rect)


game_background = load_image("zxc_back.jpg")


def game():
    global fall_time_limit
    while True:
        curr_score_text = game_text_font2.render(str(curr_score),
                                                 True, pygame.Color("red"))
        all_lines_text = game_text_font2.render(str(all_liness),
                                                True, pygame.Color("red"))
        high_score_text = game_text_font2.render(str(get_curr_high_score()),
                                                 True, pygame.Color("red"))
        screen.blit(game_background, (0, 0))
        screen.blit(game_screen, (500, 0))
        game_name_rect = game_name.get_rect(center=(500 // 2, 50))
        screen.blit(game_name, game_name_rect)
        screen.blit(end_game_text, (1000, 20))

        screen.blit(next_fig_screen, (50, 90))
        next_fig_screen.fill((255, 255, 255, 88))
        next_figure_img_rect = next_figure_img.get_rect(center=(400 // 2, 275))
        next_fig_screen.blit(next_figure_img, next_figure_img_rect)
        screen.blit(lines_screen, (50, 600))
        lines_screen.fill((255, 255, 255, 88))
        lines_label_rect = lines_label.get_rect(center=(400 // 2, 75))
        lines_screen.blit(lines_label, lines_label_rect)
        all_lines_text_rect = all_lines_text.get_rect(center=(400 // 2, 150))
        lines_screen.blit(all_lines_text, all_lines_text_rect)
        game_screen.fill((0, 0, 0))

        screen.blit(rules_screen, (975, 600))
        rules_screen.fill((255, 255, 255, 88))
        RULES_TEXT = ["ПРАВИЛА ИГРЫ",
                      "R - поворот фигуры",
                      "D - моментальный сброс фигуры",
                      "DOWN - сдвинуть на 1 клетку вниз фигуру",
                      "RIGHT - двигать фигуру вправа",
                      "LEFT - двигать фигуру влево",
                      ]
        text_coord = 0
        for line in RULES_TEXT:
            string_rendered = game_text_font5.render(line,
                                                     True, pygame.Color("red"))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            rules_screen.blit(string_rendered, intro_rect)

        screen.blit(score_screen, (975, 90))
        screen.blit(high_score_screen, (975, 300))
        high_score_screen.fill((255, 255, 255, 88))
        score_screen.fill((255, 255, 255, 88))
        curr_score_label_rect = curr_score_label.get_rect(center=(500 // 2, 75))
        score_screen.blit(curr_score_label, curr_score_label_rect)
        curr_score_text_rect = curr_score_text.get_rect(center=(500 // 2, 150))
        score_screen.blit(curr_score_text, curr_score_text_rect)
        high_score_label_rect = high_score_label.get_rect(center=(500 // 2, 75))
        high_score_screen.blit(high_score_label, high_score_label_rect)
        high_score_text_rect = high_score_text.get_rect(center=(500 // 2, 150))
        high_score_screen.blit(high_score_text, high_score_text_rect)
        tetris_field.check_field_lines()
        tetris_field.render(game_screen)

        fig.draw_figure()
        draw_next_figure()

        all_sprites.update()
        all_sprites.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    fig.add_x = - 1
                    fig.move_figure_x()
                elif event.key == pygame.K_RIGHT:
                    fig.add_x = 1
                    fig.move_figure_x()
                elif event.key == pygame.K_DOWN:
                    fig.move_figure_on_press()
                elif event.key == pygame.K_r:
                    fig.rotation = True
                    fig.rotate_figure()
                elif event.key == pygame.K_d:
                    fall_time_limit = 60
                elif event.key == pygame.K_ESCAPE:
                    tetris_field.to_main_screen()
            if event.type == pygame.QUIT:
                exit()

        fig.move_figure_y()
        tetris_field.check_game_over()

        for y, row in enumerate(tetris_field.board):
            for x, col in enumerate(row):
                if col != 0:
                    fig.figure_rect.x, fig.figure_rect.y = x * CELL_SIZE, \
                                                           y * CELL_SIZE
                    pygame.draw.rect(game_screen,
                                     col, fig.figure_rect)

        pygame.display.flip()
        clock.tick(FPS)


start_screen()
