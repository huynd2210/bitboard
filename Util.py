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

def flip_movements(movements):
    """
    Flips the movements by rotating them 180 degrees.

    :param movements: List of tuples representing the movements.
    :return: List of tuples representing the flipped movements.
    """
    return [(-x, -y) for x, y in movements]

if __name__ == '__main__':
    # from functools import reduce
    #
    # # Example list
    # numbers = [32,123,43]
    #
    # # XOR everything in the list
    # result = reduce(lambda x, y: x ^ y, numbers)
    #
    # print("XOR result:", result)

    tiger_movements = [(1, 0), (-1, 0), (0,-1)]
    flipped_tiger_movements = flip_movements(tiger_movements)

    print(f"Original: {tiger_movements}")
    print(f"Flipped: {flipped_tiger_movements}")

