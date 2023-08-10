import sys, os, subprocess, time

print("\nUpdating and copying the launcher files after download. [:")

time.sleep(0.02)

def copydata(filename):
    with open(f"CyclicWarriorsLauncherGit\\{filename}", 'rb') as f:
        new_data = f.read()

    with open(filename, 'wb') as f:
        f.truncate(0)
        f.write(new_data)

folder_path = "CyclicWarriorsLauncherGit"
exclude_file = "update_launcher.exe"

for item in os.listdir(folder_path):
    item_path = os.path.join(folder_path, item)
    if os.path.isfile(item_path) and item != exclude_file:
        print(f"Copying: {item}")
        copydata(item)

copydata("Data\\LauncherVersion.properties")

os.system('rmdir /Q/S CyclicWarriorsLauncherGit 2> {}'.format(os.devnull))

input('Launcher successfully updated! Press enter to relaunch...')

print()

subprocess.Popen("Cyclic Warriors Launcher.exe")
sys.exit()