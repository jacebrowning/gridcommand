import pomace

page = pomace.visit("http://localhost:5000", delay=2)

pomace.log.info("Starting the game")
page.click_new_board(wait=1)
page = page.click_start_game(wait=1)

pomace.log.info("Adding players")
page = page.click_blue(wait=1)
page = page.click_switch_player(wait=1)
page = page.click_red(wait=1)
assert "Round 1" in page

pomace.log.info("Planning red moves")
page.click_plan_moves(wait=1)
page.click_done_planning(wait=1)

pomace.log.info("Switching players")
page = page.click_switch_player(wait=1)

pomace.log.info("Planning blue moves")
page = page.click_blue(wait=1)
page.click_plan_moves(wait=1)
page.click_done_planning(wait=1)

pomace.log.info("Advancing the round")
page.click_next_round(wait=1)
assert "Round 2" in page

print("\n🎉\n")
