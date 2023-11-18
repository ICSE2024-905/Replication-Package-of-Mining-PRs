import os

def get_token():
    filepath = "E:\\GraduationDesign\\utils\\resources\\token.txt"
    with open(filepath, 'r') as reader:
        token = reader.readline()
    return token


def get_mysql_root_psw():
    filepath = "E:\\GraduationDesign\\utils\\resources\\mysql.txt"
    with open(filepath, 'r') as reader:
        username = reader.readline().strip("\n")
        password = reader.readline().strip("\n")
    return username, password


