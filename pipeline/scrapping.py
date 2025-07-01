from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
                blue_team = [self.extract_team_data(row) for row in chunk[:5]]
                red_team = [self.extract_team_data(row) for row in chunk[5:10]]

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

    def pipeline(self):
        self.open_website()
        self.open_more_details()
        all_games = self.extract_games_from_table()
        self.print_games(all_games)


if __name__ == "__main__":
    scraper = Team()
    scraper.pipeline()
