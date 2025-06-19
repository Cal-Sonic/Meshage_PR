import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QTreeWidget, QTreeWidgetItem, QFileDialog,
    QStackedWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QScrollArea,
    QSizePolicy, QSpacerItem, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit,
    QCheckBox, QMessageBox
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
        self.btn_database = SidebarButton("User Node Info")
        self.btn_nodes = SidebarButton("Connected Nodes")
        self.btn_chats = SidebarButton("Chats")
        self.btn_export_pdf = SidebarButton("Export PDF")
        sidebar_layout.addWidget(self.btn_database)
        sidebar_layout.addWidget(self.btn_nodes)
        sidebar_layout.addWidget(self.btn_chats)
        sidebar_layout.addWidget(self.btn_export_pdf)
        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # Stacked widget for main content
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # User Node Info Page (replaces Database page)
        self.user_node_page = QWidget()
        user_node_layout = QVBoxLayout(self.user_node_page)
        user_node_layout.setContentsMargins(32, 32, 32, 32)
        user_node_layout.setSpacing(16)
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
        user_node_layout.addWidget(self.select_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.user_node_info_label = QLabel("No database selected.")
        self.user_node_info_label.setStyleSheet('color: #fff; font-size: 15px; background: #232b45; border-radius: 12px; padding: 16px;')
        user_node_layout.addWidget(self.user_node_info_label)
        self.user_node_page.setStyleSheet('background: #181f2f; border-radius: 16px;')
        self.stack.addWidget(self.user_node_page)

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
        self.btn_database.clicked.connect(lambda: self.stack.setCurrentWidget(self.user_node_page))
        self.btn_nodes.clicked.connect(lambda: self.stack.setCurrentWidget(self.nodes_page))
        self.btn_chats.clicked.connect(lambda: self.stack.setCurrentWidget(self.chats_page))
        self.select_button.clicked.connect(self.select_db_file)
        self.btn_export_pdf.clicked.connect(self.export_pdf_dialog)

        # Set default page
        self.stack.setCurrentWidget(self.user_node_page)

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
            # Show Case Info dialog
            dlg = CaseInfoDialog(self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.case_info = dlg.get_info()
            else:
                self.case_info = None
            self.load_user_node_info()
            self.connect_and_list_tables()
        else:
            self.user_node_info_label.setText("No database selected.")
            self.nodes_tree.clear()

    def connect_and_list_tables(self):
        # Close previous connection if any
        if self.conn:
            self.conn.close()
            self.conn = None
        self.nodes_tree.clear()
        if not self.db_path:
            return
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            if "NodeInfo" in tables:
                self.load_nodeinfo()
            self.load_chat_nodes()
        except Exception as e:
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
                    name = longName if longName else str(num)
                    if hasattr(self, 'my_node_num') and self.my_node_num and str(num) == self.my_node_num:
                        name = f"{name} (User)"
                    self.node_names[str(num)] = name
            except Exception:
                pass  # NodeInfo table may not exist
            self.node_names["4294967295"] = "Public"
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
                    messages.append({'type': 'sent', 'other_id': to_id, 'payload': payload, 'from': self.my_node_num, 'to': to_id})
                else:
                    # Received message
                    received_to_counts[to_id] = received_to_counts.get(to_id, 0) + 1
                    messages.append({'type': 'received', 'other_id': from_id, 'payload': payload, 'from': from_id, 'to': to_id})
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
            # Only show sender's name above the message
            from_id = msg.get('from')
            from_name = self.node_names.get(from_id, from_id)
            name_label = QLabel(f"<b>{from_name}</b>")
            name_label.setStyleSheet('color: #b0b8d1; font-size: 13px; margin-bottom: 2px;')
            name_label.setTextFormat(Qt.TextFormat.RichText)
            self.chat_messages_layout.addWidget(name_label, alignment=align)
            bubble = QLabel(text)
            bubble.setWordWrap(True)
            bubble.setMaximumWidth(500)
            bubble.setStyleSheet('background-color: #e1ffc7; border-radius: 10px; padding: 8px; margin-bottom: 8px;' if msg.get('type') == 'sent' else 'background-color: #ffffff; border-radius: 10px; padding: 8px; margin-bottom: 8px;')
            bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            bubble.adjustSize()
            bubble.setMinimumHeight(bubble.sizeHint().height())
            self.chat_messages_layout.addWidget(bubble, alignment=align)
            # Add a small spacer for clarity
            self.chat_messages_layout.addSpacing(4)

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
                # Get column names
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

    def export_pdf_dialog(self):
        dlg = ExportSectionsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            sections = dlg.get_sections()
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

        # Connected Nodes
        if sections.get('Connected Nodes') and hasattr(self, 'nodes_tree'):
            pdf.add_page()
            page_header()
            section_header("Connected Nodes")
            for i in range(self.nodes_tree.topLevelItemCount()):
                item = self.nodes_tree.topLevelItem(i)
                row = [item.text(col) for col in range(self.nodes_tree.columnCount())]
                card("Node", [", ".join(row)])

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
    window.show()
    sys.exit(app.exec()) 