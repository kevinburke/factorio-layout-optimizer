
grid_size = (20, 20)
blocks = [
    ("Copper Mine", 1, 1),     # (name, width, height)
    ("Iron Mine", 1, 1),
    ("Coal Mine", 1, 1),
    ("Assembling", 4, 2),
    ("Chemical Plant", 3, 3),
    ("Oil Refinery", 2, 2)
]

connections = [
    (0, 1),  # Connection between Smelting and Assembling
    (1, 2),  # Connection between Assembling and Chemical Plant
    (2, 3),  # Connection between Chemical Plant and Oil Refinery
    (0, 2)   # Connection between Smelting and Chemical Plant
]
