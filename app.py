import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QSizePolicy, QStackedWidget, QPushButton,
    QScrollArea, QGridLayout, QLineEdit, QDialog, QFormLayout, QTableWidget,
    QTableWidgetItem, QDateEdit, QHeaderView, QAbstractItemView, QComboBox,
    QGroupBox
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize

# --- Data Persistence ---
DATA_FILE = "transport_data.json"

def load_data():
    """Loads application data from a JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return initialize_data()
    return initialize_data()

def save_data(data):
    """Saves application data to a JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "Save Error", f"Failed to save data: {e}")

def initialize_data():
    """Initializes the data structure with empty lists and dicts."""
    return {
        "vehicles": {},
        "trips": [],
        "vehicle_expenses": [],
        "office_expenses": []
    }

# --- Shared UI Components ---
class BackButton(QPushButton):
    """A styled back button."""
    def __init__(self, parent=None):
        super().__init__("← Back", parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f8ff;
                color: #1a237e;
                border: 2px solid #1a237e;
                border-radius: 6px;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e9f2ff;
            }
        """)

class Card(QFrame):
    """A reusable card widget for the homepage."""
    clicked = pyqtSignal(str)
    def __init__(self, icon, title, desc, page_id, parent=None):
        super().__init__(parent)
        self.page_id = page_id
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(QSize(280, 180))
        self.setStyleSheet("""
            QFrame {
                background-color: #e9f2ff;
                border-radius: 12px;
                border: 2px solid transparent;
            }
            QFrame:hover {
                background-color: #d4ecff;
                border: 2px solid #007BFF;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI Emoji", 48))
        lbl_icon.setStyleSheet("color: #007BFF;")
        layout.addWidget(lbl_icon)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #003366;")
        layout.addWidget(lbl_title)

        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Arial", 13))
        lbl_desc.setStyleSheet("color: #444444;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_desc)

    def mousePressEvent(self, event):
        self.clicked.emit(self.page_id)

# --- Pages / Widgets ---
class HomePageWidget(QWidget):
    """The main home page with navigation cards."""
    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #e9f7ff; border-radius: 12px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 15, 30, 15)
        header_layout.setSpacing(20)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title + Description
        title_container = QVBoxLayout()
        title_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label = QLabel("KTS TRANSPORT")
        title_label.setFont(QFont("Arial Black", 32, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #007BFF;")
        title_container.addWidget(title_label)
        desc_label = QLabel("134, G NVK COMPLEX, SALEM ROAD, NAMAKKAL - 637001\nPH: 6382447660")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setStyleSheet("color: #333333;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.addWidget(desc_label)
        header_layout.addLayout(title_container)
        main_layout.addWidget(header_frame)

        # Cards
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cards_layout.setSpacing(40)

        top_row = QHBoxLayout()
        top_row.setSpacing(60)
        vehicle_card = Card("👨‍✈️", "Driver & Vehicle", "Details & Management", "vehicles")
        trip_card = Card("🗺️", "Trip", "Trip Planning & Tracking", "trips")
        top_row.addWidget(vehicle_card)
        top_row.addWidget(trip_card)
        cards_layout.addLayout(top_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(60)
        office_card = Card("🏢", "Office", "Office Operations", "office")
        expenses_card = Card("💵", "Vehicle Expenses", "Manage vehicle costs", "vehicle_expenses")
        bottom_row.addWidget(office_card)
        bottom_row.addWidget(expenses_card)
        cards_layout.addLayout(bottom_row)

        main_layout.addWidget(cards_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)

        # Connect signals
        vehicle_card.clicked.connect(self.navigate.emit)
        trip_card.clicked.connect(self.navigate.emit)
        office_card.clicked.connect(self.navigate.emit)
        expenses_card.clicked.connect(self.navigate.emit)

class VehicleDriverWidget(QWidget):
    """Page for managing vehicle and driver details."""
    go_back = pyqtSignal()

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.data_key = 'vehicles'
        self.setup_ui()
        self.refresh_grid()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        back_btn = BackButton(self)
        back_btn.clicked.connect(self.go_back.emit)
        main_layout.addWidget(back_btn)

        title_label = QLabel("Driver & Vehicle Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1a237e;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        add_btn = QPushButton("Add New Vehicle")
        add_btn.setStyleSheet("""
            QPushButton { background-color: #007BFF; color: white; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #005fc1; }
        """)
        add_btn.clicked.connect(self.add_edit_vehicle)
        main_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_content = QWidget()
        self.scroll_area_content.setStyleSheet("background-color: #f0f8ff;")
        self.grid_layout = QGridLayout(self.scroll_area_content)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.grid_layout.setSpacing(20)
        self.scroll_area.setWidget(self.scroll_area_content)
        main_layout.addWidget(self.scroll_area)

    def refresh_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        vehicles = self.data.get(self.data_key, {})
        col, row = 0, 0
        for vehicle_id, details in vehicles.items():
            card = self.create_vehicle_card(vehicle_id, details)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
    
    def create_vehicle_card(self, vehicle_id, details):
        card = QFrame()
        card.setFixedSize(250, 180)
        card.setStyleSheet("""
            QFrame { background-color: #d8ecff; border: 1px solid #007BFF; border-radius: 12px; }
            QFrame QLabel { background: none; }
        """)
        layout = QVBoxLayout(card)
        
        name_label = QLabel(details.get('name', 'N/A'))
        name_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(name_label)
        
        driver_label = QLabel(f"Driver: {details.get('driver_name', 'N/A')}")
        layout.addWidget(driver_label)
        
        exp_label = QLabel(f"Exp: {details.get('driver_experience', 'N/A')}")
        layout.addWidget(exp_label)
        
        loan_total = details.get('loan_total', 0)
        loan_paid = details.get('loan_paid', 0)
        loan_remaining = float(loan_total) - float(loan_paid)
        
        loan_label = QLabel(f"Loan: {loan_remaining:.2f} (Rem.)")
        layout.addWidget(loan_label)
        
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("QPushButton { background-color: #007BFF; color: white; padding: 4px 8px; border-radius: 6px; }")
        edit_btn.clicked.connect(lambda: self.add_edit_vehicle(vehicle_id))
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 6px; }")
        delete_btn.clicked.connect(lambda: self.delete_vehicle(vehicle_id))
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        return card

    def add_edit_vehicle(self, vehicle_id=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Vehicle" if vehicle_id else "Add New Vehicle")
        form_layout = QFormLayout()

        vehicle_name = self.data[self.data_key].get(vehicle_id, {}).get('name', '') if vehicle_id else ''
        vehicle_name_edit = QLineEdit(vehicle_name)
        form_layout.addRow("Vehicle Name:", vehicle_name_edit)
        
        driver_name_edit = QLineEdit(self.data[self.data_key].get(vehicle_id, {}).get('driver_name', ''))
        form_layout.addRow("Driver Name:", driver_name_edit)

        loan_total_edit = QLineEdit(self.data[self.data_key].get(vehicle_id, {}).get('loan_total', ''))
        form_layout.addRow("Total Loan:", loan_total_edit)

        loan_paid_edit = QLineEdit(self.data[self.data_key].get(vehicle_id, {}).get('loan_paid', ''))
        form_layout.addRow("Loan Paid:", loan_paid_edit)

        main_layout = QVBoxLayout(dlg)
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        
        def on_save():
            name = vehicle_name_edit.text()
            driver = driver_name_edit.text()
            loan_total = loan_total_edit.text()
            loan_paid = loan_paid_edit.text()

            if not name or not driver:
                QMessageBox.warning(self, "Invalid Input", "Vehicle Name and Driver Name are required.")
                return

            if vehicle_id:
                self.data[self.data_key][vehicle_id]['name'] = name
                self.data[self.data_key][vehicle_id]['driver_name'] = driver
                self.data[self.data_key][vehicle_id]['loan_total'] = loan_total
                self.data[self.data_key][vehicle_id]['loan_paid'] = loan_paid
            else:
                new_id = str(len(self.data[self.data_key]) + 1)
                self.data[self.data_key][new_id] = {
                    'name': name,
                    'driver_name': driver,
                    'loan_total': loan_total,
                    'loan_paid': loan_paid
                }
            
            save_data(self.data)
            self.refresh_grid()
            dlg.accept()

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec()

    def delete_vehicle(self, vehicle_id):
        reply = QMessageBox.question(self, "Delete Vehicle",
                                     "Are you sure you want to delete this vehicle?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if vehicle_id in self.data[self.data_key]:
                del self.data[self.data_key][vehicle_id]
                save_data(self.data)
                self.refresh_grid()

class TripWidget(QWidget):
    """Page for managing trip details."""
    go_back = pyqtSignal()

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.data_key = 'trips'
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        back_btn = BackButton(self)
        back_btn.clicked.connect(self.go_back.emit)
        main_layout.addWidget(back_btn)

        title_label = QLabel("Trip Management")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1a237e;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        add_btn = QPushButton("Add New Trip")
        add_btn.setStyleSheet("""
            QPushButton { background-color: #007BFF; color: white; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #005fc1; }
        """)
        add_btn.clicked.connect(self.add_edit_trip)
        main_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Vehicle", "Source", "Destination", "Distance (km)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table)

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, trip in enumerate(self.data.get(self.data_key, [])):
            self.table.insertRow(i)
            vehicle_name = self.data['vehicles'].get(trip.get('vehicle_id'), {}).get('name', 'N/A')
            self.table.setItem(i, 0, QTableWidgetItem(trip.get('date')))
            self.table.setItem(i, 1, QTableWidgetItem(vehicle_name))
            self.table.setItem(i, 2, QTableWidgetItem(trip.get('source')))
            self.table.setItem(i, 3, QTableWidgetItem(trip.get('destination')))
            self.table.setItem(i, 4, QTableWidgetItem(str(trip.get('distance'))))

    def add_edit_trip(self, trip_data=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Trip" if trip_data else "Add New Trip")
        form_layout = QFormLayout()

        vehicle_combo = QComboBox()
        for vehicle_id, details in self.data['vehicles'].items():
            vehicle_combo.addItem(details['name'], vehicle_id)
        form_layout.addRow("Vehicle:", vehicle_combo)

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date:", date_edit)

        source_edit = QLineEdit(trip_data.get('source', '') if trip_data else '')
        form_layout.addRow("Source:", source_edit)

        destination_edit = QLineEdit(trip_data.get('destination', '') if trip_data else '')
        form_layout.addRow("Destination:", destination_edit)

        distance_edit = QLineEdit(str(trip_data.get('distance', '')) if trip_data else '')
        form_layout.addRow("Distance (km):", distance_edit)

        main_layout = QVBoxLayout(dlg)
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        
        def on_save():
            vehicle_id = vehicle_combo.currentData()
            date = date_edit.date().toString("yyyy-MM-dd")
            source = source_edit.text()
            destination = destination_edit.text()
            distance = distance_edit.text()

            if not all([vehicle_id, date, source, destination, distance]):
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return

            if trip_data:
                trip_data['vehicle_id'] = vehicle_id
                trip_data['date'] = date
                trip_data['source'] = source
                trip_data['destination'] = destination
                trip_data['distance'] = float(distance)
            else:
                new_trip = {
                    'vehicle_id': vehicle_id,
                    'date': date,
                    'source': source,
                    'destination': destination,
                    'distance': float(distance)
                }
                self.data[self.data_key].append(new_trip)
            
            save_data(self.data)
            self.refresh_table()
            dlg.accept()

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec()

class VehicleExpensesWidget(QWidget):
    """Page for managing vehicle expenses."""
    go_back = pyqtSignal()

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.data_key = 'vehicle_expenses'
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        back_btn = BackButton(self)
        back_btn.clicked.connect(self.go_back.emit)
        main_layout.addWidget(back_btn)

        title_label = QLabel("Vehicle Expenses")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1a237e;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        add_btn = QPushButton("Add New Expense")
        add_btn.setStyleSheet("""
            QPushButton { background-color: #007BFF; color: white; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #005fc1; }
        """)
        add_btn.clicked.connect(self.add_edit_expense)
        main_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Vehicle", "Description", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table)

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, expense in enumerate(self.data.get(self.data_key, [])):
            self.table.insertRow(i)
            vehicle_name = self.data['vehicles'].get(expense.get('vehicle_id'), {}).get('name', 'N/A')
            self.table.setItem(i, 0, QTableWidgetItem(expense.get('date')))
            self.table.setItem(i, 1, QTableWidgetItem(vehicle_name))
            self.table.setItem(i, 2, QTableWidgetItem(expense.get('description')))
            self.table.setItem(i, 3, QTableWidgetItem(str(expense.get('amount'))))

    def add_edit_expense(self, expense_data=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Expense" if expense_data else "Add New Expense")
        form_layout = QFormLayout()

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date:", date_edit)

        vehicle_combo = QComboBox()
        for vehicle_id, details in self.data['vehicles'].items():
            vehicle_combo.addItem(details['name'], vehicle_id)
        form_layout.addRow("Vehicle:", vehicle_combo)

        description_edit = QLineEdit(expense_data.get('description', '') if expense_data else '')
        form_layout.addRow("Description:", description_edit)

        amount_edit = QLineEdit(str(expense_data.get('amount', '')) if expense_data else '')
        form_layout.addRow("Amount:", amount_edit)

        main_layout = QVBoxLayout(dlg)
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        
        def on_save():
            date = date_edit.date().toString("yyyy-MM-dd")
            vehicle_id = vehicle_combo.currentData()
            description = description_edit.text()
            amount = amount_edit.text()

            if not all([date, vehicle_id, description, amount]):
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return

            if expense_data:
                expense_data['date'] = date
                expense_data['vehicle_id'] = vehicle_id
                expense_data['description'] = description
                expense_data['amount'] = float(amount)
            else:
                new_expense = {
                    'date': date,
                    'vehicle_id': vehicle_id,
                    'description': description,
                    'amount': float(amount)
                }
                self.data[self.data_key].append(new_expense)
            
            save_data(self.data)
            self.refresh_table()
            dlg.accept()

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec()
        
class OfficeExpensesWidget(QWidget):
    """Page for managing office expenses."""
    go_back = pyqtSignal()

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.data_key = 'office_expenses'
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        back_btn = BackButton(self)
        back_btn.clicked.connect(self.go_back.emit)
        main_layout.addWidget(back_btn)

        title_label = QLabel("Office Expenses")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1a237e;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        add_btn = QPushButton("Add New Expense")
        add_btn.setStyleSheet("""
            QPushButton { background-color: #007BFF; color: white; border-radius: 6px; padding: 8px 16px; }
            QPushButton:hover { background-color: #005fc1; }
        """)
        add_btn.clicked.connect(self.add_edit_expense)
        main_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table)
    
    def refresh_table(self):
        self.table.setRowCount(0)
        for i, expense in enumerate(self.data.get(self.data_key, [])):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(expense.get('date')))
            self.table.setItem(i, 1, QTableWidgetItem(expense.get('description')))
            self.table.setItem(i, 2, QTableWidgetItem(str(expense.get('amount'))))

    def add_edit_expense(self, expense_data=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Expense" if expense_data else "Add New Expense")
        form_layout = QFormLayout()

        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Date:", date_edit)

        description_edit = QLineEdit(expense_data.get('description', '') if expense_data else '')
        form_layout.addRow("Description:", description_edit)

        amount_edit = QLineEdit(str(expense_data.get('amount', '')) if expense_data else '')
        form_layout.addRow("Amount:", amount_edit)

        main_layout = QVBoxLayout(dlg)
        main_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        
        def on_save():
            date = date_edit.date().toString("yyyy-MM-dd")
            description = description_edit.text()
            amount = amount_edit.text()

            if not all([date, description, amount]):
                QMessageBox.warning(self, "Invalid Input", "All fields are required.")
                return

            if expense_data:
                expense_data['date'] = date
                expense_data['description'] = description
                expense_data['amount'] = float(amount)
            else:
                new_expense = {
                    'date': date,
                    'description': description,
                    'amount': float(amount)
                }
                self.data[self.data_key].append(new_expense)
            
            save_data(self.data)
            self.refresh_table()
            dlg.accept()

        save_btn.clicked.connect(on_save)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec()

# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KTS Transport Management")
        self.showMaximized()
        self.setStyleSheet("background-color: #f0f8ff;")

        self.data = load_data()

        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        self.home_page = HomePageWidget()
        self.vehicles_page = VehicleDriverWidget(self.data)
        self.trips_page = TripWidget(self.data)
        self.vehicle_expenses_page = VehicleExpensesWidget(self.data)
        self.office_expenses_page = OfficeExpensesWidget(self.data)
        
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.vehicles_page)
        self.stacked_widget.addWidget(self.trips_page)
        self.stacked_widget.addWidget(self.vehicle_expenses_page)
        self.stacked_widget.addWidget(self.office_expenses_page)

        self.page_map = {
            "home": self.home_page,
            "vehicles": self.vehicles_page,
            "trips": self.trips_page,
            "vehicle_expenses": self.vehicle_expenses_page,
            "office": self.office_expenses_page
        }

        # Connect signals
        self.home_page.navigate.connect(self.navigate_to_page)
        self.vehicles_page.go_back.connect(self.go_home)
        self.trips_page.go_back.connect(self.go_home)
        self.vehicle_expenses_page.go_back.connect(self.go_home)
        self.office_expenses_page.go_back.connect(self.go_home)

        self.stacked_widget.setCurrentWidget(self.home_page)

    def navigate_to_page(self, page_id):
        widget = self.page_map.get(page_id)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)
            if hasattr(widget, 'refresh_table'):
                widget.refresh_table()
            elif hasattr(widget, 'refresh_grid'):
                widget.refresh_grid()

    def go_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
