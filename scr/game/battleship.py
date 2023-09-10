from game.game_errors import ConstructorErrors, GameErrors


class Ship:
    # directions
    HORIZONTAL = "horizontal (to the left)"
    VERTICAL = "vertical (to the bottom)"

    def __init__(self, length, name):
        self.name = name
        self.directions = self.HORIZONTAL
        self.length = length
        self.cells = []
        self.neighbours = []  # cells around the ship
        self.putted = False

    def set_neighbours(self):
        if not self.cells:
            raise ValueError("The ship must have cells to set neighbours")
        for cell in self.cells:
            cell_neighs = cell.neighbours
            for c in cell_neighs:
                if c not in self.neighbours and not c.ship:
                    self.neighbours.append(c)
                    c.is_free = False

    def remove(self):
        cells = self.cells + self.neighbours
        for cell in cells:
            cell.empy()
        self.neighbours.clear()

    def set_cells(self, cells: list):
        self.cells = cells
        for c in cells:
            c.ship = self
            c.is_free = False

    def turn(self):
        if self.directions == self.HORIZONTAL:
            self.directions = self.VERTICAL
        else:
            self.directions = self.HORIZONTAL

    def hit(self):
        for cell in self.cells:
            if not cell.killed:
                return
        self._die()
        raise GameErrors.ShipDeath()

    def _die(self):
        for cell in self.cells:
            cell.display = cell.DIED_SHIP
        for cell in self.neighbours:
            cell.killed = True
            cell.display = cell.HIT_ON_EMPTY


class Cell:
    CELL_ID: int = 0
    ship: (Ship, None)
    killed: bool

    # Display to players
    EMPTY = "⬜"
    SHIP = "🟦"
    NEW_HIT_ON_EMPTY = "⊗"
    HIT_ON_EMPTY = "◌"
    SHIP_HIT = "❌"
    DIED_SHIP = "🟥"

    # cells-neighbours
    # (place, +line, +cell)
    PLACES = [
        ("top_left", -1, -1),
        ("top", -1, 0),
        ("top_right", -1, 1),
        ("right", 0, 1),
        ("bottom_right", 1, 1),
        ("bottom", 1, 0),
        ("bottom_left", 1, -1),
        ("left", 0, -1)
    ]

    def __init__(self):
        self.cell_id = self.CELL_ID
        self.is_free = True  # if ship or ship neighbour --> False
        self.ship = None
        self.killed = False
        self.display = self.EMPTY
        self.neighbours = []

    def __new__(cls, *args, **kwargs):
        cls.CELL_ID += 1
        return super().__new__(cls, *args, **kwargs)

    def __bool__(self):
        """ True if cell is not killed """
        return not self.killed

    def hit(self):
        self.killed = True
        if self.ship:
            self.display = self.SHIP_HIT
            self.ship.hit()
            raise GameErrors.ShipHit()
        else:
            self.display = self.NEW_HIT_ON_EMPTY

    def empy(self):
        self.is_free = True
        self.ship = None
        self.display = self.EMPTY

    def get_my_display(self):
        """show ships"""
        if self.ship and not self.killed:
            return self.SHIP
        return self.display

    def get_enemy_display(self):
        return self.display


class Field:
    """
    c: Cell
    pole = (
        (c1, c2, c3, ...),
        (c1, c2, c3, ...),
        (c1, c2, c3, ...),
        ...,
    )
    """

    FLEET = [
        {"name": "Cruiser", "length": 3, "count": 2},
        {"name": "Destroyer", "length": 2, "count": 2},
        {"name": "Torpedo boat", "length": 1, "count": 3},
    ]
    FLEET_COUNT = 7

    def __init__(self, size: int = 8):
        self.field = self.__create(size)
        self.ship_for_putting = None
        self.fleet = {"Cruiser": [], "Destroyer": [], "Torpedo boat": []}
        self.__died_ship_count = 0
        self.__create_fleet()
        self.__last_killed_cell = None
        self.saved = False

    def __getitem__(self, coords: str):
        """
        :param coords: 'i j'
        :return: Cell
        """
        try:
            line, column = map(int, coords.split())
            return self.field[line][column]
        except Exception as _:
            raise IndexError("некорректно указанные индексы")

    def put_the_ship(self, coords: str):
        if self.saved:
            raise ConstructorErrors.FieldWasSaved()
        cell = self[coords]
        ship = self.ship_for_putting
        if not ship:
            raise ConstructorErrors.NoChosenShip()
        ship_cells = self.__check_and_get_ship_cells(ship, cell)
        ship.set_cells(ship_cells)
        ship.set_neighbours()
        self.ship_for_putting = None

    def shot(self, coords):
        cell = self[coords]
        if not cell:
            raise GameErrors.KilledCell()
        try:
            self._set_last_killed_cell(cell)
            cell.hit()
        except GameErrors.ShipDeath:
            self.__died_ship_count += 1
            if self.__died_ship_count == self.FLEET_COUNT:
                raise GameErrors.GameOver()
            raise GameErrors.ShipHit

    def remove_the_ship(self, coords):
        cell = self[coords]
        ship = cell.ship
        if not ship:
            raise ConstructorErrors.NoShipOnCell()
        ship.remove()
        self.fleet[ship.name].append(ship)

    def chose(self, ship_name):
        s = self.ship_for_putting
        if s:
            self.fleet[s.name].append(s)
        ship = self.fleet[ship_name].pop()
        self.ship_for_putting = ship

    def show(self):
        pole = self.field
        ships = self.__create_ship_info()
        return pole, ships

    def get_ship(self, coords):
        cell = self[coords]
        ship = cell.ship
        return ship

    def turn_ship(self):
        ship = self.ship_for_putting
        if ship:
            ship.turn()

    def _set_last_killed_cell(self, new_cell):
        last_cell = self.__last_killed_cell
        if last_cell is not None and last_cell.display == last_cell.NEW_HIT_ON_EMPTY:
            last_cell.display = last_cell.HIT_ON_EMPTY
        self.__last_killed_cell = new_cell

    def __create_ship_info(self):
        ships_info = []
        for (name, ships) in self.fleet.items():
            if len(ships):
                ships_info.append({"name": name, "count": len(ships)})
        return ships_info

    def __create_fleet(self):
        for ship in self.FLEET:
            name, length, count = ship.values()
            for _ in range(count):
                s = Ship(length, name)
                self.fleet[ship.get("name")].append(s)

    @classmethod
    def __check_and_get_ship_cells(cls, ship, cell):
        ship_cells = []
        description = "left" if ship.directions == ship.HORIZONTAL else "bottom"
        for _ in range(ship.length):
            if not cell or not cell.is_free:
                raise ConstructorErrors.ForbiddenCellForShip()
            ship_cells.append(cell)
            try:
                cell = getattr(cell, description)
            except AttributeError:
                cell = None
        return ship_cells

    @classmethod
    def __create(cls, size: int):
        pole = tuple(tuple(Cell() for _ in range(size)) for _ in range(size))
        cls.__set_neighbours(pole)
        return pole

    @classmethod
    def __set_neighbours(cls, pole):

        def _set_n():
            try:
                if i + _i >= 0 and j + _j >= 0:
                    c = pole[i + _i][j + _j]
                    setattr(cell, place, c)
                    cell.neighbours.append(c)
            except IndexError:
                pass

        for i, line in enumerate(pole):
            for j, cell in enumerate(line):
                for (place, _i, _j) in Cell.PLACES:
                    _set_n()
