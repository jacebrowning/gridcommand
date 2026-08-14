import pomace

WAIT = 0

page = pomace.visit("http://localhost:5000", delay=2)

pomace.log.info("Creating game")
page = page.click_new_game()
page.click_two_players(wait=WAIT)
page.click_shared_device(wait=WAIT)
page.click_random_distribution(wait=WAIT)
page = page.click_new_board(wait=WAIT)
assert "Start Game" in page

pomace.log.info("Starting game")
page = page.click_start_game(wait=WAIT)
assert "Blue" in page

pomace.log.info("Adding players")
page = page.click_blue(wait=WAIT)
page = page.click_switch_player(wait=WAIT)
page = page.click_red(wait=WAIT)
assert "Round 1" in page

pomace.log.info("Planning red moves")
page = page.click_plan_moves(wait=WAIT)
assert "Submit Moves" in page
page = page.click_done_planning(wait=WAIT)
assert "Waiting" in page

pomace.log.info("Switching players")
page = page.click_switch_player(wait=WAIT)
assert "Blue" in page

pomace.log.info("Planning blue moves")
page = page.click_blue(wait=WAIT)
page = page.click_plan_moves(wait=WAIT)
assert "Submit Moves" in page
page = page.click_done_planning(wait=WAIT)

pomace.log.info("Waiting for others")
for _ in range(10):
    page = pomace.visit(page.url, delay=0.5)
    if "to plan moves" not in page:
        break
else:
    raise AssertionError("Timed out waiting for others")
assert "Show Results" in page

pomace.log.info("Applying results")
page = page.click_next_round(wait=WAIT)
assert "Round 1" in page
assert "Show Reinforcements" in page

pomace.log.info("Showing reinforcements")
page = page.click_next_round(wait=WAIT)
assert "Round 1" in page
assert "+1" in page
assert "Start Next Round" in page

pomace.log.info("Starting next round")
page = page.click_next_round(wait=WAIT)
assert "Round 2" in page
assert "Plan Moves" in page

print("\n🎉\n")
