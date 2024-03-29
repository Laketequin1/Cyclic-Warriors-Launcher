import ast
import os
import subprocess
import sys
import zipfile
import time

os.system("echo off")
os.system("cls")

def get_yes_no_input(comment):
    """
    Prompt the user with a yes/no question and return their response.

    Args:
        comment (str): The prompt to display.

    Returns:
        bool: True if the user answered yes, False if they answered no.
    """
    while True:
        answer = input(comment)

        if not isinstance(answer, str):
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

def is_git_installed():
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception as e:
        return False

def install_git():
    if not is_git_installed():
        if not get_yes_no_input("Git can not be found on your computer and the launcher can not auto-update. The launcher will still continue without installing Git.\nDo you wish to install git? y/n: "):
            print("Continuing without Git :,(")
            return
        print("Downloading git...")
        time.sleep(1)
        git_installer_url = "https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.3/Git-2.41.0.3-64-bit.exe"
        try:
            # Download Git installer
            download_command = f"Invoke-WebRequest -Uri '{git_installer_url}' -OutFile 'GitInstaller.exe'"
            subprocess.run(["powershell", "-Command", download_command], shell=True, check=True)

            # Install Git silently
            install_command = "Start-Process -Wait -FilePath 'GitInstaller.exe' -ArgumentList '/SILENT /COMPONENTS=\"icons,ext\"'"
            subprocess.run(["powershell", "-Command", install_command], shell=True, check=True)

            # Clean up the installer
            cleanup_command = "Remove-Item 'GitInstaller.exe'"
            subprocess.run(["powershell", "-Command", cleanup_command], shell=True, check=True)

            if is_git_installed():
                print("Git installation completed successfully.")
            else:
                print("Git not installed, something went wrong. Make sure Git is in your path.")
                input("Press enter to exit...")
                sys.exit()

        except subprocess.CalledProcessError as e:
            print("Error during Git installation:", e)
            input("Press enter to exit...")
            sys.exit()

install_git()

import psutil
import requests
from clint.textui import progress

if is_git_installed():
    from git import Repo

def evaluate_message(message):
    """
    Evaluates the given message as a Python literal and returns the result.

    Args:
        message (str): The message to evaluate.

    Returns:
        object: The evaluated result or None if the message is empty.
    """
    if message:
        return ast.literal_eval(message)
    return None


def fix_json(message):
    """
    Fixes the JSON format of the given message by removing unwanted characters.

    Args:
        message (str): The message to fix.

    Returns:
        str: The fixed JSON message.
    """
    message = message.replace("\\n", "").replace("\\r", "").replace(" ", "")
    return message[2:len(message) - 1]


def execute(executable_path):
    """
    Starts the game by executing the given executable.

    Args:
        executable_path (str): The path to the game executable.
    """
    subprocess.Popen(executable_path)


def set_GameVersion_input(latest_game_version, retry=False):
    if not retry:
        user_input = input(
"""The game version is not set for this new launcher installation, which is expected. You only need to do this process once.
If you have the game data already installed, please move it to the correct folder, and enter the version number (integer).
If you don't have Cyclic Warriors downloaded yet, leave the input blank.
Input: """
        )
    else:
        user_input = input("Input: ")

    if user_input.isdigit():
        user_input = int(user_input)
        if 0 <= user_input <= latest_game_version:
            return user_input
        else:
            return f"Not a valid game version! The range should be between 0 and {latest_game_version} (inclusive)."
    elif user_input == "":
        return 0
    return f"Not a valid int game version! Either enter a blank input '', or your already downloaded game version if you have it."


def manually_set_GameVersion(latest_game_version):
    """
    Get the user to set the GameVersion.properties file to the correct int.
    """
    while True:
        version = set_GameVersion_input(latest_game_version)
        if type(version) == int:
            with open('Data/GameVersion.properties', 'w') as f:
                f.write(str(version))
            break
        else:
            print(version)
    
    print("Game version data set successfully! [Good job :D]")
    return version


def download_binaries():
    """
    Downloads the binaries for the game patch and applies it.
    """
    print("Downloading binaries.")
    
    os.system('md Downloads\\Binaries\\Extracted')

    patch_zip_path = 'Downloads/Binaries/Binaries.zip'
    url = "http://reallylinux.nz/RaisSoftware/cw/Binaries.zip"

    r = requests.get(url, stream=True)
    with open(patch_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

    print("Binaried downloaded.")

    with zipfile.ZipFile(patch_zip_path, 'r') as zip_ref:
        zip_ref.extractall("Downloads/Binaries/Extracted")

    game_folder_name = os.listdir("Downloads/CyclicWarriors")[0]
    folder_name = os.listdir("Downloads/Binaries/Extracted")[0]

    os.system(f"Xcopy Downloads\\Binaries\\Extracted\\{folder_name} Downloads\\CyclicWarriors\\{game_folder_name}\\TripleHorizen\\Binaries\\Win64 /E /H /C /I /Y")

    os.system('rmdir /Q/S Downloads\\Binaries')

    print("Binaried applied.")


def completed():
    """
    Handles the completion of the download and game launch process.
    """
    input("Completed! Remember to start steam. Press enter to launch the game...")

    process_names = [p.name() for p in psutil.process_iter()]

    if "steam.exe" not in process_names:
        print("Steam not launched.")
        completed()

    print("Launching the game!")

    game_folder_path = os.listdir("Downloads/CyclicWarriors")[0]

    for file in os.listdir(f"Downloads/CyclicWarriors/{game_folder_path}"):
        if file.endswith(".exe"):
            execute(os.path.join(f"Downloads\\CyclicWarriors\\{game_folder_path}", file))
            break
    else:
        print("Game EXE file not found. Please check your game folder, or reinstall the game.")

    sys.exit()


def copydata(filename):
    with open(f"CyclicWarriorsLauncherGit\\{filename}", 'rb') as f:
        new_data = f.read()

    with open(filename, 'wb') as f:
        f.truncate(0)
        f.write(new_data)


def update_launcher():
    print("Updating Launcher... please wait, this may take a couple minutes.")

    os.system('echo off\nrmdir /Q/S CyclicWarriorsLauncherGit 2>nul')

    # Clone or open the repository
    repo_path = 'CyclicWarriorsLauncherGit'
    if os.path.exists(repo_path):
        repo = Repo(repo_path)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from('https://github.com/Laketequin1/Cyclic-Warriors-Launcher.git', repo_path)

    try:
        copydata("update_launcher.exe")
    except Exception as e:
        print(f"Warning (You can ignore this): {e}")

    subprocess.Popen("update_launcher.exe")
    sys.exit()


def download_game(game_url, map_url, version):
    """
    Downloads the full game and extracts it.

    Args:
        game_url (str): The URL to download the game.
        map_url (str): The URL to download the map data.
        version (str): The version of the game to download.
    """
    print("Downloading the full game!")
    print("The game is downloaded in two parts, the download bar will be repeated.")

    os.system('md Downloads\\CyclicWarriors')
    os.system('rmdir /Q/S Downloads\\GameData')
    os.system('md Downloads\\GameData')
    os.system('rmdir /Q/S Downloads\\MapData')
    os.system('md Downloads\\MapData\\Extracted')

    game_zip_path = 'Downloads/GameData/CyclicWarriors.zip'
    map_zip_path = 'Downloads/MapData/CyclicWarriors.zip'
    folder_path = 'Downloads/CyclicWarriors'

    r = requests.get(game_url, stream=True)
    with open(game_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

    with zipfile.ZipFile(game_zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder_path)

    r = requests.get(map_url, stream=True)
    with open(map_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

    with zipfile.ZipFile(map_zip_path, 'r') as zip_ref:
        zip_ref.extractall("Downloads/MapData/Extracted")

    game_folder_name = os.listdir("Downloads/CyclicWarriors")[0]
    folder_name = os.listdir("Downloads/MapData/Extracted")[0]

    os.system(f"Xcopy Downloads\\MapData\\Extracted\\{folder_name} Downloads\\CyclicWarriors\\{game_folder_name}\\TripleHorizen\\Content\\Paks /E /H /C /I /Y")

    with open('Data/GameVersion.properties', 'w') as f:
        f.write(version)

    os.system('rmdir /Q/S Downloads\\GameData')
    os.system('md Downloads\\GameData')
    os.system('rmdir /Q/S Downloads\\MapData')

    completed()


def download_patch(url, version, binaries_needed):
    """
    Downloads a game patch and applies it.

    Args:
        url (str): The URL to download the patch.
        version (str): The version of the patch to download.
    """
    print("Downloading a patch for the game!")

    os.system('rmdir /Q/S Downloads\\Patch')
    os.system('md Downloads\\Patch\\Extracted')

    patch_zip_path = 'Downloads/Patch/CyclicWarriors.zip'

    r = requests.get(url, stream=True)
    with open(patch_zip_path, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

    print("Data downloaded.")

    with zipfile.ZipFile(patch_zip_path, 'r') as zip_ref:
        zip_ref.extractall("Downloads/Patch/Extracted")

    game_folder_name = os.listdir("Downloads/CyclicWarriors")[0]
    folder_name = os.listdir("Downloads/Patch/Extracted")[0]

    os.system(f"Xcopy Downloads\\Patch\\Extracted\\{folder_name} Downloads\\CyclicWarriors\\{game_folder_name}\\TripleHorizen\\Content\\Paks /E /H /C /I /Y")

    os.system('md Downloads\\Patch\\Extracted')

    print("Data applied.")

    if binaries_needed:
        download_binaries()

    with open('Data/GameVersion.properties', 'w') as f:
        f.write(version)

    completed()


def main():
    url = 'http://reallylinux.nz/RaisSoftware/cw/versiondata.json'

    response = requests.get(url)
    data = evaluate_message(fix_json(str(response.content)))

    latest_game_version = list(data["Game"].keys())[0]
    
    latest_game_url = list(data["Game"].values())[0]
    latest_map_url = list(data["Mapdata"].values())[0]
    all_patches_available = list(data["Patch"].keys())
    patches = data["Patch"]

    latest_launcher_version = int(data["Launcher"])
    latest_binaries_version = int(data["Binaries"])

    with open("Data/LauncherVersion.properties", "r") as f:
        installed_launcher_version = int(f.read())

    if installed_launcher_version < latest_launcher_version and is_git_installed():
        update_launcher()

    with open("Data/GameVersion.properties", "r") as f:
        installed_game_version = f.read()

    if installed_game_version == "":
        installed_game_version = str(manually_set_GameVersion(int(latest_game_version)))

    binaries_required = int(installed_game_version) < latest_binaries_version

    if installed_game_version:
        if installed_game_version == latest_game_version:
            completed()
        else:
            for patch in all_patches_available:
                if patch == installed_game_version:
                    print(patches[patch], latest_game_version)
                    download_patch(patches[patch], latest_game_version, binaries_required)

            download_game(latest_game_url, latest_map_url, latest_game_version)
    else:
        download_game(latest_game_url, latest_map_url, latest_game_version)


if __name__ == "__main__":
    main()