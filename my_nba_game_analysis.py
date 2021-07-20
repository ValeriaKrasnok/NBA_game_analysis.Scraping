import re
import copy

file = open("nba_game_blazers_lakers_20181018.txt", "r")
play_by_play_moves = file.read()
player_template = {"player_name": None, "FG": 0, "FGA": 0, "FG%": 0, "3P": 0, "3PA": 0, "3P%": 0, "FT": 0, "FTA": 0, "FT%": 0, "ORB": 0, "DRB": 0, "TRB": 0, "AST": 0, "STL": 0, "BLK":0, "TOV": 0, "PF": 0, "PTS": 0}
home_team = {"name": None, "players_data": []}
away_team = {"name": None, "players_data": []}

def print_nba_game_stats(team_dict):
    print("Players	FG	FGA	FG%	3P	3PA	3P%	FT	FTA	FT%	ORB	DRB	TRB	AST	STL	BLK	TOV	PF	PTS") #headers
    team_data = {"FG": 0, "FGA": 0, "FG%": 0, "3P": 0, "3PA": 0, "3P%": 0, "FT": 0, "FTA": 0, "FT%": 0, "ORB": 0, "DRB": 0, "TRB": 0, "AST": 0, "STL": 0, "BLK":0, "TOV": 0, "PF": 0, "PTS": 0}
    for player in team_dict["players_data"]:
        print('  '.join(str(x) for x in list(player.values())))
        team_data["FG"] += player["FG"]
        team_data["FGA"] += player["FGA"]
        team_data["FG%"] = round(team_data["FG"]/ team_data["FGA"], 3)
        team_data["3P"] += player["3P"]
        team_data["3PA"] += player["3PA"]
        team_data["3P%"] = round(team_data["3P"]/ team_data["3PA"], 3)
        team_data["FT"] += player["FT"]
        team_data["FTA"] += player["FTA"]
        team_data["FT%"] = round(team_data["FT"]/ team_data["FTA"], 3)
        team_data["ORB"] += player["ORB"]
        team_data["DRB"] += player["DRB"]
        team_data["TRB"] = team_data["ORB"] + team_data["DRB"] 
        team_data["AST"] += player["AST"]
        team_data["STL"] += player["STL"]
        team_data["BLK"] += player["BLK"]
        team_data["TOV"] += player["TOV"]
        team_data["PF"] += player["PF"]
        team_data["PTS"] += player["PTS"]

    print('Team Totals', '  '.join(str(x) for x in list(team_data.values())))


def analyse_nba_game(play_by_play_moves): #reate a function which receives an array of play and will return a dictionary summary of the game
    game_array = play_by_play_moves.split('\n') # split raw strings into an array of events
    result = {"home_team": home_team, "away_team": away_team}
    first_event = game_array[0].split("|") #first event = first string from the array of play 
    home_team["name"] = first_event[4] #assign name of the home team
    away_team["name"] = first_event[3] #assign name of the away team
    for event in game_array: #for each event in this game
        event = event.split("|") #split each event by |
        determine_event_and_process(event)
    # iterate over each team's player and process the analytics
    for player in home_team["players_data"]: #for each player from home team calculate nba indicators
        process_player_nba_indicators(player)
    for player in away_team["players_data"]:
        process_player_nba_indicators(player)
    print_nba_game_stats(home_team)


def scored_2pt(event, relevant_team): #create a function that calculates points for "made 2-pt" events
    description = event[7] #from description extract all needed info
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0] #assign the first name in event to player from relevant team 
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name) 
    player_object["FG"]+=1 #if a player from relevant team made a 2-pt (hook shot, jump, dunk, etc.), add 1 point to FG 
    player_object["FGA"]+=1
    player_object["PTS"]+=2 #PTS includes FG and FT 
    if "assist by" in description:
        player_assister_name = re.findall("[A-Z]. [A-z]+", description)[1] 
        assist_player_object = find_player_in_team_or_create(relevant_team["players_data"], player_assister_name) #find or add this assister to the relevant team  
        assist_player_object["AST"]+=1 

def scored_3pt(event, relevant_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["FG"]+=1 #if a player from relevant team made a 3-pt jump (hook shot, etc.), add 1 point to FG, FGA, 1 point to 3P and 3 points to PTS
    player_object["FGA"]+=1
    player_object["3P"]+=1
    player_object["3PA"]+=1
    player_object["PTS"]+=3
    if "assist by" in description:
        player_assister_name = re.findall("[A-Z]. [A-z]+", description)[1]
        assist_player_object = find_player_in_team_or_create(relevant_team["players_data"], player_assister_name)        
        assist_player_object["AST"]+=1

def missed_2pt(event, relevant_team, opponent_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["FGA"]+=1 
    if "block by" in description:
        player_blocker_name = re.findall("[A-Z]. [A-z]+", description)[1]
        block_player_object = find_player_in_team_or_create(opponent_team["players_data"], player_blocker_name)        
        block_player_object["BLK"]+=1

def missed_3pt(event, relevant_team, opponent_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["FGA"]+=1 
    player_object["3PA"]+=1 
    if "block by" in description:
        player_blocker_name = re.findall("[A-Z]. [A-z]+", description)[1]
        block_player_object = find_player_in_team_or_create(opponent_team["players_data"], player_blocker_name)        
        block_player_object["BLK"]+=1   

def scored_free_throw(event,relevant_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["FT"]+=1 
    player_object["FTA"]+=1 
    player_object["PTS"]+=1 

def missed_free_throw(event,relevant_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["FTA"]+=1

def made_off_rebound(event,relevant_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["ORB"]+=1  
 
def made_def_rebound(event,relevant_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["DRB"]+=1 

def made_turnover(event,relevant_team,opponent_team):
    description = event[7]
    player_relevant_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(relevant_team["players_data"], player_relevant_name)
    player_object["TOV"]+=1 
    if "steal by" in description:
        player_stealer_name = re.findall("[A-Z]. [A-z]+", description)[1]
        steal_player_object = find_player_in_team_or_create(opponent_team["players_data"], player_stealer_name)        
        steal_player_object["STL"]+=1   

def made_foul(event,opponent_team):
    description = event[7]
    player_opp_name = re.findall("[A-Z]. [A-z]+", description)[0]
    player_object = find_player_in_team_or_create(opponent_team["players_data"], player_opp_name)
    player_object["PF"]+=1 

def process_player_nba_indicators(player_object):
    if player_object["FGA"] is not 0: 
        player_object["FG%"] = round((player_object["FG"] / player_object["FGA"]), 3) #round float to 3 digits after dot
    if player_object["3PA"] is not 0:
        player_object["3P%"] = round((player_object["3P"] / player_object["3PA"]), 3)
    if player_object["FTA"] is not 0:
        player_object["FT%"] = round((player_object["FT"] / player_object["FTA"]), 3)
    player_object["TRB"] = player_object["ORB"] + player_object["DRB"]


def determine_event_and_process(event): #this function will determine each event and process it with help of oher functions above
    description = event[7]
    relevant_team = home_team if event[2]==event[4] else away_team #assign name of relevant team to the name of home team
    opponent_team = away_team if event[2]==event[4] else home_team #in other case assign the name of opponent_team to away_team
    if "makes 2-pt" in description: 
        scored_2pt(event,relevant_team)
    if "makes 3-pt" in description:
        scored_3pt(event,relevant_team)
    if "misses 2-pt" in description:
        missed_2pt(event,relevant_team,opponent_team)
    if "misses 3-pt" in description:
        missed_3pt(event,relevant_team,opponent_team)
    if "makes free throw" in description:
        scored_free_throw(event,relevant_team)
    if "misses free throw" in description:
        missed_free_throw(event,relevant_team)
    if "Offensive rebound" in description and "Offensive rebound by Team" not in description:
        made_off_rebound(event,relevant_team)
    if "Defensive rebound" in description and "Defensive rebound by Team" not in description:
        made_def_rebound(event,relevant_team)
    if "Turnover by" in description and "Turnover by Team" not in description:
        made_turnover(event,relevant_team,opponent_team)
    if "Personal foul by" in description:
        made_foul(event,opponent_team)
    

def find_player_in_team_or_create(team, player_relevant_name): #create a function that defines if a player exists or should be created 
    for team_player in team:  
        if team_player["player_name"] == player_relevant_name: #if this team player exists (if was found his name in an array)
            return team_player #return this team player and continue to work with him 
    else: #if this team player doesn't exist
        player_object = copy.deepcopy(player_template) #create a copy of player_template
        player_object["player_name"] = player_relevant_name #assign his name to player_relevant_name
        team.append(player_object) #and add him to the team array
        return player_object 

analyse_nba_game(play_by_play_moves)





