class ConstructorErrors:

    class FieldWasSaved(Exception):
        pass

    class NoChosenShip(Exception):
        pass

    class NoShipOnCell(Exception):
        pass

    class ForbiddenCellForShip(Exception):
        pass


class GameErrors:

    class ShipHit(Exception):
        pass

    class KilledCell(Exception):
        pass

    class ShipDeath(Exception):
        pass

    class GameOver(Exception):
        pass
