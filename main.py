import os
import pandas as pd

MATCH_COUNT = 0


def generate_data(my_file):
    with open(my_file) as match_file:
        data_match = match_file.readlines()

    # parse the scores from HTML file and return list of them
    def get_score_list():
        dirty_score = []
        count = 0
        for i in data_match:
            if i.find('<div class="team__scores-kills">') != -1:
                count = 1
                continue
            if count == 1:
                dirty_score.append(i)
                count = 0
        score = []
        for i in dirty_score:
            i = i.strip()
            score.append(i)
        return score

    # parse the heroes from HTML file and return list of them
    def get_heroes_list():
        dirty_data = []
        for i in data_match:
            if i.find("<div class=\"pick\" data-tippy-content=") != -1:
                dirty_data.append(i)
        without_spaces = []
        for hero in dirty_data:
            without_spaces.append(hero.strip())
        clear_hero_names = []
        for i in without_spaces:
            index_to_start = i.find("data-tippy-content=")
            x = len("data-tippy-content=")
            clear_hero_names.append(i[index_to_start + x + 1:-2])
        # print(clear_hero_names)
        return clear_hero_names

    # parse the tournament and teams from HTML file  and return the list of them
    def get_tournament_and_teams():
        my_str = ""
        for i in data_match:
            if i.find("<meta property=\"og:title\" content=\"") != -1:
                x = len("<meta property=\"og:title\" content=\"")
                my_str = i[x + 4:-5]
                break
        local_team_1 = my_str[:my_str.find(" vs ")].strip()
        local_team_2 = my_str[len(local_team_1) + 4:my_str.find(" at ")]
        local_tournament = my_str[my_str.find(" at ") + 4:]
        return [local_team_1, local_team_2, local_tournament]

    # parse the durations from HTML file and return the list of them
    def get_duration_list():
        local_durations = []
        for i in data_match:
            if i.find('<div class="info__duration">') != -1:
                start_index = i.find('">') + 2
                end_index = i.find('</div>')
                local_durations.append(i[start_index:end_index])
        return local_durations

    # parse the side from HTML file and return the list of them
    def get_side_list():
        local_side_list = []
        for i in data_match:
            if i.find('<span class="side ') != -1:
                start_index = i.find('<span class="side ') + len('<span class="side ')
                end_index = i.find('">')
                local_side_list.append(i[start_index:end_index])
        return local_side_list

    # pase the result form HTML file and return the list of them
    def get_results():
        count = 0
        slices_of_data = []
        number_of_line_found_winner = []
        result_list = []
        for i in data_match:
            count += 1
            if i.find('<div class="info__duration">') != -1:
                slices_of_data.append(count)
        for i in range(len(data_match)):
            if data_match[i].find('<div class="winner">win</div>') != -1:
                number_of_line_found_winner.append(i)
        for i in range(len(slices_of_data)):
            if slices_of_data[i] > number_of_line_found_winner[i]:
                result_list.append('WIN')
                result_list.append('LOSE')
            else:
                result_list.append('LOSE')
                result_list.append('WIN')

        return result_list

    def generate_cvs_data_map(results, side_list, duration_list, score_list, heroes_list, tournament_and_teams):
        def get_team(map_index):
            if map_index % 2 == 1:
                return tournament_and_teams[0]
            return tournament_and_teams[1]

        global MATCH_COUNT
        MATCH_COUNT += 1
        str_representation_of_row_in_cvs = ''
        for i in range(1, len(results) + 1):
            pick = ''
            for j in range(1, 6):
                pick += heroes_list[5 * i - j] + ','
            str_representation_of_row_in_cvs += str(MATCH_COUNT) + ',' + str((i - 1) // 2 + 1) + ',' + tournament_and_teams[
                2] + ',' + get_team(i) + ',' \
                                                + side_list[i - 1] + ',' + score_list[i - 1] + ',' + results[
                                                    i - 1] + ',' + duration_list[(i - 1) // 2] + ',' + pick[:-1] + '\n'

        return str_representation_of_row_in_cvs

    return generate_cvs_data_map(get_results(), get_side_list(), get_duration_list(), get_score_list(),
                                 get_heroes_list(),
                                 get_tournament_and_teams())


my_files = os.listdir('matches_row_data')
my_data = []
for i in my_files:
    try:
        match = generate_data('matches_row_data/' + i)
        match = match.split('\n')
        for j in match:
            if len(j) > 10:
                my_data.append(j)
    except UnicodeDecodeError:
        print(("Couldn't read the file: " + i).upper())

columns = ['MATCH_ID', 'MAP', 'TOURNAMENT', 'TEAM', 'SIDE', 'SCORE', 'RESULT', 'DURATION', 'HERO_1', 'HERO_2', 'HERO_3', 'HERO_4', 'HERO_5']
print(my_data)
data = [list(i.replace(', ', '').split(',')) for i in my_data]
print(data)
df = pd.DataFrame(data, columns=columns)
print(df)
df.to_csv(r'generated_data/may_12.csv')
