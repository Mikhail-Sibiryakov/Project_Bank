"""Здесь перечислены исключения, их смысл следует из названия и их строкового
представления"""


class LowBalanceError(Exception):
    def __str__(self):
        return "Insufficient funds"


class InvalidArgMoneyError(Exception):
    def __str__(self):
        return "Invalid value money"


class InvalidArgPercentError(Exception):
    def __str__(self):
        return "Invalid value percent"


class DepositNotFinishedError(Exception):
    def __str__(self):
        return "The deposit is not finished"


class DoubtfulClientError(Exception):
    def __str__(self):
        return "Not enough data for an action"


class NotEnoughDataError(Exception):
    def __str__(self):
        return "Second name and first name are required"


class EntryNotFoundError(Exception):
    def __str__(self):
        return "Entry not found"
