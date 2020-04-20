# PyDragons
PyDragons is an AWS project for data generation, hosting, querying, and visualization initially authored by Molly Proffitt Sheets and open to collaborators.

# Updates
1.0 March 24, 2020: Uploaded initial PyDragons-AthenaDemo files
1.1 April 20, 2020: Uploaded initial PyDragons-StreamingDemo files

# Getting Started Using PyDragons-AthenaDemo
1. Grab all github files and watch the video at the youtube link here: https://youtu.be/mhvhJAFzsxo
2. Upload sample CSVs to S3 following the partition structure as shown in the video to a raw folder for each table (dragonevents and dragons). For example, you should have an S3 structure of bucketname > raw > dragonevents > 2020 > 03 > 19 > CSV and bucket name > raw > dragons > 2020 > 03 > 19 > CSV
3. Create separate folders for raw data, transformed data, and Athena queries

# Create or Modify Your Own CSV Data Sets
1. To create your own data sets, run the SpawnDragonsToCSV.py python 3 script in Terminal 
2. To modify the names output of these sets you can edit dragonnames.csv
3. To modify dragon burn, loot, sleep, and eat parameters modify dragontypes.csv
4. You can also modify the "Design Variables" section in SpawnDragonsToCSV.py to edit the number of events created,
number of dragons created, and timing between events and dragons creations
