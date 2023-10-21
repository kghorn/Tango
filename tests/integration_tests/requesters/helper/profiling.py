def print_profiling_stats(message_times: list):
    '''Print average messaging rates, durations, etc. for an array of messaging times.

    https://chess.stackexchange.com/questions/2506/what-is-the-average-length-of-a-game-of-chess
    '''

    rate = len(message_times) / sum(message_times)
    print("")
    print(f"Message rate:     {rate:,.0f} messages/second")
    print(f"Message duration: {1_000_000/rate:.2f} μs")
    print(f"Mean chess games per second: {rate/40:,.0f} games (40 moves/game on average)")