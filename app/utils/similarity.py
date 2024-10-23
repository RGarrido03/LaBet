from typing import List


# Opcao com a bilioteca
def levenshtein_distance(s1: str, s2: str) -> int:
    """
  Calcula a distância de Levenshtein entre duas strings.
  """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def find_most_similar_levenshtein(target: str, name_list: List[str]) -> tuple:
    """
  Encontra o nome mais similar usando distância de Levenshtein.
  Retorna uma tupla com o nome mais similar e sua distância.
  """
    distances = [(name, levenshtein_distance(target.lower(), name.lower()))
                 for name in name_list]
    return min(distances, key=lambda x: x[1])


# Exemplo de uso
def compare_names(target: str, name_list: List[str]):
    """
  Compara um nome alvo com uma lista de nomes usando ambos os métodos.
  """
    lev_result = find_most_similar_levenshtein(target, name_list)

    return {
        'levenshtein': {
            'nome_similar': lev_result[0],
            'distancia': lev_result[1]
        }
    }



# Opcao feita a mao
def levenshtein_distance(s1, s2):
    # Inicializa uma matriz com zeros
    matrix = [[0 for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]
    # Inicializa a primeira linha e a primeira coluna com os índices
    for i in range(len(s1) + 1):
        matrix[i][0] = i
    for j in range(len(s2) + 1):
        matrix[0][j] = j
    # Preenche a matriz usando a fórmula do algoritmo de Levenshtein
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            matrix[i][j] = min(matrix[i - 1][j] + 1,  # Remoção
                               matrix[i][j - 1] + 1,  # Inserção
                               matrix[i - 1][j - 1] + cost)  # Substituição
    # O valor na célula inferior direita da matriz é a distância de edição
    return matrix[len(s1)][len(s2)]


# Exemplo de uso
s1 = "sl benfica"
s2 = "benfica"
print("Distância de edição entre '{}' e '{}': {}".format(s1, s2, levenshtein_distance(s1, s2)))
