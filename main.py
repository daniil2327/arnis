#!/usr/bin/env python

# Copyright 2022 by louis-e, https://github.com/louis-e/.
# MIT License
# Please see the LICENSE file that should have been included as part of this package.

import os
import sys
import time
import gc
import argparse
import anvil
from random import randint
from math import floor
import numpy as np

from .getData import getData
from .processData import parseData

parser = argparse.ArgumentParser(
    description="Arnis - Generate cities from real life in Minecraft using Python"
)
parser.add_argument("--city", dest="city", help="Name of the city")
parser.add_argument("--state", dest="state", help="Name of the state")
parser.add_argument("--country", dest="country", help="Name of the country")
parser.add_argument("--bbox", dest="bbox", help="Bounding box of the city")
parser.add_argument("--file", dest="file", help="JSON file containing OSM data")
parser.add_argument("--path", dest="path", help="Path to the minecraft world")
parser.add_argument(
    "--debug",
    dest="debug",
    default=False,
    action="store_true",
    help="Enable debug mode",
)
args = parser.parse_args()
if args.city is None or args.state is None or args.country is None or args.path is None:
    if args.bbox is None and args.file is None:
        print("Error! Missing arguments")
        os._exit(1)

gc.collect()
np.seterr(all="raise")
np.set_printoptions(threshold=sys.maxsize)

processStartTime = time.time()
air = anvil.Block("minecraft", "air")
brick = anvil.Block("minecraft", "bricks")
stone = anvil.Block("minecraft", "stone")
grass_block = anvil.Block("minecraft", "grass_block")
spruce_log = anvil.Block("minecraft", "spruce_log")
birch_leaves = anvil.Block("minecraft", "birch_leaves")
dirt = anvil.Block("minecraft", "dirt")
sand = anvil.Block("minecraft", "sand")
podzol = anvil.Block.from_numeric_id(3, 2)
grass = anvil.Block.from_numeric_id(175, 2)
farmland = anvil.Block("minecraft", "farmland")
water = anvil.Block("minecraft", "water")
wheat = anvil.Block("minecraft", "wheat")
carrots = anvil.Block("minecraft", "carrots")
potatoes = anvil.Block("minecraft", "potatoes")
cobblestone = anvil.Block("minecraft", "cobblestone")
iron_block = anvil.Block("minecraft", "iron_block")
oak_log = anvil.Block.from_numeric_id(17)
oak_leaves = anvil.Block.from_numeric_id(18)
birch_log = anvil.Block("minecraft", "birch_log")
white_stained_glass = anvil.Block("minecraft", "white_stained_glass")
dark_oak_door_lower = anvil.Block(
    "minecraft", "dark_oak_door", properties={"half": "lower"}
)
dark_oak_door_upper = anvil.Block(
    "minecraft", "dark_oak_door", properties={"half": "upper"}
)
cobblestone_wall = anvil.Block("minecraft", "cobblestone_wall")
stone_brick_slab = anvil.Block.from_numeric_id(44, 5)

red_flower = anvil.Block.from_numeric_id(38)
yellow_flower = anvil.Block("minecraft","dandelion")
blue_flower = anvil.Block("minecraft", "blue_orchid")
white_flower = anvil.Block("minecraft", "azure_bluet")

white_concrete = anvil.Block("minecraft", "white_concrete")
black_concrete = anvil.Block("minecraft", "black_concrete")
gray_concrete = anvil.Block("minecraft", "gray_concrete")
light_gray_concrete = anvil.Block("minecraft", "light_gray_concrete")
green_stained_hardened_clay = anvil.Block.from_numeric_id(159, 5)
dirt = anvil.Block("minecraft", "dirt")
glowstone = anvil.Block("minecraft", "glowstone")
sponge = anvil.Block("minecraft", "sponge")

regions = {}
for x in range(0, 3):
    for z in range(0, 3):
        regions["r." + str(x) + "." + str(z)] = anvil.EmptyRegion(0, 0)


def setBlock(block, x, y, z):
    flooredX = floor(x / 512)
    flooredZ = floor(z / 512)
    identifier = "r." + str(flooredX) + "." + str(flooredZ)
    if identifier not in regions:
        regions[identifier] = anvil.EmptyRegion(0, 0)
    regions[identifier].set_block(block, x - flooredX * 512, y, z - flooredZ * 512)


def fillBlocks(block, x1, y1, z1, x2, y2, z2):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                if not (x == x2 + 1 or y == y2 + 1 or z == z2 + 1):
                    setBlock(block, x, y, z)


mcWorldPath = args.path
if mcWorldPath[-1] == "/":
    mcWorldPath = mcWorldPath[:-1]


def saveRegion(region="all"):
    if region == "all":
        for key in regions:
            regions[key].save(mcWorldPath + "/region/" + key + ".mca")
            print(f"Saved {key}")
    else:
        regions[region].save(mcWorldPath + "/region/" + region + ".mca")
        print(f"Saved {region}")


from .tree import createTree
def run():
    if not (os.path.exists(mcWorldPath + "/region")):
        print("Error! No Minecraft world found at given path")
        os._exit(1)

    rawdata = getData(args.city, args.state, args.country, args.bbox, args.file, args.debug)
    imgarray = parseData(rawdata, args)

    print("Generating minecraft world...")

    x = 0
    z = 0
    ElementIncr = 0
    ElementsLen = len(imgarray)
    lastProgressPercentage = 0
    for i in imgarray:
        progressPercentage = round(100 * (ElementIncr + 1) / ElementsLen)
        if (
            progressPercentage % 10 == 0
            and progressPercentage != lastProgressPercentage
        ):
            print(f"Pixel {ElementIncr + 1}/{ElementsLen} ({progressPercentage}%)")
            lastProgressPercentage = progressPercentage

        z = 0
        for j in i:
            setBlock(dirt, x, 0, z)
            if j == 0:  # Ground
                setBlock(grass_block, x, 1, z)
            elif j == 10:  # Street
                setBlock(black_concrete, x, 1, z)
                setBlock(air, x, 2, z)
            elif j == 11:  # Footway
                setBlock(gray_concrete, x, 1, z)
                setBlock(air, x, 2, z)
            elif j == 12:  # Natural path
                setBlock(cobblestone, x, 1, z)
            elif j == 13:  # Bridge
                setBlock(light_gray_concrete, x, 2, z)
                setBlock(light_gray_concrete, x - 1, 2, z - 1)
                setBlock(light_gray_concrete, x + 1, 2, z - 1)
                setBlock(light_gray_concrete, x + 1, 2, z + 1)
                setBlock(light_gray_concrete, x - 1, 2, z + 1)
            elif j == 14:  # Railway
                setBlock(iron_block, x, 2, z)
            elif j == 20:  # Parking
                setBlock(gray_concrete, x, 1, z)
            elif j == 21:  # Fountain border
                setBlock(light_gray_concrete, x, 2, z)
                setBlock(white_concrete, x, 1, z)
            elif j >= 22 and j <= 24:  # Fence
                if str(j)[-1] == "2" or int(str(j[0])[-1]) == 2:
                    setBlock(cobblestone_wall, x, 2, z)
                else:
                    fillBlocks(cobblestone, x, 2, z, x, int(str(j[0])[-1]), z)

                setBlock(grass_block, x, 1, z)
            elif j == 30:  # Meadow
                setBlock(grass_block, x, 1, z)
                randomChoice = randint(0, 2)
                if randomChoice == 0 or randomChoice == 1:
                    setBlock(grass, x, 2, z)
            elif j == 31:  # Farmland
                randomChoice = randint(0, 16)
                if randomChoice == 0:
                    setBlock(water, x, 1, z)
                else:
                    setBlock(farmland, x, 1, z)
                    randomChoice = randint(0, 2)
                    if randomChoice == 0:
                        setBlock(wheat, x, 2, z)
                    elif randomChoice == 1:
                        setBlock(carrots, x, 2, z)
                    else:
                        setBlock(potatoes, x, 2, z)
            elif j == 32:  # Forest
                setBlock(grass_block, x, 1, z)
                randomChoice = randint(0, 20)
                randomTree = randint(1, 3)
                randomFlower = randint(1, 4)
                if randomChoice == 20:
                    createTree(x, z, randomTree)
                elif randomChoice == 2:
                    if randomFlower == 1:
                        setBlock(red_flower, x, 2, z)
                    elif randomFlower == 2:
                        setBlock(blue_flower, x, 2, z)
                    elif randomFlower == 3:
                        setBlock(yellow_flower, x, 2, z)
                    else:
                        setBlock(white_flower, x, 2, z)
                elif randomChoice == 0 or randomChoice == 1:
                    setBlock(grass, x, 2, z)
            elif j == 33:  # Cemetery
                setBlock(podzol, x, 1, z)
                randomChoice = randint(0, 100)
                if randomChoice == 0:
                    setBlock(cobblestone, x - 1, 2, z)
                    setBlock(stone_brick_slab, x - 1, 3, z)
                    setBlock(stone_brick_slab, x, 2, z)
                    setBlock(stone_brick_slab, x + 1, 2, z)
                elif randomChoice == 1:
                    setBlock(cobblestone, x, 2, z - 1)
                    setBlock(stone_brick_slab, x, 3, z - 1)
                    setBlock(stone_brick_slab, x, 2, z)
                    setBlock(stone_brick_slab, x, 2, z + 1)
                elif randomChoice == 2 or randomChoice == 3:
                    setBlock(red_flower, x, 2, z)
            elif j == 34:  # Beach
                setBlock(sand, x, 1, z)
            elif j == 35:  # Wetland
                randomChoice = randint(0, 2)
                if randomChoice == 0:
                    setBlock(grass_block, x, 1, z)
                else:
                    setBlock(water, x, 1, z)
            elif j == 36:  # Pitch
                setBlock(green_stained_hardened_clay, x, 1, z)
            elif j == 37:  # Swimming pool
                setBlock(water, x, 1, z)
                setBlock(white_concrete, x, 0, z)
            elif j == 38:  # Water
                setBlock(water, x, 1, z)
            elif j == 39:  # Raw grass
                setBlock(grass_block, x, 1, z)

            elif j >= 50 and j <= 59:  # House corner
                fillBlocks(white_concrete, x, 2, z, x, 4, z)
            elif j >= 60 and j <= 69:  # House wall
                fillBlocks(white_concrete, x, 2, z, x, 4, z)
            elif j >= 70 and j <= 79:  # House interior
                setBlock(white_concrete, x, 2, z)

            z += 1
        x += 1
        ElementIncr += 1

    print("Saving minecraft world...")
    saveRegion()
    print(
        f"Done! Finished in {(time.time() - processStartTime):.2f} "
        + f"seconds ({((time.time() - processStartTime) / 60):.2f} minutes)"
    )
    os._exit(0)
