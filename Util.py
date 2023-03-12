import psycopg2

def connectPostgres(host, databaseName, user, password, port):
    conn = psycopg2.connect(
        host=host,
        database=databaseName,
        user=user,
        password=password,
        port=port
    )
    return conn

def saveState(state):
    conn = connectPostgres('127.0.0.1', 'postgres', 'postgres', 'postgres', 5432)
    cursor = conn.cursor()
    sql = 'insert into states(state_id, player1_board, player2_board, current_player, isEnd, winner, parent_id) values (%s, %s, %s, %s, %s, %s, %s) returning state_id;'
    cursor.execute(sql, (state))
    conn.commit()

    conn.close()