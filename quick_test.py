def progress_bar(current, total, bar_length=20):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '

    return f'Progress: [{arrow}{padding}] {int(fraction*100)}% '

test_str = 'a'
for i in range(1, 20):
    # print(f"\rprogress_bar(i, 10))
    print(f"\r{progress_bar(i, 20)}: {test_str}", end='', flush=True)