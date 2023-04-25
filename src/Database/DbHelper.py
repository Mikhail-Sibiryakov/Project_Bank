import sqlite3 as sq
from src.Helpers.MyConstants import MyConstants
from src.Helpers.StringHelper import string_wrapper


def getEntryById(table_name: str, _id) -> tuple:
    """Возвращает запись из таблицы table_name с id = _id"""
    return getMathEntry(table_name, {MyConstants.ID: _id})[0]


def getMathEntry(table_name: str, parameters: dict) -> list:
    """Возвращает запись из таблицы table_name, которая подходит по
    произвольным параметрам вида {столбец: значение}, заданным с
    помощью словаря"""
    with sq.connect(MyConstants.DB_NAME) as connect:
        cursor = connect.cursor()
        keys = tuple(parameters.keys())
        command = "SELECT * FROM " + table_name + " WHERE " + keys[0] + " == " \
                  + string_wrapper(parameters[keys[0]])
        for i in range(1, len(keys)):
            if parameters[keys[i]] == "NULL":
                command += " and " + keys[i] + " is NULL"
                continue
            command += " and " + keys[i] + " == " + \
                       string_wrapper(parameters[keys[i]])
        cursor.execute(command)
        res = cursor.fetchall()
    return res


def getAllEntry(table_name: str) -> list:
    """Возвращает все записи из таблицы table_name"""
    with sq.connect(MyConstants.DB_NAME) as connect:
        cursor = connect.cursor()
        command = "SELECT * FROM " + table_name
        cursor.execute(command)
        res = cursor.fetchall()
    return res


def deleteMathEntry(table_name: str, parameters: dict):
    """Удаляет запись из таблицы table_name, которая подходит по
        произвольным параметрам вида {столбец: значение}, заданным с
        помощью словаря"""
    with sq.connect(MyConstants.DB_NAME) as connect:
        cursor = connect.cursor()
        keys = tuple(parameters.keys())
        command = "DELETE FROM " + table_name + " WHERE " + keys[0] + " == " + \
                  string_wrapper(parameters[keys[0]])
        for i in range(1, len(keys)):
            if parameters[keys[i]] == "NULL":
                command += " and " + keys[i] + " is NULL"
                continue
            command += " and " + keys[i] + " == " + \
                       string_wrapper(parameters[keys[i]])
        cursor.execute(command)
