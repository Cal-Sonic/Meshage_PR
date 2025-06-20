# Meshage_PR

**Meshage_PR** is a PyQt6 application for parsing Meshtastic device SQLite databases extracted from mobile devices.

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

### **Option 1: Download Standalone Executable**
Check the [releases](https://github.com/Cal-Sonic/Meshage_PR/releases) for the latest standalone executable.

### **Option 2: Build from Source**

#### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

#### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Meshage_PR.git
   cd Meshage_PR
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python meshtastic_db_viewer_qt.py
   ```

#### Building Executable (Optional)

To create a standalone executable:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   pyinstaller MeshagePR.spec
   ```

3. **Find your executable in the `dist/` folder**

---

## Usage

1. **Select a Meshtastic SQLite database** (Use your forensic phone extraction parser of choice to export the db from `/data/data/com.geeksville.mesh/databases/` on Android).
2. **Enter case information** in the popup dialog.
3. **Browse node info, connected nodes, and chat history** using the sidebar.
4. **Export a PDF report** with your chosen sections.

---

## Development

### Project Structure
```
Meshage_PR/
├── meshtastic_db_viewer_qt.py    # Main application
├── requirements.txt               # Python dependencies
├── MeshagePR.spec                 # PyInstaller configuration
├── build.bat                      # Windows build script
├── run.bat                        # Windows run script
└── README.md                      # This file
```

### Dependencies
- **PyQt6**: GUI framework
- **fpdf**: PDF generation
- **sqlite3**: Database parsing (built-in)

