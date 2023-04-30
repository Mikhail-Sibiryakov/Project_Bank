from src.Bank.Bank import Bank
from src.Bank.Client import Client
from src.Structures import Types, Exceptions
from src.Structures.IdAccount import IdAccount
from src.Structures.Money import Money
from datetime import date
from src.Structures.Types import TypeBankAccount
from src.Database.DbWriter import DbWriter
from src.Helpers.MyConstants import MyConstants
from src.Helpers.StringHelper import getIntDate


class BankAccount:
    """Класс счёта банка. Используется скорее в роли абстрактного,
    так как обязывает наследников переопределить некоторые методы"""

    def __init__(self, id_account: IdAccount, balance: Money = Money(),
                 name: str = ""):
        """Конструктор общей части для всех типов счётов """
        self.balance = balance
        self.db_writer = DbWriter()
        self.id_account = id_account
        self.end_date = ""
        self.name_account = name

    def clientIsDoubtful(self) -> bool:
        """Проверка, является ли клиент сомнительным
        True - сомнительный"""
        return (self.id_account.owner.address is None) or (
                self.id_account.owner.passport is None)

    def checkWithdraw(self, amount: Money):
        """Проверка, можно ли снять сумму amount со счёта. Если нет,
        то выбрасывается исключение"""
        if self.clientIsDoubtful() and amount > self.id_account.bank.limit:
            raise Exceptions.DoubtfulClientError

    def withdraw(self, amount: Money):
        """Снятие amount со счёта"""
        self.checkWithdraw(amount)
        if self.balance - amount < 0:
            raise Exceptions.LowBalanceError
        self.balance -= amount
        self.updateDataBase()

    def topUp(self, amount: Money):
        """Пополнение счёта на amount"""
        self.balance += amount
        self.updateDataBase()

    def getLimit(self):
        """Возвращает максимальную сумму денег, которую может снять
        "сомнительный" клиент"""
        raise NotImplementedError

    def updateDataBase(self):
        """Обновление бд. "Синхронизирует" объект с тем, что лежит в бд """
        raise NotImplementedError

    def getBalance(self) -> Money:
        """Возвращает баланс счёта"""
        return self.balance


class DebitAccount(BankAccount):

    def __init__(self, bank: Bank, owner: Client, name: str = "",
                 balance: Money = Money(), _id: str = ""):
        """Создание дебетового счёта и запись его в бд"""
        my_id = IdAccount(
            TypeBankAccount.DEBIT,
            _id,
            owner,
            bank
        )
        super().__init__(my_id, balance, name)
        self.updateDataBase()

    def getLimit(self) -> Money:
        """Возвращает максимальную сумму денег, которую может снять
        "сомнительный" клиент"""
        return self.id_account.bank.limit

    def updateDataBase(self):
        """Обновление бд. "Синхронизирует" объект с тем, что лежит в бд """
        _ID = self.db_writer.update(MyConstants.TABLE_ACCOUNTS, {
            MyConstants.BALANCE: self.balance,
            MyConstants.ID_OWNER: self.id_account.owner.id,
            MyConstants.ID_BANK: self.id_account.bank.id,
            MyConstants.TYPE: Types.TypeBankAccount.DEBIT,
            MyConstants.NAME_ACCOUNT: self.name_account
        }, self.id_account.id)
        self.id_account.id = _ID if self.id_account.id == "" else \
            self.id_account.id


class DepositAccount(BankAccount):

    def __init__(self, bank: Bank, owner: Client, name: str = "",
                 balance: Money = Money(),
                 end_date: date = date.today(), _id: str = ""):
        """Создание депозита и запись его в бд"""
        my_id = IdAccount(
            TypeBankAccount.DEPOSIT,
            _id,
            owner,
            bank
        )
        super().__init__(my_id, balance, name)
        self.end_date = date(*getIntDate(end_date))
        self.updateDataBase()

    def withdraw(self, amount: Money):
        """Снятие amount со счёта"""
        self.checkWithdraw(amount)
        if date.today() >= self.end_date:
            super().withdraw(amount)
        else:
            raise Exceptions.DepositNotFinishedError
        self.updateDataBase()

    def setEndDate(self, end_date: date):
        """Установка даты окончания депозита"""
        self.end_date = end_date
        self.updateDataBase()

    def getEndDate(self) -> date:
        """Получение даты окончания депозита"""
        return self.end_date

    def updateDataBase(self):
        """Обновление бд. "Синхронизирует" объект с тем, что лежит в бд """
        _ID = self.db_writer.update(MyConstants.TABLE_ACCOUNTS, {
            MyConstants.BALANCE: self.balance,
            MyConstants.ID_OWNER: self.id_account.owner.id,
            MyConstants.ID_BANK: self.id_account.bank.id,
            MyConstants.TYPE: Types.TypeBankAccount.DEPOSIT,
            MyConstants.END_DATE: str(self.end_date),
            MyConstants.NAME_ACCOUNT: self.name_account
        }, self.id_account.id)
        self.id_account.id = _ID if self.id_account.id == "" else \
            self.id_account.id


class CreditAccount(BankAccount):

    def __init__(self, bank: Bank, owner: Client, name: str = "",
                 balance: Money = Money(), limit: Money = Money(),
                 interest_rate: str = "0.00", _id: str = ""):
        """Создание кредитного счёта и запись его в бд"""
        my_id = IdAccount(
            TypeBankAccount.CREDIT,
            _id,
            owner,
            bank
        )
        super().__init__(my_id, balance, name)
        self.__credit_limit = limit
        self.__interest_rate = interest_rate
        self.updateDataBase()

    def withdraw(self, amount: Money):
        """Снятие amount со счёта"""
        self.checkWithdraw(amount)
        debt = max(amount - self.getBalance(), Money(0))
        interest = debt.getPercent(self.__interest_rate)
        client_money = min(amount, self.balance)
        if debt + interest > self.__credit_limit:
            raise Exceptions.LowBalanceError
        self.balance = self.balance - debt - interest - client_money
        self.updateDataBase()

    def setLimit(self, limit: Money):
        """Установить кредитный лимит для счёта"""
        self.__credit_limit = limit
        self.updateDataBase()

    def updateDataBase(self):
        """Обновление бд. "Синхронизирует" объект с тем, что лежит в бд """
        _ID = self.db_writer.update(MyConstants.TABLE_ACCOUNTS, {
            MyConstants.BALANCE: self.balance,
            MyConstants.ID_OWNER: self.id_account.owner.id,
            MyConstants.ID_BANK: self.id_account.bank.id,
            MyConstants.TYPE: Types.TypeBankAccount.CREDIT,
            MyConstants.CREDIT_LIMIT: self.__credit_limit,
            MyConstants.INTEREST_RATE: self.__interest_rate,
            MyConstants.NAME_ACCOUNT: self.name_account
        }, self.id_account.id)
        self.id_account.id = _ID if self.id_account.id == "" else \
            self.id_account.id

    def getLimit(self):
        """Возвращает максимальную сумму денег, на которую можно уйти в
        минус"""
        return self.__credit_limit

    def getInterestRate(self):
        """Получение процентной ставки по кредитному счёту
        (для использования заёмных средств)"""
        return self.__interest_rate
