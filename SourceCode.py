import requests, ast, os, zipfile, subprocess, threading, psutil
from clint.textui import progress
from tokenize import String

def eval_message(message):
    if message:
        return ast.literal_eval(message)
    return None

def fix_json(message):
    message = message.replace("\\n", "").replace("\\r", "").replace(" ", "")
    
    return message[2:len(message) - 1]

def start_game(exe):
    subprocess.call(exe)

def completed():
    input("Completed! Remember to start steam. Press enter to launch game...")
    
    s = (p.name() for p in psutil.process_iter())
    
    if not "steam.exe" in s:
        print("Steam not launched.")
        completed()
    
    print("Launching game!")
    
    game_folder_name = os.listdir("Downloads/CyclicWarriors")[0]
    
    for file in os.listdir(f"Downloads/CyclicWarriors/{game_folder_name}"):
        if file.endswith(".exe"):
            start_game(os.path.join(f"Downloads\CyclicWarriors\{game_folder_name}", file))
            break
    exit()

def download_game(game_url, map_url, version):
    print("Downloading full game!")
    print("The game is downloaded in two parts, the download bar will be repeated.")
    
    os.system('echo off\nrmdir /Q/S Downloads\CyclicWarriors')
    os.system('md Downloads\CyclicWarriors')
    
    os.system('echo off\nrmdir /Q/S Downloads\GameData')
    os.system('md Downloads\GameData')
    
    os.system('echo off\nrmdir /Q/S Downloads\MapData')
    os.system('md Downloads\MapData\Extracted')
    
    game_zip_path = 'Downloads/GameData/CyclicWarriors.zip'
    map_zip_path = 'Downloads/MapData/CyclicWarriors.zip'
    folder_path = 'Downloads/CyclicWarriors'
    
    r = requests.get(game_url, stream=True)
    with open(game_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()

    with zipfile.ZipFile(game_zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder_path)
    
    r = requests.get(map_url, stream=True)
    with open(map_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()
    
    with zipfile.ZipFile(map_zip_path, 'r') as zip_ref:
        zip_ref.extractall("Downloads/MapData/Extracted")
    
    game_folder_name = os.listdir("Downloads/CyclicWarriors")[0]
    folder_name = os.listdir("Downloads/MapData/Extracted")[0]
    
    os.system(f"Xcopy Downloads\MapData\Extracted\{folder_name} Downloads\CyclicWarriors\{game_folder_name}\TripleHorizen\Content\Paks /E /H /C /I /Y")
    
    with open('Data/version.properties', 'w') as f:
        f.write(version)
    
    os.system('echo off\nrmdir /Q/S Downloads\GameData')
    os.system('md Downloads\GameData')
    
    os.system('echo off\nrmdir /Q/S Downloads\MapData')
    os.system('md Downloads\MapData\Extracted')
    
    completed()

def download_local():
    print("Downloading local file game!")
    
    os.system('echo off\nrmdir /Q/S Downloads\CyclicWarriors')
    os.system('md Downloads\CyclicWarriors\CyclicWarriorsCU')
    
    game_folder_name = "CyclicWarriorsCU"
    
    exe_folder_location = input("Enter the full location of the folder containing the .exe for the game.\nIt should look something like C:\\Users\\user01\\GamesFolder\\CyclicWarriors\\CyclicWarriors33\nDirectory: ")
    
    game_version = input("Enter the version of the game you are installing. It should be a number like 36\nVersion Number: ")
    
    print(f'Xcopy "{exe_folder_location}" Downloads\CyclicWarriors\{game_folder_name} /E /H /C /I /Y')
    os.system(f'Xcopy "{exe_folder_location}" Downloads\CyclicWarriors\{game_folder_name} /E /H /C /I /Y')
    
    print("Done transfering!")
        
    with open('Data/version.properties', 'w') as f:
        f.write(game_version)
    
    completed()

def download_patch(url, version):
    print("Downloading patch for the game!")
    
    os.system('echo off\nrmdir /Q/S Downloads\Patch')
    os.system('md Downloads\Patch\Extracted')
    
    patch_zip_path = 'Downloads/Patch/CyclicWarriors.zip'
    
    r = requests.get(url, stream=True)
    with open(patch_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()
    
    with zipfile.ZipFile(patch_zip_path, 'r') as zip_ref:
        zip_ref.extractall("Downloads/Patch/Extracted")
    
    game_folder_name = os.listdir("Downloads/CyclicWarriors")[0]
    folder_name = os.listdir("Downloads/Patch/Extracted")[0]
    
    os.system(f"Xcopy Downloads\Patch\Extracted\{folder_name} Downloads\CyclicWarriors\{game_folder_name}\TripleHorizen\Content\Paks /E /H /C /I /Y")
    
    os.system('echo off\nrmdir /Q/S Downloads\CyclicWarriors')
    os.system('md Downloads\Patch\Extracted')
    
    with open('Data/version.properties', 'w') as f:
        f.write(version)
    
    completed()

def yes_no(comment):
    while True:
        answer = input(comment)

        if type(answer) != str:
            print("Not a y/n")
            continue
        
        answer = answer.lower()
        
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("Not a y/n")
            continue

url = 'http://reallylinux.nz/RaisSoftware/cw/versiondata.json'
r = requests.get(url)

versions = eval_message(fix_json(str(r.content)))

latest_version = list(versions["Game"].keys())[0]
latest_version_url = list(versions["Game"].values())[0]

latest_version_map_url = list(versions["Mapdata"].values())[0]

all_patches_avalable = list(versions["Patch"].keys())
patches = versions["Patch"]

with open("Data/version.properties", "r") as f:
    installed_version = f.read()

if yes_no("Do you want to install a local game file? y/n: "):
    download_local()

if installed_version:
    if installed_version == latest_version:
        completed()
    else:
        for patch in all_patches_avalable:
            if patch == installed_version:
                download_patch(patches[patch], latest_version)
        
        download_game(latest_version_url, latest_version_map_url, latest_version)
else:
    download_game(latest_version_url, latest_version_map_url, latest_version)