import uuid
import random
import os

import DbConnector

database_connection = DbConnector.DbConnector()


def clean_link(_link):
    cleaned_link = _link[_link.index('wiki-schools'):].replace("%25", "%")
    cleaned_link = cleaned_link.replace("/", "\\")
    return cleaned_link


def de_clean_link(_link):
    return _link[_link.index('wiki-schools'):].replace("%", "%25")


def get_distance(_current_page_id, _target_page_id):
    return 3 # IMPORTANT: This is only a TEMPORARY FIX to improve performance since no distance feedback is provided and all missions have the same initial distance
    sql_statement = "SELECT path_length FROM path_lengths WHERE (page_id = %s) AND (target_page_id = %s) LIMIT 1"
    sql_args = (_current_page_id, _target_page_id)
    sql_result = database_connection.execute(sql_statement, sql_args, "SELECT")

    if len(sql_result) <= 0:
        return -1

    return sql_result[0]['path_length']


def get_page_amount():
    sql_statement = "SELECT COUNT(id) AS amount FROM pages"
    sql_args = ()
    sql_result = database_connection.execute(sql_statement, sql_args, "SELECT")
    return sql_result[0]["amount"]


def get_page_random():
    page_amount = get_page_amount()
    random_id = random.randint(0, page_amount)
    sql_statement = "SELECT * FROM pages WHERE id = %s LIMIT 1"
    sql_args = random_id
    sql_result = database_connection.execute(sql_statement, sql_args, "SELECT")
    return sql_result[0]


def get_page(_id):
    sql_statement = "SELECT * FROM pages WHERE id = %s LIMIT 1"
    sql_result = database_connection.execute(sql_statement, _id, "SELECT")

    sql_result[0]['url'] = sql_result[0]['link'].replace(os.path.sep, "/").replace("%", "%25")
    return sql_result[0]


def create_game_random():
    start_page = get_page_random()
    goal_page = get_page_random()
    game_name = str(uuid.uuid4())

    new_game = {"game_name": game_name, "start_page": start_page, "goal_page": goal_page}
    sql_statement = "INSERT INTO games (game_name,start_page_id,goal_page_id) VALUES(%s,%s,%s)"
    sql_args = (game_name, start_page['id'], goal_page['id'])
    database_connection.execute(sql_statement, sql_args, "INSERT")
    database_connection.commit()

    return new_game


def get_page_by_link(_link):
    stripped_link = clean_link(_link)
    sql_statement = "SELECT id FROM pages WHERE link = %s LIMIT 1"
    page_result = database_connection.execute(sql_statement, stripped_link, "SELECT")

    if len(page_result) == 0:
        return None

    return get_page(page_result[0]['id'])


def fetch_hubs(_page, _max_distance, _limit):
    current_influence = 0
    influence_query = database_connection.execute('SELECT influence '
                                                  'FROM hub_mapping '
                                                  'WHERE hub_id = %s '
                                                  'LIMIT 1',
                                                  _page['id'],
                                                  "SELECT")
    if len(influence_query) > 0:
        current_influence = influence_query[0]['influence']

    related_hubs = list()
    sql_statement = 'SELECT hub_id ' \
                    'FROM hub_mapping ' \
                    'WHERE (node_id = %s) ' \
                    'AND (influence > %s)' \
                    'AND (distance < %s) ' \
                    'ORDER BY distance ASC'
    hubs = database_connection.execute(sql_statement, (_page['id'], current_influence, _max_distance), "SELECT")

    count = 0

    for hub in hubs:
        if count >= _limit:
            break
        related_hubs.append(get_page(hub['hub_id']))
        count += 1

    return related_hubs


def fetch_game(_id):
    sql_statement = "SELECT * from games WHERE id = %s LIMIT 1"
    game = database_connection.execute(sql_statement, _id, "SELECT")

    distance = get_distance(game[0]['start_page_id'], game[0]['goal_page_id'])
    new_game = {"game_name": game[0]['game_name'], "start_page": get_page(game[0]['start_page_id']),
                "goal_page": get_page(game[0]['goal_page_id']), "distance": distance}
    return new_game


def fetch_list(_name):
    sql_statement = "SELECT * FROM gamelists WHERE name = %s LIMIT 1"
    gamelist = database_connection.execute(sql_statement, _name, "SELECT")
    return gamelist[0]


def update_session(_session_id, _gamelist_name, _gamelist_index, _user_id, _completed, _tutorial_completed, _mission_list):
    exist_check = database_connection.execute("SELECT id "
                                              "FROM gamesessions "
                                              "WHERE session_id = %s "
                                              "LIMIT 1",
                                              _session_id,
                                              "SELECT")
    print("USER ID: " + _user_id)
    if len(exist_check) != 0:
        sql_statement = "UPDATE gamesessions " \
                        "SET list_name = %s, list_index = %s, completed = %s , tutorial_completed = %s, mission_list = %s" \
                        "WHERE session_id = %s " \
                        "LIMIT 1"
        database_connection.execute(sql_statement, (_gamelist_name, _gamelist_index, _completed, _tutorial_completed, _mission_list, _session_id), "UPDATE")

    else:
        sql_statement = "INSERT INTO gamesessions (user_id, list_name, list_index, session_id, tutorial_completed, mission_list) " \
                        "VALUES (%s, %s, %s, %s, %s, %s)"
        database_connection.execute(sql_statement, (_user_id, _gamelist_name, _gamelist_index, _session_id, _tutorial_completed, _mission_list), "INSERT")

    database_connection.commit()


def fetch_session(_session_id):
    session_data = database_connection.execute("SELECT * "
                                               "FROM gamesessions "
                                               "WHERE session_id = %s "
                                               "AND completed = 0",
                                               _session_id,
                                               "SELECT")

    if len(session_data) == 0:
        return False

    print('########################################')
    print("RESTORING")
    print('########################################')
    session_data = session_data[0]
    if session_data['completed']:
        return False
    else:
        return session_data