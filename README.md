# Factorio Layout Optimizer

This project arose because I constantly felt like I was making poor decisions
with where I placed everything in my base. This is a pretty simple attempt to
minimize belt distance between different parts of your base.

<img
src="https://github.com/kevinburke/factorio-layout-optimizer/blob/main/graphs/labs-and-rocket.png?raw=true"
alt="Optimized Factorio base placement"
/>

### Usage

```
python main.py --fast    # Render best answer in 15 seconds
python main.py           # Render best answer after 4 minutes
```

### Install

1. Download this project from Github

2. Run the following

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

Then you can run `python main.py` to generate a base layout.

### What's Happening Here

This library divides your base up into "blocks," where each block has a specific
purpose - "red science," "iron smelting," or "rocket silo" for example. The
connections between each block are defined, as well as the entry points -
where belts enter and exit each block. So for example, iron smelting needs a
connection to the coal mine and the copper mine.

Minimizing travel distance is a type of problem that is known to be "NP
complete," which is a fancy way of saying, it's expensive to compute the answer.
We put all of the blocks into a SAT solver, which can approximate a good
solution for the problem. The SAT solver is part of Google's operations research
tooling library.

A block has a width and height. You can customize the blocks in `factorio.py`
- we have two starter blocks, one which has the requirements to build 2 rocket
parts per minute, and one which can get you all the sciences.

```python
blocks = {
    # You're responsible for getting belts from the mines to your base
    "Copper Mine": (1, 1),
    "Stone Mine": (1, 1),

    "Copper Smelting": electric_smelter(80.4),
    "Iron Smelting": electric_smelter(108.6),
    "Steel Smelting": electric_smelter(60),
```

And then we define a series of "connections" between each of the blocks. Each
connection has a start, an end, and then the point on the start at which you
exit the block, and the point at the end at which you enter the block - which
are shortened to "TL" (top left), "BM" (bottom middle), etc.

```python
connections = [
    ("Coal Mine", "Copper Smelting", "MM", "LM"),
    ("Copper Mine", "Copper Smelting", "MM", "LM"),

    ("Coal Mine", "Iron Smelting", "MM", "BM"),
    ("Ore Mine", "Iron Smelting", "MM", "BM"),

    # ...
```

We plug these all into the SAT solver, and then get out a graph like one of the
ones in the "graphs" directory.

### Simplifying assumptions

- I used existing blueprints from factorio.school for almost all of the blocks.

- We don't chart the space needed to actually get the belts from one place to
  the other, so you need to allocate space for this in your factory.

- The blocks can't rotate, even though blueprints can. I tried to add rotation
  but it ended up blowing up the complexity, to the point where

### Help wanted

The API can almost certainly be better, and could for example emit blueprints
of the base for you, which would be pretty cool. I also don't have much interest
in super bases, but I can see why you'd want to optimize these as well.

We could also almost certainly improve the rendering, and the method used
to import data - for example you could just specify the items you want to
produce and the rate, and we could generate a base for you, similar to how Kirk
McDonald's website works.

I don't have time to work on any of this but if you do I'm happy to grant commit
access or point people at a fork.
