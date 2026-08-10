# Grid Command

A grid-based strategy game inspired by *Same Time Risk*.

Up to four colors share a board. You and your opponents plan moves at the same time, then reveal them together — so every attack, defense, and reinforcement is a bet on what everyone else will do.

## How to play

1. **Set up** a board (size, number of human players, optional random territory). Open slots are filled by computer opponents.
2. **Pick a color** and claim your starting position.
3. **Plan** by sending units from each cell toward neighboring cells — reinforce allies, march into empty ground, or strike an enemy.
4. When everyone is ready, **reveal** the moves, then step through:
   - **Show Results** — clashes and captures resolve
   - **Show Reinforcements** — pending units appear on the grid (`+N` on the strongest cells)
   - **Start Next Round** — reinforcements are applied to those cells, then plan again
5. The last color with territory on the board wins.

### Reinforcements

Each living color gains roughly **one unit per two territories** held (`cells ÷ 2`, rounded down), with a **minimum of one** if they still own any cell. For example: 1–3 cells → +1, 4–5 → +2, 6–7 → +3. Units are previewed and then placed on the player's strongest cells first (highest unit count), spreading extras round-robin if they receive more than one.

Play solo against the computers, pass a shared device around the table, or join the same game from different browsers.
