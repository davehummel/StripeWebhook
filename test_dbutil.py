import os

from psycopg.errors import UniqueViolation

import db_utils as du


def test_create_account():
    token_db_connection = os.getenv("TOKEN_DB_CONNECTION")
    if token_db_connection == None :
        assert False,"No TOKEN_DB_CONNECT env variable"
        return
    du.set_token_db_connection(token_db_connection)

    #cleanup just in case
    du.delete_account("Test1@gmail.com")

    du.create_account("Test1@gmail.com","Mr Test 1","testy1")

    try:
        du.create_account("Test1@gmail.com", "Mr Test 1", "testy1")
        assert False,"Inserted same contact_id twice!"
    except UniqueViolation as e:
        pass

    assert du.delete_account('Test1@gmail.com'),"Couldn't delete account"


def test_token_purchase():
    token_db_connection = os.getenv("TOKEN_DB_CONNECTION")
    if token_db_connection == None :
        assert False,"No TOKEN_DB_CONNECT env variable"
        return
    du.set_token_db_connection(token_db_connection)

    #cleanup just in case
    du.delete_account("Test1@gmail.com")

    du.create_account("Test1@gmail.com","Mr Test 1","testy1")

    assert du.add_tokens("Test1@gmail.com",10) is not None, "Couldn't add tokens"

    assert du.delete_account('Test1@gmail.com'),"Couldn't delete account"


