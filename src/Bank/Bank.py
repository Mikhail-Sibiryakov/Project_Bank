from src.Database.DbWriter import DbWriter
from src.Helpers.MyConstants import MyConstants
from src.Structures.Money import Money


class Bank:
    """Класс банк"""

    def __init__(self, name: str, limit: Money, _id: str = ""):
        """Создание объекта банк и запись его в бд"""
        self.name = name
        self.limit = limit
        self.id = _id
        self.updateDatabase()

    def updateDatabase(self):
        """Обновление бд. "Синхронизирует" объект с тем, что лежит в бд """
        db = DbWriter()
        _ID = db.update(MyConstants.TABLE_BANKS, {
            MyConstants.NAME: self.name,
            MyConstants.LIMIT: self.limit
        }, self.id)
        self.id = _ID if self.id == "" else self.id

    def updateName(self, name: str):
        """Обновление имени банка, в том числе в бд"""
        self.name = name
        self.updateDatabase()

    def updateLimit(self, limit: Money):
        """Обновление лимита (снятие денег на неподтверждённом аккаунте) банка,
        в том числе в бд"""
        self.limit = limit
        self.updateDatabase()
