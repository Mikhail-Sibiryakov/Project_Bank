from src.Structures import Exceptions


class Money:
    """Класс денег, нет погрешности вычислений с плавающей точкой.
    Два знака после запятой.
    Умеет сложение/вычитание, сравнение.
    Магические методы имеют естественный смысл"""

    def __init__(self, *args):
        """Создание объекта денег.
        Может быть создано либо из int - будет воспринято как копейки/центы
        Может быть создано из строки вида "2023.77"
        При невалидных значениях бросает исключение"""
        self.__cents = 0
        if not args:
            self.__cents = 0
        elif len(args) > 1:
            raise Exceptions.InvalidArgMoneyError
        elif isinstance(args[0], str):
            if '.' not in args[0]:
                raise Exceptions.InvalidArgMoneyError
            a, b = args[0].split('.')
            if len(b) == 1:
                b += '0'
            if len(b) > 2 or (not b.isdigit()):
                raise Exceptions.InvalidArgMoneyError
            sign = -1 if a[0] == '-' else 1
            self.__cents = (abs(int(a)) * 100 + int(b)) * sign
        elif isinstance(args[0], int):
            self.__cents = args[0]
        else:
            raise Exceptions.InvalidArgMoneyError

    def __add__(self, other):
        return Money(self.__cents + other.__cents)

    def __sub__(self, other):
        return Money(self.__cents - other.__cents)

    def __int__(self):
        return self.__cents

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return int(self) != int(other)

    def __lt__(self, other):
        return int(self) < int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __str__(self):
        sign = '-' if self.__cents < 0 else ''
        abs_value = abs(self.__cents)
        part = str(abs_value % 100)
        if len(part) < 2:
            part = '0' + part
        return sign + str(abs_value // 100) + '.' + part

    def getPercent(self, percent: str):
        """По строке вида "5.61" возвращает соответствующее значение процента
        от суммы денег объекта
        Возвращает Money"""
        if '.' not in percent:
            raise Exceptions.InvalidArgPercentError
        whole, part = percent.split('.')
        if len(part) == 1:
            part += '0'
        if (not whole.isdigit()) or (not part.isdigit()) or (len(part) != 2):
            raise Exceptions.InvalidArgPercentError
        value = int(self)
        tmp = (value * (int(whole) * 100 + int(part)))
        return Money(tmp // 10 ** 4)

    def getCents(self):
        return self.__cents
