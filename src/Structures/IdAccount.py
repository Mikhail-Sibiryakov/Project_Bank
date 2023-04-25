from src.Bank.Bank import Bank
from src.Bank.Client import Client
from src.Structures.Types import TypeBankAccount


class IdAccount:
    """Класс-структура для идентификации счёта"""

    def __init__(self, type: TypeBankAccount, number: str, owner: Client, bank: Bank):
        self.id = number
        self.type = type
        self.owner = owner
        self.bank = bank
