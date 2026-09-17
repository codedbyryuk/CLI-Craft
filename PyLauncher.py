import minecraft_launcher_lib
try:
    from simple_term_menu import TerminalMenu
except (ImportError, NotImplementedError):
    TerminalMenu = None
import subprocess
import uuid
import sys
import os
import zipfile
import shutil
import requests
import json
import platform

# Windows-compatible replacement for simple_term_menu.
# Linux/macOS continue using the original TerminalMenu when available.
def show_menu(options, title=""):
    if TerminalMenu is not None and platform.system() != "Windows":
        return TerminalMenu(options, title=title).show()

    print(f"\n{title}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice = input("Select an option (Enter to cancel): ").strip()
            if choice == "":
                return None
            index = int(choice) - 1
            if 0 <= index < len(options):
                return index
        except ValueError:
            pass
        print("Invalid selection. Please enter a number from the list.")

# Modpacks installation

def install_modpack(mc_version,minecraft_dir):
    query = input(f'\nSearch for a {mc_version} modpack: ').strip()
    if not query:
        return
    headers = {"User-Agent": "SovernLab/1.0 (contact@sovern.lab)"}
    search_url = "https://api.modrinth.com/v2/search"
    params = {
        "query":query,
        "facets":f'[["versions:{mc_version}"]]',
        "limit":10
    }

    response = requests.get(search_url,params=params).json()
    hits = response.get('hits',[])

    if not hits:
        print("No compatible modpacks found :(")
        return
    
    options = [f"{h['title']} by {h['author']}" for h in hits]
    index = show_menu(options, title=f"[Select a Modpac for {mc_version}]")

    if index is None:return
    selected_hit = hits[index]
    project_id = selected_hit['project_id']

    verion_url = f"https://api.modrinth.com/v2/project/{project_id}/version"

    v_response = requests.get(verion_url).json()

    target_version = next((v for v in v_response if mc_version in v['game_versions']),v_response[0])
    download_url = target_version['files'][0]['url']
    pack_name = target_version['files'][0]['filename']


    print(f"[*] Downloading {pack_name}")
    r = requests.get(download_url,headers=headers)
    with open(pack_name,"wb") as f:
        f.write(r.content)

    with zipfile.ZipFile(pack_name,'r') as zip_ref:

        print("[*] Reading index and downloading mods...")
        with zip_ref.open('modrinth.index.json') as f:
            index_data = json.load(f)
            for mod_file in index_data['files']:
                mod_download_url = mod_file['downloads'][0]
                # Path usually looks like 'mods/example-mod.jar'
                dest_path = os.path.join(minecraft_dir, mod_file['path'])
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                if not os.path.exists(dest_path):
                    print(f"  + Downloading {os.path.basename(dest_path)}")
                    mod_r = requests.get(mod_download_url, headers=headers)
                    with open(dest_path, "wb") as mf:
                        mf.write(mod_r.content)

        for file in zip_ref.namelist():
            if file.startswith('overrides/'):
                relative_path = file.replace('overrides/','', 1)
                if relative_path:
                    dest_path = os.path.join(minecraft_dir,relative_path)
                    os.makedirs(os.path.dirname(dest_path),exist_ok=True)
                    with zip_ref.open(file) as source, open(dest_path,"wb") as target:
                        shutil.copyfileobj(source,target)
    os.remove(pack_name)
    print(f"\n[*] {selected_hit['title']} installed successfully!")

# --- CONFIGURATION ---
minecraft_directory = os.path.join(os.getcwd(), "minecraft_data")

# username = input("Enter a username: ").strip()
filename = "usernames.txt"
if os.path.exists(filename):
    with open(filename, "r") as file:
        # current_saved_name = file.read().strip()
        user_list = [line.strip() for line in file.readlines() if line.strip()]
else:
    # current_saved_name = None
    user_list = []

menu_options = user_list + ["+ Add New User"]

choice_index = show_menu(menu_options, title="[Select User]")
selected_choice = menu_options[choice_index]

if selected_choice == "+ Add New User":
    username = input("Enter new username: ").strip()

    if username and username not in user_list:
        with open(filename,"a") as file:
            file.write(username + "\n")
        print(f"[*] User {username} saved!")
else:
    username = selected_choice
print(f"[*] Logged in as: {username}")
print("Loading versions...")

#------- Versions handling ------

installed_path = os.path.join(minecraft_directory, "versions")
installed_versions = []

if os.path.exists(installed_path):
    # Get all folders that actually contain a .json file
    installed_versions = [f for f in os.listdir(installed_path) if os.path.isdir(os.path.join(installed_path, f))]

# --- 2. UPDATE MAIN MENU ---
start_opts = ["Play Installed Version", "Install New Version/Modpack"]
start_choice = show_menu(start_opts, title="[Sovern Launcher]")

if start_choice == 0:
    if not installed_versions:
        print("Nothing installed yet!")
        sys.exit()
    v_idx = show_menu(installed_versions, title="[Select Installed Version]")
    version_id = installed_versions[v_idx]
    instance_directory = os.path.join(minecraft_directory, "instances", version_id)
    is_fabric = "fabric" in version_id.lower()
    # Skip the download section and go straight to RAM/Launch
    
elif start_choice == 1:

    all_versions = minecraft_launcher_lib.utils.get_version_list()
    releases = [v['id'] for v in all_versions if v['type'] == 'release']

    # 2. Add a 'Search' step first to narrow it down
    search_term = input("Search version (e.g., 1.8 or 1.21): ").strip()

    # 3. Filter the list to only show the top 10 matches for that search
    filtered = [v for v in releases if search_term in v][:10]

    if not filtered:
        print("No versions found matching that search.")
    else:
        # 4. Show the menu with ONLY those 10 items
        index = show_menu(filtered, title=f"[Results for '{search_term}']")
        if index is not None:
            mc_version = filtered[index]
            print(f"Selected: {mc_version}")
            instance_directory = os.path.join(minecraft_directory, "instances", mc_version)

            if not os.path.exists(instance_directory):
                os.makedirs(instance_directory, exist_ok=True)
                print(f'[*] Created unique instance at: {instance_directory}')



    # if os.path.exists("minecraft_data/versions"):
    #     print("Available versions:")
    #     version_list = os.listdir("minecraft_data/versions")
    #     for item in version_list:
    #         print(item)
    # else:
    #     print("Nothings there to play :(")

    # mc_version = input("Enter the version you want to play: ").strip()

    def version_tuple(v):
        return tuple(map(int,(v.split("."))))

    is_fabric=False
    

    if version_tuple(mc_version) >= version_tuple('1.14.1'):
        # is_fabric = input("Do you want to play with Fabric? (y/n): ").lower() == 'y'

        fabric_opts = ["Vanilla", "Modpack(Fabric)"]
        is_fabric = show_menu(fabric_opts, title=f"Launch {mc_version} with: ") == 1

        if is_fabric:
            install_modpack(mc_version,instance_directory)
            loader = minecraft_launcher_lib.fabric.get_latest_loader_version()
            version_id = f'fabric-loader-{loader}-{mc_version}'
            new_instance_path = os.path.join(minecraft_directory, "instances", version_id)
            if not os.path.exists(new_instance_path):
                os.rename(instance_directory, new_instance_path)
            instance_directory = new_instance_path
        else:
            version_id=mc_version
    else:
        version_id=mc_version




ram_allocate=input("Enter ram allocation size: ").strip()
# Ensure the folder exists in current project directory
if not os.path.exists(minecraft_directory):
    os.makedirs(minecraft_directory)
    print(f"[*] Created folder at: {minecraft_directory}")

# --- CALLBACKS ---
def print_status(status):
    print(f"[*] {status}")

def find_java_versions():
    java_paths = []

    # 1. Java from PATH
    java_from_path = shutil.which("java")
    if java_from_path:
        java_paths.append(java_from_path)

    # 2. JAVA_HOME
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java_exe = os.path.join(java_home, "bin", "java.exe")
        if os.path.exists(java_exe):
            java_paths.append(java_exe)

    # 3. Common Windows Java installation directories
    search_dirs = [
        r"C:\Program Files\Java",
        r"C:\Program Files\Eclipse Adoptium",
        r"C:\Program Files\Eclipse Foundation",
        r"C:\Program Files\Microsoft",
        r"C:\Program Files\Amazon Corretto",
        r"C:\Program Files\BellSoft",
        r"C:\Program Files\Zulu",
        r"C:\Program Files\OpenJDK",
        r"C:\Program Files\AdoptOpenJDK",
    ]

    for base_dir in search_dirs:
        if not os.path.exists(base_dir):
            continue

        for root, dirs, files in os.walk(base_dir):
            if "java.exe" in files:
                java_exe = os.path.join(root, "java.exe")
                java_paths.append(java_exe)

    # Remove duplicates
    java_paths = list(dict.fromkeys(
        os.path.abspath(path) for path in java_paths
        if os.path.exists(path)
    ))

    return java_paths


def get_java_version(java_path):
    try:
        result = subprocess.run(
            [java_path, "-version"],
            capture_output=True,
            text=True
        )

        # Java prints its version to stderr
        output = result.stderr + result.stdout

        for line in output.splitlines():
            if 'version "' in line:
                version = line.split('version "')[1].split('"')[0]
                return version

        return "Unknown"

    except Exception:
        return "Unknown"


def select_java():
    java_paths = find_java_versions()

    if not java_paths:
        print("\n❌ No Java installations were found.")
        sys.exit()

    java_options = []

    for path in java_paths:
        version = get_java_version(path)
        java_options.append(
            f"Java {version}  —  {path}"
        )

    selected_index = show_menu(
        java_options,
        title="[Select Java Version]"
    )

    if selected_index is None:
        print("Java selection cancelled.")
        sys.exit()

    selected_java = java_paths[selected_index]
    selected_version = get_java_version(selected_java)

    print(f"\n[*] Selected Java {selected_version}")
    print(f"[*] Java path: {selected_java}")

    return selected_java

version_folder = os.path.join(minecraft_directory, "versions", version_id)

print("--- Custom Launcher ---")

if os.path.exists(version_folder):
    print(f"[!] Version {version_id} is already installed.")
    choice = input("Would you like to (1) Launch now or (2) Re-install/Update? [Default 1]: ")
else:
    print(f"[!] Version {version_id} is NOT installed.")
    choice = "2"
# --- 1. INSTALLATION ---
if choice=="2":
    def print_progress(current, *args):
        # prints a progress line
        if args:
            total = args[0]
            print(f"Progress: {current}/{total}", end="\r")
        else:
            print(f"Progress: {current}", end="\r")

    callback = {
        "setStatus": print_status,
        "s"
        "setProgress": print_progress
    }
    print(f"--- Downloading Minecraft {version_id} to Local Folder ---")
    try:
        minecraft_launcher_lib.install.install_minecraft_version(
            version=mc_version, 
            minecraft_directory=minecraft_directory, 
            callback=callback
        )
        if is_fabric:
            print(f"[*] Installing Fabric loader {loader}...")
            minecraft_launcher_lib.fabric.install_fabric(mc_version,minecraft_directory,loader)

    except Exception as e:
        print(f"\n❌ Error during download: {e}")
        sys.exit()

# --- 2. COMMAND GENERATION ---
user_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}"))
optimization_flags = [
    "-XX:+UseG1GC", "-XX:+ParallelRefProcEnabled", "-XX:MaxGCPauseMillis=200", 
    "-XX:+UnlockExperimentalVMOptions", "-XX:+DisableExplicitGC", "-XX:+AlwaysPreTouch", 
    "-XX:G1NewSizePercent=30", "-XX:G1MaxNewSizePercent=40", "-XX:G1HeapRegionSize=8M", 
    "-XX:G1ReservePercent=20", "-XX:G1HeapWastePercent=5", "-XX:G1MixedGCCountTarget=4", 
    "-XX:InitiatingHeapOccupancyPercent=15", "-XX:G1MixedGCLiveThresholdPercent=90", 
    "-XX:G1RSetUpdatingPauseTimePercent=5", "-XX:SurvivorRatio=32", 
    "-XX:+PerfDisableSharedMem", "-XX:MaxTenuringThreshold=1","-Dlog4j2.formatMsgNoLookups=true"
]
zgc_flags = [
    "-XX:+UseZGC", 
    "-XX:+ZGenerational", 
    "-XX:+UseLargePages", 
    "-XX:+AlwaysPreTouch"
]

if is_fabric or version_id >= '1.17.1':
    active_flags = zgc_flags
else:
    active_flags = optimization_flags

java_path = select_java()

options = {
    "username": username,
    "uuid": user_uuid,
    "token": "",
    "jvmArguments": [f"-Xmx{ram_allocate}G", f"-Xms{ram_allocate}G"],
    "gameDirectory": instance_directory,
    "executablePath": java_path
}

# the launch command
command = minecraft_launcher_lib.command.get_minecraft_command(version_id, minecraft_directory, options)
env = os.environ.copy()
if os.name != "nt":
    env["MESA_LOADER_DRIVER_OVERRIDE"] = ""
    env["GALLIUM_DRIVER"] = ""
# --- 3. LAUNCH ---
print(f"\n---[*] Launching {version_id} from {minecraft_directory} ---")
try:
    subprocess.Popen(command,env=env)
    print("Success! Launcher closing...")
    os._exit(0) 
except Exception as e:
    print(f"❌ Failed to start: {e}")