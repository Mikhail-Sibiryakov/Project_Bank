from src.Helpers.MyConstants import MyConstants
from src.Structures.Passport import Passport
from src.Database.DbWriter import DbWriter


class Client:
    """Класс клиента банка"""

    def __init__(self, first_name: str, second_name: str, address: str,
                 passport: Passport, _id: str = ""):
        """Конструктор клиента"""
        self.first_name = first_name
        self.second_name = second_name
        self.address = address
        self.passport = passport
        self.id = _id
        self.db_writer = DbWriter()
        self.updateDatabase()

    def updatePassport(self, passport: Passport):
        """Обновление паспорта клиента, синхронизация объекта с его записью в
        бд"""
        self.passport = passport
        self.updateDatabase()

    def updateAddress(self, address: str):
        """Обновление адреса клиента, синхронизация объекта с его записью в
        бд"""
        self.address = address
        self.updateDatabase()

    def updateDatabase(self):
        """Синхронизация объекта с его записью в бд"""
        d = {
            MyConstants.FIRST_NAME: self.first_name,
            MyConstants.SECOND_NAME: self.second_name,
            MyConstants.ADDRESS: self.address
        }
        if self.passport is not None:
            d[MyConstants.SERIA] = str(self.passport.series)
            d[MyConstants.NUMBER] = str(self.passport.number)

        _ID = self.db_writer.update(MyConstants.TABLE_USERS, d, self.id)
        self.id = _ID if self.id == "" else self.id
