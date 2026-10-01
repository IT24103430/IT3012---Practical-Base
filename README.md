# IT3012 Practical 04: Informed Search

Practical 04 builds on the code and lab documents from `origin/Lab-03`.
The completed work is on the local `Lab-04` branch.

`SearchAgent` now supports BFS, DFS, UCS, and A* (the default). A* uses
Manhattan distance by default; set `agent.heuristic_type = 'euclidean'`
to use straight-line distance, or `agent.active_algo = 'BFS'`, `'DFS'`,
or `'UCS'` to compare earlier algorithms. Movement costs one per step.

Run the checkpoints and a repeatable simulation:

```sh
python3 lab04_demo.py
python3 -m unittest -v test_suite
```

Run the animated simulation with a Python installation that includes Tkinter:

```sh
python3 visual_grid_game.py
```

The GUI injects `SearchAgent` and uses A*. It retains the earlier labs' hidden
traps and opponents; A* optimizes movement length, so it does not account for
hidden hazards or guarantee the best score. `remaining_food` is a count;
`all_food` supplies the food coordinates used for planning. Position is tracked
from the known start and valid planned moves, preserving Lab 02's local sensors.

The completed written answers and verification results are in
[lab04-IT24103430.pdf](lab04-IT24103430.pdf), with editable source in
[docs/lab04-answers.md](docs/lab04-answers.md). To regenerate the PDF, install
`reportlab` in a virtual environment and run `python docs/build_lab04_pdf.py`.
