import pulp
import pandas as pd

MAX_GOALKEEPER = 2
MAX_DEFENDER = 5
MAX_MIDFIELDER = 5
MAX_FORWARD = 1
MY_BUDGET = 20.9
MIN_PRICE_PER_PLAYER = 0.5
NO_PLAYERS = 13
MAX_BUDGET = MY_BUDGET - MIN_PRICE_PER_PLAYER * (NO_PLAYERS - MAX_FORWARD - MAX_MIDFIELDER - MAX_DEFENDER - MAX_GOALKEEPER)

print(MAX_BUDGET)

# Przykładowe dane
data = {
    "ID": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    "position": ["Forward", "Midfielder", "Defender", "Goalkeeper", "Forward", "Defender", "Midfielder", "Forward", "Defender", "Goalkeeper", "Forward", "Midfielder", "Defender", "Midfielder", "Goalkeeper", "Forward", "Midfielder"],
    "price": [4.5, 5.0, 4.0, 4.5, 5.5, 3.5, 6.0, 4.0, 5.0, 3.5, 4.5, 5.5, 4.0, 6.5, 4.0, 5.0, 4.5],
    "name": ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6", "Player 7", "Player 8", "Player 9", "Player 10", "Player 11", "Player 12", "Player 13", "Player 14", "Player 15", "Player 16", "Player 17"],
    "club": ["Club A", "Club A", "Club B", "Club C", "Club C", "Club A", "Club B", "Club B", "Club C", "Club A", "Club A", "Club B", "Club C", "Club B", "Club A", "Club B", "Club C"],
    "points": [20, 30, 25, 15, 28, 12, 33, 21, 26, 14, 19, 27, 29, 24, 18, 22, 23]
}

# Wczytanie danych do DataFrame
df = pd.DataFrame(data)
#df = pd.read_csv(r'C:\Users\a797405\Documents\Tableau_SI\fantasy_ekstraklasa\2425-j\data\data_for_solver.csv')
#df = pd.read_csv(r'C:\Users\a797405\Documents\Tableau_SI\fantasy_1_liga\2425-j\data\to_solver.csv')
print(df)
#exit()
# Tworzymy problem maksymalizacyjny
problem = pulp.LpProblem("Maximize_Points", pulp.LpMaximize)

# Tworzymy zmienne binarne dla każdego zawodnika (1 - zawodnik wybrany, 0 - nie wybrany)
player_vars = pulp.LpVariable.dicts("Player", df.index, cat="Binary")

# Funkcja celu: Maksymalizuj sumę punktów wybranych zawodników
problem += pulp.lpSum(df.loc[i, "points"] * player_vars[i] for i in df.index), "Total Points"

# Ograniczenie 1: Dokładnie 2 bramkarzy
problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "position"] == "BRAMKARZ") == MAX_GOALKEEPER, "Select exactly 2 Goalkeepers"

# Ograniczenie 2: Dokładnie 5 obrońców
problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "position"] == "OBROŃCA") == MAX_DEFENDER, "Select exactly 5 Defenders"

# Ograniczenie 3: Dokładnie 5 pomocników
problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "position"] == "POMOCNIK") == MAX_MIDFIELDER, "Select exactly 5 Midfielders"

# Ograniczenie 4: Dokładnie 3 napastników
problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "position"] == "NAPASTNIK") == MAX_FORWARD, "Select exactly 3 Forwards"

# Ograniczenie 5: Suma cen nie może przekroczyć 30
problem += pulp.lpSum(df.loc[i, "price"] * player_vars[i] for i in df.index) <= MAX_BUDGET, "Total Price Limit"

# Ograniczenie 6: Maksymalnie 3 zawodników z każdego klubu
clubs = df["club"].unique()
for club in clubs:
    problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "club"] == club) <= 2, f"Max 3 players from {club}"

# Ograniczenie 7:
#problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "ID"] == 1475) == 1, "Select ISHAK"

problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "club"] == "RUCH CHORZÓW") >= 2, "Select players from GKŁ"

problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "club"] == "POLONIA WARSZAWA") >= 1, "Select players from WIS"

# Ograniczenie 7: Tylko młodzieżowcy

#problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "young"] == True) == 15, "Select young players only"

# Ograniczenie 7: Tylko z Polski
# problem += pulp.lpSum(player_vars[i] for i in df.index if df.loc[i, "country"] == "POLSKA") == 15, "Select polish players"

# Rozwiązujemy problem
problem.solve()

# Wyświetlamy status rozwiązania
print(f"Status: {pulp.LpStatus[problem.status]}")

# Wyświetlamy wybranych zawodników
selected_players = df[df.index.isin([i for i in df.index if player_vars[i].varValue == 1])]
print(f"Selected players:\n{selected_players[['name', 'position', 'club', 'price', 'points']]}")

# Suma punktów
total_points = sum(df.loc[i, "points"] for i in df.index if player_vars[i].varValue == 1)
print(f"Total Points: {total_points}")
