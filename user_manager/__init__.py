#!/usr/bin/python3
"""
@version: python3.x
@author:m-jay
@contact: blog.m-jay.cn
@software: PyCharm
@time: 2020-12-2 21:26
"""
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
from typing import List, Union, Optional
import os,time
import subprocess

ENCODING: str = "utf-8"


# assert not os.getuid(), "Please use root to operate it."


class UserNotFoundError(Exception):
    pass


class CreateUserFailed(Exception):
    pass


class DeleteUserFailed(Exception):
    pass


class ModifyUserFailed(Exception):
    pass


def _create_pipe(cmd: str) -> subprocess.Popen:
    return subprocess.Popen(cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )


class _INFO:
    name: str
    uid: int
    gid: int
    comment: str
    home_path: str
    shell_path: str


class User:
    info: _INFO

    def __init__(self, user_name: str, **kwargs):
        """
        创建一个用户对象, 稍后你可以操作它.
        Create a user obj which you can operate.

        :param user_name: the user name you will operate.
        """

        self.info = _INFO()
        self.__translated = False

        if 'string' in kwargs:
            # 是否由 list_users 传入
            self.__translate_info(kwargs['string'])
        else:
            # 当用户主动创建时手动解析
            # /etc/passwd
            # root:x:0:0:root:/root:/bin/bash
            #  ^user name
            with open("/etc/passwd", 'r', encoding=ENCODING) as fp:
                s = fp.readline()
                while s:
                    if s[:s.find(':')] == user_name:
                        self.__translate_info(s)
                        break
                    s = fp.readline()

            if not self.__translated:
                raise UserNotFoundError("Cannot found the user in system")

    def __translate_info(self, string: str):
        # 用户名: 口令:用户标识号: 组标识号:注释性描述: 主目录:登录Shell
        string = string.rstrip()
        result = string.split(':')
        self.info.name = result[0]
        self.info.uid = int(result[2])
        self.info.gid = int(result[3])
        self.info.comment = result[4]
        self.info.home_path = result[5]
        self.info.shell_path = result[6]

        self.__translated = True

    def __refresh(func):
        """
        装饰器,用于更新用户状态
        """

        def warpper(self, *args, **kwargs):
            r = func(self, *args, **kwargs)
            self.__init__(self.info.name)
            return r

        return warpper

    def chpwd(self, passwd: str):
        """
            更改用户的密码
            change the passwd for this user.
        """
        passwd += '\n'
        pipe = _create_pipe(f'passwd --stdin {self.info.name}')
        pipe.communicate(passwd.encode('utf-8'))
        pipe.wait(5)
        pipe.kill()


    def lock(self):
        """
        锁定此账户,此后将不能登录
        Lock this user, after that this user will not abole to login.
        :return:
        """
        pipe = _create_pipe(f'passwd --lock {self.info.name}')
        pipe.wait(5)
        if pipe.poll() != 0:
            raise ModifyUserFailed("Modify the user failed.: \n" + pipe.stderr.read().decode(ENCODING))
        pipe.kill()

    def unlock(self):
        """
        解锁此用户,允许此用户的登陆. 解锁前请确保你已经设置密码
        Unlock this user, after that we will allow this user to login.
        Before you unlock this user, making sure you had been set the passwd yet.
        :return:
        """
        pipe = _create_pipe(f'passwd --unlock {self.info.name}')
        pipe.wait(5)
        if pipe.poll() != 0:
            raise ModifyUserFailed("Modify the user failed.: \n" + pipe.stderr.read().decode(ENCODING))
        pipe.kill()

    @__refresh
    def modify(self, **kwargs):
        """
        修改用户信息,可以使用同 `add_user` 函数相同的参数.
        modify the user info, use the same params with def `add_user`

        :param comment:str
            任何字符串。通常是关于登录的简短描述，当前用于用户全名。
            Any string. Usually a short description of the login, currently used for the full name of the user.

        :param home_dir:str
            新创建的用户将会使用 home_dir 作为他的登陆目录.
            The new user will be created using HOME_DIR as the value for the user's login directory.

        :param move_home:bool
            当时修改了用户的家目录时是是否同时移动该目录?
            when you change the home dir, do you want to move the dir at the same time?

            此项默认为真.
            This is default to True.

        :param expire_date:str
            用户过期的时间, 使用 YYYY-MM-DD 的格式表示.
            The date on which the user account will be disabled. The date is specified in the format YYYY-MM-DD.

        :param inactive:str
            密码过期后，账户被彻底禁用之前的天数。0 表示立即禁用
            The number of days before the account is completely disabled after the password has expired. 0 means disable immediately

        :param group:str
            用户初始登陆组的组名或号码。组名必须已经存在。组号码必须指代已经存在的组。
            the main group this user belongs to.

        :param groups:str
            用户的从属组,可以有多个,使用逗号隔开
            A list of supplementary groups which the user is also a member of. Each group is separated from the next by a comma, example "gp1,a,b,c"

        :param append_to_group:bool
            将用户追加至上边 groups 中提到的附加组中，并不从其它组中删除此用户.
            Append this user to the groups list at above, and don't remove this user at the other groups.

        :param shell_path:str
            指定用户登录的Shell脚本的路径.
            set the path to the shell script where the user logs in.

        :param uid:str
            为这个用户设置 uid.
            set the uid for this user.

        :param non-unique_uid:bool
            是否是不唯一的UID,如果设置为 True, 则允许创建与之ID相同的用户
            Whether it is the non-unique uid. If set to True, users with the same ID are allowed to be created.
        """
        s = "usermod "
        if 'comment' in kwargs:
            s += f"""--comment "{kwargs['comment']}" """
        if 'home_dir' in kwargs:
            s += f"""--home "{kwargs['home_dir']}" """
            if kwargs.get('move_home'):
                s += "--move-home "
        if 'expire_date' in kwargs:
            s += f"--expiredate {kwargs['expire_date']} "
        if 'inactive' in kwargs:
            s += f"--inactive {kwargs['inactive']} "
        if 'group' in kwargs:
            s += f"--gid {kwargs['group']} "
        if 'groups' in kwargs:
            s += f"--groups {kwargs['groups']} "
            if kwargs.get("append_to_group"):
                s += "--append "
        if 'shell_path' in kwargs:
            s += f"""--shell "{kwargs['shell_path']}" """
        if 'uid' in kwargs:
            s += f"--uid {kwargs['uid']} "
            if 'non-unique_uid' in kwargs:
                s += '--non-unique '

        s += self.info.name

        print(s)

        pipe = _create_pipe(s)
        pipe.wait(5)
        if pipe.poll() == 0:
            # succeed.
            pipe.kill()
        else:
            pipe.kill()
            raise ModifyUserFailed(
                "Modify the user failed.: \n" + pipe.stderr.read().decode(ENCODING)
            )


def list_users() -> List[User]:
    """
    List all the user in this system
    :return: A user obj see the class `User`
    """
    users: list = []
    with open("/etc/passwd", 'r', encoding=ENCODING) as fp:
        s = fp.readline()
        while s:
            users.append(User('', string=s))
            s = fp.readline()
    return users


def add_user(
        user_name: str,
        base_dir: str = "",
        comment: str = "",
        home_dir: str = "",
        have_home: bool = True,
        expire_date: str = "",
        inactive: str = "",
        group: str = "",
        groups: str = "",
        have_group: bool = True,
        system_user: bool = False,
        shell_path: str = "",
        uid: str = "",
        unique_uid: bool = True,
) -> User:
    """
    创建一个账户,成功后返回它的 User 对象, 如果你留空其他参数,将会使用默认方式创建
    Create a user in system, if it was succeed, return a user obj of this user.
    If you want to get more info for the args, see the help in shell `useradd`
    :param user_name:
        欲创建的用户名
        The user name you will be create.

    :param base_dir:
        如果没有指定家目录，则使用 base_dir.
        The default base directory for the system if HOME_DIR is not specified. BASE_DIR is concatenated with the account name to define the home directory.

    :param comment:
        任何字符串。通常是关于登录的简短描述，当前用于用户全名。
        Any string. Usually a short description of the login, currently used for the full name of the user.

    :param home_dir:
        新创建的用户将会使用 home_dir 作为他的登陆目录.
        The new user will be created using HOME_DIR as the value for the user's login directory.
    :param have_home:
        如果设置为 True ,将不创建家目录,这个选项会覆盖上面的 home_dir 选项
        if you set this in True, we will not create a directory , this will override param `home_dir`
    :param expire_date:
        用户过期的时间, 使用 YYYY-MM-DD 的格式表示.
        The date on which the user account will be disabled. The date is specified in the format YYYY-MM-DD.

    :param inactive:
        密码过期后，账户被彻底禁用之前的天数。0 表示立即禁用
        The number of days before the account is completely disabled after the password has expired. 0 means disable immediately

    :param group:
        用户初始登陆组的组名或号码。组名必须已经存在。组号码必须指代已经存在的组。
        the main group this user belongs to.

    :param groups:
        用户的从属组,可以有多个,使用逗号隔开
        A list of supplementary groups which the user is also a member of. Each group is separated from the next by a comma, example "gp1,a,b,c"

    :param have_group:
        如果设置为 False, 将不会设置用户组, 覆盖上面的 group 和 groups 参数
        If set to False, the user group will not be set, and the `group` and `groups` param will be override.

    :param system_user:
        欲创建的用户是否为系统用户?
        Is the user to be created a system user?

    :param shell_path:
        指定用户登录的Shell脚本的路径.
        set the path to the shell script where the user logs in.

    :param uid:
        为这个用户设置 uid.
        set the uid for this user.

    :param unique_uid:
        是否是唯一的UID,如果设置为 False, 则允许创建与之ID相同的用户
        Whether it is the unique uid. If set to false, users with the same ID are allowed to be created.

    :return: A User object. See `user_manger.User()`
    """

    s = "useradd "
    if base_dir:
        s += f"""--base-dir "{base_dir}" """
    if comment:
        s += f"""--comment "{comment}" """
    if home_dir and have_home:
        s += f"""--create-home --home-dir "{home_dir}" """
    if not have_home:
        s += "--no-create-home "
    if expire_date:
        s += f"--expiredate {expire_date} "
    if inactive:
        s += f"--inactive {inactive} "
    if group and have_group:
        s += f"--gid {group} "
    if groups and have_group:
        s += f"--groups {groups} "
    if not have_group:
        s += "--no-user-group "
    if system_user:
        s += "--system "
    if shell_path:
        s += f"""--shell "{shell_path}" """
    if uid:
        s += f"--uid {uid} "
    if not unique_uid:
        s += "--non-unique "

    s += user_name

    pipe = _create_pipe(s)
    pipe.wait(5)
    if pipe.poll() == 0:
        # succeed.
        pipe.kill()
        return User(user_name)
    else:
        pipe.kill()
        raise CreateUserFailed(
            "Create the user failed.: \n" + pipe.stderr.read().decode(ENCODING)
        )


def del_user(
        user_name: str,
        remove_home: bool = False,
        remove_all_files: bool = False,
        backup: bool = False,
        backup_to: str = "",
        system: bool = False
):
    """
    删除一个用户, 如果失败,抛出错误
    delete a user.
    :param user_name:
        欲移除的用户名
        The user name you will remove.
    :param remove_home:
        删除用户时顺便删除他的家目录
        remove the users home directory and mail spool
    :param remove_all_files:
        删除该用户所有的全部文件
        remove all files owned by user
    :param backup:
        在删除用户之前备份所有文件, 如果你设置此项为真,确保你同时传入了 `back_to` 参数
        backup files before removing. If you set this to true, make sure you pass in `back_to` at the same time.
    :param backup_to:
        备份的目标目录, 配合 `backup` 参数使用.
        target directory for the backups. Use with the `backup` parameter.
    :param system:
        当该用户时系统用户时才删除它.
        only remove if system user
    """

    s = "userdel "
    if remove_home:
        s += "--remove-home "
    if remove_all_files:
        s += "--remove-all-files "
    if backup:
        assert backup_to, "If you set `backup` to True, please take a arg to `backup_to`"
        s += f"--backup --backup-to {backup_to} "
    if system:
        s += "--system "

    s += user_name

    pipe = _create_pipe(s)
    pipe.wait(5)

    if pipe.poll() != 0:
        pipe.kill()
        raise DeleteUserFailed(pipe.stderr.read().decode(ENCODING))
    else:
        pipe.kill()
        return True
