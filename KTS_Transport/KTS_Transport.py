import sys
import os
import json
import csv
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QDateEdit, QDialog, QFormLayout, QMessageBox, QComboBox,
    QStackedWidget, QFrame, QSizePolicy, QScrollArea, QGridLayout,
    QGroupBox, QFileDialog, QHeaderView
)
from PySide6.QtGui import QFont, QPixmap, QImageReader
from PySide6.QtCore import Qt, QDate, QTimer

# A simple style sheet for the entire application
STYLE_SHEET = """
QMainWindow, QWidget, QDialog {
    background-color: #f0f5fa;
    color: #1a237e;
    font-family: Arial, sans-serif;
    font-size: 14px;
}
QLabel {
    color: #1a237e;
    font-weight: 600;
}
QLineEdit, QDateEdit, QComboBox, QTableWidget {
    background-color: #ffffff;
    border: 2px solid #1a237e;
    border-radius: 5px;
    padding: 4px 8px;
    color: #1a237e;
}
QPushButton {
    background-color: #1a237e;
    color: #ffffff;
    border-radius: 6px;
    font-weight: bold;
    min-width: 75px;
    min-height: 32px;
}
QPushButton:hover {
    background-color: #3f51b5;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #d8ecff;
    padding: 6px;
    border: 1px solid #1a237e;
    font-weight: bold;
}
QFrame#NavigationFrame {
    background-color: #d4e7f6;
    border-radius: 12px;
}
QFrame#CardFrame {
    background-color: #e9f2ff;
    border-radius: 12px;
}
QFrame#CardFrame:hover {
    background-color: #d4ecff;
}
QGroupBox {
    border: 1px solid #1a237e;
    border-radius: 8px;
    margin-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
    background-color: #f0f5fa;
    color: #1a237e;
}
"""

# --- Data Management (Simple JSON based persistence) ---

def load_data(filename):
    """Loads data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, filename):
    """Saves data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# --- Main Application Window & Navigation ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KTS Transport")
        self.showMaximized()
        self.setStyleSheet(STYLE_SHEET)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.create_pages()
        self.setup_navigation()

    def create_pages(self):
        self.home_page = HomePage(self.navigate)
        self.vehicle_driver_page = VehicleDriverPage()
        self.trip_page = TripPage()
        self.office_page = OfficeDetailsPage()
        self.expenses_page = VehicleExpensesPage()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.vehicle_driver_page)
        self.stacked_widget.addWidget(self.trip_page)
        self.stacked_widget.addWidget(self.office_page)
        self.stacked_widget.addWidget(self.expenses_page)

    def setup_navigation(self):
        self.home_page.navigate_signals['vehicle_driver'].connect(lambda: self.navigate('VehicleDriver'))
        self.home_page.navigate_signals['trip_report'].connect(lambda: self.navigate('Trip'))
        self.home_page.navigate_signals['office_details'].connect(lambda: self.navigate('OfficeDetails'))
        self.home_page.navigate_signals['vehicle_expenses'].connect(lambda: self.navigate('VehicleExpenses'))

    def navigate(self, page_name):
        pages = {
            'Home': self.home_page,
            'VehicleDriver': self.vehicle_driver_page,
            'Trip': self.trip_page,
            'OfficeDetails': self.office_page,
            'VehicleExpenses': self.expenses_page
        }
        if page_name in pages:
            self.stacked_widget.setCurrentWidget(pages[page_name])

# --- 1. Homepage ---
# Rebuilt from homepage.py
class HomePage(QWidget):
    navigate_signals = {
        'vehicle_driver': Qt.Signal(),
        'trip_report': Qt.Signal(),
        'office_details': Qt.Signal(),
        'vehicle_expenses': Qt.Signal()
    }

    def __init__(self, navigate_callback):
        super().__init__()
        self.navigate_callback = navigate_callback
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(40)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #e9f7ff; border-radius: 12px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 10, 30, 10)
        header_layout.setSpacing(20)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Truck image - Placeholder, user needs to add an image.
        # Please place a file named `truck_image.png` in the `assets` folder.
        truck_image = QPixmap("assets/truck_image.png")
        if not truck_image.isNull():
            lbl_image = QLabel()
            lbl_image.setPixmap(truck_image.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
            header_layout.addWidget(lbl_image)

        lbl_header = QLabel("KTS Transport Management System")
        lbl_header.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        lbl_header.setStyleSheet("color: #003366;")
        header_layout.addWidget(lbl_header)
        main_layout.addWidget(header_frame)

        # Navigation Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Navigation Cards
        self.add_card(grid_layout, 0, 0, "Vehicle & Driver", "Manage vehicle and driver information.", self.navigate_callback, "VehicleDriver")
        self.add_card(grid_layout, 0, 1, "Trip Report", "Track and manage trip details.", self.navigate_callback, "Trip")
        self.add_card(grid_layout, 1, 0, "Office Details", "Manage office expenses and financial records.", self.navigate_callback, "OfficeDetails")
        self.add_card(grid_layout, 1, 1, "Vehicle Expenses", "Record and view all vehicle expenses.", self.navigate_callback, "VehicleExpenses")

        main_layout.addLayout(grid_layout)
        main_layout.addStretch(1)

    def add_card(self, layout, row, col, title, desc, nav_callback, nav_target):
        frame = QFrame()
        frame.setObjectName("CardFrame")
        frame.setStyleSheet("background-color: #e9f2ff; border-radius: 12px;")
        frame.setFixedSize(300, 180)
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.setSpacing(10)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #003366;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(lbl_title)

        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Arial", 12))
        lbl_desc.setStyleSheet("color: #444444;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.addWidget(lbl_desc)

        frame.mousePressEvent = lambda event: nav_callback(nav_target)
        layout.addWidget(frame, row, col)

# --- 2. Vehicle & Driver Management ---
# Rebuilt from vehicle and driver.py
class VehicleDriverPage(QWidget):
    def __init__(self):
        super().__init__()
        self.vehicles_data = load_data("vehicles.json")
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.refresh_grid()

    def setup_ui(self):
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Manage Vehicles & Drivers"))
        add_vehicle_btn = QPushButton("Add New Vehicle")
        add_vehicle_btn.clicked.connect(self.add_vehicle)
        header_layout.addStretch(1)
        header_layout.addWidget(add_vehicle_btn)
        self.main_layout.addLayout(header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.vehicle_grid_layout = QGridLayout(self.grid_widget)
        self.vehicle_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.scroll_area.setWidget(self.grid_widget)
        self.main_layout.addWidget(self.scroll_area)

    def refresh_grid(self):
        for i in reversed(range(self.vehicle_grid_layout.count())):
            widget_to_remove = self.vehicle_grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        vehicles = list(self.vehicles_data.keys())
        for i, vehicle_name in enumerate(vehicles):
            row = i // 2
            col = i % 2
            vehicle_card = self.create_vehicle_card(vehicle_name, self.vehicles_data[vehicle_name])
            self.vehicle_grid_layout.addWidget(vehicle_card, row, col)

    def create_vehicle_card(self, name, data):
        frame = QFrame()
        frame.setObjectName("CardFrame")
        frame.setFixedSize(300, 200)
        vbox = QVBoxLayout(frame)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.setSpacing(10)

        lbl_name = QLabel(name)
        lbl_name.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        vbox.addWidget(lbl_name)

        lbl_driver = QLabel(f"Driver: {data.get('driver_name', 'N/A')}")
        lbl_driver.setFont(QFont("Arial", 12))
        vbox.addWidget(lbl_driver)

        lbl_loan_rem = QLabel(f"Loan Remaining: ₹{data.get('loan_remaining', 'N/A')}")
        lbl_loan_rem.setFont(QFont("Arial", 12))
        vbox.addWidget(lbl_loan_rem)

        edit_btn = QPushButton("Edit Details")
        edit_btn.clicked.connect(lambda: self.edit_vehicle(name))
        vbox.addWidget(edit_btn)

        return frame

    def add_vehicle(self):
        dialog = VehicleDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_vehicle_name = dialog.name_edit.text().strip()
            if new_vehicle_name:
                self.vehicles_data[new_vehicle_name] = {}
                save_data(self.vehicles_data, "vehicles.json")
                self.refresh_grid()
            else:
                QMessageBox.warning(self, "Invalid Name", "Vehicle name cannot be empty.")

    def edit_vehicle(self, vehicle_name):
        dialog = VehicleEditDialog(self, vehicle_name, self.vehicles_data[vehicle_name])
        if dialog.exec() == QDialog.Accepted:
            self.vehicles_data[vehicle_name] = dialog.details_data
            save_data(self.vehicles_data, "vehicles.json")
            QMessageBox.information(self, "Saved", "Details saved successfully.")
            self.refresh_grid()

class VehicleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Vehicle")
        layout = QVBoxLayout(self)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter vehicle name (e.g., Truck 1234)")
        layout.addWidget(self.name_edit)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

class VehicleEditDialog(QDialog):
    def __init__(self, parent, vehicle_name, details_data):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Details for {vehicle_name}")
        self.details_data = details_data
        layout = QFormLayout(self)

        self.driver_name_edit = QLineEdit(self.details_data.get('driver_name', ''))
        self.driver_contact_edit = QLineEdit(self.details_data.get('driver_contact', ''))
        self.loan_total_edit = QLineEdit(self.details_data.get('loan_total', ''))
        self.loan_paid_edit = QLineEdit(self.details_data.get('loan_paid', ''))
        self.loan_remaining_label = QLabel(self.details_data.get('loan_remaining', 'N/A'))

        layout.addRow("Driver Name:", self.driver_name_edit)
        layout.addRow("Driver Contact:", self.driver_contact_edit)
        layout.addRow("Total Loan:", self.loan_total_edit)
        layout.addRow("Paid Loan:", self.loan_paid_edit)
        layout.addRow("Loan Remaining:", self.loan_remaining_label)

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_and_accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def save_and_accept(self):
        try:
            total = float(self.loan_total_edit.text() or 0)
            paid = float(self.loan_paid_edit.text() or 0)
            remaining = total - paid
            self.loan_remaining_label.setText(f"{remaining:.2f}")
            self.details_data['loan_remaining'] = f"{remaining:.2f}"
            self.details_data['driver_name'] = self.driver_name_edit.text()
            self.details_data['driver_contact'] = self.driver_contact_edit.text()
            self.details_data['loan_total'] = self.loan_total_edit.text()
            self.details_data['loan_paid'] = self.loan_paid_edit.text()
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for loan amounts.")

# --- 3. Trip Report ---
# Rebuilt from TRIP.py (tkinter) to PyQt6
class TripPage(QWidget):
    def __init__(self):
        super().__init__()
        self.records = load_data("trip_records.json").get("trips", [])
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Top Bar
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #d8ecff; border-radius: 8px; padding: 10px;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.add_trip_btn = QPushButton("Add New Trip")
        self.add_trip_btn.clicked.connect(self.add_trip)
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        self.import_btn = QPushButton("Import from CSV")
        self.import_btn.clicked.connect(self.import_from_csv)
        self.delete_all_btn = QPushButton("Delete All Trips")
        self.delete_all_btn.clicked.connect(self.delete_all)

        top_layout.addWidget(self.add_trip_btn)
        top_layout.addWidget(self.export_btn)
        top_layout.addWidget(self.import_btn)
        top_layout.addWidget(self.delete_all_btn)
        main_layout.addWidget(top_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Vehicle No", "Starting Location", "Destination", "Distance (km)", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

    def refresh_table(self):
        self.table.setRowCount(len(self.records))
        for i, record in enumerate(self.records):
            for j, value in enumerate(record[:-1]):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

            # Actions column with edit/delete buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, r=record: self.edit_trip(r))

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, r=record: self.delete_trip(r))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)

            self.table.setCellWidget(i, 5, actions_widget)

    def add_trip(self):
        dialog = TripDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_record = [
                dialog.date_edit.date().toString("yyyy-MM-dd"),
                dialog.vehicle_no_edit.text(),
                dialog.start_loc_edit.text(),
                dialog.dest_loc_edit.text(),
                dialog.distance_edit.text(),
                {} # placeholder for details
            ]
            self.records.append(new_record)
            save_data({"trips": self.records}, "trip_records.json")
            self.refresh_table()

    def edit_trip(self, record):
        dialog = TripDialog(self, record)
        if dialog.exec() == QDialog.Accepted:
            record[0] = dialog.date_edit.date().toString("yyyy-MM-dd")
            record[1] = dialog.vehicle_no_edit.text()
            record[2] = dialog.start_loc_edit.text()
            record[3] = dialog.dest_loc_edit.text()
            record[4] = dialog.distance_edit.text()
            save_data({"trips": self.records}, "trip_records.json")
            self.refresh_table()

    def delete_trip(self, record):
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this trip?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.records.remove(record)
            save_data({"trips": self.records}, "trip_records.json")
            self.refresh_table()

    def delete_all(self):
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete all trip records?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.records = []
            save_data({"trips": self.records}, "trip_records.json")
            self.refresh_table()

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "trips.csv", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Vehicle No", "Starting Location", "Destination", "Distance (km)"])
                for record in self.records:
                    writer.writerow(record[:-1])
            QMessageBox.information(self, "Export Successful", f"Trip data exported to {file_path}")

    def import_from_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                new_records = []
                for row in reader:
                    if len(row) == 5:
                        row.append({})
                        new_records.append(row)
            self.records.extend(new_records)
            save_data({"trips": self.records}, "trip_records.json")
            self.refresh_table()
            QMessageBox.information(self, "Import Successful", f"{len(new_records)} records imported from {file_path}")

class TripDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Trip")
        layout = QFormLayout(self)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.vehicle_no_edit = QLineEdit()
        self.start_loc_edit = QLineEdit()
        self.dest_loc_edit = QLineEdit()
        self.distance_edit = QLineEdit()

        if record:
            self.date_edit.setDate(QDate.fromString(record[0], "yyyy-MM-dd"))
            self.vehicle_no_edit.setText(record[1])
            self.start_loc_edit.setText(record[2])
            self.dest_loc_edit.setText(record[3])
            self.distance_edit.setText(record[4])

        layout.addRow("Date:", self.date_edit)
        layout.addRow("Vehicle No:", self.vehicle_no_edit)
        layout.addRow("Starting Location:", self.start_loc_edit)
        layout.addRow("Destination:", self.dest_loc_edit)
        layout.addRow("Distance (km):", self.distance_edit)

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

# --- 4. Office Details ---
# Rebuilt from office details.py
class OfficeDetailsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.records_data = load_data("office_records.json")
        self.monthly_records = []
        self.setup_ui()
        self.refresh_records()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.total_frame = QFrame()
        total_layout = QHBoxLayout(self.total_frame)
        self.txt_rent = QLineEdit()
        self.txt_bill = QLineEdit()
        self.txt_salary = QLineEdit()
        self.txt_other = QLineEdit()
        self.txt_total = QLineEdit()

        total_layout.addWidget(QLabel("Rent Total:"))
        total_layout.addWidget(self.txt_rent)
        total_layout.addWidget(QLabel("Bill Total:"))
        total_layout.addWidget(self.txt_bill)
        total_layout.addWidget(QLabel("Salary Total:"))
        total_layout.addWidget(self.txt_salary)
        total_layout.addWidget(QLabel("Other Total:"))
        total_layout.addWidget(self.txt_other)
        total_layout.addWidget(QLabel("Grand Total:"))
        total_layout.addWidget(self.txt_total)
        main_layout.addWidget(self.total_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.records_widget = QWidget()
        self.records_layout = QVBoxLayout(self.records_widget)
        self.scroll_area.setWidget(self.records_widget)
        main_layout.addWidget(self.scroll_area)

        self.add_month_btn = QPushButton("Add New Month")
        self.add_month_btn.clicked.connect(self.add_new_month)
        self.save_all_btn = QPushButton("Save All Records")
        self.save_all_btn.clicked.connect(self.confirm_save_all)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_month_btn)
        button_layout.addWidget(self.save_all_btn)
        main_layout.addLayout(button_layout)

    def refresh_records(self):
        for i in reversed(range(self.records_layout.count())):
            widget_to_remove = self.records_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        self.monthly_records = []
        for month, data in self.records_data.items():
            monthly_group = MonthlyRecordGroup(month, data)
            self.monthly_records.append(monthly_group)
            self.records_layout.addWidget(monthly_group)

        self.update_totals()

    def update_totals(self):
        total_rent, total_bill, total_salary, total_other = 0, 0, 0, 0
        for group in self.monthly_records:
            data = group.data
            total_rent += float(data.get('rent', 0) or 0)
            total_bill += float(data.get('bill', 0) or 0)
            total_salary += float(data.get('salary', 0) or 0)
            total_other += float(data.get('other', 0) or 0)

        self.txt_rent.setText(f"₹{total_rent:.2f}")
        self.txt_bill.setText(f"₹{total_bill:.2f}")
        self.txt_salary.setText(f"₹{total_salary:.2f}")
        self.txt_other.setText(f"₹{total_other:.2f}")
        self.txt_total.setText(f"₹{total_rent + total_bill + total_salary + total_other:.2f}")

    def add_new_month(self):
        month_name = QDate.currentDate().toString("yyyy-MM")
        if month_name not in self.records_data:
            self.records_data[month_name] = {
                "rent": "0", "bill": "0", "salary": "0", "other": "0"
            }
            save_data(self.records_data, "office_records.json")
            self.refresh_records()
        else:
            QMessageBox.warning(self, "Exists", "This month's record already exists.")

    def confirm_save_all(self):
        reply = QMessageBox.question(self, "Confirm Save", "Are you sure you want to save all records?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for group in self.monthly_records:
                month = group.month
                self.records_data[month] = group.data
            save_data(self.records_data, "office_records.json")
            self.update_totals()
            QMessageBox.information(self, "Saved", "All records have been saved.")

class MonthlyRecordGroup(QGroupBox):
    def __init__(self, month, data, parent=None):
        super().__init__(month, parent)
        self.month = month
        self.data = data
        self.setStyleSheet("QGroupBox { border: 2px solid #1a237e; margin-top: 20px; font-weight: bold; } QGroupBox::title { subcontrol-origin: top; subcontrol-position: top center; padding: 0 5px; }")

        self.layout = QFormLayout(self)
        self.rent_edit = QLineEdit(self.data.get('rent', ''))
        self.bill_edit = QLineEdit(self.data.get('bill', ''))
        self.salary_edit = QLineEdit(self.data.get('salary', ''))
        self.other_edit = QLineEdit(self.data.get('other', ''))

        self.layout.addRow("Rent:", self.rent_edit)
        self.layout.addRow("Bill:", self.bill_edit)
        self.layout.addRow("Salary:", self.salary_edit)
        self.layout.addRow("Other:", self.other_edit)

# --- 5. Vehicle Expenses ---
# Rebuilt from vehicle expenses final.py
class VehicleExpensesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.records = load_data("expenses_records.json").get("expenses", [])
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Vehicle:"))
        self.filter_vehicle = QLineEdit()
        filter_layout.addWidget(self.filter_vehicle)

        filter_layout.addWidget(QLabel("Date Filter:"))
        self.date_filter_combo = QComboBox()
        self.date_filter_combo.addItems(["All", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 12 Months"])
        self.date_filter_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_filter_combo)

        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self.apply_filters)
        reset_btn = QPushButton("Reset Filters")
        reset_btn.clicked.connect(self.reset_filters)

        filter_layout.addWidget(apply_btn)
        filter_layout.addWidget(reset_btn)
        main_layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Vehicle", "Expense Type", "Amount (₹)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        add_btn = QPushButton("Add New Expense")
        add_btn.clicked.connect(self.add_expense)
        main_layout.addWidget(add_btn)

    def refresh_table(self, filtered_records=None):
        records_to_display = filtered_records if filtered_records is not None else self.records
        self.table.setRowCount(len(records_to_display))
        for i, record in enumerate(records_to_display):
            for j, value in enumerate(record):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def add_expense(self):
        dialog = ExpenseDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_record = [
                dialog.date_edit.date().toString("yyyy-MM-dd"),
                dialog.vehicle_edit.text(),
                dialog.type_combo.currentText(),
                dialog.amount_edit.text()
            ]
            self.records.append(new_record)
            save_data({"expenses": self.records}, "expenses_records.json")
            self.refresh_table()

    def apply_filters(self):
        vehicle_filter = self.filter_vehicle.text().strip().lower()
        date_filter_type = self.date_filter_combo.currentText()

        filtered = []
        date_from, date_to = None, QDate.currentDate()

        if date_filter_type == "Last 1 Month":
            date_from = QDate.currentDate().addMonths(-1)
        elif date_filter_type == "Last 3 Months":
            date_from = QDate.currentDate().addMonths(-3)
        elif date_filter_type == "Last 6 Months":
            date_from = QDate.currentDate().addMonths(-6)
        elif date_filter_type == "Last 12 Months":
            date_from = QDate.currentDate().addYears(-1)
        else: # "All"
            date_from = None
            date_to = None

        for record in self.records:
            vehicle_match = not vehicle_filter or (len(record) > 1 and record[1].lower() == vehicle_filter)

            record_date = QDate.fromString(record[0], "yyyy-MM-dd") if record[0] else None
            date_match = True
            if date_from and record_date:
                date_match = date_from <= record_date <= date_to

            if vehicle_match and date_match:
                filtered.append(record)

        self.refresh_table(filtered)

    def reset_filters(self):
        self.filter_vehicle.clear()
        self.date_filter_combo.setCurrentIndex(0)
        self.refresh_table()

class ExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Expense")
        layout = QFormLayout(self)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.vehicle_edit = QLineEdit()
        self.amount_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Fuel", "Maintenance", "Driver Salary", "Toll", "RTO Tax", "Other"])

        layout.addRow("Date:", self.date_edit)
        layout.addRow("Vehicle No:", self.vehicle_edit)
        layout.addRow("Expense Type:", self.type_combo)
        layout.addRow("Amount (₹):", self.amount_edit)

        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())