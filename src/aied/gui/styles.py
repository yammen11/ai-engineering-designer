APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #0b1220;
    color: #e5e7eb;
    font-family: "Segoe UI";
    font-size: 10.5pt;
}
QFrame#Card {
    background: #111827;
    border: 1px solid #243244;
    border-radius: 14px;
}
QLabel#Title {
    font-size: 22pt;
    font-weight: 700;
    color: #f8fafc;
}
QLabel#Subtitle {
    color: #94a3b8;
    font-size: 10pt;
}
QLabel#SectionTitle {
    font-size: 12pt;
    font-weight: 700;
    color: #f1f5f9;
}
QLineEdit, QTextEdit {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 9px;
    padding: 8px;
    color: #f8fafc;
    selection-background-color: #2563eb;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #3b82f6;
}
QPushButton {
    background: #172033;
    border: 1px solid #334155;
    border-radius: 9px;
    padding: 9px 13px;
    color: #f8fafc;
    font-weight: 600;
}
QPushButton:hover {
    background: #22304a;
    border: 1px solid #475569;
}
QPushButton#PrimaryButton {
    background: #2563eb;
    border: 1px solid #3b82f6;
    padding: 11px 18px;
    font-size: 11pt;
}
QPushButton#PrimaryButton:hover {
    background: #1d4ed8;
}
QPushButton:disabled {
    background: #1f2937;
    color: #64748b;
    border-color: #334155;
}
QLabel#PathLabel {
    color: #94a3b8;
    background: #0f172a;
    border: 1px solid #243244;
    border-radius: 8px;
    padding: 7px;
}
QLabel#StatusGood { color: #86efac; }
QLabel#StatusBusy { color: #fbbf24; }
QLabel#StatusBad { color: #fca5a5; }
QSplitter::handle {
    background: #1e293b;
    width: 3px;
}
"""
