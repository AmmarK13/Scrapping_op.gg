from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import random

class Team():
    def __init__(self, wait_time=20):
        self.driver = webdriver.Chrome()
        self.wait_time = wait_time
        self.team = {}

    def open_website(self):
        name = input("Enter name for Summoner (format: name-1234): ")
        self.driver.get(f"https://op.gg/lol/summoners/me/{name}")

    def get_match_history(self):
        try:
            show_more = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Show more"]'))
            )
            print("✅ Button found!")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", show_more)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", show_more)
            print("✅ Button clicked.")
            time.sleep(10)
        except Exception as e:
            print("❌ Could not find or click the button.")
            print("Error:", e)

    def open_more_details(self):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//button[contains(@class,'bg-') and contains(@class,'game-item-color-200') and contains(@class,'md:hidden')]"
                ))
            )
            buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'bg-') and contains(@class,'game-item-color-200') and contains(@class,'md:hidden')]"
            )
            print(f"✅ Found {len(buttons)} potential detail buttons")
            for i, btn in enumerate(buttons):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    self.driver.execute_script("arguments[0].click();", btn)
                    print(f"✔️ Clicked button #{i + 1}")
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ Failed to click button #{i + 1}: {e}")
        except Exception as e:
            print(f"❌ Could not find detail buttons at all: {e}")

    def extract_team_data(self, row):
        champ_data = {"champion": "unknown", "summoners": [], "Runes": []}
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
            time.sleep(0.2)
            champ_link = row.find_element(By.XPATH, ".//a[contains(@href,'/lol/champions/') and contains(@href,'/build')]")
            href = champ_link.get_attribute("href")
            champ_data["champion"] = href.split("/lol/champions/")[1].split("/")[0]

            # Summoner Spells
            spell_imgs = row.find_elements(By.XPATH, ".//img[contains(@src, '/spell/Summoner')]")
            for img in spell_imgs:
                src = img.get_attribute("src")
                champ_data["summoners"].append(src.split("/")[-1].split(".")[0])

            # Primary Rune
            runes_imgs = row.find_elements(By.XPATH, ".//img[contains(@src,'/perk/')]")
            for img in runes_imgs:
                alt = img.get_attribute("alt")
                champ_data["Runes"].append(alt)

            # Secondary Rune
            second_rune = row.find_element(By.XPATH, ".//img[contains(@src,'/perkStyle/')]")
            champ_data["Runes"].append(second_rune.get_attribute("alt"))

        except Exception as e:
            print(f"⚠️ Failed to extract data for row: {e}")
        return champ_data
    def split_teams_by_color(self, rows):
        blue_rows = []
        red_rows = []

        for row in rows:
            try:
                # Find all <td> elements inside this <tr>
                td_elements = row.find_elements(By.TAG_NAME, "td")
                team_detected = False

                for td in td_elements:
                    class_attr = td.get_attribute("class")
                    if "!bg-main-100"in class_attr or "!bg-main-200" in class_attr:
                        blue_rows.append(row)
                        team_detected = True
                        break
                    elif "!bg-red-100" in class_attr or "!bg-red-200" in class_attr:
                        red_rows.append(row)
                        team_detected = True
                        break

                if not team_detected:
                    print("⚠️ No team color class detected in row")

            except Exception as e:
                print(f"⚠️ Error while detecting team: {e}")

        return blue_rows, red_rows





    def extract_games_from_table(self):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tr[@class='!border-b-0']"))
            )
            table_rows = self.driver.find_elements(By.XPATH, "//tr[@class='!border-b-0']")
            print(f"✅ Found {len(table_rows)} rows (expecting ~200 for 20 games)")
            all_games = {}

            for i in range(0, len(table_rows), 10):
                chunk = table_rows[i:i+10]
                game_key = f"game_{i // 10 + 1}"




                # 🔍 Detect teams by color-coded row class
                blue_rows,red_rows=self.split_teams_by_color(chunk)
            

                if len(blue_rows) != 5 or len(red_rows) != 5:
                    print("⚠️ Team row count not 5 each — fallback to order-based split")
                    blue_rows = chunk[:5]
                    red_rows = chunk[5:10]

                # 🟦 Extract data for blue team
                blue_team = [self.extract_team_data(row) for row in blue_rows]
                # 🔴 Extract data for red team
                red_team = [self.extract_team_data(row) for row in red_rows]

                all_games[game_key] = {"blue": blue_team, "red": red_team}

            return all_games

        except Exception as e:
            print("❌ Could not extract table rows.")
            print("Error:", e)
            return {}


    def print_games(self, games):
        for game_number, teams in games.items():
            print(f"\n🎮 {game_number}")
            print("  🔵 Blue Team:")
            for champ in teams['blue']:
                print(f"     - {champ}")
            print("  🔴 Red Team:")
            for champ in teams['red']:
                print(f"     - {champ}")
    def write_games_to_csv(self, games, filename="match_data.csv"):
        file_exists = os.path.exists(filename)
        game_id = 1

        # If file exists, figure out current max game_id
        if file_exists:
            with open(filename, "r", newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                ids = [int(row[0]) for row in reader if row]
                if ids:
                    game_id = max(ids) + 1

        with open(filename, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["game_id", "team1", "team2", "team1_sums", "team2_sums", "team1_runes", "team2_runes", "label"])

            for _, match in games.items():
                blue_team = match["blue"]
                red_team = match["red"]

                # Randomize assignment
                if random.choice([True, False]):
                    team1, team2 = blue_team, red_team
                    label = 1  # blue = team1 → team1 wins
                else:
                    team1, team2 = red_team, blue_team
                    label = 0  # blue = team2 → team1 loses

                def flatten_team(team):
                    champs = ",".join([x["champion"] for x in team])
                    sums = "|".join(["+".join(x["summoners"]) for x in team])
                    runes = "|".join(["+".join(x["Runes"]) for x in team])
                    return champs, sums, runes

                team1_champs, team1_sums, team1_runes = flatten_team(team1)
                team2_champs, team2_sums, team2_runes = flatten_team(team2)

                writer.writerow([game_id, team1_champs, team2_champs, team1_sums, team2_sums, team1_runes, team2_runes, label])
                game_id += 1

    def pipeline(self):
        self.open_website()
        self.open_more_details()
        all_games = self.extract_games_from_table()
        self.print_games(all_games)
        self.write_games_to_csv(all_games)


if __name__ == "__main__":
    scraper = Team()
    scraper.pipeline()
