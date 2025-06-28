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

    def get_champions(self):
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href,'/lol/champions/') and contains(@href,'/build')]"))
            )
            anchor_tags = self.driver.find_elements(By.XPATH, "//a[contains(@href,'/lol/champions/')]")
            href_tags = [tag.get_attribute("href") for tag in anchor_tags][5:]


            print("\n🌐 Champion HREFs:")
            for i, href in enumerate(href_tags):
                print(f"{i+1}. {href}")

            return href_tags
        except Exception as e:
            print("❌ Champion links NOT FOUND")
            print("Error:", e)
    
    def clean_href(self, href_array):
        cleaned_hrefs = []

        for i in range(0, len(href_array), 11):
            chunk = href_array[i:i+11]
            unique_chunk = []
            seen = set()

            for href in chunk:
                # Extract champion name
                try:
                    champion_name = href.split("/lol/champions/")[1].split("/")[0]
                except IndexError:
                    print(f"⚠️ Skipping malformed href: {href}")
                    continue

                if champion_name not in seen:
                    seen.add(champion_name)
                    unique_chunk.append(champion_name)
                else:
                    print(f"🗑️ Removed duplicate in group: {champion_name}")

            cleaned_hrefs.extend(unique_chunk)

        return cleaned_hrefs


    def make_game_champion_map(self, href_array):
        game_map = {}

        for i in range(0, len(href_array), 10):  
            chunk = href_array[i:i+10]
            game_key = f"game_{i // 10 + 1}"
            game_map[game_key] = chunk

        return game_map


                


    def pipeline(self):
        self.open_website()
        self.get_match_history()
        self.open_more_details()
        href_array=self.get_champions()
        cleaned_href=self.clean_href(href_array)
        game_map=self.make_game_champion_map(cleaned_href)


        for game, champions in game_map.items():
            print(f"{game}:")
            for champ in champions:
                print(f"  - {champ}")





if __name__ == "__main__":
    scraper = Team()
    scraper.pipeline()
