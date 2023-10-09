

def team_goals_over(team, matches, n_matches, n_goals, home_away_all):
    goals_array = []
    counter = 0
    if len(matches) > 1:
        if home_away_all == 'all':
            for x in matches[:n_matches]:
                if x['home_id'] == team:
                    if x['score']['fulltime']['home'] > n_goals:
                        goals_array.append(x)
                else:
                    if x['score']['fulltime']['away'] > n_goals:
                        goals_array.append(x)
        elif home_away_all == 'home':
            for x in matches:
                if x['home_id'] == team:
                    counter += 1
                    if x['score']['fulltime']['home'] > n_goals:
                        goals_array.append(x)
                        if counter == n_matches:
                            break

        else:
            for x in matches:
                if x['away_id'] == team:
                    counter += 1
                    if x['score']['fulltime']['away'] > n_goals:
                        goals_array.append(x)
                        if counter == n_matches:
                            break

    return len(goals_array)


##No Goals##
def team_no_goals_for_against(team, matches, n_matches, no_goals_for):
    no_goals_array = []
    if len(matches) > 1 and no_goals_for:
        for x in matches[:n_matches]:
            if x['home_id'] == team:
                if x['score']['fulltime']['home'] == 0:
                    no_goals_array.append(x)
            else:
                if x['score']['fulltime']['away'] == 0:
                    no_goals_array.append(x)
    elif len(matches) > 1 and not no_goals_for:
        for x in matches[:n_matches]:
            if x['home_id'] == team:
                if x['score']['fulltime']['away'] == 0:
                    no_goals_array.append(x)
            else:
                if x['score']['fulltime']['home'] == 0:
                    no_goals_array.append(x)
    else:
        pass
    return len(no_goals_array)


def team_no_score_draw(matches, n_matches):
    no_score_array = []
    if len(matches) > 1:
        for x in matches[:n_matches]:
            if x['score']['fulltime']['home'] == 0 and x['score']['fulltime']['away'] == 0:
                no_score_array.append(x)
    return len(no_score_array)