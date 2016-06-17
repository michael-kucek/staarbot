def get_col_w(array):
    rows = len(array)
    cols = len(array[0])
    max_len = []
    big_len = []
    for j in range(cols):
        small_len = []
        for i in range(rows):
            small_len.append(len(array[i][j]))
        big_len.append(small_len)
    for row in big_len:
        max_len.append(max(row))
    return max_len

def create_table(array):
    response = '```'
    max_len = get_col_w(array)
    for row in array:
        for i in range(len(row)):
            if len(row[i]) < max_len[i]:
                ws = max_len[i] - len(row[i])
                # even
                if ws % 2 == 0:
                    response += " " * (ws // 2) + row[i] + " " * (ws // 2)
                else:
                    response += " " * (ws // 2) + row[i] + " " * (ws // 2 + 1)
            else:
                response += row[i]
            if i != len(row) - 1:
                response += '|'
        response += '\n'
    response += '```'
    return response


test_array = [['a1a', 'b1', 'c1aasdfklja'], ['a2', 'baa2', 'c2']]
