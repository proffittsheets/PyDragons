import numpy # In shell run "pip3 install numpy" if you run into errors
import math
import random
import time
import sys
import json
import csv
from uuid import uuid4
from datetime import datetime


# See this error? Check your python version in shell with "python --version".
# Run this script using Python 3 by typing "python3 SpawnDragonsToCSV.py"
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


################################################################################
#                             DESIGN VARIABLES                                 #
################################################################################
eventsTick = 20000         # Number of ticks to loop through to create events
initialDragonsCount = 10   # Number of initial dragons to create
newDragonsCount = 1        # Number of new dragons to create per loop tick
cageDragonsCount = 1       # Number of dragons to cage per loop tick
numEvents = 5              # Number of dragon actions to create per loop tick
eventSleepInterval = 0.025 # Time between each dragon action event being created
dmSleepInterval = 0.25     # Controls overall speed of dragon machine

# Create empty lists to store dragon adjectives and last names
FName = []
LNameStart = []
LNameEnd = []

# Create empty list to store dragon types
DragonTypes = []

# Create empty dictionary to store dragon type parameters
DragonTypesDict = {}

# Create empty list to store our current dragons
dragons = []


################################################################################
#                         CSV IMPORTS & CLEAN-UP                               #
################################################################################
# Import Names CSV and Populate Lists
with open('dragonnames.csv', newline='') as csvfile:
    csv.reader(csvfile, delimiter=',', quotechar="'")

    # Skip Header Row
    next(csvfile)

    for row in csvfile:
        data = row.split(',')
        i=0
        while i < len(data):
            data[i]=data[i].replace('\n','')
            data[i]=data[i].replace('\r','')
            i=i+1

        # Update Names Lists
        FName.append(data[0])
        LNameStart.append(data[1])
        LNameEnd.append(data[2])

# Import Dragon Types CSV and Populate DragonTypesDict
with open ('dragontypes.csv', newline='') as typescsvfile:
    csv.reader(typescsvfile, delimiter=',', quotechar='"')

    # Skip Header Row
    next(typescsvfile)

    for rows in typescsvfile:
        data = rows.split(',')
        i=0
        while i < len(data):
             data[i]=data[i].replace('\r','')
             data[i]=data[i].replace('\n','')
             data[i]=data[i].replace('"','')
             data[i]=data[i].replace(' ','')
             i=i+1

        # Update Dragon Types Dictionary
        DragonTypesDict.update({data[0]:{"RegionPref": data[1],
        "Sleep": float(data[2]), "Burn": float(data[3]), "Loot": float(data[4]),
        "Eat": float(data[5]), "MinFt": float(data[6]), "MaxFt": float(data[7]),
        "BurnMin": int(data[8]), "BurnMax": int(data[9]),
        "FoodTypes": data[10].split('|'), "LootTypes": data[11].split('|')
        }})

        # Update Dragon List
        DragonTypes.append(data[0])

# Dictionary of Towns
TownsDict = {
    "Coastal": {"Sanddollar Bay":{"Size_km": 7.5, "Pop": 7503},"Anchor Bay":{"Size_km": 7, "Pop": 280},"Low Fog Cove":{"Size_km": 2, "Pop": 5},
        "Pebble Bay":{"Size_km": 1, "Pop": 20},"Obsidian Beach":{"Size_km": 1.5, "Pop": 55},"Slate Sea Island":{"Size_km": 134, "Pop": 486000}
    },

    "Mountains": {"Rosewood Ridge":{"Size_km": 8, "Pop": 5730},"Cedar Ridge":{"Size_km": 205, "Pop": 568000},"Hickerywood Village":{"Size_km": 22, "Pop": 12300},
        "Cheateaus at Jade Lake":{"Size_km": 5, "Pop": 105},"Cabins at Metal Mountain":{"Size_km": 10, "Pop": 45},"Periwinkle Palace":{"Size_km": 0.5, "Pop": 50}
    },

    "Riverside": {"Cheateaus of Dahm":{"Size_km": 10, "Pop": 11200},"Harvestpatch Village":{"Size_km": 10, "Pop": 9650},"Whistleton Village":{"Size_km": 10, "Pop": 4500},
        "Merryton":{"Size_km": 32, "Pop": 26890},"Ruby Coral Cove":{"Size_km": 4.5, "Pop": 1250},"Mulberria":{"Size_km": 115, "Pop": 35200}
    },

    "Valley": {"Town of Sleepton":{"Size_km": 38, "Pop": 45350},"Town of Rockton":{"Size_km": 25, "Pop": 18000},"Town of Mistycliff":{"Size_km": 20, "Pop": 15300},
        "Amberville":{"Size_km": 36, "Pop": 65390},"Sprucepatch":{"Size_km": 185, "Pop": 20500}
    },
}


################################################################################
#                       EXPORT CSV SETUPS & FUNCTIONS                          #
################################################################################
# Write Header to Dragon CSV
dragon_csv_columns = ['dragonID','eventUUID','eventTimestamp',
'utc_offset','eventName','name','type','region','size_ft']

with open('dragons.csv', 'a+', newline='') as csvfile:
    dragonWriter = csv.DictWriter(csvfile, fieldnames=dragon_csv_columns)
    dragonWriter.writeheader()

# Write Header to Action CSV
action_csv_columns = ['dragonID','eventUUID','eventTimestamp',
'utc_offset','eventName','state','value','valueType','location','affectedPop']

with open('dragonevents.csv', 'a+', newline='') as csvfile:
    actionWriter = csv.DictWriter(csvfile, fieldnames=action_csv_columns)
    actionWriter.writeheader()

def sendDragonCreated(dragon):
    """Send Dragon Created Event to CSV."""

    with open('dragons.csv', 'a+', newline='') as csvfile:
        dragonWriter = csv.DictWriter(csvfile, fieldnames=dragon_csv_columns)
        dragonWriter.writerow(dragon)
    print('Dragon Created:' + str(dragon))

def sendActionCreated(action):
    """Send Dragon Action Event to CSV"""

    with open('dragonevents.csv', 'a+', newline='') as csvfile:
        actionWriter = csv.DictWriter(csvfile, fieldnames=action_csv_columns)
        actionWriter.writerow(action)
    print('Action:' + str(action))


################################################################################
#                                MAIN FUNCTIONS                               #
################################################################################
def create_dragon():
    """Spawn a new dragon."""

    dragon_type = random.choice(DragonTypes)
    spawned_dragon_dict = DragonTypesDict[dragon_type]
    MinFt = spawned_dragon_dict["MinFt"]
    MaxFt = spawned_dragon_dict["MaxFt"]

    dragon = {}
    dragon['dragonID'] = str(uuid4())
    dragon['eventUUID'] = str(uuid4())
    dragon['eventTimestamp'] = getCurrentUTCTime()
    dragon['utc_offset'] = getOffset()
    dragon['eventName'] = 'dragonSpawned'
    dragon['name'] = random.choice(FName) + ' ' + random.choice(LNameStart) + random.choice(LNameEnd)
    dragon['type'] = dragon_type
    dragon['region'] = spawned_dragon_dict["RegionPref"]
    dragon['size_ft'] = random.randrange(MinFt, MaxFt)

    # Send Data
    sendDragonCreated(dragon)

    return dragon

def create_new_dragons():
    """Create multiple new dragons and appends list of dragons"""

    n = 0
    while n < newDragonsCount:
        n = n + 1

        # Spawn a Dragon
        dragon = create_dragon()

        # Append List
        dragons.append(dragon)

def cage_dragons():
    """Cages dragons."""

    n = 0
    while n < cageDragonsCount:
        n = n + 1

        # Pick a Dragon
        dragon = random.choice(dragons)

        # Remove it from the list of current dragons
        dragons.remove(dragon)

def create_dragon_action():
    """Create a new dragon action event"""

    random.shuffle(dragons)
    dragon = random.choice(dragons)
    currenttype = dragon['type']

    # Store all our values for code legibility
    spawned_dragon_dict = DragonTypesDict[currenttype]
    regionPref = spawned_dragon_dict["RegionPref"]
    sleepChance = spawned_dragon_dict["Sleep"]
    burnChance = spawned_dragon_dict["Burn"]
    lootChance = spawned_dragon_dict["Loot"]
    eatChance = spawned_dragon_dict["Eat"]
    burnMin = spawned_dragon_dict["BurnMin"]
    burnMax = spawned_dragon_dict["BurnMax"]
    foodTypes = spawned_dragon_dict["FoodTypes"]
    lootTypes = spawned_dragon_dict["LootTypes"]

    # Pick a dragon state based on % weight it will occur for the dragon type
    weightsList = [sleepChance, burnChance, lootChance, eatChance]
    stateChoices = ['sleeping','burning','looting','eating']
    state = random.choices(stateChoices, weightsList, k=1)[0]

    # Pick a Town
    PrefDict = TownsDict[regionPref]
    Town = random.choice(list(PrefDict))
    TownParam = PrefDict[str(Town)]

    # Create the action event
    action = {}
    action['dragonID'] = dragon['dragonID']
    action['eventUUID'] = str(uuid4())
    action['eventTimestamp'] = getCurrentUTCTime()
    action['utc_offset'] = getOffset()
    action['eventName'] = 'dragonAction'
    action['state'] = state
    action['value'] = getValue(state, burnMin, burnMax)
    action['valueType'] = getValueType(state, foodTypes, lootTypes)
    action['location'] = Town
    action['affectedPop'] = getAffected(state, TownParam["Pop"])

    # Send Data
    sendActionCreated(action)

    return action

def getCurrentUTCTime():
    """Gets Current UTC Time."""

    utcdt = datetime.utcnow()
    currentUTCTime = utcdt.strftime('%Y-%m-%d %H:%M:%S')

    return currentUTCTime

def getOffset():
    """Determines hours between local time and UTC as a timezone offset"""

    ts = time.time()
    utc_offset = (datetime.fromtimestamp(ts) -
    datetime.utcfromtimestamp(ts)).total_seconds()

    offset = str(round(utc_offset / 3600)) + ':00'

    return offset

def getValue(state, burnMin, burnMax):
    """Determines a value based on state for a dragon action to return"""

    if state == 'burning':
        return random.randrange(burnMin, burnMax)
    elif state == 'eating':
        return random.randrange(1,75)
    elif state == 'looting':
        return random.randrange(1,5)
    else: return 0

def getValueType(state, foodTypes, lootTypes):
    """Determines a value type based on state for a dragon action to return"""

    if state == 'burning':
        return '$'
    elif state == 'eating':
        return random.choice(foodTypes)
    elif state == 'looting':
        return random.choice(lootTypes)
    else: return 'Zzz'

def getAffected(state, Pop):
    """Determines the # of people to affect based on a Town's pop"""

    if state == 'burning':
        return math.ceil(random.randrange(1,Pop)*.75)
    elif state == 'eating':
        return math.ceil(random.randrange(1,Pop)*.05)
    elif state == 'looting':
        return math.ceil(random.randrange(1,Pop)*.05)
    else: return 0

def write_events():
    """Write multiple dragon action events and send 'em up."""

    n = 0
    while n < numEvents:
        time.sleep(eventSleepInterval)
        n = n + 1
        event = create_dragon_action()

def spawn_initial_dragons():
    """Funtion creates an initial list of 10 dragons."""

    n = 0
    while n < initialDragonsCount:
        n = n + 1

        # Spawn a dragon
        dragon = create_dragon()

        # Append list of current dragons
        dragons.append(dragon)

    print('Initial dragons spawned' + '\n')

def spawn_dragon_machine():
    """Iterates over create dragons, dragon actions, and cage functions."""

    n = 0
    while n < eventsTick:
        time.sleep(dmSleepInterval)
        n = n + 1

        create_new_dragons()

        # Let's have those dragons take action
        write_events()

        # They're a bit dangerous. Let's cage some
        cage_dragons()


################################################################################
#                               START MACHINE                                  #
################################################################################
# Let's create some starter dragons!
spawn_initial_dragons()

# Let's do this. Start the dragon machine.
spawn_dragon_machine()
