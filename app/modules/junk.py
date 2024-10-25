from datasketch import MinHash, MinHashLSH


# Função para gerar MinHash a partir de uma string
def minhash_string(s):
    m = MinHash()
    for word in s.split():
        m.update(word.encode("utf8"))
    return m


# Lista de equipes padronizadas
team_names = ["Burgo CF", "FC Barcelona", "Real Madrid", "Atletico Madrid"]

# Criar MinHash LSH
lsh = MinHashLSH(threshold=0.5, num_perm=128)
team_minhashes = {}

# Adicionar MinHashes para cada equipe na LSH
for team in team_names:
    m = minhash_string(team)
    lsh.insert(team, m)
    team_minhashes[team] = m

# Verificar o nome de entrada
input_name = "Real Burgo CF"
input_minhash = minhash_string(input_name)
result = lsh.query(input_minhash)

print(result)  # Vai imprimir ['Burgo CF'] se for similar o suficiente


import difflib


def get_most_similar_name(input_name, possible_names):
    return difflib.get_close_matches(input_name, possible_names, n=1, cutoff=0.5)


team_names = ["Sport Boys", "FC Barcelona", "Real Madrid", "Atletico Madrid"]

input_name = "Sport Boys Association"
most_similar_name = get_most_similar_name(input_name, team_names)
print(
    most_similar_name[0] if most_similar_name else "Nenhuma correspondência encontrada"
)
