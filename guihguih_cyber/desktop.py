"""PySide6 desktop interface for the implemented local M1/M2 subset."""

import sys
import threading
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QListWidget, QStackedWidget)

from .ai import MODEL_STATUS
from .monitor import FolderMonitor
from .quarantine import Quarantine
from .scanner import scan_path
from .storage import HistoryStore


class Signals(QObject):
    completed = Signal(dict)
    monitor_event = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GuihGuih Cyber")
        self.resize(1180, 760)
        self.store = HistoryStore()
        self.quarantine = Quarantine(self.store)
        self.signals = Signals()
        self.signals.completed.connect(self.show_report)
        self.signals.monitor_event.connect(self.monitor_event)
        self.cancel = threading.Event()
        self.monitor = FolderMonitor(lambda p: self.signals.monitor_event.emit(str(p)))
        self._build()
        self.refresh_history()
        self.refresh_quarantine()

    def _build(self):
        central = QWidget(); outer = QHBoxLayout(central); outer.setContentsMargins(0, 0, 0, 0)
        nav = QListWidget(); nav.setFixedWidth(220)
        for label in ["Visão geral", "Verificação", "Monitoramento", "Quarentena", "Histórico", "GuihGuih AI", "Rede", "Ransomware", "Configurações"]: nav.addItem(label)
        nav.setCurrentRow(0)
        self.stack = QStackedWidget()
        nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        outer.addWidget(nav)
        outer.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self.dashboard = QWidget(); lay = QVBoxLayout(self.dashboard); lay.setContentsMargins(32, 28, 32, 24)
        lay.addWidget(self._title("Painel de proteção", "Estado real dos recursos locais"))
        state = self._card("SCANNER LOCAL", "Disponível · análise manual", "Regras simples + SHA-256 · arquivos nunca são executados")
        lay.addWidget(state)
        row = QHBoxLayout(); self.quick_button = QPushButton("Verificação rápida"); self.quick_button.clicked.connect(lambda: self.choose_scan(folder=True)); row.addWidget(self.quick_button)
        full = QPushButton("Verificação completa"); full.clicked.connect(self.scan_home); row.addWidget(full)
        custom = QPushButton("Personalizada…"); custom.clicked.connect(lambda: self.choose_scan(folder=False)); row.addWidget(custom)
        cancel = QPushButton("Cancelar"); cancel.clicked.connect(self.cancel.set); row.addWidget(cancel)
        lay.addLayout(row)
        self.summary = QLabel("Nenhuma verificação nesta sessão"); self.summary.setObjectName("muted"); lay.addWidget(self.summary)
        self.results = QTableWidget(0, 4); self.results.setHorizontalHeaderLabels(["Estado", "Arquivo", "SHA-256", "Detecção / motivo"]); self.results.horizontalHeader().setStretchLastSection(True); self.results.horizontalHeader().setSectionResizeMode(1, self.results.horizontalHeader().ResizeMode.Stretch); lay.addWidget(self.results, 1)
        lay.addWidget(QLabel("Sem achados significa apenas que as regras locais não corresponderam; não prova que o arquivo é seguro."))
        self.stack.addWidget(self.dashboard)

        self.monitor_page = QWidget(); ml = QVBoxLayout(self.monitor_page); ml.setContentsMargins(32,28,32,24); ml.addWidget(self._title("Monitoramento de pastas", "Somente caminhos adicionados explicitamente"))
        controls = QHBoxLayout(); add = QPushButton("Adicionar pasta"); add.clicked.connect(self.add_monitor_folder); controls.addWidget(add); start = QPushButton("Iniciar"); start.clicked.connect(self.start_monitor); controls.addWidget(start); stop = QPushButton("Parar"); stop.clicked.connect(self.monitor.stop); controls.addWidget(stop); ml.addLayout(controls)
        self.mon_status = QLabel("Desligado"); ml.addWidget(self.mon_status); self.mon_events = QListWidget(); ml.addWidget(self.mon_events, 1)
        self.stack.addWidget(self.monitor_page)

        self.quarantine_page = QWidget(); ql = QVBoxLayout(self.quarantine_page); ql.setContentsMargins(32,28,32,24); ql.addWidget(self._title("Quarentena reversível", "Armazena cópia protegida; não apaga a origem"))
        quarantine_controls = QHBoxLayout(); qadd = QPushButton("Adicionar cópia à quarentena…"); qadd.clicked.connect(self.quarantine_file); quarantine_controls.addWidget(qadd); restore = QPushButton("Restaurar selecionado…"); restore.clicked.connect(self.restore_selected); quarantine_controls.addWidget(restore); ql.addLayout(quarantine_controls)
        self.qtable = QTableWidget(0, 3); self.qtable.setHorizontalHeaderLabels(["ID", "Origem", "SHA-256"]); self.qtable.horizontalHeader().setStretchLastSection(True); self.qtable.horizontalHeader().setSectionResizeMode(1, self.qtable.horizontalHeader().ResizeMode.Stretch); ql.addWidget(self.qtable,1); self.stack.addWidget(self.quarantine_page)

        for title, detail in [("Histórico", "Sessões SQLite locais"), ("GuihGuih AI", "Experimental · sem modelo treinado"), ("Rede", "Não implementado"), ("Ransomware", "Não implementado"), ("Configurações", "Configurações avançadas ainda não implementadas")]:
            page = QWidget(); pl = QVBoxLayout(page); pl.setContentsMargins(32,28,32,24); pl.addWidget(self._title(title, detail))
            if title == "Histórico":
                self.history = QTableWidget(0,5); self.history.setHorizontalHeaderLabels(["Sessão", "Data UTC", "Caminho", "Arquivos", "Achados"]); self.history.horizontalHeader().setStretchLastSection(True); self.history.horizontalHeader().setSectionResizeMode(2, self.history.horizontalHeader().ResizeMode.Stretch); pl.addWidget(self.history,1)
            else:
                note = QLabel(self._feature_note(title)); note.setWordWrap(True); note.setObjectName("muted"); pl.addWidget(note)
            pl.addStretch(); self.stack.addWidget(page)
        self.setStyleSheet(STYLE)

    def _title(self, title, subtitle):
        box = QWidget(); l = QVBoxLayout(box); l.setContentsMargins(0,0,0,12); h = QLabel(title); h.setObjectName("title"); s = QLabel(subtitle); s.setObjectName("muted"); l.addWidget(h); l.addWidget(s); return box

    def _card(self, kicker, title, detail):
        box = QFrame(); box.setObjectName("card"); l = QVBoxLayout(box); a=QLabel(kicker); a.setObjectName("accent"); b=QLabel(title); b.setObjectName("cardTitle"); c=QLabel(detail); c.setObjectName("muted"); l.addWidget(a); l.addWidget(b); l.addWidget(c); return box

    def _feature_note(self, title):
        notes = {"GuihGuih AI": f"Estado: {MODEL_STATUS}. Extração estática experimental disponível; nenhum modelo foi treinado ou validado, então não há classificação de IA.", "Rede": "Coleta de eventos de serviços autorizados, reputação e bloqueio não implementados.", "Ransomware": "Detecção comportamental e backups versionados não implementados.", "Configurações": "Preferências de retenção e limites ainda não disponíveis."}
        return notes.get(title, "")

    def choose_scan(self, folder):
        path = QFileDialog.getExistingDirectory(self, "Selecionar pasta") if folder else QFileDialog.getOpenFileName(self, "Selecionar arquivo")[0]
        if path: self.start_scan(path)

    def scan_home(self):
        self.start_scan(str(Path.home()))

    def start_scan(self, path):
        self.cancel.clear(); self.summary.setText("Verificando…")
        threading.Thread(target=self._scan_worker, args=(path,), daemon=True).start()

    def _scan_worker(self, path):
        report = scan_path(path, self.cancel)
        report["scan_id"] = self.store.save_scan(report)
        self.signals.completed.emit(report)

    def show_report(self, report):
        self.results.setRowCount(0)
        for result in report["files"]:
            row=self.results.rowCount(); self.results.insertRow(row)
            reason="; ".join(f"{f['rule_id']}: {f['explanation']}" for f in result["findings"])
            for col, value in enumerate([result["status"], result["path"], result["sha256"] or "—", reason or result["error"] or "Nenhuma regra acionada"]): self.results.setItem(row,col,QTableWidgetItem(str(value)))
        self.summary.setText(f"Varredura #{report['scan_id']} · {report['files_scanned']} arquivos · {report['finding_count']} achados · {report['error_count']} erros" + (" · cancelada" if report["cancelled"] else ""))
        self.refresh_history()

    def refresh_history(self):
        if not hasattr(self, "history"): return
        rows=self.store.recent_scans(100); self.history.setRowCount(0)
        for item in rows:
            row=self.history.rowCount(); self.history.insertRow(row)
            for col, key in enumerate(["id","started_at","root_path","files_scanned","findings"]): self.history.setItem(row,col,QTableWidgetItem(str(item[key])))

    def add_monitor_folder(self):
        path=QFileDialog.getExistingDirectory(self,"Adicionar pasta monitorada")
        if path:
            try: self.monitor.add_folder(path); self.mon_events.addItem(f"Pasta permitida: {path}")
            except (OSError, ValueError) as exc: QMessageBox.warning(self,"Pasta inválida",str(exc))

    def start_monitor(self):
        try: self.monitor.start(); self.mon_status.setText("Ativo · alterações detectadas por polling local")
        except ValueError as exc: QMessageBox.information(self,"Monitoramento",str(exc))

    def monitor_event(self, path): self.mon_events.addItem(f"Alteração: {path} · considere executar uma verificação")

    def refresh_quarantine(self):
        if not hasattr(self,"qtable"): return
        rows=self.quarantine.items(); self.qtable.setRowCount(0)
        for item in rows:
            row=self.qtable.rowCount(); self.qtable.insertRow(row)
            for col,key in enumerate(["id","original_path","sha256"]): self.qtable.setItem(row,col,QTableWidgetItem(item[key]))

    def quarantine_file(self):
        path=QFileDialog.getOpenFileName(self,"Escolher arquivo para copiar à quarentena")[0]
        if not path: return
        answer=QMessageBox.warning(self,"Confirmar cópia",f"Será criada uma cópia protegida. O arquivo original permanecerá no local.\n\n{path}",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes: return
        try: self.quarantine.quarantine_copy(path,confirmed=True); self.refresh_quarantine()
        except Exception as exc: QMessageBox.critical(self,"Quarentena",str(exc))

    def restore_selected(self):
        row=self.qtable.currentRow()
        if row < 0: return
        item_id=self.qtable.item(row,0).text(); target=QFileDialog.getSaveFileName(self,"Restaurar cópia em novo caminho")[0]
        if not target: return
        answer=QMessageBox.warning(self,"Confirmar restauração",f"Restaurar a cópia para:\n{target}",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes: return
        try: self.quarantine.restore_copy(item_id,target,confirmed=True); QMessageBox.information(self,"Restauração","Cópia restaurada com hash verificado.")
        except Exception as exc: QMessageBox.critical(self,"Restauração",str(exc))

    def closeEvent(self, event):
        self.monitor.stop(); event.accept()


STYLE = """
QWidget { background:#080f18; color:#e8f0f7; font-family:'Segoe UI'; font-size:13px; }
QListWidget { background:#0b1420; border:0; padding:16px 10px; color:#9db0c4; }
QListWidget::item { padding:13px 12px; border-radius:6px; }
QListWidget::item:selected { background:#14283a; color:#78e7b0; }
QLabel#title { font-size:28px; font-weight:700; color:#f0f6fb; }
QLabel#muted { color:#8ca2b7; }
QLabel#accent { color:#78e7b0; font-size:10px; font-weight:700; letter-spacing:2px; }
QFrame#card { background:#101b29; border:1px solid #20364b; border-radius:9px; padding:14px; }
QLabel#cardTitle { font-size:19px; font-weight:700; }
QPushButton { background:#14283a; color:#dce8f2; border:1px solid #284058; border-radius:5px; padding:10px 14px; }
QPushButton:hover { border-color:#78e7b0; }
QHeaderView::section { background:#142235; color:#78e7b0; padding:8px; border:0; }
QTableWidget { background:#0c1622; alternate-background-color:#101d2a; gridline-color:#203044; border:1px solid #203044; }
"""


def main():
    app = QApplication(sys.argv); window = MainWindow(); window.show(); sys.exit(app.exec())


if __name__ == "__main__": main()

