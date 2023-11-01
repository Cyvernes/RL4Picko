from dice import *

def ab_strat(grill: list[bool], me: int, op: int):

    # initialisation
    previous_choices = 0
    nb_available_dice = N_DICE
    score = 0

    dice_results = draw_dice(nb_available_dice)
    (choice, exp_score) = strategy(dice_results, previous_choices, nb_available_dice, score)
    
    # continue until no more dice to pick
    while choice >= 0:
        previous_choices |= (1 << choice)
        nb_available_dice -= dice_results[choice]
        score += (5 if choice == 0 else choice)*dice_results[choice]

        dice_results = draw_dice(nb_available_dice)
        (choice, exp_score) = strategy(dice_results, previous_choices, nb_available_dice, score)
    
    # choose domino
    if score == op:
        return score

    for dom in range(score, DOMINO_MIN-1, -1):
        if grill[dom]:
            return dom

    return 0