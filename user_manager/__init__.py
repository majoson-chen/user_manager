#!/usr/bin/python3
"""
@version: python3.x
@author:m-jay
@contact: blog.m-jay.cn
@software: PyCharm
@time: 2020-12-2 21:26
"""
from typing import List

"""
    对 Linux 的系统用户进行管理
    请使用root用户运行此模块
    A manger to the user system in Linux with python.
    Please ran this module by root user.
    
    class User:
        info:dict {
            "name": str
            "uid": int
            "gid": int
            "comment": str
            "home_path": str
            "shell_path": str
        }
        
        class Passwd:
            change  () Change the password for this user.
            lock    () lock this user. (disable this user)
            unlock  () unlock this user. (enable this user)
            delete  () delete the pwd of this user.
            keep    () keep pwd not to overdue.
            maximum () set the maximum time does the pwd can be used.
            minimum () set the minimum time does the pwd can be used.
            and more ...
        
"""

import os, subprocess


class UserNotFound(Exception):
    pass


def __create_pipe(cmd: str) -> subprocess.Popen:
    return subprocess.Popen(cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE
                            )


class User:
    class info:
        name: str
        uid: int
        gid: int
        comment: str
        home_path: str
        shell_path: str

    def __init__(self, user_name: str, encoding: str = "utf-8", **kwargs):
        """
        创建一个用户对象, 稍后你可以操作它.
        Create a user obj which you can operate.

        :param user_name: the user name you will operate.
        """
        assert not os.getuid(), "Please use root to operate it."

        if 'string' in kwargs:
            # 是否由 list_users 传入
            self.__translate_info(kwargs['string'])
        else:
            # 当用户主动创建时手动解析
            # /etc/passwd
            # root:x:0:0:root:/root:/bin/bash
            #  ^user name
            with open("/etc/passwd", 'r', encoding=encoding) as fp:
                s = fp.readline()
                while s:
                    if s[:s.find(':')] == user_name:
                        self.__translate_info(s)
                        break

            if not self.__translated:
                raise UserNotFound("Cannot found the user in system")

    def __translate_info(self, string: str):
        # 用户名: 口令:用户标识号: 组标识号:注释性描述: 主目录:登录Shell
        result = string.split(':')
        self.info.name = result[0]
        self.info.uid = int(result[2])
        self.info.gid = int(result[3])
        self.info.comment = result[4]
        self.info.home_path = result[5]
        self.info.shell_path = result[6]

        self.__translated = True


def list_users(encoding: str = "utf-8") -> List[User]:
    """
    List all the user in this system
    :param encoding: which the encoding way to open the system file.
    :return: A user obj see the class `User`
    """
    users: list = []
    with open("/etc/passwd", 'r', encoding=encoding) as fp:
        s = fp.readline()
        while s:
            users.append(User('', string=s))
            s = fp.readline()
    return users
