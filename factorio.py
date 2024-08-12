import math

def electric_smelter(num_furnaces):
    # we use a basic model and assume you replace stone with electric (so
    # smelter can occupy same physical layout)

    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/5d7c46cad2773d4b5f185d6b2c5606a8d9e2abf9/position/1

    # this covers the splitter and belt tunnel
    splitter_belt_tunnel_width = 4

    # 2 furnaces take up 22 squares
    return (4 + math.ceil(num_furnaces/2), 11)

def green_circuit(num_assemblers):
    packs = math.ceil(num_assemblers/2)

    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/af8b75847d0714575989e1efac4f8cc5e7470f9d/position/0
    first_value = min(26, packs * 13)

    # lazy https://claude.ai/chat/f936dad3-e427-42a9-b516-da32f2fd5a23
    if packs <= 2:
        second_value = 13
    elif packs <= 4:
        second_value = 26
    else:
        second_value = 26 + 13 * ((packs - 1) // 2 - 1)

    return (first_value, second_value)

def red_circuit(num_assemblers):
    # inner belt: left side red circuits, right side half green, half plastic
    # outer belt: one side copper, one side coils
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/87805c2ea48b411ef0f8e561758f6229ffb04cda/position/0
    # https://imgur.com/T5WlY0M
    # need one copper coil for every 6 red circuits
    copper_coils = math.ceil(num_assemblers/6)
    if copper_coils == 1:
        # 8 wide, 4 for copper, 4 per red assembler
        return (8, 4 + 4*num_assemblers)
    # 4 height for every two assemblers
    # 4 height for every 2 copper coil assemblers
    return (14, math.ceil(copper_coils/2)*4 + math.ceil(num_assemblers/2)*4)

def plastic(num_chemical_plants):
    # https://fbe.teoxoy.com/?source=https://www.factorio.school/api/blueprintData/265ce01196a689ef5ea6eae916b84b812b06784e/
    # petroleum gas above the chem plant
    # plastic out on top belt
    # copper on bottom belt
    if num_chemical_plants <= 3:
        return (4*num_chemical_plants, 7)

    # use both sides of belt
    return (4*math.ceil(num_chemical_plants/2), 12)

grid_size = (100, 100)

# https://kirkmcdonald.github.io/calc.html#data=1-1-19&items=rocket-part:r:2
blocks = {
    "Copper Mine": (1, 1),
    "Ore Mine": (1, 1),
    "Coal Mine": (1, 1),
    "Copper Smelting": electric_smelter(49.4),
    "Iron Smelting": electric_smelter(26.2),
    "Steel Smelting": electric_smelter(5.4),

    "Plastic": plastic(3.2),

    # No separate copper coil block - all assembly part of green or red circuits
    "Green Circuit Assembly": green_circuit(13),
    "Red Circuit Assembly": red_circuit(28),
}

print("blocks: {}", blocks)

connections = [
    ("Coal Mine", "Copper Smelting"),
    ("Copper Mine", "Copper Smelting"),
    ("Coal Mine", "Iron Smelting"),
    ("Ore Mine", "Iron Smelting"),
    ("Iron Smelting", "Steel Smelting"),
    ("Coal Mine", "Steel Smelting"),

    ("Copper Smelting", "Green Circuit Assembly"),
    ("Copper Smelting", "Red Circuit Assembly"),
    ("Coal Mine", "Plastic"),
    ("Plastic", "Red Circuit Assembly"),
    ("Green Circuit Assembly", "Red Circuit Assembly"),
]
