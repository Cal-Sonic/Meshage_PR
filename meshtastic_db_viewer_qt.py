import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTreeWidget, QTreeWidgetItem, QFileDialog,
    QStackedWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QScrollArea,
    QSizePolicy, QSpacerItem, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit,
    QCheckBox, QMessageBox, QToolButton, QStyle, QGroupBox, QHeaderView
)
from PyQt6.QtCore import Qt
import os
import sqlite3
import re
from fpdf import FPDF as BaseFPDF

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

class CaseInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Case Information")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.case_id = QLineEdit()
        self.case_name = QLineEdit()
        self.caseworker = QLineEdit()
        self.agency = QLineEdit()
        self.evidence_number = QLineEdit()
        self.description = QTextEdit()
        self.description.setMaximumHeight(60)
        layout.addRow("Case ID:", self.case_id)
        layout.addRow("Case Name:", self.case_name)
        layout.addRow("Caseworker:", self.caseworker)
        layout.addRow("Agency / Organization:", self.agency)
        layout.addRow("Evidence Number:", self.evidence_number)
        layout.addRow("Description:", self.description)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
    def get_info(self):
        return {
            'Case ID': self.case_id.text(),
            'Case Name': self.case_name.text(),
            'Caseworker': self.caseworker.text(),
            'Agency': self.agency.text(),
            'Evidence Number': self.evidence_number.text(),
            'Description': self.description.toPlainText()
        }

class ExportSectionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Sections to Export")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        self.cb_case = QCheckBox("Case Info")
        self.cb_user = QCheckBox("User Node Info")
        self.cb_nodes = QCheckBox("Connected Nodes")
        self.cb_chats = QCheckBox("Chats")
        self.cb_case.setChecked(True)
        self.cb_user.setChecked(True)
        self.cb_nodes.setChecked(True)
        self.cb_chats.setChecked(True)
        layout.addWidget(self.cb_case)
        layout.addWidget(self.cb_user)
        layout.addWidget(self.cb_nodes)
        layout.addWidget(self.cb_chats)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
    def get_sections(self):
        return {
            'Case Info': self.cb_case.isChecked(),
            'User Node Info': self.cb_user.isChecked(),
            'Connected Nodes': self.cb_nodes.isChecked(),
            'Chats': self.cb_chats.isChecked()
        }

class FPDF(BaseFPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

class MeshagePR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meshage_PR")
        self.setGeometry(100, 100, 1100, 700)
        # Modern stylesheet for the whole app (will be further refined)
        self.setStyleSheet("""
            QMainWindow {
                background: #181A20;
                font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
                font-size: 15px;
                color: #E5E7EB;
            }
            QWidget#sidebar {
                background: #23272F;
                border-top-right-radius: 18px;
                border-bottom-right-radius: 18px;
            }
            QLabel#logo_label {
                color: #3B82F6;
                font-size: 26px;
                font-weight: 700;
                padding-left: 18px;
                letter-spacing: 1px;
            }
            QToolButton {
                background: transparent;
                color: #E5E7EB;
                border: none;
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 16px;
                text-align: left;
            }
            QToolButton:hover, QToolButton:checked {
                background: #3B82F6;
                color: #fff;
            }
            QGroupBox {
                background: #23272F;
                border-radius: 16px;
                margin-top: 16px;
                padding: 18px;
                border: 1px solid #353945;
            }
            QLabel.section_header {
                color: #3B82F6;
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 12px;
            }
        """)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar (overhauled)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 24, 0, 24)
        sidebar_layout.setSpacing(10)
        self.logo_label = QLabel("Meshage_PR")
        self.logo_label.setObjectName("logo_label")
        sidebar_layout.addWidget(self.logo_label)
        sidebar_layout.addSpacing(30)
        # Navigation buttons (icons assigned later)
        self.btn_database = QToolButton()
        self.btn_database.setText("User Node Info")
        self.btn_database.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_nodes = QToolButton()
        self.btn_nodes.setText("Connected Nodes")
        self.btn_nodes.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_chats = QToolButton()
        self.btn_chats.setText("Chats")
        self.btn_chats.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_export_pdf = QToolButton()
        self.btn_export_pdf.setText("Export PDF")
        self.btn_export_pdf.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        sidebar_layout.addWidget(self.btn_database)
        sidebar_layout.addWidget(self.btn_nodes)
        sidebar_layout.addWidget(self.btn_chats)
        sidebar_layout.addWidget(self.btn_export_pdf)
        sidebar_layout.addStretch()
        self.btn_settings = QToolButton()
        self.btn_settings.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.btn_settings.setToolTip("Settings / About")
        sidebar_layout.addWidget(self.btn_settings, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.sidebar)

        # Main content area (overhauled)
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.stack)

        # User Node Info Page (card style)
        self.user_node_page = QWidget()
        self.user_node_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        user_node_layout = QVBoxLayout(self.user_node_page)
        user_node_layout.setContentsMargins(40, 40, 40, 40)
        user_node_layout.setSpacing(20)
        # Section header
        user_header = QLabel("User Node Info")
        user_header.setProperty("class", "section_header")
        user_node_layout.addWidget(user_header)
        # Card container
        user_card = QGroupBox()
        user_card_layout = QVBoxLayout(user_card)
        self.select_button = QPushButton("Select Meshtastic .db File")
        user_card_layout.addWidget(self.select_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.user_node_info_label = QLabel("No database selected.")
        self.user_node_info_label.setWordWrap(True)
        user_card_layout.addWidget(self.user_node_info_label)
        user_node_layout.addWidget(user_card)
        user_node_layout.addStretch()
        self.stack.addWidget(self.user_node_page)

        # Connect select_button to select_db_file
        self.select_button.clicked.connect(self.select_db_file)

        # Connected Nodes Page (modern card/table style)
        self.nodes_page = QWidget()
        self.nodes_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        nodes_layout = QVBoxLayout(self.nodes_page)
        nodes_layout.setContentsMargins(40, 40, 40, 40)
        nodes_layout.setSpacing(20)
        nodes_header = QLabel("Connected Nodes")
        nodes_header.setProperty("class", "section_header")
        nodes_layout.addWidget(nodes_header)
        nodes_card = QGroupBox()
        nodes_card_layout = QVBoxLayout(nodes_card)
        # Table with placeholder data
        self.nodes_table = QTableWidget(3, 6)
        self.nodes_table.setHorizontalHeaderLabels(["num", "user_longName", "user_shortName", "lastHeard", "hopsAway", "channel"])
        vh = self.nodes_table.verticalHeader()
        if vh is not None:
            vh.setVisible(False)
            vh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            vh.setDefaultSectionSize(0)  # Hide the vertical header bar completely
            vh.setMinimumSectionSize(0)
        self.nodes_table.setShowGrid(False)
        self.nodes_table.setAlternatingRowColors(True)
        self.nodes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.nodes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.nodes_table.setStyleSheet('QTableWidget { border-radius: 12px; background: #23272F; color: #E5E7EB; font-size: 15px; } QHeaderView::section { background: #23272F; color: #3B82F6; font-weight: 600; border: none; } QTableWidget::item:selected { background: #3B82F6; color: #fff; }')
        # Placeholder data
        placeholder_data = [
            ["1234", "Alice", "A", "2024-06-01 12:00", "1", "1"],
            ["5678", "Bob", "B", "2024-06-01 12:05", "2", "1"],
            ["9012", "Charlie", "C", "2024-06-01 12:10", "1", "2"]
        ]
        for row_idx, row_data in enumerate(placeholder_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setForeground(Qt.GlobalColor.white)
                self.nodes_table.setItem(row_idx, col_idx, item)
        self.nodes_table.resizeColumnsToContents()
        nodes_card_layout.addWidget(self.nodes_table)
        nodes_card_layout.addStretch()
        nodes_layout.addWidget(nodes_card)
        nodes_layout.addStretch()
        self.stack.addWidget(self.nodes_page)

        # Chats Page (modern messenger style)
        self.chats_page = QWidget()
        self.chats_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        chats_layout = QVBoxLayout(self.chats_page)
        chats_layout.setContentsMargins(40, 40, 40, 40)
        chats_layout.setSpacing(20)
        chats_header = QLabel("Chats")
        chats_header.setProperty("class", "section_header")
        chats_layout.addWidget(chats_header)
        # Card container for chat content
        chats_card = QGroupBox()
        chats_card_layout = QHBoxLayout(chats_card)
        chats_card_layout.setSpacing(0)
        # Contacts list (left)
        self.chats_contacts_list = QListWidget()
        self.chats_contacts_list.setFixedWidth(220)
        self.chats_contacts_list.setStyleSheet('QListWidget { border-radius: 12px; background: #23272F; color: #E5E7EB; font-size: 15px; } QListWidget::item:selected { background: #3B82F6; color: #fff; }')
        # Placeholder contacts
        contacts = ["Alice (1234)", "Bob (5678)", "Charlie (9012)"]
        self.chats_contacts_list.addItems(contacts)
        chats_card_layout.addWidget(self.chats_contacts_list)
        # Chat area (right)
        chat_area_container = QGroupBox()
        chat_area_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow vertical expansion
        chat_area_layout = QVBoxLayout(chat_area_container)
        chat_area_layout.setContentsMargins(16, 16, 16, 16)
        chat_area_layout.setSpacing(8)
        # Scrollable chat area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet('QScrollArea { border-radius: 12px; background: #23272F; }')
        self.chat_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow vertical expansion
        self.chat_messages_area = QWidget()
        self.chat_messages_layout = QVBoxLayout(self.chat_messages_area)
        self.chat_messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_messages_area)
        chat_area_layout.addWidget(self.chat_scroll)
        # Remove addStretch here to allow scroll area to fill
        chat_area_container.setStyleSheet('QGroupBox { background: #23272F; border-radius: 12px; border: 1px solid #353945; }')
        chats_card_layout.addWidget(chat_area_container)
        chats_card_layout.setStretch(0, 0)  # Contacts list fixed
        chats_card_layout.setStretch(1, 1)  # Chat area expands
        chats_layout.addWidget(chats_card)
        chats_layout.setStretchFactor(chats_card, 1)  # Make the card fill vertical space
        # Remove the bottom addStretch to allow full expansion
        self.stack.addWidget(self.chats_page)
        # Navigation logic for sidebar buttons
        self.btn_database.clicked.connect(lambda: self.stack.setCurrentWidget(self.user_node_page))
        self.btn_nodes.clicked.connect(lambda: self.stack.setCurrentWidget(self.nodes_page))
        self.btn_chats.clicked.connect(lambda: self.stack.setCurrentWidget(self.chats_page))
        self.btn_export_pdf.clicked.connect(lambda: self.stack.setCurrentWidget(self.export_page))
        self.chats_contacts_list.currentRowChanged.connect(lambda idx: self.show_chat_for_selected())

        # Export PDF Page (modern card style)
        self.export_page = QWidget()
        self.export_page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        export_layout = QVBoxLayout(self.export_page)
        export_layout.setContentsMargins(40, 40, 40, 40)
        export_layout.setSpacing(20)
        export_header = QLabel("Export PDF")
        export_header.setProperty("class", "section_header")
        export_layout.addWidget(export_header)
        export_card = QGroupBox()
        export_card_layout = QVBoxLayout(export_card)
        export_card_layout.setSpacing(16)
        # Section checkboxes
        self.cb_case = QCheckBox("Case Info")
        self.cb_user = QCheckBox("User Node Info")
        self.cb_nodes = QCheckBox("Connected Nodes")
        self.cb_chats = QCheckBox("Chats")
        self.cb_case.setChecked(True)
        self.cb_user.setChecked(True)
        self.cb_nodes.setChecked(True)
        self.cb_chats.setChecked(True)
        export_card_layout.addWidget(self.cb_case)
        export_card_layout.addWidget(self.cb_user)
        export_card_layout.addWidget(self.cb_nodes)
        export_card_layout.addWidget(self.cb_chats)
        # Export button
        self.export_button = QPushButton("Export PDF")
        export_card_layout.addWidget(self.export_button, alignment=Qt.AlignmentFlag.AlignLeft)
        export_layout.addWidget(export_card)
        export_layout.addStretch()
        self.stack.addWidget(self.export_page)
        # Navigation logic for sidebar button
        self.btn_export_pdf.clicked.connect(lambda: self.stack.setCurrentWidget(self.export_page))
        # Wire up export button
        self.export_button.clicked.connect(self.export_pdf_from_page)

        # Placeholder for future logic
        self.db_path = None
        self.conn = None
        self.chat_data = {}
        self.local_id = None
        self.node_names = {}  # {user_id: longName}

    def setup_sidebar_icons(self):
        app_style = QApplication.style()
        if app_style is not None:
            self.btn_database.setIcon(app_style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            self.btn_nodes.setIcon(app_style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            self.btn_chats.setIcon(app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
            self.btn_export_pdf.setIcon(app_style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
            self.btn_settings.setIcon(app_style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))

    def select_db_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Meshtastic SQLite DB", "", "All Files (*.*)")
        if file_path:
            self.db_path = file_path
            # Show Case Info dialog
            dlg = CaseInfoDialog(self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.case_info = dlg.get_info()
            else:
                self.case_info = None
            self.load_user_node_info()
            self.load_connected_nodes()
            self.load_chats()
        else:
            self.user_node_info_label.setText("No database selected.")
            self.nodes_table.setRowCount(0)
            self.chats_contacts_list.clear()
            self.clear_chat_messages()

    def connect_and_list_tables(self):
        # Close previous connection if any
        if self.conn:
            self.conn.close()
            self.conn = None
        # TODO: Reimplement Connected Nodes page and clear nodes_tree
        if not self.db_path:
            return
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            if "NodeInfo" in tables:
                pass  # TODO: Reimplement load_nodeinfo for new UI
            # TODO: Reimplement load_chat_nodes for new UI
        except Exception as e:
            if self.conn:
                self.conn.close()
                self.conn = None

    def load_user_node_info(self):
        self.my_node_num = None
        if not self.db_path:
            self.user_node_info_label.setText("No database selected.")
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM MyNodeInfo LIMIT 1;")
            row = cursor.fetchone()
            if row:
                col_names = [desc[0] for desc in cursor.description]
                info = "<b>User Node Info:</b><br>"
                for name, value in zip(col_names, row):
                    info += f"<b>{name}:</b> {value}<br>"
                    if name == "myNodeNum":
                        self.my_node_num = str(value)
                self.user_node_info_label.setText(info)
            else:
                self.user_node_info_label.setText("No MyNodeInfo found in database.")
            conn.close()
        except Exception as e:
            self.user_node_info_label.setText(f"Error loading MyNodeInfo: {e}")

    def load_connected_nodes(self):
        if not self.db_path:
            self.nodes_table.setRowCount(0)
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT num, user_longName, user_shortName, lastHeard, hopsAway, channel FROM NodeInfo;")
            rows = cursor.fetchall()
            self.nodes_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setForeground(Qt.GlobalColor.white)
                    self.nodes_table.setItem(row_idx, col_idx, item)
            self.nodes_table.resizeColumnsToContents()
            if not rows:
                self.nodes_table.setRowCount(0)
            conn.close()
        except Exception as e:
            self.nodes_table.setRowCount(0)
            # Optionally show error in a label or status bar

    def load_chats(self):
        self.chats_contacts_list.clear()
        self.chat_data = {}
        self.local_id = None
        self.node_names = {}  # {user_id: longName}
        if not self.db_path:
            self.clear_chat_messages()
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Load node names from NodeInfo
            try:
                cursor.execute("SELECT num, user_longName FROM NodeInfo;")
                for num, longName in cursor.fetchall():
                    name = longName if longName else str(num)
                    self.node_names[str(num)] = name
            except Exception:
                pass  # NodeInfo table may not exist
            self.node_names["4294967295"] = "Public"
            cursor.execute("SELECT message FROM log;")
            rows = cursor.fetchall()
            print(f"Loaded {len(rows)} log messages from database.")
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
                    messages.append({'type': 'sent', 'other_id': to_id, 'payload': payload, 'from': self.my_node_num, 'to': to_id})
                else:
                    # Received message
                    received_to_counts[to_id] = received_to_counts.get(to_id, 0) + 1
                    messages.append({'type': 'received', 'other_id': from_id, 'payload': payload, 'from': from_id, 'to': to_id})
            print(f"Parsed {len(messages)} chat messages.")
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
            print(f"Chat data keys (user_ids): {list(self.chat_data.keys())}")
            # Populate chat contacts list
            for user_id in self.chat_data:
                display_name = self.node_names.get(user_id, user_id)
                self.chats_contacts_list.addItem(f"{display_name} ({user_id})")
            conn.close()
            # Show chat for first contact by default
            if self.chats_contacts_list.count() > 0:
                self.chats_contacts_list.setCurrentRow(0)
                self.show_chat_for_selected()
            else:
                self.clear_chat_messages()
        except Exception as e:
            print(f"Error loading chats: {e}")
            self.chats_contacts_list.clear()
            self.clear_chat_messages()

    def clear_chat_messages(self):
        for i in reversed(range(self.chat_messages_layout.count())):
            item = self.chat_messages_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def show_chat_for_selected(self):
        self.clear_chat_messages()
        selected_items = self.chats_contacts_list.selectedItems()
        if not selected_items:
            print('No chat user selected.')
            return
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
            from_id = msg.get('from')
            from_name = self.node_names.get(from_id, from_id)
            name_label = QLabel(f"<b>{from_name}</b>")
            name_label.setStyleSheet('color: #E5E7EB; font-size: 13px; margin-bottom: 2px;')
            name_label.setTextFormat(Qt.TextFormat.RichText)
            self.chat_messages_layout.addWidget(name_label, alignment=align)
            bubble = QLabel(text)
            bubble.setWordWrap(True)
            bubble.setMaximumWidth(400)
            bubble.setStyleSheet(
                'background-color: #3B82F6; color: #fff; border-radius: 10px; padding: 10px; margin-bottom: 8px;' if msg.get('type') == 'sent' else
                'background-color: #353945; color: #E5E7EB; border-radius: 10px; padding: 10px; margin-bottom: 8px;'
            )
            self.chat_messages_layout.addWidget(bubble, alignment=align)

    def export_pdf_from_page(self):
        sections = {
            'Case Info': self.cb_case.isChecked(),
            'User Node Info': self.cb_user.isChecked(),
            'Connected Nodes': self.cb_nodes.isChecked(),
            'Chats': self.cb_chats.isChecked()
        }
        self.export_pdf(sections)

    def export_pdf(self, sections):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.alias_nb_pages()

        # Helper for page header
        def page_header():
            pdf.set_fill_color(34, 51, 102)  # Navy blue
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 12, "Meshage_PR Export Report", ln=True, fill=True)
            pdf.set_font("Arial", size=11)
            pdf.set_text_color(200, 200, 200)
            case_num = self.case_info.get('Case ID', '') if hasattr(self, 'case_info') and self.case_info else ''
            caseworker = self.case_info.get('Caseworker', '') if hasattr(self, 'case_info') and self.case_info else ''
            pdf.cell(0, 8, f"Case Number: {case_num}    Caseworker: {caseworker}", ln=True, fill=True)
            pdf.ln(4)
            pdf.set_text_color(0, 0, 0)

        # Helper for section header
        def section_header(title):
            pdf.set_fill_color(34, 51, 102)  # Navy blue
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 16, title, ln=True, fill=True)
            pdf.ln(6)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", size=12)

        # Helper for card
        def card(title, lines):
            pdf.set_fill_color(230, 235, 245)
            pdf.set_draw_color(34, 51, 102)
            pdf.set_line_width(0.5)
            y1 = pdf.get_y()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font("Arial", size=12)
            for line in lines:
                pdf.multi_cell(0, 8, line)
            y2 = pdf.get_y()
            pdf.rect(10, y1-2, 190, y2-y1+4)
            pdf.ln(4)

        # Case Info
        if sections.get('Case Info') and hasattr(self, 'case_info') and self.case_info:
            pdf.add_page()
            page_header()
            section_header("Case Info")
            lines = [f"{k}: {v}" for k, v in self.case_info.items()]
            card("Case Details", lines)

        # User Node Info
        label = getattr(self, 'user_node_info_label', None)
        if sections.get('User Node Info') and label is not None and isinstance(label, QLabel):
            pdf.add_page()
            page_header()
            section_header("User Node Info")
            text = label.text().replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
            lines = [line for line in text.split('\n') if line.strip()]
            card("Node Details", lines)

        # TODO: Reimplement Connected Nodes export for new UI

        # Chats
        if sections.get('Chats') and hasattr(self, 'chat_data'):
            pdf.add_page()
            page_header()
            section_header("Chats")
            for user_id, messages in self.chat_data.items():
                chat_title = f"Chat with {self.node_names.get(user_id, user_id)}"
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, chat_title, ln=True)
                pdf.ln(2)
                for msg in messages:
                    sender = self.node_names.get(msg.get('from'), msg.get('from'))
                    text = msg.get('payload', '')
                    is_user = hasattr(self, 'my_node_num') and msg.get('from') == self.my_node_num

                    # Bubble settings
                    pdf.set_font("Arial", "I", 9)
                    sender_w = pdf.get_string_width(sender) + 8
                    pdf.set_font("Arial", "", 11)
                    lines = text.split('\n')
                    max_line = max(lines, key=lambda l: pdf.get_string_width(l) if l else 0)
                    bubble_w = min(max(pdf.get_string_width(max_line) + 16, 40), 90)  # min 40, max 90mm
                    bubble_h = 8 * len(lines) + 14
                    y = pdf.get_y()
                    if is_user:
                        x = 200 - bubble_w  # right align
                        pdf.set_fill_color(225, 255, 199)
                    else:
                        x = 10  # left align
                        pdf.set_fill_color(255, 255, 255)

                    # Draw sender name
                    pdf.set_xy(x, y)
                    pdf.set_font("Arial", "I", 9)
                    pdf.cell(bubble_w, 6, sender, ln=2, align='L', fill=False, border=0)
                    # Draw bubble
                    pdf.set_xy(x, pdf.get_y())
                    pdf.set_font("Arial", "", 11)
                    bubble_text_y = pdf.get_y()
                    pdf.multi_cell(bubble_w, 8, text, border=0, align='L', fill=True)
                    # Remove outline around the bubble
                    pdf.ln(2)
                pdf.ln(4)

        # Save dialog
        default_filename = "report.pdf"
        evidence_number = ''
        if hasattr(self, 'case_info') and self.case_info:
            evidence_number = self.case_info.get('Evidence Number', '').strip()
        if evidence_number:
            default_filename = f"{evidence_number}_report.pdf"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", default_filename, "PDF Files (*.pdf)")
        if save_path:
            try:
                pdf.output(save_path)
                QMessageBox.information(self, "Export Complete", f"PDF exported to: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export PDF:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MeshagePR()
    window.setup_sidebar_icons()  # Assign icons after QApplication is created
    window.show()
    sys.exit(app.exec()) 