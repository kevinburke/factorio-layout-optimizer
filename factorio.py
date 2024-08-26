import math

class Block:
    def __init__(self, width, height, weight=1, fixed_x=None, fixed_y=None):
        self.width = width
        self.height = height
        self.weight = weight
        self.fixed_x = fixed_x
        self.fixed_y = fixed_y

class Connection:
    def __init__(self, source, target, source_pos, target_pos, weight=1):
        self.source = source
        self.target = target
        self.source_pos = source_pos
        self.target_pos = target_pos
        self.weight = int(weight * 10)

def electric_smelter(num_furnaces):
    # https://www.factorio.school/view/-LM4FAS99hG83TEAl_9T

    # we use a basic model and assume you replace stone with electric (so
    # smelter can occupy same physical layout)

    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/5d7c46cad2773d4b5f185d6b2c5606a8d9e2abf9/position/1

    # 2 electric furnaces take up 39 squares (13*3)

    # 12 smelters on each side fills a yellow belt
    # 24 smelters on each side fills a red belt

    # https://steamcommunity.com/sharedfiles/filedetails/?id=862972621
    num_furnaces = math.ceil(num_furnaces)
    # "4 + 4" covers belts to and from and associated splitting
    if num_furnaces < (24 * 2):
        # if we have fewer than 48, just put them in one long line 13 wide
        return (4 + 4 + math.ceil(num_furnaces/2*3), 13)
    num_stacks = math.ceil(num_furnaces / 48)
    # each "stack" is a collection of 48 furnaces, 24 on either side of a belt
    return (4 + 4 + 24*3, 13*num_stacks)

def green_circuit(num_assemblers):
    packs = math.ceil(num_assemblers/2)

    # https://www.factorio.school/view/-KoqgcmWqjJGLf6csjL4
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/af8b75847d0714575989e1efac4f8cc5e7470f9d/position/0
    width = min(26, packs * 13)

    # lazy https://claude.ai/chat/f936dad3-e427-42a9-b516-da32f2fd5a23
    # add height at the bottom for input and belts
    if packs <= 2:
        height = 13 + 4
    elif packs <= 4:
        height = 26 + 4
    else:
        height = 26 + 4 + 13 * ((packs - 1) // 2 - 1)

    return (width, height)

def red_circuit(num_assemblers):
    # inner belt: left side red circuits, right side half green, half plastic
    # outer belt: one side copper, one side coils
    # this is 12 assemblers: https://www.factorio.school/view/-Kp6eLXuhwCqXBXr0ltW
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/87805c2ea48b411ef0f8e561758f6229ffb04cda/position/0
    # https://imgur.com/T5WlY0M
    # need one copper coil for every 6 red circuits
    num_assemblers = math.ceil(num_assemblers)
    copper_coils = math.ceil(num_assemblers/6)
    if copper_coils == 1:
        # 8 wide, 4 for copper, 4 per red assembler
        return (4 + 4*num_assemblers, 8)
    # 4 height for every two assemblers
    # 4 height for every 2 copper coil assemblers
    return (math.ceil(copper_coils/2)*4 + math.ceil(num_assemblers/2)*4, 14)

def blue_circuit(num_assemblers):
    # https://www.factorio.school/view/-KpX1-lyYhE-3-DfxTba
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/be6ac0d54651537214601211c9d98984a16d9d3e/position/0
    # center belt is red circuits
    # left/right belts are green circuits
    # outer belts are blue circuits
    packs = math.ceil(num_assemblers/4)
    return (17, packs*9)

def plastic(num_chemical_plants):
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/265ce01196a689ef5ea6eae916b84b812b06784e/
    # petroleum gas above the chem plant
    # plastic out on top belt
    # copper on bottom belt
    if num_chemical_plants <= 3:
        return (4*math.ceil(num_chemical_plants), 7)

    # use both sides of belt
    return (4*math.ceil(num_chemical_plants/2), 12)

def advanced_oil(num_oil_plants):
    # https://www.factorio.school/view/-LZpCwcZo6mMnV7TZdG1
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/6dfc4516b341d0bdbbc56c22a2a74b65b28535a7/
    return (22, 2+5+(5+1)*math.ceil(num_oil_plants))

def low_density_structure(num_assemblers):
    # https://www.factorio.school/view/-M5Dma3GTTR-aB704Bxa
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/15759bc3e06d659beff0c65b9ff95fff4efcec40/

    # 14 high
    # 4 extra wide
    # 3 wide for every 2 assemblers
    return (14, 4 + math.ceil(num_assemblers/2)*3)

def min_speed_module(num_assemblers):
    # height:
    # - belt above
    # - inserter
    # - 3 for assembler
    # - inserter
    # - belt below
    return (7, math.ceil(num_assemblers) * 3 + 5)

def solid_fuel(num_plants):
    # ??
    # https://www.factorio.school/view/-L_dgvit-TLeoWF3EL6K
    return (7, math.ceil(num_plants) * 3 + 5)

def rocket_fuel(num_assemblers):
    # https://www.factorio.school/view/-NfTYT_f1XATK_h5dfoz
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/7adea92fb28bef85a361d46b6976064aedf817f5/
    # each one takes up 7 - pipe, 3 assembler, 2 belts, inserter
    return (7, math.ceil(num_assemblers) * 3 + 5)

def power_plant(power_mw):
    chunks = math.ceil(power_mw/1.8)
    # 15 wide: one belt, inserter, 2 for boiler, 10 for two steam engines, one
    #    for power poles
    # two chunks take up 7 height
    if chunks <= 20:
        return Block(15, math.ceil(chunks*7/2)+3)
    if chunks <= 40:
        # four chunks take up 7 height
        return Block(30, math.ceil(chunks*7/4)+3)
    if chunks <= 60:
        # six chunks take up 7 height
        return Block(45, math.ceil(chunks*7/6)+6)
    return Block(60, math.ceil(chunks*7/8)+6)

# 2 rocket parts a minute, full rocket silo in 10 minutes
# https://kirkmcdonald.github.io/calc.html#zip=dY2xDsIwDET/JhMRpbBQKR9jOQasOnGUOAN/32ZhCrrl9J50F8Eg3PyZp0ucw+penSQ0FY5+VJdK1RjWxbFRagG6aQJjzb4hU0byBXDf6nZfLqJvbsY4UfihxAgyUeOg45/Jbixs34mpijuZbyw6wPXxQwWqnWg9AA==
rocket_blocks = {
    "Copper Mine": (1, 1),
    "Ore Mine": (1, 1),
    "Coal Mine": (1, 1),
    "Water": (1, 1),
    "Oil": (1, 1),
    "Stone": (1, 1),

    "Copper Smelting": electric_smelter(72.3),

    "Iron Smelting": electric_smelter(58.6),

    "Steel Smelting": electric_smelter(21.4),
    "Stone Smelting": electric_smelter(1.4),

    "Plastic": plastic(3.9),

    # No separate copper coil block - all assembly part of green or red circuits
    "Green Circuit Assembly": green_circuit(23),
    "Red Circuit Assembly": red_circuit(47.4),
    "Blue Circuit Assembly": blue_circuit(12.3),

    "Advanced Oil Processing": advanced_oil(10.7),

    # these are included in the Advanced Oil processing footprint
    # need 1.5 light oil crackers
    "Light Oil Cracking": (1, 1),
    # 1.2 crackers
    "Heavy Oil Cracking": (1, 1),

    "Sulfur": plastic(1),
    "Sulfuric Acid": (15, 10),

    "Low Density Structure": low_density_structure(13.4),

    "Electric Engine Unit": plastic(4.5),
    "Concrete": plastic(2.3),

    "Solid Fuel": solid_fuel(6.7),
    "Rocket Fuel": rocket_fuel(13.4),

    # one speed module assembler can feed three RCU's
    "Rocket Control Unit": electric_smelter(20),

    "Rocket Silo Assembler": (6, 6),
    "Rocket": (10, 10),
}

# ratios:
#
# https://www.reddit.com/r/factorio/comments/birqnl/boiler_fuel_consumption_and_steam_engine_setup/
# one steam engine can produce 900kW, two steam engines = 1.8MW
# Solid fuel: 360 per minute for 40 boilers

# https://kirkmcdonald.github.io/calc.html#zip=dY2xDsIwDET/JhMRpbBQKR9jOQasOnGUOAN/32ZhCrrl9J50F8Eg3PyZp0ucw+penSQ0FY5+VJdK1RjWxbFRagG6aQJjzb4hU0byBXDf6nZfLqJvbsY4UfihxAgyUeOg45/Jbixs34mpijuZbyw6wPXxQwWqnWg9AA==
#
map_exchange_string = """
>>>eNpjZGBkyGUAgwZ7EOZgSc5PzFm9apU9CINEuJLzCwpSi3Tzi
1KRhTmTi0pTUnXzM1EVp+al5lbqJiUWp0JMhJjMkVmUn4duAmtxS
X4eqkhJUWpqMYwHwtylRYl5maW5IL0wMTBmvPX2nXtDixwDCP+vZ
1D4/x+EgawHQBtBmIGxAaSSkREoBgOsyTmZaWkMDAqOQOwElmZgr
BZZ5/6wagqQCQZ6DlDGB6jIgSSYiCeM4eeAU0oFxjBBMscYDD4jM
SCWloDsh6jicEAwIJItIElGxt63Wxd8P3bBjvHPyo+XfJMS7BkNX
UXefTBaZweUZAf5kwlOzJoJAjthXmGAmfnAHip1057x7BkQeGPPy
ArSIQIiHCyAxAFvZgZGAT4ga0EPkFCQYYA5zQ5mjIgDYxoYfIP55
DGMcdke3R/AgLABGS4HIk6ACLCFcJcxQpgO/Q6MDvIwWUmEEqB+I
wZkN6QgfHgSZu1hJPvRHIIZEcj+QBNRccASDVwgC1PgxAtmuGuA4
XmBHcZzmO/AyAxigFR9AYpBeCAZmFEQWsABHNzMDAjwwZ5hRnPfH
ADWYLKe<<<
"""

# 500 = ~15.5 squares
# 250 = ~8 squares
grid_size = (32*16, 32*8)
max_x, max_y = grid_size
default_hint_x = max_x/4

required_power_mw = 150
boilers = math.ceil(required_power_mw/1.8)

# 2460 green circuits/minute. 2.8 belts. 1300 go to blue circuit, 850 go to
#      red circuit
# Each assembler = 90/minute
# 4 green circuit assemblers = 360/minute
total_green_circuits = 27.4

# 425 red circuits/minute, half a belt
total_red_circuits = 56.7

# 6338 iron plates/minute. one block is 24 smelters
total_iron_smelting = 169.1

total_steel_smelting = 87.4

total_copper_smelting = 157.4

blocks = {
    # top left is (0, 0)
    "Copper Mine": Block(28, 28, fixed_x=7*32, fixed_y=40),
    "Ore Mine": Block(20, 32, fixed_x=1, fixed_y=2*32+5),
    "Coal Mine": Block(1, 1, fixed_x=1, fixed_y=max_y-3*32+16),
    "Stone Mine": Block(16, 16, fixed_x=36, fixed_y=2*32-5),
    "Water": Block(60, 52, fixed_x=3*32+2, fixed_y=max_y-53),
    "Oil": Block(1, 1, fixed_x=7*32+10, fixed_y=3*32-5),

    "Cliffs": Block(20, 25, fixed_x=6*32+20, fixed_y=3*32),
    "Cliffs 2": Block(24, 20, fixed_x=7*32+12, fixed_y=2*32+10),

    "Power Plant": power_plant(power_mw=required_power_mw),

    # ~34.7 for LDS
    "Copper Smelting - LDS": electric_smelter(24),
    # 98.4 for green circuits
    "Copper Smelting - GC": electric_smelter(24*4),
    "Copper Smelting - Other": electric_smelter(total_copper_smelting - 24*4 - 24),

    "Iron Smelting - Steel": electric_smelter(24*3),
    "Iron Smelting - GC": electric_smelter(24*2),
    "Iron Smelting - Other": electric_smelter(total_iron_smelting - 24*3 - 24*2),

    "Steel Smelting - Purple": electric_smelter(24*2),
    "Steel Smelting - Other": electric_smelter(total_steel_smelting - 24*2),

    "Stone Smelting": electric_smelter(3.7),

    "Advanced Oil Processing": advanced_oil(12.5),
    # 1.2 crackers
    "Heavy Oil Cracking": (10, 10),
    # need 4.9 light oil crackers - these are covered in advanced oil
    "Light Oil Cracking": (10, 10),

    "Plastic": plastic(9.8),

    # 2460 green circuits/minute. 2.8 belts. 1300 go to blue circuit, 850 go to
    #      red circuit
    # Each assembler = 90/minute

    # For blue circuits
    "Green Circuit Assembly - Blue": green_circuit(4*3),

    # Red circuits
    "Green Circuit Assembly - Red": green_circuit(4*2),

    # All others
    "Green Circuit Assembly - Other": green_circuit(total_green_circuits - 4*3-4*2),

    # 4.66 blocks
    "Red Circuit - RCU": red_circuit(12),
    "Red Circuit - Other": red_circuit(total_red_circuits - 12),
    "Blue Circuit Assembly": blue_circuit(14.5),

    # https://www.factorio.school/view/-M3UFESzD4DDkv8E__6l
    "Inserter Mall": (7, 28),

    "Assembler Mall": (18, 7),
    "Medium Power Pole Mall": (7, 8),

    # https://www.factorio.school/view/-L8geV1--kQGYWiMW4v6
    # Add some height for iron gear assembler
    "Belt Mall": (16, 18),

    # This is covered as part of Yellow Science
    # "Low Density Structure": low_density_structure(20),

    # tileable science: https://www.factorio.school/view/-KnQ865j-qQ21WoUPbd3

    # 1 gear assembler
    # only really need one side of the belt
    "Red Science": (15, 12),

    # 2 gear assemblers
    # 1 inserter assembler
    # 1 belt assembler
    "Green Science": (18, 16),

    # 12 blue science factories
    # 10 engine assemblers
    # 1 pipe assembler
    # 1 gear assembler
    # it's 25x18, but add some buffer for belt input/output
    "Blue Science": (27, 18+6),
    # "Blue Science": blue_science(12),

    # 7 purple science uses:
    # 3 rail assemblers
    # 2 furnace assemblers
    # 5 productivity module assemblers
    # 2 iron assemblers
    #
    # add a third furnace in here
    # 15 = 3 assemblers, plus add a lot for belts input/output
    "Purple Science": (33, 15+6),

    # 4 engine assemblers
    # 4 electric engine assemblers
    # 7 flying robot frames
    #
    # height is 10 assemblers, plus we typically need lots of belts
    "Yellow Science": (41, 30+6),

    # 0.2
    "Sulfuric Acid": plastic(1),

    # 0.3 - covered in advanced oil
    "Lubricant": plastic(1),

    "Battery": plastic(1.4),

    # yellow science covers 4 of 5.6
    "Electric Engine Unit": plastic(3),

    "Sulfur": plastic(1),

    "Concrete": plastic(1.7),

    # 6.7 solid fuel for rocket fuel
    #
    # 12 solid fuel for 40 boilers (72 MW)
    "Solid Fuel": solid_fuel(6.7 + 24),
    "Rocket Fuel": rocket_fuel(13.4),
    "Rocket Control Unit": electric_smelter(20),
    "Rocket": (11, 9),

    "Lab": (19, 24),
}

print("blocks: {}".format(blocks))

# rotatable_blocks = {name for name, (w, h) in blocks.items() if w != h and w > 5 and h > 5}
rotatable_blocks = {
    'Copper Smelting - GC',
    'Copper Smelting - Other',
    'Green Circuit Assembly - Blue',
    'Green Circuit Assembly - Red',
    'Green Circuit Assembly - Other',
    'Iron Smelting - Steel',
    'Iron Smelting - GC',
    'Steel Smelting - Purple',
    'Steel Smelting - Other',
    'Red Circuit - Other',
    'Advanced Oil Processing',
    'Solid Fuel',
    'Rocket Fuel',
    'Rocket Control Unit',
    'Blue Circuit',
    'Inserter Mall',
    'Yellow Science',
}

connections = [
    Connection("Coal Mine", "Copper Smelting - LDS", "MM", "BM", 1),
    Connection("Copper Mine", "Copper Smelting - LDS", "MM", "BM", 1),
    Connection("Coal Mine", "Copper Smelting - GC", "MM", "BM", 1.5),
    Connection("Copper Mine", "Copper Smelting - GC", "MM", "BM", 4),
    Connection("Coal Mine", "Copper Smelting - Other", "MM", "BM", 1),
    Connection("Copper Mine", "Copper Smelting - Other", "MM", "BM", 1),

    Connection("Coal Mine", "Iron Smelting - Steel", "MM", "LM", 1),
    Connection("Coal Mine", "Iron Smelting - GC", "MM", "LM", 1),
    Connection("Coal Mine", "Iron Smelting - Other", "MM", "LM", 1),

    Connection("Ore Mine", "Iron Smelting - Steel", "MM", "LM", 3),
    Connection("Ore Mine", "Iron Smelting - GC", "MM", "LM", 2),
    Connection("Ore Mine", "Iron Smelting - Other", "MM", "LM", 1),

    Connection("Iron Smelting - Steel", "Steel Smelting - Purple", "RM", "LM", 2),
    ("Coal Mine", "Steel Smelting - Purple", "MM", "LM"),
    Connection("Iron Smelting - Steel", "Steel Smelting - Other", "RM", "LM", 2),
    ("Coal Mine", "Steel Smelting - Other", "MM", "LM"),

    ("Stone Mine", "Stone Smelting", "RM", "LM"),
    ("Coal Mine", "Stone Smelting", "MM", "LM"),

    Connection("Iron Smelting - GC", "Green Circuit Assembly - Blue", "RM", "BM", 1),
    Connection("Iron Smelting - GC", "Green Circuit Assembly - Red", "RM", "BM", 1),
    Connection("Iron Smelting - GC", "Green Circuit Assembly - Other", "RM", "BM", 1),

    Connection("Copper Smelting - GC", "Green Circuit Assembly - Blue", "RM", "BL", 2),
    Connection("Copper Smelting - GC", "Green Circuit Assembly - Red", "RM", "BL", 1),
    Connection("Copper Smelting - GC", "Green Circuit Assembly - Other", "RM", "BL", 1),

    Connection("Coal Mine", "Power Plant", "RM", "MM", math.ceil(boilers/20)),
    Connection("Water", "Power Plant", "RM", "MM", math.ceil(boilers/20)),

    ("Iron Smelting - Other", "Inserter Mall", "RM", "BL"),
    ("Green Circuit Assembly - Other", "Inserter Mall", "BM", "BR"),

    ("Iron Smelting - Other", "Assembler Mall", "RM", "TL"),
    ("Green Circuit Assembly - Other", "Assembler Mall", "BM", "TL"),
    ("Steel Smelting - Other", "Assembler Mall", "RM", "BL"),

    ("Iron Smelting - Other", "Medium Power Pole Mall", "RM", "BL"),
    ("Steel Smelting - Other", "Medium Power Pole Mall", "RM", "BR"),
    ("Copper Smelting - Other", "Medium Power Pole Mall", "BM", "BR"),

    ("Iron Smelting - Other", "Belt Mall", "RM", "TM"),
    ("Green Circuit Assembly - Other", "Belt Mall", "BM", "TL"),

    ("Advanced Oil Processing", "Plastic", "TL", "TL"),
    ("Light Oil Cracking", "Plastic", "RM", "TL"),
    ("Coal Mine", "Plastic", "MM", "LM"),

    ("Copper Smelting - Other", "Red Circuit - RCU", "RM", "TL"),
    ("Green Circuit Assembly - Red", "Red Circuit - RCU", "BM", "LM"),
    ("Plastic", "Red Circuit - RCU", "RM", "LM"),
    ("Copper Smelting - Other", "Red Circuit - Other", "RM", "TL"),
    ("Green Circuit Assembly - Red", "Red Circuit - Other", "BM", "LM"),
    ("Plastic", "Red Circuit - Other", "RM", "LM"),

    ("Heavy Oil Cracking", "Light Oil Cracking", "MM", "MM"),

    ("Water", "Advanced Oil Processing", "TL", "TL"),
    ("Oil", "Advanced Oil Processing", "TL", "TL"),

    ("Advanced Oil Processing", "Light Oil Cracking", "TL", "MM"),
    ("Advanced Oil Processing", "Heavy Oil Cracking", "TL", "MM"),

    ("Water", "Sulfur", "MM", "MM"),
    ("Advanced Oil Processing", "Sulfur", "MM", "MM"),

    ("Advanced Oil Processing", "Lubricant", "TL", "MM"),

    ("Water", "Sulfuric Acid", "MM", "MM"),
    ("Iron Smelting - Other", "Sulfuric Acid", "RM", "MM"),
    ("Sulfur", "Sulfuric Acid", "MM", "MM"),

    ("Sulfuric Acid", "Blue Circuit Assembly", "MM", "TL"),
    ("Green Circuit Assembly - Blue", "Blue Circuit Assembly", "BM", "BM"),
    ("Red Circuit - Other", "Blue Circuit Assembly", "LM", "BM"),

    ("Steel Smelting - Other", "Low Density Structure", "RM", "MM"),
    ("Plastic", "Low Density Structure", "RM", "MM"),
    ("Copper Smelting - LDS", "Low Density Structure", "RM", "MM"),

    ("Green Circuit Assembly - Other", "Speed Module", "BM", "MM"),
    ("Red Circuit - Other", "Speed Module", "LM", "MM"),

    Connection("Iron Smelting - Other", "Red Science", "RM", "TR", 2),
    Connection("Copper Smelting - Other", "Red Science", "RM", "TR", 2),

    ("Iron Smelting - Other", "Green Science", "RM", "TR"),
    ("Green Circuit Assembly - Other", "Green Science", "BM", "TR"),

    ("Iron Smelting - Other", "Blue Science", "RM", "TL"),
    ("Steel Smelting - Other", "Blue Science", "RM", "TM"),
    ("Red Circuit - Other", "Blue Science", "LM", "TR"),
    ("Sulfur", "Blue Science", "MM", "TR"),

    ("Lubricant", "Yellow Science", "MM", "BL"),
    ("Green Circuit Assembly - Other", "Yellow Science", "BM", "TL"),
    ("Steel Smelting - Other", "Yellow Science", "RM", "TM"),
    ("Iron Smelting - Other", "Yellow Science", "RM", "TL"),
    ("Plastic", "Yellow Science", "MM", "MM"),
    ("Copper Smelting - Other", "Yellow Science", "RM", "TR"),
    ("Battery", "Yellow Science", "MM", "TL"),
    ("Blue Circuit Assembly", "Yellow Science", "MM", "TM"),

    ("Steel Smelting - Purple", "Purple Science", "RM", "TL"),
    ("Iron Smelting - Other", "Purple Science", "RM", "TL"),
    ("Stone Mine", "Purple Science", "RM", "TL"),
    ("Stone Smelting", "Purple Science", "RM", "TM"),
    ("Red Circuit - Other", "Purple Science", "LM", "TM"),
    ("Green Circuit Assembly - Other", "Purple Science", "BM", "TM"),

    Connection("Red Science", "Lab", "TL", "BL", 2),
    Connection("Green Science", "Lab", "TL", "BL", 1.5),

    ("Blue Science", "Lab", "TR", "BL"),
    ("Yellow Science", "Lab", "TM", "BL"),
    ("Purple Science", "Lab", "TR", "BL"),

    ("Sulfuric Acid", "Battery", "MM", "MM"),

    ("Advanced Oil Processing", "Solid Fuel", "TL", "MM"),
    ("Heavy Oil Cracking", "Solid Fuel", "MM", "MM"),

    ("Advanced Oil Processing", "Rocket Fuel", "TL", "MM"),
    ("Heavy Oil Cracking", "Rocket Fuel", "MM", "MM"),
    ("Solid Fuel", "Rocket Fuel", "MM", "MM"),

    Connection("Solid Fuel", "Power Plant", "MM", "MM", 0.5),

    ("Speed Module", "Rocket Control Unit", "MM", "MM"),
    ("Blue Circuit Assembly", "Rocket Control Unit", "MM", "MM"),

    ("Water", "Concrete", "MM", "MM"),
    ("Iron Ore", "Concrete", "MM", "MM"),
    ("Stone Smelting", "Concrete", "RM", "MM"),

    ("Lubricant", "Electric Engine Unit", "MM", "TL"),
    ("Green Circuit Assembly - Other", "Electric Engine Unit", "BM", "MM"),
    # hack - this reuses the engine assemblers from blue science
    ("Blue Science", "Electric Engine Unit", "MM", "MM"),

    ("Concrete", "Rocket Silo Assembler", "MM", "MM"),
    ("Electric Engine Unit", "Rocket Silo Assembler", "MM", "MM"),
    ("Blue Circuit Assembly", "Rocket Silo Assembler", "MM", "MM"),
    ("Steel Smelting - Other", "Rocket Silo Assembler", "RM", "MM"),

    ("Rocket Fuel", "Rocket", "MM", "MM"),
    ("Low Density Structure", "Rocket", "MM", "MM"),
    ("Rocket Control Unit", "Rocket", "MM", "MM"),
]
