from bs4 import BeautifulSoup
from urllib.request import urlopen

class ProbDist(dict):
    """A Probability Distribution; an {outcome: probability} mapping."""
    def __init__(self, mapping=(), **kwargs):
        self.update(mapping, **kwargs)
        # Make probabilities sum to 1.0; assert no negative probabilities
        total = sum(self.values())
        for outcome in self:
            self[outcome] = self[outcome] / total
            assert self[outcome] >= 0

    def p(event, space):
        """The probability of an event, given a sample space of outcomes.
        event: a collection of outcomes, or a predicate that is true of outcomes in the event.
        space: a set of outcomes or a probability distribution of {outcome: frequency} pairs."""

        # if event is a predicate it, "unroll" it as a collection
        if is_predicate(event):
            event = such_that(event, space)

        # if space is not an equiprobably collection (a simple set),
        # but a probability distribution instead (a dictionary set),
        # then add (union) the probabilities for all favorable outcomes
        if isinstance(space, ProbDist):
            return sum(space[o] for o in space if o in event)

        # simplest case: what we played with in our previous lesson
        else:
            return Fraction(len(event & space), len(space))

    is_predicate = callable

# Here we either return a simple collection in the case of equiprobable outcomes, or a dictionary collection in the
# case of non-equiprobably outcomes
def such_that(predicate, space):
    """The outcomes in the sample pace for which the predicate is true.
    If space is a set, return a subset {outcome,...} with outcomes where predicate(element) is true;
    if space is a ProbDist, return a ProbDist {outcome: frequency,...} with outcomes where predicate(element) is true."""
    if isinstance(space, ProbDist):
        return ProbDist({o:space[o] for o in space if predicate(o)})
    else:
        return {o for o in space if predicate(o)}

def joint(A, B, sep=''):
    """The joint distribution of two independent probability distributions.
    Result is all entries of the form {a+sep+b: P(a)*P(b)}"""
    return ProbDist({a + sep + b: A[a] * B[b]
                    for a in A
                    for b in B})

standings_before_singapore_gp = ['https://web.archive.org/web/20190916070017/https://www.formula1.com/en/results.html/2019/drivers.html']
driver_points_before_singapore = []
driver_first_names = []
driver_last_names = []
for driver in standings_before_singapore_gp:
    html = urlopen('' + driver)
    soup = BeautifulSoup(html.read(), 'lxml')
    for pts in soup.find_all("td", class_="dark bold"):
        total_points = pts.get_text()
        driver_points_before_singapore.append(int(total_points))
    driver_first_names.append([item.get_text()[0] for item in soup.select("span.hide-for-tablet")])
    driver_first_names = driver_first_names[0]
    driver_last_names.append([item.get_text()[0] for item in soup.select("span.hide-for-mobile")])
    driver_last_names = driver_last_names[0]
driver_full_names = ([''.join(full_name) for full_name in zip(driver_first_names, driver_last_names)])
driver_standings_before_singapore = dict(zip(driver_full_names, driver_points_before_singapore))
driver_points_after_singapore = []
driver_first_names1 = []
driver_last_names1 = []
SGP = ProbDist(driver_standings_before_singapore)

standings_after_singapore_gp = ['https://www.formula1.com/en/results.html/2019/drivers.html']
for driver1 in standings_after_singapore_gp:
    html1 = urlopen('' + driver1)
    soup1 = BeautifulSoup(html1.read(), 'lxml')
    for pts1 in soup1.find_all("td", class_="dark bold"):
        total_points1 = pts1.get_text()
        driver_points_after_singapore.append(int(total_points1))
    driver_first_names1.append([item1.get_text()[0] for item1 in soup1.select("span.hide-for-tablet")])
    driver_first_names1 = driver_first_names1[0]
    driver_last_names1.append([item1.get_text()[0] for item1 in soup1.select("span.hide-for-mobile")])
    driver_last_names1 = driver_last_names1[0]
driver_full_names1 = ([''.join(full_name1) for full_name1 in zip(driver_first_names1, driver_last_names1)])
driver_standings_after_singapore = dict(zip(driver_full_names1, driver_points_after_singapore))
RGP = ProbDist(driver_standings_after_singapore)

driver_win_both = {k: SGP[k]*RGP[k] for k in SGP}

print("\033[1m" + "Question 1.1 (20 points)" + "\033[0m" + "\n")
print("Probability Distribution for each F1 driver to win the Singaporean Grand Prix: " + str(SGP) + "\n")
print("Probability Distribution for each F1 driver to win both Singaporean and Russian Grand Prix: " + str(driver_win_both) + "\n")

after_singapore_constructors_url = ['https://www.bbc.com/sport/formula1/constructors-world-championship/standings']
auto_manufacturers_after_singapore = []
constuctors_total_points_list_after_singapore = []
for constructor in after_singapore_constructors_url:
    html = urlopen('' + constructor)
    soup = BeautifulSoup(html.read(), 'lxml')
    for points in soup.find_all("td", class_="table__cell table__cell--right"):
        points_string = points.get_text()
        constuctors_total_points_list_after_singapore.append(int(points_string))
    for teams in soup.find_all("td", class_="table__cell table__cell--left table__cell--bold"):
        team_string = teams.get_text()
        auto_manufacturers_after_singapore.append(team_string)

team_standings_after_singapore = dict(zip(auto_manufacturers_after_singapore, constuctors_total_points_list_after_singapore))
points_gotten_in_singapore = {'Mercedes': 22, 'Ferrari': 43, 'Red Bull': 23, 'McLaren': 6, 'Renault': 2, 'Toro Rosso': 4, 'Racing Point': 0, 'Alfa Romeo': 1, 'Haas': 26, 'Williams': 1}
team_standings_before_singapore = {key: team_standings_after_singapore[key] - points_gotten_in_singapore.get(key, 0) for key in team_standings_after_singapore.keys()}

SGP_teams = ProbDist(team_standings_before_singapore) # Team Probability Distribution for Singapore after Italy Grand Prix
RGP_teams = ProbDist(team_standings_after_singapore) # Team Probability Distribution for Russia after Singapore Grand Prix

team_win_both = {k: SGP_teams[k]*RGP_teams[k] for k in SGP_teams}
team_win_atleast_one = {k: SGP_teams[k]+RGP_teams[k] for k in SGP_teams}

print("Mercedes Win Both: " + str(round((team_win_both.get('Mercedes'))*100,2)) + " %" + "\n")
print("Mercedes Win Atleast One: " + str(round((team_win_atleast_one.get('Mercedes'))*100,2)) + " %" + "\n")
print("Ferrari Win Both: " + str(round((team_win_both.get('Ferrari'))*100,2)) + " %" + "\n")
print("Ferrari Win Atleast One: " + str(round((team_win_atleast_one.get('Ferrari'))*100,2)) +  " %" + "\n")
print("Red Bull Win Both: " + str(round((team_win_both.get('Red Bull'))*100,2)) + " %" + "\n")
print("Red Bull Win Atleast One: " + str(round((team_win_atleast_one.get('Red Bull'))*100,2)) + " %" + "\n")
print("Renault Win Both: " + str(round((team_win_both.get('Renault'))*100,2)) + " %" + "\n")
print("Renault Win Atleast One: " + str(round((team_win_atleast_one.get('Renault'))*100,2)) + " %" + "\n")

print("\033[1m" + "Question 1.2 (30 points)" + "\033[0m" + "\n")

TeamTeam = joint(SGP_teams, RGP_teams, ' ')

def mercedes_and_mercedes(outcome): return 'Mercedes' in outcome and 'Mercedes' in outcome
mercedes_win_2 = such_that(mercedes_and_mercedes, TeamTeam)
print("If Mercedes wins the first race, probability that Mercedes wins the next one is: " + str(round(mercedes_win_2.get('Mercedes Mercedes')*100, 2)) + " %" + "\n")

def ferrari_and_ferrari(outcome): return 'Ferrari' in outcome and 'Ferrari' in outcome
ferrari_win_2 = such_that(ferrari_and_ferrari, TeamTeam)
print("If Ferrari wins the first race, probability that Ferrari wins the next one is: " + str(round(ferrari_win_2.get('Ferrari Ferrari')*100, 2)) + " %" + "\n")

def redbull_and_redbull(outcome): return 'Red Bull' in outcome and 'Red Bull' in outcome
redbull_win_2 = such_that(redbull_and_redbull, TeamTeam)
print("If Red Bull wins the first race, probability that Red Bull wins the next one is: " + str(round(redbull_win_2.get('Red Bull Red Bull')*100, 2)) + " %" + "\n")

def renault_and_renault(outcome): return 'Renault' in outcome and 'Renault' in outcome
renault_win_2 = such_that(renault_and_renault, TeamTeam)
print("If Renault wins the first race, probability that Renault wins the next one is: " + str(round(renault_win_2.get('Renault Renault')*100, 2)) + " %" + "\n")

mercedes_win_both = team_win_both.get('Mercedes')
mercedes_win_atleast_one = team_win_atleast_one.get('Mercedes')
print("If Mercedes wins at least one of the two races, probability that Mercedes wins both is: " + str(round(((mercedes_win_both/mercedes_win_atleast_one)*100),2)) + " %" + "\n")

ferrari_win_both = team_win_both.get('Ferrari')
ferrari_win_atleast_one = team_win_atleast_one.get('Ferrari')
print("If Ferrari wins at least one of the two races, probability that Ferrari wins both is: " + str(round(((ferrari_win_both/ferrari_win_atleast_one)*100),2)) + " %" + "\n")

redbull_win_both = team_win_both.get('Red Bull')
redbull_win_atleast_one = team_win_atleast_one.get('Red Bull')
print("If Red Bull wins at least one of the two races, probability that Red Bull wins both is: " + str(round(((redbull_win_both/redbull_win_atleast_one)*100),2)) + " %" + "\n")

renault_win_both = team_win_both.get('Renault')
renault_win_atleast_one = team_win_atleast_one.get('Renault')
print("If Renault wins at least one of the two races, probability that Renault wins both is: " + str(round(((renault_win_both/renault_win_atleast_one)*100),2)) + " %" + "\n")


print("\033[1m" + "Question 1.3 (50 points)" + "\033[0m" + "\n")
weather_dict = {'Rain': 0.2, 'Sun': 0.2, 'Clouds': 0.2, 'Snow': 0.2, 'Fog': 0.2}
weather_probability_dist = ProbDist(weather_dict) # unneccesary but follows previous convention

TeamWeather_SGP = joint(SGP_teams, weather_probability_dist)
TeamWeather_RGP = joint(RGP_teams, weather_probability_dist)

TeamWeather_SGP_TeamWeather_RGP = joint(TeamWeather_SGP, TeamWeather_RGP)

condition = 'MercedesRain'

mercedes_wins_one_on_rainy = [value for key, value in TeamWeather_SGP_TeamWeather_RGP.items() if (condition in key)]
mercedes_win_both = team_win_both.get('Mercedes')
print("Given Mercedes wins one of the two races on a rainy day, probability that Mercedes wins both races is: " + str(round((mercedes_win_both/sum(mercedes_wins_one_on_rainy)*100), 2)) + " %")
