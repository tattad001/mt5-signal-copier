from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QPushButton, QLabel, QLineEdit, QComboBox, 
                            QDoubleSpinBox, QTextEdit)
from PyQt5.QtCore import QThread, pyqtSignal

class SignalCopierGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telegram to MT5 Signal Copier")
        self.setGeometry(100, 100, 600, 400)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Connection Status
        self.status_label = QLabel("Status: Disconnected")
        layout.addWidget(self.status_label)
        
        # Lot Size Control
        self.lot_size_input = QDoubleSpinBox()
        self.lot_size_input.setRange(0.01, 100.0)
        self.lot_size_input.setValue(0.1)
        self.lot_size_input.setSingleStep(0.01)
        layout.addWidget(QLabel("Lot Size:"))
        layout.addWidget(self.lot_size_input)
        
        # Telegram Channels
        self.channel_input = QLineEdit()
        layout.addWidget(QLabel("Telegram Channels (comma separated):"))
        layout.addWidget(self.channel_input)
        
        # Broker Symbols
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(['XAUUSDz', 'USTECz', 'US30z'])
        layout.addWidget(QLabel("Broker Symbol:"))
        layout.addWidget(self.symbol_combo)
        
        # Start/Stop Button
        self.start_button = QPushButton("Start Copier")
        self.start_button.clicked.connect(self.toggle_copier)
        layout.addWidget(self.start_button)
        
        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(QLabel("Activity Log:"))
        layout.addWidget(self.log_display)
        
        central_widget.setLayout(layout)
        
        # Worker Thread
        self.worker_thread = None
        self.is_running = False
    
    def toggle_copier(self):
        if self.is_running:
            self.stop_copier()
        else:
            self.start_copier()
    
    def start_copier(self):
        if not self.worker_thread:
            self.worker_thread = CopierThread(
                channels=self.channel_input.text().split(','),
                lot_size=self.lot_size_input.value(),
                symbol=self.symbol_combo.currentText()
            )
            self.worker_thread.log_signal.connect(self.update_log)
            self.worker_thread.status_signal.connect(self.update_status)
            self.worker_thread.start()
            self.is_running = True
            self.start_button.setText("Stop Copier")
    
    def stop_copier(self):
        if self.worker_thread:
            self.worker_thread.stop()
            self.worker_thread = None
            self.is_running = False
            self.start_button.setText("Start Copier")
    
    def update_log(self, message):
        self.log_display.append(message)
    
    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

class CopierThread(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    
    def __init__(self, channels, lot_size, symbol):
        super().__init__()
        self.channels = channels
        self.lot_size = lot_size
        self.symbol = symbol
        self._running = True
    
    def run(self):
        self.status_signal.emit("Connecting...")
        # Initialize your TelegramMonitor and TradeExecutor here
        # Set up the main loop with error handling
    
    def stop(self):
        self._running = False
        self.status_signal.emit("Stopping...")