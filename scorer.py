import xml.etree.ElementTree as ET
import collections

# Configuration
PRINT_COMMENTARY = 0
PRINT_SCORECARD = 1

# Constants
MAX_OVERS_PER_INNINGS = 20
MAX_OVERS_PER_BOWLER = MAX_OVERS_PER_INNINGS / 5
BALLS_PER_OVER = 6
ADD_WIDES_NOBALLS_TO_BOWLERS_CONCEDED_RUNS = 0

# Functions
def oversBowled( balls ):
    "Given ball count, return overs in 0.0 format"
    overs_integer = int(balls) // BALLS_PER_OVER
    overs_fraction = (int(balls) % BALLS_PER_OVER)
    overs_bowled = str(overs_integer) + '.' + str(overs_fraction)
    return overs_bowled

# Containers
##card_batting = [collections.OrderedDict(), collections.OrderedDict()] # ordered dictionary
##batsman_status = [{}, {}]                                             # regular dictionary
##card_bowling = [collections.OrderedDict(), collections.OrderedDict()] # ordered dictionary
card_batting = []   # ordered dictionary
batsman_status = [] # regular dictionary
card_bowling = []   # ordered dictionary
innings_index = 0   # keep track of innings

# Begin parsing input file
tree = ET.parse('commentary.xml')
commentary = tree.getroot()
for innings in commentary:
    card_batting.append(collections.OrderedDict())
    batsman_status.append({})
    card_bowling.append(collections.OrderedDict())
    team = innings.attrib.get('team')
    total = 0
    ball_count = 0
    batsman_count = 0
    bowler_count = 0
    wicket_count = 0
    over = 0
    over_sub = 0
    runs_this_over = 0
    extras_wide = 0
    extras_noball = 0
    extras_legbye = 0
    extras_bye = 0
    extras_total = 0
    for ball in innings:
        order = int(ball.attrib.get('order'))
        delivery = ball.attrib.get('delivery')
        bowler = ball.find('bowler').text
        striker = ball.find('striker').text
        nonstriker = ball.find('nonstriker').text
        runs = int(ball.find('runs').text)
        runs_type = ball.find('runs').attrib.get('type')    # expecting: boundary, bye, leg bye
        total = total + runs
        over = int(ball_count) // BALLS_PER_OVER            # '//' forces integer division
        over_sub = (int(ball_count) % BALLS_PER_OVER) + 1   # 1 added for indexing 1-6

        #----------------------------------------------------------------------------
        # Batting total and extras
        #----------------------------------------------------------------------------
        if delivery == 'wide':
            total = total + 1
            extras_wide = extras_wide + 1 + runs
            if PRINT_COMMENTARY == 1:
                print(str(over).zfill(2) + '.' + str(over_sub), bowler, 'to', striker, '-->', runs, 'runs', '(WIDE)')
        elif delivery == 'no ball':
            total = total + 1
            # if the striker scores runs, these are counted for his score
            # else, all runs counted towards noball
            extras_noball = extras_noball + 1 + runs
            if PRINT_COMMENTARY == 1:
                print(str(over).zfill(2) + '.' + str(over_sub), bowler, 'to', striker, '-->', runs, 'runs', '(NO BALL)')
        elif delivery == 'leg bye':
            ball_count = ball_count + 1
            extras_legbye = extras_legbye + runs
            if PRINT_COMMENTARY == 1:
                print(str(over).zfill(2) + '.' + str(over_sub), bowler, 'to', striker, '-->', runs, 'runs', '(Leg Bye)')
        elif delivery == 'bye':
            ball_count = ball_count + 1
            extras_bye = extras_bye + runs
            if PRINT_COMMENTARY == 1:
                print(str(over).zfill(2) + '.' + str(over_sub), bowler, 'to', striker, '-->', runs, 'runs', '(Bye)')
        elif delivery == 'ok':
            ball_count = ball_count + 1
            if PRINT_COMMENTARY == 1:
                print(str(over).zfill(2) + '.' + str(over_sub), bowler, 'to', striker, '-->', runs, 'runs')

        #----------------------------------------------------------------------------
        # Wicket
        #----------------------------------------------------------------------------
        wicket = ball.find('wicket')
        if wicket != None:
            wicket_count = wicket_count + 1
            
            style = wicket.attrib.get('style')
            if style == 'caught':
                style_sh = 'c'
            elif style == 'stumped':
                style_sh = 'st'
            elif style == 'runout':
                style_sh = 'run out'
            elif style == 'bowled':
                style_sh = 'b'
            elif style == 'lbw':
                style_sh = 'lbw'
            elif style == 'hit wicket':
                style_sh = 'h/w'
            elif style == 'retired':
                style_sh = 'retired out'
            else:
                style_sh = ''
            
            victim = wicket.find('victim').text
            fielder = wicket.find('fielder')
            if fielder != None:
                fielder = fielder.text
                if style == 'runout':
                    if PRINT_COMMENTARY == 1:
                        print('     OUT (#' + str(wicket_count) + '):', victim, style_sh, '(' + fielder + ')')
                    batsman_status[innings_index][victim] = style_sh + ' (' + fielder + ')'
                else:
                    if PRINT_COMMENTARY == 1:
                        print('     OUT (#' + str(wicket_count) + '):', victim, style_sh, fielder, 'b', bowler)
                    batsman_status[innings_index][victim] = style_sh + ' ' + fielder + ' b ' + bowler
            else:
                if style == 'retired':
                    if PRINT_COMMENTARY == 1:
                        print('     OUT (#' + str(wicket_count) + '):', victim, style_sh)
                    batsman_status[innings_index][victim] = style_sh
                elif style == 'bowled':
                    if PRINT_COMMENTARY == 1:
                        print('     OUT (#' + str(wicket_count) + '):', victim, style_sh, bowler)
                    batsman_status[innings_index][victim] = style_sh + ' ' + bowler
                else:
                    if PRINT_COMMENTARY == 1:
                        print('     OUT (#' + str(wicket_count) + '):', victim, style_sh, 'b', bowler)
                    batsman_status[innings_index][victim] = style_sh + ' b ' + bowler
        else:
            batsman_status[innings_index][striker] = 'not out'
            batsman_status[innings_index][nonstriker] = 'not out'

        #----------------------------------------------------------------------------
        # Batting Record
        #----------------------------------------------------------------------------
        # Add striker details to scorecard
        if striker not in card_batting[innings_index]:
            # batsman is not yet on the scorecard; add name and details
            sample_data_batting = {'Order' : 0, 'Status' : 'not out', 'Runs' : 0, 'Balls' : 0, '4s' : 0, '6s' : 0, '0s' : 0, 'S/R' : 0.00}
            card_batting[innings_index][striker] = sample_data_batting;
            batsman_count = batsman_count + 1
            card_batting[innings_index][striker]['Order'] = batsman_count

        if delivery == 'ok':
            card_batting[innings_index][striker]['Runs'] = card_batting[innings_index][striker]['Runs'] + runs
            card_batting[innings_index][striker]['Balls'] = card_batting[innings_index][striker]['Balls'] + 1
            if runs_type == 'boundary':
                if runs == 4:
                    card_batting[innings_index][striker]['4s'] = card_batting[innings_index][striker]['4s'] + 1
                elif runs == 6:
                    card_batting[innings_index][striker]['6s'] = card_batting[innings_index][striker]['6s'] + 1
            if runs == 0:
                card_batting[innings_index][striker]['0s'] = card_batting[innings_index][striker]['0s'] + 1
            card_batting[innings_index][striker]['S/R'] = "{0:.2f}".format((card_batting[innings_index][striker]['Runs'] / card_batting[innings_index][striker]['Balls']) * 100, 2)
        elif delivery == 'no ball':
            # If the batsman hits the ball and takes runs, these are scored as runs by the batsman.
            # Runs may also be scored without the batsman hitting the ball, but these are recorded as No ball extras rather than byes or leg byes.
            if runs_type == 'boundary|offthebat' or runs_type == 'offthebat':
                card_batting[innings_index][striker]['Runs'] = card_batting[innings_index][striker]['Runs'] + runs
                if runs_type == 'boundary':
                    if runs == 4:
                        card_batting[innings_index][striker]['4s'] = card_batting[innings_index][striker]['4s'] + 1
                    elif runs == 6:
                        card_batting[innings_index][striker]['6s'] = card_batting[innings_index][striker]['6s'] + 1
                card_batting[innings_index][striker]['S/R'] = "{0:.2f}".format((card_batting[innings_index][striker]['Runs'] / card_batting[innings_index][striker]['Balls']) * 100, 2)

        # Add the nonstriker to the scorecard
        if nonstriker not in card_batting[innings_index]:
            sample_data_batting = {'Order' : 0, 'Status' : 'not out', 'Runs' : 0, 'Balls' : 0, '4s' : 0, '6s' : 0, '0s' : 0, 'S/R' : 0.00}
            card_batting[innings_index][nonstriker] = sample_data_batting;
            batsman_count = batsman_count + 1
            card_batting[innings_index][nonstriker]['Order'] = batsman_count

        #----------------------------------------------------------------------------
        # Bowling Record
        #----------------------------------------------------------------------------
        # Add bowling details to scorecard
        bowlers_wicket = ['caught', 'stumped', 'bowled', 'lbw', 'hit wicket'] # excludes runout and retired
        if bowler not in card_bowling[innings_index]:
            # bowler is not yet on the scorecard; add name and details
            sample_data_bowling = {'Order' : 0, 'Balls' : 0, 'Maidens' : 0, 'Runs' : 0, 'Wickets' : 0, 'E/R' : 0.00, 'Wides' : 0, 'No Balls' : 0, '4s' : 0, '6s' : 0, '0s' : 0}
            card_bowling[innings_index][bowler] = sample_data_bowling;
            bowler_count = bowler_count + 1
            card_bowling[innings_index][bowler]['Order'] = bowler_count

        if delivery == 'wide':
            card_bowling[innings_index][bowler]['Wides'] = card_bowling[innings_index][bowler]['Wides'] + 1 + runs
            if ADD_WIDES_NOBALLS_TO_BOWLERS_CONCEDED_RUNS > 0:
                card_bowling[innings_index][bowler]['Runs'] = card_bowling[innings_index][bowler]['Wides']
        elif delivery == 'nb':
            card_bowling[innings_index][bowler]['No Balls'] = card_bowling[innings_index][bowler]['No Balls'] + 1 + runs
            if ADD_WIDES_NOBALLS_TO_BOWLERS_CONCEDED_RUNS > 0:
                card_bowling[innings_index][bowler]['Runs'] = card_bowling[innings_index][bowler]['No Balls']
        else: # delivery == 'ok'
            card_bowling[innings_index][bowler]['Balls'] = card_bowling[innings_index][bowler]['Balls'] + 1
            runs_this_over = runs_this_over + runs
            if card_bowling[innings_index][bowler]['Balls'] % BALLS_PER_OVER == 0:
                if runs_this_over == 0:
                    card_bowling[innings_index][bowler]['Maidens'] = card_bowling[innings_index][bowler]['Maidens'] + 1
                runs_this_over = 0
            card_bowling[innings_index][bowler]['Runs'] = card_bowling[innings_index][bowler]['Runs'] + runs
            if wicket != None:
                if style in bowlers_wicket:
                    card_bowling[innings_index][bowler]['Wickets'] = card_bowling[innings_index][bowler]['Wickets'] + 1
            if runs_type == 'boundary':
                if runs == 4:
                    card_bowling[innings_index][bowler]['4s'] = card_bowling[innings_index][bowler]['4s'] + 1
                elif runs == 6:
                    card_bowling[innings_index][bowler]['6s'] = card_bowling[innings_index][bowler]['6s'] + 1
            if runs == 0:
                card_bowling[innings_index][bowler]['0s'] = card_bowling[innings_index][bowler]['0s'] + 1

    if PRINT_COMMENTARY == 1:
        print('\n')
    if PRINT_SCORECARD == 1:
        print(team + ' scorecard:')
        print('------------------------------------------------------------------------------------------------------')
        print('No. ' + 'Batsman'
              + '\t\t' + 'Status'
              + '{:45}'.format(' ') + '{:>3}'.format('R')
              + ' ' + '{:>3}'.format('B')
              + ' ' + '{:>7}'.format('S/R')
              + '  | ' + '{:>2}'.format('4s')
              + ' ' + '{:>2}'.format('6s')
              + ' ' + '{:>2}'.format('0s'))
        print('--------------------------------------------------------------------------------------------+---------')
        for key, value in card_batting[innings_index].items():
            if len(key) > 11:
                gap = '\t'
            else:
                gap = '\t\t'
            print(str(card_batting[innings_index][key]['Order']).zfill(2) + '. ' + key
                  + gap + '{:50}'.format(batsman_status[innings_index][key])
                  + ' ' + '{:>3}'.format(card_batting[innings_index][key]['Runs'])
                  + ' ' + '{:>3}'.format(card_batting[innings_index][key]['Balls'])
                  + ' ' + '{:>7}'.format(card_batting[innings_index][key]['S/R'])
                  + '  | ' + '{:>2}'.format(card_batting[innings_index][key]['4s'])
                  + ' ' + '{:>2}'.format(card_batting[innings_index][key]['6s'])
                  + ' ' + '{:>2}'.format(card_batting[innings_index][key]['0s']))
        extras_str = '(' + 'b ' + str(extras_bye) + ', lb ' + str(extras_legbye) + ', nb ' + str(extras_noball) + ', w ' + str(extras_wide) + ')'
        extras_total = extras_wide + extras_noball + extras_legbye + extras_bye
        print('......................................................................................................')
        print('    ' + 'Extras' + '\t\t' + '{:50}'.format(extras_str) + ' ' + '{:>3}'.format(str(extras_total)))
        print('------------------------------------------------------------------------------------------------------')
        overs_bowled = str(over + (over_sub // 6)) + '.' + str(over_sub % 6)
        total_str = '(' + str(wicket_count) + ' wickets; ' + str(overs_bowled) + ' overs)'
        print('    ' + 'Total' + '\t\t' + '{:50}'.format(total_str) + ' ' + '{:>3}'.format(str(total)))
        print('')
        print('---------------------------------------------------------------------')
        print('No. ' + 'Bowler'
              + '\t\t' + '{:>4}'.format('O')
              + ' '    + '{:>3}'.format('M')
              + ' '    + '{:>3}'.format('R')
              + ' '    + '{:>3}'.format('W')
              + ' '    + '{:>5}'.format('E/R')
              + '\t| ' + '{:>3}'.format('Wd')
              + ' '    + '{:>3}'.format('NB')
              + ' '    + '{:>3}'.format('4s')
              + ' '    + '{:>3}'.format('6s')
              + ' '    + '{:>3}'.format('0s'))
        print('------------------------------------------------+--------------------')
        for key, value in card_bowling[innings_index].items():
            card_bowling[innings_index][key]['E/R'] = '{:.2f}'.format(card_bowling[innings_index][key]['Runs'] / float(oversBowled(card_bowling[innings_index][key]['Balls'])))
            if len(key) > 11:
                gap = '\t'
            else:
                gap = '\t\t'
            print(str(card_bowling[innings_index][key]['Order']).zfill(2) + '. ' + key
                  + gap + '{:>4}'.format(oversBowled(card_bowling[innings_index][key]['Balls']))
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['Maidens'])
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['Runs'])
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['Wickets'])
                  + ' ' + '{:>5}'.format(card_bowling[innings_index][key]['E/R'])
                  + '\t| ' + '{:>3}'.format(card_bowling[innings_index][key]['Wides'])
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['No Balls'])
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['4s'])
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['6s'])
                  + ' ' + '{:>3}'.format(card_bowling[innings_index][key]['0s']))
        print('---------------------------------------------------------------------')
        innings_index = innings_index + 1
        print('')
