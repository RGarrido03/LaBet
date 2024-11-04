import json
from unidecode import unidecode


def generate_insert_statements(data):
    insert_statements = []
    for club in data["ClubData"]:
        statement = f"INSERT INTO app_team (id, name, abbreviation, logo, sport_id, normalized_name) VALUES ({club['ID']}, '{club['Name'].replace("'", "''")}', '{club['ShortName']}', '{club['ImageURL']}', 1, '{unidecode(club['Name']).lower().replace("'", "''")}');"
        insert_statements.append(statement)
    return insert_statements


f = open("clubs.json", "r")
data = json.load(f)
insert_statements = generate_insert_statements(data)

with open("data.sql", "w") as f:
    f.write("INSERT INTO app_sport (id, name) VALUES (1, 'Football');" + "\n")
    for stmt in insert_statements:
        f.write(stmt + "\n")
