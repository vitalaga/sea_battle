from random import randint


class FieldException(Exception):
    pass


class FieldOutException(FieldException):
    def __str__(self):
        return "Вы стреляете за доску"


class FieldUsedException(FieldException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку."


class FieldWrongShipException(FieldException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, a, b):
        self.bow = bow
        self.a = a
        self.b = b
        self.lives = a

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.a):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.b == 0:
                cur_x += i

            elif self.b == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shoot):
        return shoot in self.dots


class Field:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.board = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.board):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, 1), (-1, 0), (-1, -1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.board[cur.x][cur.y] = "-"
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise FieldWrongShipException()
        for d in ship.dots:
            self.board[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise FieldOutException()
        if d in self.busy:
            raise FieldUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.board[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.board[d.x][d.y] = "-"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, field, enemy):
        self.field = field
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except FieldException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютер: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Нужно ввести две координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not(y.isdigit()):
                print(" Можно ввести только числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_field()
        co = self.random_field()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_field(self):
        field = Field(size=self.size)
        attempts = 0
        for ln in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), ln, randint(0, 1))
                try:
                    field.add_ship(ship)
                    break
                except FieldWrongShipException:
                    pass
        field.begin()
        return field

    def random_field(self):
        field = None
        while field is None:
            field = self.try_field()
        return field

    def greetings(self):
        print("*******************")
        print("      МОРСКОЙ      ")
        print("        БОЙ        ")
        print("*******************")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        print("-" * 20)
        print("Доска пользователя:" + "\t"*4 + "")
        print(self.us.field)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.field)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.field.defeat():
                self.print_boards()
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.field.defeat():
                self.print_boards()
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greetings()
        self.loop()


play = Game()
play.start()
