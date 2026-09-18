# CLI-Craft  Launcher

A lightweight custom Minecraft launcher for Windows that lets you manage Minecraft versions, offline usernames, Java installations, Fabric modpacks, RAM allocation, and separate Minecraft instances — all from a simple terminal interface.

---

## Features

* - **Launch Minecraft from a custom launcher**
* - **Install Minecraft versions**
* - **Re-install or update already installed versions**
* - **Save multiple usernames**
* - **Separate Minecraft instances for different versions**
* - **Fabric support**
* - **Modrinth modpack search and installation**
* - **Automatic Java installation detection**
* - **Choose which Java installation to use**
* - **Custom RAM allocation**
* - **Minecraft JVM optimization flags**
* - **Windows-compatible menus**
* - **Keeps Minecraft data separate from the launcher executable**
* - **Downloads Minecraft files directly using Mojang/Minecraft launcher APIs through `minecraft_launcher_lib`**
* - **Automatically creates required folders**
* - **Offline username support**

---

# Installation

## 1. Create a folder

First, create a **new empty folder** anywhere you want.

For example:

```text
CLI-Craft Launcher/
```

Put the launcher executable inside this folder:

```text
CLI-Craft Launcher/
└── CLI-Craft Launcher.exe
```

### Important

**Do not move the `.exe` around after installing/using the launcher unless you also move the `minecraft_data` folder with it.**

The launcher stores Minecraft data in a folder called:

```text
minecraft_data
```

The folder is created **next to the `.exe`** when the launcher is run.

After using the launcher, your folder will look something like:

```text
CLI-Craft Launcher/
├── CLI-Craft Launcher.exe
└── minecraft_data/
    ├── versions/
    ├── instances/
    ├── assets/
    ├── libraries/
    └── ...
```

Keeping the executable and `minecraft_data` together allows the launcher to keep all of its Minecraft files in one location.

---

# First Launch

Double-click:

```text
CLI-Craft Launcher.exe
```

The launcher will open a terminal window.

---

## Step 1 — Select or create a username

The launcher first shows your saved usernames.

For example:

```text
[Select User]

  1. Steve
  2. Alex
  3. + Add New User
```

Select an existing username or choose:

```text
+ Add New User
```

If you create a new username, it will be saved in:

```text
usernames.txt
```

The username will be available the next time you launch CLI-Craft  Launcher.

### Example

```text
Enter new username: Steve

[*] User Steve saved!
[*] Logged in as: Steve
```

The launcher uses an **offline UUID** generated from the username.

---

# Step 2 — Choose what you want to do

After selecting a username, you will see:

```text
[CLI-Craft  Launcher]

  1. Play Installed Version
  2. Install New Version/Modpack
```

---

# Playing an Installed Version

Choose:

```text
1. Play Installed Version
```

The launcher will display the Minecraft versions already installed in `minecraft_data/versions`.

Example:

```text
[Select Installed Version]

  1. 1.20.1
  2. 1.21.1
  3. fabric-loader-0.18.1-1.21.1
```

Select the version you want to launch.

The launcher will then use that version's instance.

---

# Installing a New Minecraft Version

Choose:

```text
2. Install New Version/Modpack
```

The launcher will ask you to search for a Minecraft version.

For example:

```text
Search version (e.g., 1.8 or 1.21): 1.21
```

It will search through Minecraft's available release versions and display matching results.

Example:

```text
[Results for '1.21']

  1. 1.21.1
  2. 1.21
  3. 1.21.3
  4. 1.21.4
```

Select the version you want.

The launcher then creates a separate instance for that Minecraft version.

---

# Vanilla or Fabric

For supported Minecraft versions, the launcher gives you a choice:

```text
Launch 1.21.1 with:

  1. Vanilla
  2. Modpack(Fabric)
```

### Vanilla

Selecting **Vanilla** installs and launches normal Minecraft without Fabric.

### Fabric

Selecting **Modpack(Fabric)** enables Fabric support.

The launcher will:

1. Ask you to search for a Modrinth modpack.
2. Search Modrinth for modpacks compatible with your selected Minecraft version.
3. Display matching modpacks.
4. Download the selected modpack.
5. Read its `modrinth.index.json`.
6. Download the required mods.
7. Extract the modpack's `overrides` files.
8. Install the required Fabric loader.
9. Create a separate Fabric instance.

---

# Installing a Modrinth Modpack

When Fabric mode is selected, you'll see:

```text
Search for a 1.21.1 modpack:
```

Enter the modpack you want.

For example:

```text
Search for a 1.21.1 modpack: Sodium
```

The launcher searches Modrinth and displays compatible results.

Select one from the menu.

The launcher will then download the modpack and install its files into the Minecraft instance.

You don't need to manually download each mod.

---

# RAM Allocation

Before launching Minecraft, the launcher asks:

```text
Enter ram allocation size:
```

Enter the amount of RAM in **GB**.

For example:

```text
Enter ram allocation size: 4
```

Minecraft will then be launched with:

```text
-Xmx4G
-Xms4G
```

This means Minecraft starts with 4 GB of allocated memory and can use up to 4 GB.

### Example recommendations

For a PC with:

* **8 GB RAM:** try `3` or `4`
* **16 GB RAM:** try `4`–`6`
* **32 GB RAM:** try `6`–`8`

Don't allocate all of your system RAM to Minecraft. Windows and other applications also need memory.

---

# Java Selection

CLI-Craft  Launcher automatically searches your system for Java installations.

It checks:

* Java available through `PATH`
* `JAVA_HOME`
* Common Java installation directories

Including locations such as:

```text
C:\Program Files\Java
C:\Program Files\Eclipse Adoptium
C:\Program Files\Eclipse Foundation
C:\Program Files\Microsoft
C:\Program Files\Amazon Corretto
C:\Program Files\BellSoft
C:\Program Files\Zulu
C:\Program Files\OpenJDK
C:\Program Files\AdoptOpenJDK
```

The launcher then displays the Java installations it finds.

Example:

```text
[Select Java Version]

  1. Java 17.0.12 — C:\Program Files\Java\jdk-17\bin\java.exe
  2. Java 21.0.4 — C:\Program Files\Java\jdk-21\bin\java.exe
```

Select the Java installation you want Minecraft to use.

---

# Existing Versions

If you try to install a Minecraft version that is already installed, the launcher will detect it.

You'll see:

```text
[!] Version 1.21.1 is already installed.
Would you like to (1) Launch now or (2) Re-install/Update? [Default 1]:
```

Enter:

```text
1
```

to launch the existing installation.

Or:

```text
2
```

to reinstall/update it.

---

# Minecraft Data Location

All Minecraft files are stored inside:

```text
minecraft_data
```

which is located in the same folder as the launcher.

Example:

```text
CLI-Craft Launcher/
│
├── CLI-Craft Launcher.exe
├── usernames.txt
│
└── minecraft_data/
    ├── versions/
    ├── instances/
    ├── assets/
    ├── libraries/
    └── ...
```

This means the launcher does **not** depend on the normal `.minecraft` directory for its main game data.

This also makes the launcher portable: you can keep the launcher and its Minecraft data together in one folder.

---

# Important: Do Not Run the EXE From Random Locations

The launcher uses its **current working directory** when creating:

```text
minecraft_data
```

For the intended setup, create one dedicated folder and keep the launcher there.

For example:

```text
D:\Games\CLI-Craft Launcher\
```

Put:

```text
CLI-Craft Launcher.exe
```

inside it and launch the EXE from there.

After Minecraft is installed:

```text
D:\Games\CLI-Craft Launcher\
├── CLI-Craft Launcher.exe
├── usernames.txt
└── minecraft_data\
```

Keep these files/folders together.

---

# Project Structure

A typical installation will eventually look like:

```text
CLI-Craft Launcher/
│
├── CLI-Craft Launcher.exe
│
├── usernames.txt
│
└── minecraft_data/
    │
    ├── assets/
    │
    ├── libraries/
    │
    ├── versions/
    │   ├── 1.20.1/
    │   ├── 1.21.1/
    │   └── ...
    │
    └── instances/
        ├── 1.20.1/
        ├── 1.21.1/
        └── fabric-loader-.../
```

---

# Requirements

The compiled Windows executable is intended to be run on Windows.

You should also have a compatible Java installation available. The launcher detects installed Java versions and lets you select one.

An internet connection is required when:

* Installing a Minecraft version
* Installing Fabric
* Searching for Modrinth modpacks
* Downloading mods
* Downloading Minecraft libraries/assets

An internet connection is not necessarily required for the launcher itself after the required Minecraft files have already been installed, although Minecraft may still require network access for multiplayer and other online features.

---

# Controls

The launcher uses numbered menus on Windows.

Example:

```text
[Select User]

  1. Steve
  2. Alex
  3. + Add New User

Select an option:
```

Enter the number corresponding to your choice.

Press **Enter without entering a number** to cancel a menu where cancellation is supported.

---

# Troubleshooting

## "No Java installations were found."

Install Java and make sure it is available through `PATH` or installed in one of the common Java directories searched by the launcher.

Then restart CLI-Craft  Launcher.

---

## Minecraft does not start

Check:

* You selected a valid Java installation.
* You allocated a reasonable amount of RAM.
* The selected Minecraft version is installed correctly.
* Your Java version is compatible with the Minecraft version.
* The Minecraft files finished downloading successfully.

---

## The launcher creates `minecraft_data` somewhere unexpected

Make sure you are launching the EXE from the dedicated launcher folder.

The launcher stores its data relative to its current working directory.

---

## A modpack cannot be found

Make sure:

* The modpack exists on Modrinth.
* The modpack supports the Minecraft version you selected.
* You have an internet connection.

The launcher only searches for modpacks compatible with the selected Minecraft version.

---

# Notes

CLI-Craft  Launcher is a custom launcher project built around:

* `minecraft_launcher_lib`
* Modrinth's API
* Python
* Fabric
* Windows-compatible terminal menus

It is designed to provide a simple way to keep multiple Minecraft versions and instances separated without relying on the standard Minecraft launcher interface.

---

## Quick Start

If you just want to get into Minecraft as quickly as possible:

```text
1. Create a new folder.
2. Put CLI-Craft Launcher.exe inside it.
3. Run CLI-Craft Launcher.exe.
4. Select an existing username or create one.
5. Select "Install New Version/Modpack".
6. Search for your Minecraft version.
7. Select the version.
8. Choose Vanilla or Modpack(Fabric).
9. If using Fabric, select a Modrinth modpack.
10. Enter your RAM allocation in GB.
11. Select your Java installation.
12. Minecraft launches.
```

**Keep `CLI-Craft Launcher.exe`, `usernames.txt`, and `minecraft_data` together in the same launcher folder.**
