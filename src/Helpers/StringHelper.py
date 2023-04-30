def string_wrapper(s: str) -> str:
    """Оборачивает строку в одинарные кавычки"""
    return "'" + str(s) + "'"


def tuple_wrapper(t: tuple) -> str:
    """Возвращает строку из кортежа аналогично стандартному print(tuple)"""
    result = '('
    for i in range(len(t)):
        result += string_wrapper(t[i])
        if i + 1 != len(t):
            result += ', '
    return result + ')'


def getIntDate(s) -> list:
    """Возвращает целочисленный список из строки-даты со значениями даты"""
    s = str(s)
    return [int(i) for i in s.split('-')]
