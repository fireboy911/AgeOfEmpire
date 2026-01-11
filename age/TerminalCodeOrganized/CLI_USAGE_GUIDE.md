# Battle Simulation CLI - Usage Guide

## Overview
The new CLI provides a comprehensive command-line interface for running battle simulations, tournaments, and analyzing outcomes.

## Commands

### 1. `battle run` - Run a Single Battle

**Syntax:**
```bash
python MainTerminal.py run <scenario> <AI1> <AI2> [-t] [-d DATAFILE] [--seed SEED]
```

**Parameters:**
- `<scenario>`: The scenario to run (e.g., `square_scenario`, `chevron_scenario`)
- `<AI1>`: First AI (e.g., `DaftGeneral`, `BrainDeadGeneral`)
- `<AI2>`: Second AI (e.g., `DaftGeneral`, `BrainDeadGeneral`)
- `-t`: Launch terminal view (headless mode)
- `-d DATAFILE`: Save battle results to a data file
- `--seed SEED`: Set random seed for reproducibility

**Examples:**
```bash
# Run a simple battle
python MainTerminal.py run square_scenario DaftGeneral BrainDeadGeneral -t

# Run a battle and save results
python MainTerminal.py run square_scenario DaftGeneral BrainDeadGeneral -t -d battle_results.txt

# Run with a specific seed for reproducibility
python MainTerminal.py run square_scenario DaftGeneral BrainDeadGeneral -t --seed 42

# Run on chevron scenario
python MainTerminal.py run chevron_scenario DaftGeneral DaftGeneral -t -d chevron_test.txt
```

**Output:**
- Battle statistics (time, steps, winner)
- Event log (last 20 events)
- Optional: Data file with complete event log

---

### 2. `battle load` - Load a Saved Battle

**Syntax:**
```bash
python MainTerminal.py load <savefile>
```

**Parameters:**
- `<savefile>`: Path to the save file to load

**Examples:**
```bash
python MainTerminal.py load saved_battles/match_001.save
```

**Status:** Not yet implemented

---

### 3. `battle tourney` - Run a Tournament

**Syntax:**
```bash
python MainTerminal.py tourney [-G AI1 AI2 ...] [-S SCENARIO1 SCENARIO2 ...] [-N ROUNDS] [-na] [-d DATAFILE]
```

**Parameters:**
- `-G`: List of AIs to participate (default: `DaftGeneral BrainDeadGeneral`)
- `-S`: List of scenarios to use (default: `square_scenario`)
- `-N`: Number of rounds per matchup (default: 10)
- `-na`: Do NOT alternate player positions across rounds
- `-d`: Save tournament results to a data file

**Examples:**
```bash
# Default tournament (2 AIs, 1 scenario, 10 rounds)
python MainTerminal.py tourney

# Tournament with 2 rounds per matchup
python MainTerminal.py tourney -N 2 -d results.txt

# Tournament with multiple scenarios
python MainTerminal.py tourney -G DaftGeneral BrainDeadGeneral -S square_scenario chevron_scenario -N 5

# Tournament with no position alternation
python MainTerminal.py tourney -N 10 -na

# Complex tournament setup
python MainTerminal.py tourney -G AI1 AI2 AI3 -S scenario1 scenario2 -N 20 -d tournament_summary.txt
```

**Output:**
- Tournament progress
- Match results (wins-losses-draws)
- Optional: Results file with summary statistics

**Example Output:**
```
Running tournament with 2 AIs, 1 scenarios, 2 rounds each
AIs: DaftGeneral, BrainDeadGeneral
Scenarios: square_scenario
Alternate positions: True

Tournament Results (2 matches):
DaftGeneral vs BrainDeadGeneral (square_scenario): 2-0-0
Tournament results saved to tournament_results.txt
```

---

### 4. `battle plot` - Plot Outcomes

**Syntax:**
```bash
python MainTerminal.py plot <AI> <plotter> <scenario> <unit1> <unit2> ... [-r RANGE] [-N ROUNDS]
```

**Parameters:**
- `<AI>`: AI to analyze (e.g., `DaftGeneral`)
- `<plotter>`: Plotter type (e.g., `PlotLanchester`)
- `<scenario>`: Scenario to test (e.g., `Lanchester`)
- `<unit1> <unit2> ...`: Units to include in analysis
- `-r/--range`: Parameter range (e.g., `1,100`)
- `-N`: Number of rounds per test (default: 10)

**Examples:**
```bash
# Analyze Lanchester equations with Knight and Crossbow units
python MainTerminal.py plot DaftGeneral PlotLanchester Lanchester Knight Crossbow -r 1,100

# Multiple unit analysis
python MainTerminal.py plot BrainDeadGeneral PlotWinrate scenario1 Knight Monk Pikeman -r 10,50 -N 20
```

**Status:** Stub implemented, functionality to be added

---

## Real-World Usage Examples

### Example 1: Quick Battle Test
```bash
python MainTerminal.py run square_scenario DaftGeneral BrainDeadGeneral -t -d quick_test.txt
```
Runs a single battle with DaftGeneral vs BrainDeadGeneral on the square scenario and saves results.

### Example 2: Reproducible Testing
```bash
python MainTerminal.py run square_scenario DaftGeneral BrainDeadGeneral -t --seed 123 -d test_123.txt
```
Runs the same battle configuration every time using seed 123.

### Example 3: Tournament Between Two AIs
```bash
python MainTerminal.py tourney -G DaftGeneral BrainDeadGeneral -S square_scenario chevron_scenario -N 10 -d full_tournament.txt
```
Runs a 10-round tournament on two scenarios, alternating player positions.

### Example 4: Quick Tournament
```bash
python MainTerminal.py tourney -N 2 -d quick_tournament.txt
```
Runs a quick tournament with default settings (2 AIs, 1 scenario, 2 rounds).

---

## Output Files

### Battle Results File (`-d` option with `run`)
Contains:
- Battle end time and winner
- Simulation statistics
- Complete event log

**Example:**
```
Battle ended at t=57.0s steps=285. Winner: P1
Simulation took 1.31s wall time. Engine ticks: 57.00
Events:
   Unit 105 (P2) died at tick 16.80
   Unit 101 (P2) died at tick 17.00
   ...
```

### Tournament Results File (`-d` option with `tourney`)
Contains:
- Total number of matches
- Results for each matchup (wins-losses-draws)

**Example:**
```
Tournament Results (2 matches):
DaftGeneral vs BrainDeadGeneral (square_scenario): 2-0-0
```

---

## Important Notes

1. **Working Directory:** Always run commands from the `age/TerminalCodeOrganized` directory
2. **AI Names:** Use exact names: `DaftGeneral`, `BrainDeadGeneral`
3. **Scenario Names:** Use exact names: `square_scenario`, `chevron_scenario`
4. **Position Alternation:** By default, AIs alternate positions across tournament rounds unless `-na` is specified
5. **File Output:** Data files are created in the current working directory

---

## Future Enhancements

- [ ] Implement `load` command for saved battles
- [ ] Implement `plot` command with visualization
- [ ] Add more AI strategies
- [ ] Add more scenarios
- [ ] Support for saving/loading game state
- [ ] Statistical analysis tools
