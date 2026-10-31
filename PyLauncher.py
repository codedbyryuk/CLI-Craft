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
import re

print(r"""╔─────────────────────────────────────────────────────────────────────────────────────────────────────────╗
│                                                                                                         │
│                                                                                                         │
│                                                                                                         │
│      ██████╗██╗     ██╗       ██████╗██████╗  █████╗ ███████╗████████╗                                  │
│     ██╔════╝██║     ██║      ██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝                                  │
│     ██║     ██║     ██║█████╗██║     ██████╔╝███████║█████╗     ██║                                     │
│     ██║     ██║     ██║╚════╝██║     ██╔══██╗██╔══██║██╔══╝     ██║                                     │
│     ╚██████╗███████╗██║      ╚██████╗██║  ██║██║  ██║██║        ██║                                     │
│      ╚═════╝╚══════╝╚═╝       ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝                                     │
│                                                                                                         │
│                                 ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗      │
│                                 ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗     │
│                                 ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝     │
│                                 ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗     │
│                                 ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║     │
│                                 ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝     │
│                                                                                                         │
│                                                                                                         │
│                                                                                                         │
╚─────────────────────────────────────────────────────────────────────────────────────────────────────────╝""")


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

def safe_join(base, relative):
   
    base = os.path.abspath(base)
    dest = os.path.abspath(os.path.join(base, relative))
    if os.path.commonpath([base, dest]) != base:
        raise ValueError(f"Unsafe path in modpack: {relative}")
    return dest

def install_modpack(mc_version, minecraft_dir):
    query = input(f'\nSearch for a {mc_version} modpack: ').strip()
    if not query:
        return
    headers = {"User-Agent": "SovernLab/1.0 (contact@sovern.lab)"}
    search_url = "https://api.modrinth.com/v2/search"
    params = {
        "query": query,
        
        "facets": json.dumps([
            [f"versions:{mc_version}"],
            ["project_type:modpack"],
            ["categories:fabric"],
        ]),
        "limit": 10
    }

    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        hits = response.json().get('hits', [])
    except requests.RequestException as e:
        print(f"[!] Modrinth search failed: {e}")
        return

    if not hits:
        print("No compatible modpacks found :(")
        return

    options = [f"{h['title']} by {h['author']}" for h in hits]
    index = show_menu(options, title=f"[Select a Modpack for {mc_version}]")

    if index is None:
        return
    selected_hit = hits[index]
    project_id = selected_hit['project_id']

    try:
        version_url = f"https://api.modrinth.com/v2/project/{project_id}/version"
        v_response = requests.get(version_url, headers=headers, timeout=30, params={
            "game_versions": json.dumps([mc_version]),
            "loaders": json.dumps(["fabric"]),
        })
        v_response.raise_for_status()
        versions = v_response.json()
    except requests.RequestException as e:
        print(f"[!] Could not fetch modpack versions: {e}")
        return

    if not versions:
        print(f"[!] No Fabric build of this modpack for {mc_version}.")
        return

    target_version = versions[0]  
    files = target_version['files']
    pack_file = next((f for f in files if f.get('primary')), files[0])
    download_url = pack_file['url']
    pack_name = pack_file['filename']

    print(f"[*] Downloading {pack_name}")
    r = requests.get(download_url, headers=headers, timeout=120)
    r.raise_for_status()
    with open(pack_name, "wb") as f:
        f.write(r.content)

    try:
        with zipfile.ZipFile(pack_name, 'r') as zip_ref:
            print("[*] Reading index and downloading mods...")
            with zip_ref.open('modrinth.index.json') as f:
                index_data = json.load(f)

            for mod_file in index_data['files']:
               
                if mod_file.get('env', {}).get('client') == 'unsupported':
                    continue
                mod_download_url = mod_file['downloads'][0]
               
                dest_path = safe_join(minecraft_dir, mod_file['path'])
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                if not os.path.exists(dest_path):
                    print(f"  + Downloading {os.path.basename(dest_path)}")
                    try:
                        mod_r = requests.get(mod_download_url, headers=headers, timeout=120)
                        mod_r.raise_for_status()
                    except requests.RequestException as e:
                        print(f"  ! Failed to download {os.path.basename(dest_path)}: {e}")
                        continue
                    with open(dest_path, "wb") as mf:
                        mf.write(mod_r.content)

            for file in zip_ref.namelist():
                if file.endswith('/'): 
                    continue
                for prefix in ('overrides/', 'client-overrides/'):
                    if file.startswith(prefix):
                        relative_path = file[len(prefix):]
                        if relative_path:
                            dest_path = safe_join(minecraft_dir, relative_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            with zip_ref.open(file) as source, open(dest_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                        break
    finally:
        os.remove(pack_name)
    print(f"\n[*] {selected_hit['title']} installed successfully!")

# --- configs ---
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
if choice_index is None:
    sys.exit()
selected_choice = menu_options[choice_index]

if selected_choice == "+ Add New User":
    username = input("Enter new username: ").strip()
    if not username:
        print("Username can't be empty.")
        sys.exit()

    if username not in user_list:
        with open(filename, "a") as file:
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
   
    installed_versions = [
        f for f in os.listdir(installed_path)
        if os.path.isfile(os.path.join(installed_path, f, f + ".json"))
    ]

FABRIC_ID_RE = re.compile(r"^fabric-loader-(.+)-(\d+(?:\.\d+)+)$")

def version_tuple(v):
    return tuple(int(p) for p in v.split("."))


start_opts = ["Play Installed Version", "Install New Version/Modpack"]
start_choice = show_menu(start_opts, title="[Sovern Launcher]")
loader = None

if start_choice == 0:
    if not installed_versions:
        print("Nothing installed yet!")
        sys.exit()
    v_idx = show_menu(installed_versions, title="[Select Installed Version]")
    if v_idx is None:
        sys.exit()
    version_id = installed_versions[v_idx]
    instance_directory = os.path.join(minecraft_directory, "instances", version_id)
    os.makedirs(instance_directory, exist_ok=True)

  
    fabric_match = FABRIC_ID_RE.match(version_id)
    is_fabric = fabric_match is not None
    if fabric_match:
        loader, mc_version = fabric_match.groups()
    else:
        mc_version = version_id

elif start_choice == 1:
    all_versions = minecraft_launcher_lib.utils.get_version_list()
    releases = [v['id'] for v in all_versions if v['type'] == 'release']

    search_term = input("Search version (e.g., 1.8 or 1.21): ").strip()
    filtered = [v for v in releases if search_term in v][:10]

    if not filtered:
        print("No versions found matching that search.")
        sys.exit()

    index = show_menu(filtered, title=f"[Results for '{search_term}']")
    if index is None:
        sys.exit()
    mc_version = filtered[index]
    print(f"Selected: {mc_version}")

    is_fabric = False
    if version_tuple(mc_version) >= (1, 14, 1):
        fabric_opts = ["Vanilla", "Modpack(Fabric)"]
        fabric_choice = show_menu(fabric_opts, title=f"Launch {mc_version} with: ")
        if fabric_choice is None:
            sys.exit()
        is_fabric = fabric_choice == 1

    if is_fabric:
        loader = minecraft_launcher_lib.fabric.get_latest_loader_version()
        version_id = f'fabric-loader-{loader}-{mc_version}'
    else:
        version_id = mc_version

    instance_directory = os.path.join(minecraft_directory, "instances", version_id)
    if not os.path.exists(instance_directory):
        os.makedirs(instance_directory, exist_ok=True)
        print(f'[*] Created unique instance at: {instance_directory}')

    if is_fabric:
        install_modpack(mc_version, instance_directory)
else:
    sys.exit()

def ask_ram():
    while True:
        raw = input("Enter RAM allocation in GB [default 4]: ").strip().lower().rstrip("g").strip()
        if raw == "":
            return 4
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("Please enter a whole number of GB, e.g. 4")

ram_allocate = ask_ram()

if not os.path.exists(minecraft_directory):
    os.makedirs(minecraft_directory)
    print(f"[*] Created folder at: {minecraft_directory}")

# --- callbacks ---
def print_status(status):
    print(f"[*] {status}")

def find_java_versions():
    java_paths = []
    exe_name = "java.exe" if os.name == "nt" else "java"

    
    java_from_path = shutil.which("java")
    if java_from_path:
        java_paths.append(java_from_path)

  
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java_exe = os.path.join(java_home, "bin", exe_name)
        if os.path.exists(java_exe):
            java_paths.append(java_exe)

    
    search_dirs = [
        os.path.join(minecraft_directory, "runtime"), 
        r"C:\Program Files\Java",
        r"C:\Program Files\Eclipse Adoptium",
        r"C:\Program Files\Eclipse Foundation",
        r"C:\Program Files\Microsoft",
        r"C:\Program Files\Amazon Corretto",
        r"C:\Program Files\BellSoft",
        r"C:\Program Files\Zulu",
        r"C:\Program Files\OpenJDK",
        r"C:\Program Files\AdoptOpenJDK",
        "/usr/lib/jvm",
        "/Library/Java/JavaVirtualMachines",
    ]

    for base_dir in search_dirs:
        if not os.path.exists(base_dir):
            continue

        for root, dirs, files in os.walk(base_dir):
          
            if exe_name in files and os.path.basename(root) == "bin":
                java_paths.append(os.path.join(root, exe_name))

   
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
    choice = input("Would you like to (1) Launch now or (2) Re-install/Update? [Default 1]: ").strip()
else:
    print(f"[!] Version {version_id} is NOT installed.")
    choice = "2"
# --- 1. INSTALLATION ---
if choice=="2":
    progress = {"max": 0}

    def set_max(m):
        progress["max"] = m

    def print_progress(current):
        print(f"Progress: {current}/{progress['max']}", end="\r")

    callback = {
        "setStatus": print_status,
        "setMax": set_max,
        "setProgress": print_progress,
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
            minecraft_launcher_lib.fabric.install_fabric(mc_version, minecraft_directory, loader, callback=callback)

    except Exception as e:
        print(f"\n❌ Error during download: {e}")
        sys.exit()

#
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
def get_java_major(version_str):
    """'1.8.0_345' -> 8, '17.0.9' -> 17, '21' -> 21, unknown -> 0"""
    m = re.match(r"(\d+)(?:\.(\d+))?", version_str or "")
    if not m:
        return 0
    major = int(m.group(1))
    if major == 1 and m.group(2):
        major = int(m.group(2))
    return major

java_path = select_java()
java_major = get_java_major(get_java_version(java_path))

if java_major >= 21:
    active_flags = ["-XX:+UseZGC"]
    if java_major < 24:  
        active_flags.append("-XX:+ZGenerational")
    active_flags += ["-XX:+UseLargePages", "-XX:+AlwaysPreTouch"]
else:
    active_flags = optimization_flags

options = {
    "username": username,
    "uuid": user_uuid,
    "token": "",
    "jvmArguments": [f"-Xmx{ram_allocate}G", f"-Xms{ram_allocate}G", *active_flags],
    "gameDirectory": instance_directory,
    "executablePath": java_path
}

# the launch command
command = minecraft_launcher_lib.command.get_minecraft_command(version_id, minecraft_directory, options)
env = os.environ.copy()
if os.name != "nt":
    env["MESA_LOADER_DRIVER_OVERRIDE"] = ""
    env["GALLIUM_DRIVER"] = ""
# --- launch ---
print(f"\n---[*] Launching {version_id} from {minecraft_directory} ---")
try:
    subprocess.Popen(command,env=env)
    print("Success! Launcher closing...")
    os._exit(0) 
except Exception as e:
    print(f"❌ Failed to start: {e}")