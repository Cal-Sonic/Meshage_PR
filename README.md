# Meshage_PR

**Meshage_PR** is a modern, forensics-inspired PyQt6 application for visually exploring and analyzing Meshtastic device SQLite databases extracted from mobile devices. It provides a sleek, user-friendly interface for digital investigators, hobbyists, and anyone interested in Meshtastic mesh network data.

---

## Features

- **Case Management:**  
  Enter and store case metadata (Case ID, Case Name, Caseworker, Agency, Evidence Number, Description) for each analysis session.

- **User Node Info:**  
  View detailed information about the user's own node, including hardware, firmware, and GPS status.

- **Connected Nodes:**  
  List all nodes seen by the device, including signal metrics, user info, and connection context.

- **Chats:**  
  Browse and visualize chat histories, with clear sender/receiver identification and modern chat bubble styling.

- **PDF Report Export:**  
  Export a professional, customizable PDF report. Select which sections to include, and automatically name the report with the evidence number.

---

## Supported Devices & Database Location

- **This tool has only been tested with databases extracted from the Android version of Meshtastic.**
- The Meshtastic database can be found at:
  ```
  /data/data/com.geeksville.mesh/databases/
  ```
  (You will need to use your forensic phone extraction tool of choice to access this path and export the database file.)

---

## Installation

### 1. **Clone the Repository**
```bash
git clone https://github.com/Cal-Sonic/Meshage_PR.git
cd Meshage_PR
```
#### Or

### 2. **Cheack the releases for stand along executable**

## Usage

1. **Select a Meshtastic SQLite database** (Use your forensic phone extraction parser of choice to export the db from `/data/data/com.geeksville.mesh/databases/` on Android).
2. **Enter case information** in the popup dialog.
3. **Browse node info, connected nodes, and chat history** using the sidebar.
4. **Export a PDF report** with your chosen sections.

