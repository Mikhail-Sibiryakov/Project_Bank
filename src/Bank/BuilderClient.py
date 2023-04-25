from src.Structures import Exceptions
from src.Bank.Client import Client
from src.Structures.Passport import Passport


class BuilderClient:
    """Реализация паттерна Builder для создания клиента"""

    def __init__(self):
        self.__first_name = None
        self.__second_name = None
        self.__address = None
        self.__passport = None
        self.__id = ""

    def firstName(self, first_name: str):
        """Устанавливает имя для будущего объекта-клиента, возвращает ссылку
        на себя же для дальнейшей "настройки" объекта строителя"""
        self.__first_name = first_name
        return self

    def secondName(self, second_name: str):
        """Устанавливает фамилию для будущего объекта-клиента, возвращает ссылку
                на себя же для дальнейшей "настройки" объекта строителя"""
        self.__second_name = second_name
        return self

    def address(self, address: str):
        """Устанавливает адрес для будущего объекта-клиента, возвращает ссылку
                на себя же для дальнейшей "настройки" объекта строителя"""
        self.__address = address
        return self

    def passport(self, series: int, number: int):
        """Устанавливает паспорт для будущего объекта-клиента, возвращает ссылку
                на себя же для дальнейшей "настройки" объекта строителя"""
        self.__passport = Passport(series, number)
        return self

    def setId(self, _id: str):
        """Устанавливает id для будущего объекта-клиента, возвращает ссылку
                на себя же для дальнейшей "настройки" объекта строителя"""
        self.__id = _id
        return self

    def check(self):
        """Проверка обязательных условий (имя и фамилия должны быть установлены)
         для создания объекта-клиента"""
        return (self.__first_name is not None) and (
                    self.__second_name is not None)

    def build(self) -> Client:
        """Сборка объекта-клиента, возвращает объект-клиент пользователю"""
        if not self.check():
            raise Exceptions.NotEnoughDataError
        client = Client(self.__first_name, self.__second_name, self.__address,
                        self.__passport, self.__id)
        return client
