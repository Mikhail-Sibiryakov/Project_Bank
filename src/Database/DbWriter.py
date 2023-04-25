from src.Helpers.MyConstants import MyConstants
from src.Helpers.StringHelper import tuple_wrapper, string_wrapper
import sqlite3 as sq
from src.Database.DbHelper import deleteMathEntry


class DbWriter:
    """Класс для записи в бд"""

    def __init__(self):
        """Создание объекта-читателя и создание необходимых таблиц"""
        self.createTableUsers()
        self.createTableAccounts()
        self.createTableTransactions()
        self.createTableBanks()

    def createTable(self, name_table: str, columns: tuple, types: tuple):
        """Создание таблице (если её не существовало) с именем name_table,
        кортежом названий стобцов и ожидаемых типов данных в них."""
        with sq.connect(MyConstants.DB_NAME) as connect:
            cursor = connect.cursor()
            command = MyConstants.CREATE_TABLE + " " + name_table + " " + '('
            command += MyConstants.ID + " " + MyConstants.INT + " " + \
                       MyConstants.AUTO_INC
            for i in zip(columns, types):
                command += ',' + i[0] + " " + i[1] + " DEFAULT NULL "
            command += ')'
            cursor.execute(command)

    def insert(self, name_table: str, d: dict) -> str:
        """Вставка данных в таблицу name_table по словарю d вида
        {столбец: значение}
        Возвращает id, которое получит запись"""
        with sq.connect(MyConstants.DB_NAME) as connect:
            cursor = connect.cursor()
            command = "INSERT INTO " + name_table + " "
            column_names = tuple_wrapper(tuple(d.keys()))
            values = tuple_wrapper(tuple(d.values()))
            command += column_names + " VALUES " + values
            cursor.execute(command)
            connect.commit()
        tmp = \
            cursor.execute("SELECT max(_ID) FROM " + name_table).fetchall()[0][
                0]
        return tmp

    def update(self, name_table: str, d: dict, _id):
        """Обновление данных в таблице name_table по словарю d вида
        {столбец: значение} с помощью id записи
        Возвращает id обновляемой записи.
        Вставляет запись в бд, если указать _id="" """
        if _id == "":
            return self.insert(name_table, d)
        with sq.connect(MyConstants.DB_NAME) as connect:
            cursor = connect.cursor()
            command = "UPDATE " + name_table + " SET "
            keys = tuple(d.keys())
            for i in range(len(keys)):
                command += str(keys[i]) + " = " + string_wrapper(
                    str(d[keys[i]]))
                if i + 1 != len(keys):
                    command += ', '
            command += " WHERE " + MyConstants.ID + " = " + str(_id)
            cursor.execute(command)
            connect.commit()
        return "-1"

    def createTableUsers(self):
        """Создание таблицы клиентов"""
        self.createTable(MyConstants.TABLE_USERS,
                         (
                             MyConstants.FIRST_NAME,
                             MyConstants.SECOND_NAME,
                             MyConstants.SERIA,
                             MyConstants.NUMBER,
                             MyConstants.ADDRESS
                         ),
                         (
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT
                         )
                         )

    def createTableAccounts(self):
        """Создание таблицы счетов"""
        self.createTable(MyConstants.TABLE_ACCOUNTS,
                         (
                             MyConstants.BALANCE,
                             MyConstants.ID_OWNER,
                             MyConstants.ID_BANK,
                             MyConstants.TYPE,
                             MyConstants.END_DATE,
                             MyConstants.CREDIT_LIMIT,
                             MyConstants.INTEREST_RATE,
                             MyConstants.NAME_ACCOUNT
                         ),
                         (
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT
                         )
                         )

    def createTableTransactions(self):
        """Создание таблицы транзакций"""
        self.createTable(MyConstants.TABLE_TRANSACTIONS,
                         (
                             MyConstants.TYPE,
                             MyConstants.FROM,
                             MyConstants.OTHER,
                             MyConstants.AMOUNT,
                             MyConstants.IS_UNDO,
                         ),
                         (
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.TXT,
                             MyConstants.INT
                         )
                         )

    def createTableBanks(self):
        """Создание таблицы банков"""
        self.createTable(MyConstants.TABLE_BANKS,
                         (
                             MyConstants.NAME,
                             MyConstants.LIMIT
                         ),
                         (
                             MyConstants.TXT,
                             MyConstants.TXT
                         )
                         )

    def deleteAccountById(self, _id: str):
        """Удаление счёта по его id в бд"""
        deleteMathEntry(MyConstants.TABLE_ACCOUNTS, {MyConstants.ID: _id})
