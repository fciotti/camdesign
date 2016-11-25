import csv


def read(filename):
    x = []
    y = []
    levels = []

    with open(filename) as file:
        lines = csv.reader(file, delimiter=';')

        # Checking input file format
        cc = len(next(lines))
        if cc not in [2, 3]:
            raise ValueError
        file.seek(0)

        for line in lines:
            if len(line) != cc:
                raise ValueError
            pos = list(map(float, line))
            if cc == 2:
                x.append(pos[0])
                y.append(pos[1])
            elif cc == 3:
                levels.append(pos)
                if pos[1] == 0:
                    x.append(pos[0])
                    y.append(pos[2])
                else:
                    x.append(pos[0])
                    y.append(pos[2])
                    x.append(pos[0] + pos[1])
                    y.append(pos[2])

    # Matching last and first element
    if cc == 2:
        x.append(x[0] + 1)
        y.append(y[0])
    elif cc == 3:
        levels.append(levels[0][:])
        levels[-1][0] += 1
        x.append(levels[-1][0])
        y.append(levels[-1][2])
    return x, y, levels


def write(filename, x, y):
    with open(filename, 'w') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(zip(x, y))
