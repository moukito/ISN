from model.QLearningAgent import QLearningAgent

for _ in range(1000000):
    game = [[0 for _ in range(5)] for _ in range(5)]

    for i in range(5):
        game[i].insert(0, 3)
        game[i].insert(len(game[i]), 3)

    game.insert(0, [3 for _ in range(7)])
    game.insert(len(game), [3 for _ in range(7)])

    game[1][-2] = 1

    game[-2][-2] = 2

    PLAY = True
    WIN = 1
    MOVE = 1 / 50
    GAMEOVER = -10

    def find_p():
        for i in range(1, len(game) - 1):
            for j in range(1, len(game[i]) - 1):
                if game[i][j] == 1:
                    return i, j

    def up():
        x, y = find_p()
        if game[x - 1][y] not in [2, 3]:
            game[x][y], game[x - 1][y] = game[x - 1][y], game[x][y]
            return MOVE
        elif game[x - 1][y] == 2:
            return WIN
        else:
            return GAMEOVER

    def down():
        x, y = find_p()
        if game[x + 1][y] not in [2, 3]:
            game[x][y], game[x + 1][y] = game[x + 1][y], game[x][y]
            return MOVE
        elif game[x + 1][y] == 2:
            return WIN
        else:
            return GAMEOVER

    def left():
        x, y = find_p()
        if game[x][y - 1] not in [2, 3]:
            game[x][y], game[x][y - 1] = game[x][y - 1], game[x][y]
            return MOVE
        elif game[x][y - 1] == 2:
            return WIN
        else:
            return GAMEOVER

    def right():
        x, y = find_p()
        if game[x][y + 1] not in [2, 3]:
            game[x][y], game[x][y + 1] = game[x][y + 1], game[x][y]
            return MOVE
        elif game[x][y + 1] == 2:
            game[x][y], game[x][y + 1] = 0, game[x][y]
            return WIN
        else:
            return GAMEOVER

    actions = [up, down, left, right]

    model = QLearningAgent(actions, exploration_rate=0.5)

    while PLAY:
        state = tuple(find_p())
        action = model.choose_action(state)
        reward = actions[action]()

        model.update_q_table(state, action, reward, find_p())

        if reward == WIN or reward == GAMEOVER:
            PLAY = False

    model.save_state(model.q_state)
    model.save_table(model.q_load)
    if _ % 1000 == 0:
        print(f"Episode {_} done")
print("Training done")
