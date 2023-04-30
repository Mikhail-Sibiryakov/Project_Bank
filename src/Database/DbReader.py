from Bank.Client import Client
from src.Structures import Types
from src.Bank.Bank import Bank
from src.Bank import BankAccount, Transaction
from src.Bank.BuilderClient import BuilderClient
from src.Bank.Transaction import WithdrawTransaction, TopUpTransaction, \
    TransferTransaction
from src.Structures.Money import Money
from src.Helpers.MyConstants import MyConstants
from src.Database.DbHelper import getMathEntry, getEntryById, getAllEntry


class DbReader:
    """Класс для чтения бд"""

    def makeClient(self, entry: tuple) -> Client:
        """Возвращает объект клиента по записи из бд"""
        _ID, first_name, second_name, seria, number, address = entry
        builder = BuilderClient()
        tmp = builder.setId(str(_ID)).firstName(first_name).secondName(
            second_name)
        if seria is not None and seria != MyConstants.NULL and seria != '' \
                and seria != MyConstants.NONE:
            tmp = tmp.passport(int(seria), int(number))
        if address is not None and address != MyConstants.NULL and address != \
                '' and address != MyConstants.NONE:
            tmp = tmp.address(address)
        return tmp.build()

    def getClientByName(self, first_name: str, second_name: str) -> Client:
        """Возвращает объект клиента по его имени и фамилии"""
        d = {MyConstants.FIRST_NAME: first_name,
             MyConstants.SECOND_NAME: second_name}
        res = getMathEntry(MyConstants.TABLE_USERS, d)[0]
        return self.makeClient(res)

    def getBankById(self, _id) -> Bank:
        """Возвращает объект банка по его id"""
        _ID, name, limit = getEntryById(MyConstants.TABLE_BANKS, _id)
        return Bank(name, Money(limit), _ID)

    def getTransactionById(self, _id) -> Transaction.Transaction:
        """Возвращает объект транзакции по его id"""
        _ID, type_tr, from_acc, other_acc, amount, is_undo = \
            getEntryById(MyConstants.TABLE_TRANSACTIONS, _id)
        acc = self.getBankAccountById(from_acc)
        if type_tr == str(Types.TypeTransaction.TOP_UP):
            return TopUpTransaction(acc, Money(amount), bool(is_undo), _ID)
        if type_tr == str(Types.TypeTransaction.WITHDRAW):
            return WithdrawTransaction(acc, Money(amount), bool(is_undo), _ID)
        if type_tr == str(Types.TypeTransaction.TRANSFER):
            other = self.getBankAccountById(other_acc)
            return TransferTransaction(acc, other, Money(amount),
                                       bool(is_undo), _ID)

    def getBankByName(self, name: str) -> Bank:
        """Возвращает объект банка по его имени"""
        _ID, name_bank, limit = \
            getMathEntry(MyConstants.TABLE_BANKS, {MyConstants.NAME: name})[0]
        return Bank(name, Money(limit), _ID)

    def getClientById(self, _id) -> Client:
        """Возвращает объект клиента по его id"""
        return self.makeClient(getEntryById(MyConstants.TABLE_USERS, _id))

    def gatBankAccountFromEntry(self, entry: tuple) -> BankAccount.BankAccount:
        """Возвращает объект счёта по записи из бд"""
        _ID, balance, id_owner, id_bank, type_acc, end_date, credit_limit, \
        interest_rate, name = entry
        bank = self.getBankById(id_bank)
        res = None
        if int(type_acc) == Types.TypeBankAccount.DEBIT:
            res = BankAccount.DebitAccount(bank, self.getClientById(id_owner),
                                           name, Money(balance), _ID)
        elif int(type_acc) == Types.TypeBankAccount.DEPOSIT:
            res = BankAccount.DepositAccount(bank,
                                             self.getClientById(id_owner),
                                             name, Money(balance), end_date,
                                             _ID)
        elif int(type_acc) == Types.TypeBankAccount.CREDIT:
            res = BankAccount.CreditAccount(bank, self.getClientById(id_owner),
                                            name, Money(balance),
                                            Money(credit_limit), interest_rate,
                                            _ID)
        return res

    def getBankAccountById(self, _id) -> BankAccount.BankAccount:
        """Возвращает объект счёта по его id"""
        return self.gatBankAccountFromEntry(
            getEntryById(MyConstants.TABLE_ACCOUNTS, _id))

    def getAllTransaction(self, user_id: str) -> list:
        """Возвращает все транзакции клиента по id клиента"""
        accounts_by_user = self.getAllAccounts(user_id)
        all_transaction = []
        for acc in accounts_by_user:
            all_transaction += \
                getMathEntry(MyConstants.TABLE_TRANSACTIONS,
                             {
                                 MyConstants.FROM: acc.id_account.id})
            all_transaction += \
                getMathEntry(MyConstants.TABLE_TRANSACTIONS,
                             {
                                 MyConstants.OTHER: acc.id_account.id})
        ans = []
        for transaction in all_transaction:
            _ID, type_tr, id_from, id_other, amount, is_undo = transaction
            acc_from = self.getBankAccountById(id_from)
            if int(type_tr) == Types.TypeTransaction.WITHDRAW:
                ans.append(
                    Transaction.WithdrawTransaction(acc_from, Money(amount),
                                                    bool(int(is_undo)), _ID))
            elif int(type_tr) == Types.TypeTransaction.TOP_UP:
                ans.append(
                    Transaction.TopUpTransaction(acc_from, Money(amount),
                                                 bool(int(is_undo)),
                                                 _ID))
            elif int(type_tr) == Types.TypeTransaction.TRANSFER:
                ans.append(Transaction.TransferTransaction(
                    acc_from,
                    self.getBankAccountById(
                        id_other),
                    Money(amount),
                    bool(int(is_undo)),
                    _ID))
        return ans

    def getAllAccounts(self, user_id: str):
        """Возвращает все счета клиента по id клиента"""
        all_acc = getMathEntry(MyConstants.TABLE_ACCOUNTS,
                               {MyConstants.ID_OWNER: user_id})
        ans = []
        for acc in all_acc:
            ans.append(self.gatBankAccountFromEntry(acc))
        return ans

    def isExistClient(self, first_name: str, second_name: str) -> bool:
        """Возвращает True если клиент есть в бд, False - иначе"""
        d = {MyConstants.FIRST_NAME: first_name,
             MyConstants.SECOND_NAME: second_name}

        if len(getMathEntry(MyConstants.TABLE_USERS, d)) != 0:
            return True
        else:
            return False

    def getAllBanks(self) -> list:
        """Возвращает список всех банков"""
        all_banks = []
        for entry in getAllEntry(MyConstants.TABLE_BANKS):
            _ID, name_bank, limit = entry
            all_banks.append(Bank(name_bank, Money(limit), _ID))
        return all_banks
