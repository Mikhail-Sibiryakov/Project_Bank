from src.Database.DbWriter import DbWriter
from src.Bank.BankAccount import BankAccount
from src.Helpers.MyConstants import MyConstants
from src.Structures import Types
from src.Structures.Money import Money


class Transaction:
    """Реализация паттерна command для транзакций банка"""

    def __init__(self, account: BankAccount, is_undo: bool = False,
                 _id: str = ""):
        """Конструктор общей части для всех типов транзакций"""
        self.account = account
        self.id_tr = _id
        self.is_undo = is_undo
        self.db_writer = DbWriter()

    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError

    def updateDataBase(self):
        raise NotImplementedError


class WithdrawTransaction(Transaction):
    """Класс транзакций снятия денег со счёта"""

    def __init__(self, account: BankAccount, amount: Money,
                 is_undo: bool = False, _id: str = ""):
        """Создание транзакции-снятия"""
        super().__init__(account, is_undo, _id)
        self.amount = amount

    def execute(self):
        """Выполнение транзакции, обновление данных о ней в бд"""
        self.account.withdraw(self.amount)
        self.is_undo = False
        self.updateDataBase()

    def undo(self):
        """Отмена транзакции, обновление данных о ней в бд"""
        self.account.topUp(self.amount)
        self.is_undo = True
        self.updateDataBase()

    def updateDataBase(self):
        """Обновление записи в бд об этой транзакции"""
        _ID = self.db_writer.update(MyConstants.TABLE_TRANSACTIONS, {
            MyConstants.TYPE: Types.TypeTransaction.WITHDRAW,
            MyConstants.FROM: self.account.id_account.id,
            MyConstants.AMOUNT: self.amount,
            MyConstants.IS_UNDO: int(self.is_undo)
        }, self.id_tr)
        self.id_tr = _ID if self.id_tr == "" else self.id_tr


class TopUpTransaction(Transaction):
    """Класс транзакций пополнения на счёт"""

    def __init__(self, account: BankAccount, amount: Money,
                 is_undo: bool = False, _id: str = ""):
        """Создание транзакции-пополнения"""
        super().__init__(account, is_undo, _id)
        self.amount = amount

    def execute(self):
        """Выполнение транзакции, обновление данных о ней в бд"""
        self.account.topUp(self.amount)
        self.is_undo = False
        self.updateDataBase()

    def undo(self):
        """Отмена транзакции, обновление данных о ней в бд"""
        self.account.withdraw(self.amount)
        self.is_undo = True
        self.updateDataBase()

    def updateDataBase(self):
        """Обновление записи в бд об этой транзакции"""
        _ID = self.db_writer.update(MyConstants.TABLE_TRANSACTIONS, {
            MyConstants.TYPE: Types.TypeTransaction.TOP_UP,
            MyConstants.FROM: self.account.id_account.id,
            MyConstants.AMOUNT: self.amount,
            MyConstants.IS_UNDO: int(self.is_undo)
        }, self.id_tr)
        self.id_tr = _ID if self.id_tr == "" else self.id_tr


class TransferTransaction(Transaction):

    def __init__(self, from_account: BankAccount, other_account: BankAccount,
                 amount: Money,
                 is_undo: bool = False, _id: str = ""):
        """Создание транзакции-перевода денег"""
        super().__init__(from_account, is_undo, _id)
        self.other = other_account
        self.amount = amount

    def execute(self):
        """Выполнение транзакции, обновление данных о ней в бд"""
        self.account.withdraw(self.amount)
        self.other.topUp(self.amount)
        self.is_undo = False
        self.updateDataBase()

    def undo(self):
        """Отмена транзакции, обновление данных о ней в бд"""
        self.other.withdraw(self.amount)
        self.account.topUp(self.amount)
        self.is_undo = True
        self.updateDataBase()

    def updateDataBase(self):
        """Обновление записи в бд об этой транзакции"""
        _ID = self.db_writer.update(MyConstants.TABLE_TRANSACTIONS, {
            MyConstants.TYPE: Types.TypeTransaction.TRANSFER,
            MyConstants.FROM: self.account.id_account.id,
            MyConstants.OTHER: self.other.id_account.id,
            MyConstants.AMOUNT: self.amount,
            MyConstants.IS_UNDO: int(self.is_undo)
        }, self.id_tr)
        self.id_tr = _ID if self.id_tr == "" else self.id_tr
