# user_manager
 A python project which can manage the users or groups in linux.  
 By this module, you can oprate the users in a simple and automatic way.

## install
```shell
pip install user_manager
or
python setup.py install
```

## how to use

example:
- select a user and modify it.
   ```python
   import user_manager

   user = user_manager.User ("jay")
   user.chpwd("123456") #change passwd to `123456`

   user.modify(comment="This is the user named jay.")

   ```
- create a user and delete it
   ```python
   import user_manager
   user = user_manager.add_user ("test") # create a user named test.
   user.chpwd ("123456") #change passwd to `123456`
    #modify the user

   # if you want to know more arguments, pluase see the tips on this module.

   user_manager.del_user (user.info.name)
   ```
- list all the users and traverse it.
    ```python
    import user_manager
    users = user_manager.list_users () # get the user list.
    for i in users:
        print ("User: ", i.info.name)
    # traverse the user list an print the user name.

    ```