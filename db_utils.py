import logging

from psycopg_pool import ConnectionPool

token_db_pool = None


def set_token_db_connection(connection_string: str):
    if len(connection_string) > 0:
        global token_db_pool
        token_db_pool = ConnectionPool(conninfo=connection_string, )
        token_db_pool.open(wait=True)
        logging.info("Token DB Setup : Connected")
    else:
        logging.error("Token DB Setup : No DB - Don't run in production!")


def create_account(contact_id: str, full_name: str, nick_name: str, player_type: str = "paid_active"):
    with token_db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
           WITH r1 AS (
                INSERT INTO player_table
                VALUES (uuid_generate_v4(), %(nick_name)s, %(player_type)s)
                RETURNING id AS player_id)
            , r2 AS (
                INSERT INTO player_stats_table (player_id)
                SELECT player_id FROM r1)
            INSERT INTO player_payment_table (contact_id,player_id,full_name)
            SELECT %(contact_id)s,player_id,%(full_name)s FROM r1
            RETURNING player_id;
           """,
                        {"nick_name": nick_name,
                         "player_type": player_type,
                         "contact_id": contact_id.lower(),
                         "full_name": full_name
                         }
                        )




def delete_account(contact_id: str):
    with token_db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT player_id FROM player_payment_table WHERE contact_id = %s"
                        , (contact_id.lower(),))

            result = cur.fetchone()
            if result is None:
                logging.warning("Unable to delete player by contact_id:" + contact_id.lower())
                return False

            logging.warning("Deleting player_id:" + str(result[0]))


            cur.execute("DELETE FROM token_table WHERE player_id = %s;"
                        , (result[0],))

            cur.execute("DELETE FROM player_payment_table WHERE player_id = %s;"
                        , (result[0],))

            cur.execute("DELETE FROM player_stats_table WHERE player_id = %s"
                        , (result[0],))

            cur.execute("DELETE FROM player_table WHERE id = %s;"
                        , (result[0],))

            return True


def add_tokens(contact_id: str, token_count: int):
    with token_db_pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT player_id FROM player_payment_table WHERE contact_id = %s"
                        , (contact_id.lower(),))

            result = cur.fetchone()
            if result is None:
                logging.warning("Unable to add tokens by contact_id:" + contact_id.lower())
                return False

            cur.execute("""
            INSERT INTO token_table(player_id, content, owner_id)
            SELECT %(player_id)s,'{}', %(player_id)s
                FROM generate_series(1,10)
            """
                        , {"player_id": result[0]})

            logging.info(
                f"Created {token_count} tokens for {contact_id} "
            )

            return str(result[0])
    return None
