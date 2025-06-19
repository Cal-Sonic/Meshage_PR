import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTreeWidget, QTreeWidgetItem, QFileDialog,
    QStackedWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt
import os
import sqlite3
import re

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet('''
            QPushButton {
                color: #fff;
                background: transparent;
                border: none;
                text-align: left;
                padding-left: 24px;
                font-size: 16px;
                font-family: "Segoe UI", "Arial", sans-serif;
            }
            QPushButton:hover, QPushButton:checked {
                background: #223366;
                border-radius: 8px;
            }
        ''')

class MeshagePR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meshage_PR")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet('''
            QMainWindow {
                background: #181f2f;
            }
        ''')

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setStyleSheet('''
            QWidget {
                background: #142047;
                border-top-right-radius: 16px;
                border-bottom-right-radius: 16px;
            }
        ''')
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 32, 0, 32)
        sidebar_layout.setSpacing(12)
        self.logo_label = QLabel("Meshage_PR")
        self.logo_label.setStyleSheet('color: #fff; font-size: 22px; font-weight: bold; padding-left: 24px;')
        sidebar_layout.addWidget(self.logo_label)
        sidebar_layout.addSpacing(24)
        self.btn_database = SidebarButton("Database")
        self.btn_nodes = SidebarButton("Connected Nodes")
        self.btn_chats = SidebarButton("Chats")
        sidebar_layout.addWidget(self.btn_database)
        sidebar_layout.addWidget(self.btn_nodes)
        sidebar_layout.addWidget(self.btn_chats)
        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # Stacked widget for main content
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Database Page
        self.db_page = QWidget()
        db_layout = QVBoxLayout(self.db_page)
        db_layout.setContentsMargins(32, 32, 32, 32)
        db_layout.setSpacing(16)
        self.select_button = QPushButton("Select Meshtastic .db File")
        self.select_button.setStyleSheet('''
            QPushButton {
                background: #223366;
                color: #fff;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #2d3a5a;
            }
        ''')
        db_layout.addWidget(self.select_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.db_label = QLabel("No database selected.")
        self.db_label.setStyleSheet('color: #fff; font-size: 15px;')
        db_layout.addWidget(self.db_label)
        self.tables_label = QLabel("Tables:")
        self.tables_label.setStyleSheet('color: #b0b8d1; font-size: 14px; margin-top: 12px;')
        db_layout.addWidget(self.tables_label)
        self.tables_list = QListWidget()
        self.tables_list.setStyleSheet('background: #232b45; color: #fff; border-radius: 8px; font-size: 14px;')
        db_layout.addWidget(self.tables_list)
        self.db_page.setStyleSheet('background: #181f2f; border-radius: 16px;')
        self.stack.addWidget(self.db_page)

        # Connected Nodes Page
        self.nodes_page = QWidget()
        nodes_layout = QVBoxLayout(self.nodes_page)
        nodes_layout.setContentsMargins(32, 32, 32, 32)
        nodes_layout.setSpacing(16)
        self.nodes_tree = QTreeWidget()
        self.nodes_tree.setHeaderLabels(["num", "user_longName", "user_shortName", "lastHeard", "hopsAway", "channel"])
        self.nodes_tree.setStyleSheet('background: #232b45; color: #fff; border-radius: 8px; font-size: 14px;')
        nodes_layout.addWidget(self.nodes_tree)
        self.nodes_page.setStyleSheet('background: #181f2f; border-radius: 16px;')
        self.stack.addWidget(self.nodes_page)

        # Chats Page
        self.chats_page = QWidget()
        chats_layout = QHBoxLayout(self.chats_page)
        chats_layout.setContentsMargins(32, 32, 32, 32)
        chats_layout.setSpacing(16)
        # Contacts list
        self.chats_nodes_list = QListWidget()
        self.chats_nodes_list.setStyleSheet('background: #232b45; color: #fff; border-radius: 8px; font-size: 15px; min-width: 180px;')
        chats_layout.addWidget(self.chats_nodes_list)
        self.chats_nodes_list.itemSelectionChanged.connect(self.on_chat_node_select)
        # Chat area (scrollable)
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet('background: #232b45; border-radius: 12px;')
        self.chat_messages_area = QWidget()
        self.chat_messages_layout = QVBoxLayout(self.chat_messages_area)
        self.chat_messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_messages_area)
        chats_layout.addWidget(self.chat_scroll)
        self.chats_page.setStyleSheet('background: #181f2f; border-radius: 16px;')
        self.stack.addWidget(self.chats_page)

        # Navigation
        self.btn_database.clicked.connect(lambda: self.stack.setCurrentWidget(self.db_page))
        self.btn_nodes.clicked.connect(lambda: self.stack.setCurrentWidget(self.nodes_page))
        self.btn_chats.clicked.connect(lambda: self.stack.setCurrentWidget(self.chats_page))
        self.select_button.clicked.connect(self.select_db_file)

        # Set default page
        self.stack.setCurrentWidget(self.db_page)

        # Placeholder for future logic
        self.db_path = None
        self.conn = None
        self.chat_data = {}
        self.local_id = None
        self.node_names = {}  # {user_id: longName}

    def select_db_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Meshtastic SQLite DB", "", "All Files (*.*)")
        if file_path:
            self.db_path = file_path
            self.db_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.connect_and_list_tables()
        else:
            self.db_label.setText("No database selected.")
            self.tables_list.clear()
            self.nodes_tree.clear()

    def connect_and_list_tables(self):
        # Close previous connection if any
        if self.conn:
            self.conn.close()
            self.conn = None
        self.tables_list.clear()
        self.nodes_tree.clear()
        if not self.db_path:
            self.db_label.setText("No database selected.")
            return
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                self.tables_list.addItem(table)
            if "NodeInfo" in tables:
                self.load_nodeinfo()
            self.load_chat_nodes()
        except Exception as e:
            self.db_label.setText(f"Failed to open database: {e}")
            if self.conn:
                self.conn.close()
                self.conn = None

    def load_nodeinfo(self):
        self.nodes_tree.clear()
        if not self.conn:
            item = QTreeWidgetItem(["No database connection", "", "", "", "", ""])
            self.nodes_tree.addTopLevelItem(item)
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT num, user_longName, user_shortName, lastHeard, hopsAway, channel FROM NodeInfo;")
            rows = cursor.fetchall()
            for row in rows:
                item = QTreeWidgetItem([str(col) if col is not None else '' for col in row])
                self.nodes_tree.addTopLevelItem(item)
            if not rows:
                item = QTreeWidgetItem(["No nodes found", "", "", "", "", ""])
                self.nodes_tree.addTopLevelItem(item)
        except Exception as e:
            item = QTreeWidgetItem([f"Error: {e}", "", "", "", "", ""])
            self.nodes_tree.addTopLevelItem(item)

    def load_chat_nodes(self):
        self.chats_nodes_list.clear()
        self.chat_data = {}
        self.local_id = None
        self.node_names = {}  # {user_id: longName}
        if not self.conn:
            return
        try:
            # Load node names from NodeInfo
            cursor = self.conn.cursor()
            try:
                cursor.execute("SELECT num, user_longName FROM NodeInfo;")
                for num, longName in cursor.fetchall():
                    self.node_names[str(num)] = longName if longName else str(num)
            except Exception:
                pass  # NodeInfo table may not exist
            cursor.execute("SELECT message FROM log;")
            rows = cursor.fetchall()
            sent_to_counts = {}
            received_to_counts = {}
            messages = []
            for (msg,) in rows:
                # Only parse if portnum is TEXT_MESSAGE_APP
                portnum_match = re.search(r'portnum: ?TEXT_MESSAGE_APP', msg)
                if not portnum_match:
                    continue
                # Extract 'from', 'to', and payload
                from_match = re.search(r'^from: (\d+)', msg, re.MULTILINE)
                to_match = re.search(r'^to: (\d+)', msg, re.MULTILINE)
                payload_match = re.search(r'payload: "([^"]+)"', msg)
                if not payload_match or not to_match:
                    continue
                payload = payload_match.group(1)
                to_id = to_match.group(1)
                from_id = from_match.group(1) if from_match else None
                # Heuristic: if from_id is None, it's a sent message
                if from_id is None:
                    # Sent message
                    sent_to_counts[to_id] = sent_to_counts.get(to_id, 0) + 1
                    messages.append({'type': 'sent', 'other_id': to_id, 'payload': payload})
                else:
                    # Received message
                    received_to_counts[to_id] = received_to_counts.get(to_id, 0) + 1
                    messages.append({'type': 'received', 'other_id': from_id, 'payload': payload})
            # Infer local_id as the most common 'to' in sent or received messages
            if sent_to_counts:
                self.local_id = max(sent_to_counts, key=lambda k: sent_to_counts[k])
            elif received_to_counts:
                self.local_id = max(received_to_counts, key=lambda k: received_to_counts[k])
            # Group messages by other user
            for msg in messages:
                other_id = msg['other_id']
                if other_id not in self.chat_data:
                    self.chat_data[other_id] = []
                self.chat_data[other_id].append(msg)
            # Populate chat nodes list
            for user_id in self.chat_data:
                display_name = self.node_names.get(user_id, user_id)
                self.chats_nodes_list.addItem(f"{display_name} ({user_id})")
        except Exception as e:
            self.chats_nodes_list.addItem(f"Error: {e}")

    def on_chat_node_select(self):
        # Clear previous chat display
        for i in reversed(range(self.chat_messages_layout.count())):
            item = self.chat_messages_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        selected_items = self.chats_nodes_list.selectedItems()
        if not selected_items:
            print('No chat user selected.')
            return
        # Extract user_id from display string
        user_id_match = re.search(r'\((\d+)\)$', selected_items[0].text())
        if not user_id_match:
            print('Could not extract user_id from selected item:', selected_items[0].text())
            return
        user_id = user_id_match.group(1)
        print(f'Selected user_id: {user_id}')
        messages = self.chat_data.get(user_id, [])
        print(f'Found {len(messages)} messages for user_id {user_id}')
        for msg in messages:
            print('Message:', msg)
            text = msg.get('payload', '')
            align = Qt.AlignmentFlag.AlignRight if msg.get('type') == 'sent' else Qt.AlignmentFlag.AlignLeft
            # Get node name if available
            node_name = self.node_names.get(user_id, user_id)
            name_label = QLabel(f"<b>{node_name}</b>")
            name_label.setStyleSheet('color: #b0b8d1; font-size: 13px; margin-bottom: 2px;')
            name_label.setTextFormat(Qt.TextFormat.RichText)
            self.chat_messages_layout.addWidget(name_label, alignment=align)
            bubble = QLabel(text)
            bubble.setWordWrap(True)
            bubble.setStyleSheet('background-color: #e1ffc7; border-radius: 10px; padding: 8px;' if msg.get('type') == 'sent' else 'background-color: #ffffff; border-radius: 10px; padding: 8px;')
            self.chat_messages_layout.addWidget(bubble, alignment=align)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeshagePR()
    window.show()
    sys.exit(app.exec()) 