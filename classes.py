import random 

class BoardOutException(Exception):
    pass

class BoardCrossException(Exception):
    pass

class Dot:
    def __init__(self, x, y, shotted = False, hitted = False):
        self.x = x
        self.y = y
        self.shotted = shotted
        self.hitted = hitted

    def __eq__(self, other):
        if isinstance(other, Dot):
            return self.x == other.x and self.y == other.y

class Ship:
    def __init__(self, length, direction, bow_x, bow_y):
        self.length = length
        self.bow = Dot(bow_x, bow_y)
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []

        if self.direction == 'горизонтальное':
            for i in range(self.length):
                dot = Dot(self.bow.x + i, self.bow.y)
                ship_dots.append(dot)
        elif self.direction == 'вертикальное':
            for i in range(self.length):
                dot = Dot(self.bow.x, self.bow.y + i)
                ship_dots.append(dot)
        return ship_dots
    
    def contour(self):
        contour_dots = []
        
        for dot in self.dots():
            for x in range(dot.x - 1, dot.x + 2):
                for y in range(dot.y - 1, dot.y + 2):
                    if Dot(x, y) not in self.dots() and Dot(x, y) not in contour_dots:
                        contour_dots.append(Dot(x, y))
                        contour_dots.append(dot)
        return contour_dots
    
class Board:
    def __init__(self, hid):
        self.board = []
        self.ships = []
        self.hid = hid
        self.ships_alive = 0 
        self.forbidden = []
        self.shot_dots = []
        
    def add_ship(self, length, direction, bow_x, bow_y):
        ship = Ship(length, direction, bow_x, bow_y)
        
        if self.out(ship.dots()):
            raise BoardOutException('\nКорабль вне поля!\n')
        if any(dot in self.forbidden for dot in ship.dots()):
            raise BoardCrossException('\nКорабли пересекаются!\n') 
        
        self.board.append(ship)
        self.ships_alive += 1
        self.ships.append(ship)
        self.forbidden.extend(dot for dot in ship.contour())
        return self.board
    
    def draw_board(self):
        play_board = [[' ○ ' for j in range(6)] for i in range(6)]
        
        if self.hid:
            for ship in self.ships:
                for dot in ship.dots():
                    play_board[dot.y - 1][dot.x - 1] = ' ■ '  
        
        for dot in self.shot_dots:
            if dot.shotted:
                if dot.hitted:
                    play_board[dot.y - 1][dot.x - 1] = ' X '
                else:
                    play_board[dot.y - 1][dot.x - 1] = ' T '
            
        board_str = f'\n  1  2  3  4  5  6 \n'
        for i, row in enumerate(play_board):
            board_str += f'{i+1}{"".join(row)}\n'
        return board_str
    
    def clear_board(self):
        self.board.clear()
        self.ships.clear()
        self.ships_alive = 0 
        self.forbidden.clear()
        self.shot_dots.clear()
    
    def out(self, ship_dots):
        for dot in ship_dots:
            if dot.x < 1 or dot.y > 6 or dot.x > 6 or dot.y < 1:
                return True
        return False 
    
    def shot(self, x, y):
        if x < 1 or y > 6 or x > 6 or y < 1 :
            raise BoardOutException('\nВыстрел за пределы поля!\n')
        if Dot(x, y) in self.shot_dots:
            raise BoardCrossException('\nНельзя делать выстрел в одну точку несколько раз!\n')

        hitted = False
        
        for ship in self.ships:
            for dot in ship.dots():
                
                if dot.x == x and dot.y == y:
                    ship.lives -= 1
                    hitted = True
                    
                    if ship.lives == 0:
                        self.ships_alive -= 1 

        self.shot_dots.append(Dot(x, y, True, hitted))
        return hitted                    

class Player:
    def __init__(self, own_board, enemy_board):
        self.own_board = own_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        repeat_shot = False
    
        while not repeat_shot:
            x, y = self.ask()
            try:
                if self.enemy_board.shot(x, y):
                    for ship in self.enemy_board.ships:  
                        for dot in ship.dots():          
                            if ship.lives == 0 and dot == Dot(x, y):
                                print('\nКорабль убит!\n')
                                
                    repeat_shot = True
            except (BoardOutException, BoardCrossException) as e:
                print(e)
                continue
            self.enemy_board.draw_board()
            break

        return repeat_shot
                     
class User(Player):
    def ask(self):
        print('Твой ход!')
        dots = input('Введите координаты для выстрела x и y через пробел: ')
        x, y = dots.split()
        
        if len(dots.split()) != 2:
            print('\nОшибка! Введи данные в формате: x y.\n')
        
        x, y =  int(x), int(y)
        return x, y
        
class AI(Player):    
    def ask(self):
        print('\nХод ИИ!\n')
        x = random.randint(1, 6)
        y = random.randint(1, 6)
        return x, y
        
class Game:
    def __init__(self):
        self.board = Board(True)
        self.ai_board = Board(False)
        self.user = User(self.board, self.ai_board)
        self.ai = AI(self.ai_board, self.board)

    def random_board(self):
        max_attempts = 1000
        direction = ['горизонтальное', 'вертикальное']
        ship_len = [3, 2, 2, 1, 1, 1, 1]
        
        attempts = 0
        isError = True
        
        while isError:
            isError = False
            
            for length in ship_len:
                while True:
                    random_data = [random.choice(direction), random.randint(1, 6), random.randint(1, 6)]
                    try:
                        self.ai_board.add_ship(length, random_data[0], random_data[1], random_data[2])
                        print(self.ai_board.draw_board())   
                        break
                    except (BoardOutException, BoardCrossException):
                        attempts += 1
                        
                    if attempts > max_attempts:
                        attempts = 0
                        isError = True
                        break
                if isError:
                    self.ai_board.clear_board()
                    break
            
        print(attempts)    
        return self.ai_board
              
    def user_add_ship(self, length):
        while True:
            input_data = input(f'Введи направление (горизонтальное/вертикальное) и координаты (x, y) для {length}-палубного корабля через пробел: ')
            ship_data = input_data.split(' ')
            
            if len(ship_data) != 3 or ',' in input_data or len(ship_data) == 0:
                print('\nОшибка! Введи данные в формате: направление x y.\n')
                continue
            if ship_data[0] not in ['горизонтальное', 'вертикальное']:
                print('\nНапрвыление задано неверно! Введите "горизонтальное" или "вертикальное".\n')
                continue
            else:
                try:
                    self.board.add_ship(length, ship_data[0], int(ship_data[1]), int(ship_data[2]))
                except (BoardOutException, BoardCrossException) as e:
                    print(e)                   
                    continue
                
                print(self.board.draw_board())
                break
    
    def user_board(self):
        print(self.board.draw_board())
        
        for _ in range(1):
            self.user_add_ship(3)
        
        for _ in range(2):
            self.user_add_ship(2)
        
        for _ in range(4):
            while True:    
                input_data = input('Введи координаты (x, y) для однопалубного корабля через пробел: ')
                ship_data = input_data.split(' ')
                    
                if len(ship_data) != 2 or ',' in input_data or len(ship_data) == 0 or ship_data[1] == '':
                    print('\nОшибка! Введи данные в формате: x y.\n')
                    continue
                    
                try:
                    self.board.add_ship(1, 'горизонтальное', int(ship_data[0]), int(ship_data[1]))
                except (BoardOutException, BoardCrossException) as e:
                    print(e)                   
                    continue
                
                if self.board.ships_alive < 4:
                    print(self.board.draw_board())
                break
        return self.board
    
    def combine_boards(self, board_1, board_2):
        combined_board = ''
        board_lines_1 = board_1.draw_board().split('\n')
        board_lines_2 = board_2.draw_board().split('\n')
        
        for line_1, line_2 in zip(board_lines_1, board_lines_2):
            combined_board += line_1 + '   ' + line_2 + '\n'
        print(combined_board)
    
    def greet(self):
        print('''
Привет! 
Это игра "Морской бой!" и твой противник - ИИ.
Перед тем как начать игру ознакомься с правилами:
1. Морской бой играется на квадратном поле с координатной сеткой 6х6.
2. Каждому игроку на старте выдаются несколько кораблей разного размера: один трехпалубный, 
два двухпалубных и четыре однопалубных корабля.
3. Корабли размещаются на поле горизонтально или вертикально. Они не могут касаться друг друга 
и соседних клеток, а также не могут выходить за пределы поля.
4. Игроки стреляют по противнику, называя координаты цели на поле. Если выстрел приходится 
в пустую клетку, то знак меняется на "T". Если выстрел попадает в клетку с кораблем, 
то знак меняется на "X". Когда все палубы корабля поражены, в консоли отобразиться надпись - "Корабль убит!".
5. Цель игры — потопить все корабли противника раньше, чем он сделает то же самое с вашими 
кораблями. Первый игрок, чей флот будет полностью потоплен, проигрывает.
              
Давай расставим корабли на твоем поле!
        ''')

        self.user_board()
        self.random_board()
        self.combine_boards(self.board, self.ai_board)
    
    def loop(self):
        while True:
            if not self.user.move():
                self.ai.move()
                self.combine_boards(self.board, self.ai_board)
                
                if self.board.ships_alive == 0:
                    print('\nПобедил ИИ!\n')
                    break
                elif self.ai_board.ships_alive == 0:
                    print('\nТы выиграл!\n')
                    break
            else:
                self.combine_boards(self.board, self.ai_board)
                continue
                
    def start(self):
        self.greet()
        self.loop()
        
game = Game()
game.start()






