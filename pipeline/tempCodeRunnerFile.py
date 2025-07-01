    try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tr[@class='!border-b-0']"))
            )
            table_rows = self.driver.find_elements(By.XPATH, "//tr[@class='!border-b-0']")

            print(f"✅ Found {len(table_rows)} rows (expecting ~200 for 20 games)")

            all_games = {}

            for i in range(0, len(table_rows), 10):
                chunk = table_rows[i:i+10]
                game_index = i // 10 + 1
                game_key = f"game_{game_index}"

                blue_team = []
                red_team = []

                # 🟦 Blue Team (first 5 rows)
                for row in chunk[:5]:
                    champ_data = {"champion": "unknown", "summoners": []}
                    try:
                        champ_link = row.find_element(By.XPATH, ".//a[contains(@href,'/lol/champions/') and contains(@href,'/build')]")
                        href = champ_link.get_attribute("href")
                        champ_name = href.split("/lol/champions/")[1].split("/")[0]
                        champ_data["champion"] = champ_name

                        # Get summoner spells
                        spell_imgs = row.find_elements(By.XPATH, ".//img[contains(@src,'/meta/images/15.13.1/spell')]")
                        for img in spell_imgs:
                            src = img.get_attribute("src")
                            spell_name = src.split("/")[-1].split(".")[0]
                            champ_data["summoners"].append(spell_name)
                    except:
                        pass

                    blue_team.append(champ_data)

                # 🔴 Red Team (last 5 rows)
                for row in chunk[5:10]:
                    champ_data = {"champion": "unknown", "summoners": []}
                    try:
                        champ_link = row.find_element(By.XPATH, ".//a[contains(@href,'/lol/champions/') and contains(@href,'/build')]")
                        href = champ_link.get_attribute("href")
                        champ_name = href.split("/lol/champions/")[1].split("/")[0]
                        champ_data["champion"] = champ_name

                        spell_imgs = row.find_elements(By.XPATH, ".//img[contains(@src,'/meta/images/15.13.1/spell')]")
                        for img in spell_imgs:
                            src = img.get_attribute("src")
                            spell_name = src.split("/")[-1].split(".")[0]
                            champ_data["summoners"].append(spell_name)
                    except:
                        pass

                    red_team.append(champ_data)

                all_games[game_key] = {
                    "blue": blue_team,
                    "red": red_team
                }

            return all_games

        except Exception as e:
            print("❌ Could not extract table rows.")
            print("Error:", e)
            return {}