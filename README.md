# TIPE

Can interactions between League of Legends players predict who wins a game, and
which combat patterns lead to a win? This project replays real games, turns each
game into a sequence of interaction graphs, learns a decision tree on those graphs,
and mines the frequent subgraphs behind its winning rules.

It was my TIPE (the research project of the French *classes préparatoires*) in 2024.
The method follows Yang, Harrison & Roberts (2014), originally applied to Dota 2.

![Frequent combat subgraphs across successive time frames](screenshots/Frequent%20Subgraphs.png)

*Frequent combat subgraphs, one panel per time frame.*

## How it works

1. **Collect games.** Scrape replay identifiers from
   [League of Graphs](https://www.leagueofgraphs.com/) with a headless Firefox.
2. **Record interactions.** Launch each replay in the League of Legends client and
   read the LiveEvents API stream on port 34243. Every `OnDamageGiven` and death
   event is kept.
3. **Build graphs.** Split each game into 2-minute time frames. In each frame, build a
   directed graph with one node per player plus a `DEATH` node: an edge `s → t`
   means `s` damaged `t`, and `s → DEATH` means `s` died.
4. **Select features.** Each node gets in/out degree, closeness, betweenness and
   eigenvector centrality. With up to 30 frames, 11 nodes and 5 measures, that is
   1650 candidate features. A genetic
   algorithm picks a small subset that keeps the decision tree accurate without
   overfitting.
5. **Extract rules.** Build a C4.5 decision tree on the selected features. Each
   path from the root to a leaf is a combat rule ("if T1-R5 out-degree in frame 11
   > 1 and …, then T2 wins").
6. **Mine patterns.** For each frequent and accurate rule, enumerate the subgraphs
   of the games that match it and keep those present in a large share of them. This
   gives the mean combat graph behind the rule.

## Results

**Dataset.** 233 replays recorded out of 4,072 scraped games, all EUW ranked
games (229 Solo/Duo, 4 Flex) with players mostly Master to Challenger.

**Feature selection.** The genetic algorithm produced 14 feature sets of 4 to 7
features each (listed in `main.py`). Its fitness is the tree's accuracy minus a
penalty for each extra feature.

**Rules.** One tree, built on 5 selected features, gives two strong rules:

| Rule | Prediction | Games covered | Accuracy |
|---|---|---|---|
| T1-R5 and T1-R1 each hit more than one enemy in frames 11 and 12, `DEATH` eigenvector centrality > 0.16 in frame 9, T2-R5 betweenness ≤ 0.08 in frame 8, T2-R4 closeness ≤ 0.35 in frame 2 | T2 wins | 63 / 233 | 78% |
| T1-R5 hits at most one enemy in frame 11, T1-R1 at most four in frame 12, `DEATH` eigenvector centrality ≤ 0.61 in frame 9, T2-R5 betweenness ≤ 0.17 in frame 8, T2-R4 closeness > 0.16 in frame 2 | T1 wins | 33 / 233 | 79% |

Read literally, the first rule says that team 1 tends to lose when its R5 and R1
are both fighting several enemies around minutes 22 to 26, after a frame with many
deaths around minute 18.

**Combat patterns.** The frequent subgraphs (top of this page) show the fights
behind a rule frame by frame: early one-on-one trades between the same roles,
then team fights where most edges point to `DEATH`. Graphs for each rule are in
[`graph_images/single_rule/`](graph_images/single_rule).

**Limits.** 233 games is small for 1650 features, so the rules overfit easily and
were not checked on a held-out set. The scraped games are also not a random sample
of all games.

The full write-up (in French) is in [`docs/TIPE.pdf`](docs/TIPE.pdf), and the
slides are in [`presentation/presentation.pdf`](presentation/presentation.pdf).

## Data availability

This dataset can no longer be extended. Riot removed the LiveEvents API shortly
after I started recording games, and I don't know of another way to get
player-to-player damage events. More recently, Riot also removed the ability to
watch other players' replays, so the games can't be replayed either.

233 games are not enough to draw real conclusions, but the recorded events in
[`get_data/data/`](get_data/data) are all there is. The collection and recording
steps below are kept for reference and no longer work as is.

## Run it

You need Python 3 and Graphviz for `pygraphviz`.

```sh
pip install networkx matplotlib pillow tqdm selenium pydirectinput pygraphviz
```

Run every script from the repository root.

**Collect games** (any OS). Download
[geckodriver v0.33.0](https://github.com/mozilla/geckodriver/releases/tag/v0.33.0)
and the [uBlock Origin 1.53.0](https://github.com/gorhill/uBlock/releases/tag/1.53.0)
Firefox `.xpi`. Place them at `get_data/drivers/geckodriver` and
`get_data/drivers/ublock_origin-1.53.0.xpi`, then run:

```sh
python get_games.py
```

**Record replays** (Windows only, with League of Legends installed and LiveEvents
enabled). The script opens one replay at a time, drives it with simulated input, and
saves its events to `get_data/data/<id>.json`:

```sh
python run_replays.py
```

**Analyse** (still works on the recorded data in this repo). `main.py` contains
each step: dataset stats, parsing games into objects, building graphs, training
features, and frequent subgraph mining. Uncomment the steps you want in `main()`,
then run:

```sh
python main.py
```

## Layout

- `get_games.py`, `run_replays.py`, `main.py`: entry points.
- `classes/`: game model, C4.5 implementation, frequent subgraph mining, and data
  loading.
- `methods/`: graph building, decision trees, rule extraction, genetic feature
  selection, and subgraph images.
- `get_data/`: replay capture over LiveEvents and dataset statistics.
- `presentation/`: Beamer slides.

## References

- Yang, P., Harrison, B. E., & Roberts, D. L. (2014). *Identifying patterns in
  combat that are predictive of success in MOBA games.* FDG.
- Quinlan, J. R. (1993). *C4.5: Programs for Machine Learning.* Morgan Kaufmann.
- Stein, G., Chen, B., Wu, A. S., & Hua, K. A. (2005). *Decision tree classifier for
  network intrusion detection with GA-based feature selection.* ACM-SE 43.