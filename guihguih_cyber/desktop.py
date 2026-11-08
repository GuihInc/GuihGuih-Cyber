"""PySide6 desktop interface for the implemented local M1/M2 subset."""

import sys
import threading
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QListWidget, QStackedWidget, QComboBox, QFormLayout)

from .ai import MODEL_STATUS
from .monitor import FolderMonitor
from .quarantine import Quarantine
from .ransomware import ChangeBurstDetector
from .scanner import scan_path
from .storage import HistoryStore


LOGO_PATH = Path(__file__).with_name("assets") / "logo.png"


class Signals(QObject):
    completed = Signal(dict)
    monitor_event = Signal(str)
    ransomware_alert = Signal(dict)


class MainWindow(QMainWindow):
    def __init__(self, store=None):
        super().__init__()
        self.setWindowTitle("GuihGuih Cyber")
        self.setWindowIcon(QIcon(str(LOGO_PATH)))
        self.resize(1120, 730)
        self.setMinimumSize(870, 625)
        self.store = store if store is not None else HistoryStore()
        self.quarantine = Quarantine(self.store)
        self.signals = Signals()
        self.signals.completed.connect(self.show_report)
        self.signals.monitor_event.connect(self.monitor_event)
        self.signals.ransomware_alert.connect(self.show_ransomware_alert)
        self.cancel = threading.Event()
        self.ransomware_detector = ChangeBurstDetector(
            threshold=self._ransomware_threshold_preference()
        )
        self.monitor = FolderMonitor(
            self._on_monitored_change,
            interval=self._monitor_interval_preference(),
        )
        self._build()
        self.refresh_history()
        self.refresh_quarantine()

    def _build(self):
        central = QWidget()
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(218)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 22, 14, 18)
        brand = QHBoxLayout()
        brand.setSpacing(8)
        brand.addWidget(self._logo(44))
        brand_text = QVBoxLayout()
        name = QLabel("GuihGuih")
        name.setObjectName("brand")
        edition = QLabel("C Y B E R")
        edition.setObjectName("accent")
        brand_text.addWidget(name)
        brand_text.addWidget(edition)
        brand.addLayout(brand_text, 1)
        sidebar_layout.addLayout(brand)
        sidebar_layout.addSpacing(22)
        nav = QListWidget()
        nav.setObjectName("navigation")
        nav.addItems(["Visão geral", "Verificação", "Monitoramento", "Quarentena",
                      "Histórico", "GuihGuih AI", "Rede", "Ransomware", "Configurações"])
        nav.setAccessibleName("Navegação principal")
        nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sidebar_layout.addWidget(nav, 1)
        footer = QLabel("ANÁLISE LOCAL")
        footer.setObjectName("sidebarFooter")
        sidebar_layout.addWidget(footer)
        self.stack = QStackedWidget()
        nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        outer.addWidget(sidebar)
        outer.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        dashboard = QWidget()
        overview = QVBoxLayout(dashboard)
        overview.setContentsMargins(32, 26, 32, 24)
        overview.setSpacing(16)
        overview.addWidget(self._title("Visão geral", "Central de segurança local"))
        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(26, 20, 22, 20)
        hero_text = QVBoxLayout()
        hero_text.setSpacing(10)
        badge = QLabel("●  SCANNER DISPONÍVEL")
        badge.setObjectName("badge")
        hero_text.addWidget(badge, 0, Qt.AlignmentFlag.AlignLeft)
        heading = QLabel("Verificação de arquivos")
        heading.setObjectName("heroTitle")
        hero_text.addWidget(heading)
        description = QLabel("Analise arquivos e pastas com regras locais e SHA-256.")
        description.setObjectName("muted")
        description.setWordWrap(True)
        hero_text.addWidget(description)
        open_scan = QPushButton("Abrir verificação  →")
        open_scan.setObjectName("primary")
        open_scan.setAccessibleName("Abrir página de verificação")
        open_scan.clicked.connect(lambda: nav.setCurrentRow(1))
        hero_text.addWidget(open_scan, 0, Qt.AlignmentFlag.AlignLeft)
        hero_layout.addLayout(hero_text, 1)
        hero_layout.addWidget(self._logo(156), 0, Qt.AlignmentFlag.AlignVCenter)
        overview.addWidget(hero)
        activity = self._card("ATIVIDADE", "Última verificação", "Consulte as sessões completas em Histórico.")
        self.latest_scan = QLabel("Nenhuma verificação registrada.")
        self.latest_scan.setObjectName("muted")
        self.latest_scan.setWordWrap(True)
        activity.layout().insertWidget(2, self.latest_scan)
        overview.addWidget(activity)
        tools_title = QLabel("Ferramentas locais")
        tools_title.setObjectName("cardTitle")
        overview.addWidget(tools_title)
        shortcuts = QHBoxLayout()
        shortcuts.setSpacing(10)
        for index, title, description in (
            (2, "Monitoramento", "Acompanhar pastas"),
            (3, "Quarentena", "Gerenciar cópias"),
            (4, "Histórico", "Consultar verificações"),
        ):
            shortcut = QPushButton(f"{title}\n{description}")
            shortcut.setObjectName("shortcut")
            shortcut.clicked.connect(lambda checked=False, index=index: nav.setCurrentRow(index))
            shortcuts.addWidget(shortcut, 1)
        overview.addLayout(shortcuts)
        overview.addStretch()
        self.stack.addWidget(dashboard)

        scan_page = QWidget()
        lay = QVBoxLayout(scan_page)
        lay.setContentsMargins(32, 26, 32, 24)
        lay.setSpacing(14)
        lay.addWidget(self._title("Verificação", "Selecione um arquivo ou uma pasta para analisar."))
        row = QHBoxLayout(); self.quick_button = QPushButton("Selecionar pasta…"); self.quick_button.clicked.connect(lambda: self.choose_scan(folder=True)); row.addWidget(self.quick_button)
        self.quick_button.setObjectName("primary")
        full = QPushButton("Verificar pasta pessoal"); full.clicked.connect(self.scan_home); row.addWidget(full)
        custom = QPushButton("Selecionar arquivo…"); custom.clicked.connect(lambda: self.choose_scan(folder=False)); row.addWidget(custom)
        cancel = QPushButton("Cancelar"); cancel.clicked.connect(self.cancel.set); row.addWidget(cancel)
        lay.addLayout(row)
        self.summary = QLabel("Nenhuma verificação nesta sessão"); self.summary.setObjectName("muted"); lay.addWidget(self.summary)
        self.results = QTableWidget(0, 4); self.results.setHorizontalHeaderLabels(["Estado", "Arquivo", "SHA-256", "Detecção / motivo"]); self.results.horizontalHeader().setStretchLastSection(True); self.results.horizontalHeader().setSectionResizeMode(1, self.results.horizontalHeader().ResizeMode.Stretch); lay.addWidget(self.results, 1)
        note = QLabel("Sem achados: nenhuma regra local correspondeu aos arquivos analisados.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        lay.addWidget(note)
        self.stack.addWidget(scan_page)

        self.monitor_page = QWidget(); ml = QVBoxLayout(self.monitor_page); ml.setContentsMargins(32,28,32,24); ml.addWidget(self._title("Monitoramento de pastas", "Somente caminhos adicionados explicitamente"))
        controls = QHBoxLayout(); add = QPushButton("Adicionar pasta"); add.clicked.connect(self.add_monitor_folder); controls.addWidget(add); start = QPushButton("Iniciar"); start.clicked.connect(self.start_monitor); controls.addWidget(start); stop = QPushButton("Parar"); stop.clicked.connect(self.stop_monitor); controls.addWidget(stop); ml.addLayout(controls)
        self.mon_status = QLabel("Desligado"); ml.addWidget(self.mon_status); self.mon_events = QListWidget(); ml.addWidget(self.mon_events, 1)
        self.stack.addWidget(self.monitor_page)

        self.quarantine_page = QWidget(); ql = QVBoxLayout(self.quarantine_page); ql.setContentsMargins(32,28,32,24); ql.addWidget(self._title("Quarentena reversível", "Armazena cópia protegida; não apaga a origem"))
        quarantine_controls = QHBoxLayout(); qadd = QPushButton("Adicionar cópia à quarentena…"); qadd.clicked.connect(self.quarantine_file); quarantine_controls.addWidget(qadd); restore = QPushButton("Restaurar selecionado…"); restore.clicked.connect(self.restore_selected); quarantine_controls.addWidget(restore); ql.addLayout(quarantine_controls)
        self.qtable = QTableWidget(0, 3); self.qtable.setHorizontalHeaderLabels(["ID", "Origem", "SHA-256"]); self.qtable.horizontalHeader().setStretchLastSection(True); self.qtable.horizontalHeader().setSectionResizeMode(1, self.qtable.horizontalHeader().ResizeMode.Stretch); ql.addWidget(self.qtable,1); self.stack.addWidget(self.quarantine_page)

        for title, detail in [("Histórico", "Sessões SQLite locais"), ("GuihGuih AI", "Experimental · sem modelo treinado"), ("Rede", "Não implementado")]:
            page = QWidget(); pl = QVBoxLayout(page); pl.setContentsMargins(32,28,32,24); pl.addWidget(self._title(title, detail))
            if title == "Histórico":
                self.history = QTableWidget(0,5); self.history.setHorizontalHeaderLabels(["Sessão", "Data UTC", "Caminho", "Arquivos", "Achados"]); self.history.horizontalHeader().setStretchLastSection(True); self.history.horizontalHeader().setSectionResizeMode(2, self.history.horizontalHeader().ResizeMode.Stretch); pl.addWidget(self.history,1)
            else:
                note = QLabel(self._feature_note(title)); note.setWordWrap(True); note.setObjectName("muted"); note.setProperty("class", "featureNote"); pl.addWidget(note)
            pl.addStretch(); self.stack.addWidget(page)
        self._build_ransomware_page()
        self._build_settings_page()
        nav.setCurrentRow(0)
        self.setStyleSheet(STYLE)

    def _monitor_interval_preference(self):
        raw = self.store.get_preference("monitor_poll_interval", "2.0")
        try:
            interval = float(raw)
        except (TypeError, ValueError):
            return 2.0
        return interval if interval in (1.0, 2.0, 5.0) else 2.0

    def _ransomware_threshold_preference(self):
        raw = self.store.get_preference("ransomware_change_threshold", "20")
        try:
            threshold = int(raw)
        except (TypeError, ValueError):
            return 20
        return threshold if threshold in (10, 20, 50) else 20

    def _build_ransomware_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)
        layout.addWidget(self._title(
            "Monitor de alterações rápidas",
            "Heurística local experimental para pastas que você adicionou ao Monitoramento",
        ))
        status = self._card(
            "ALERTA LOCAL · SEM BLOQUEIO",
            "Detecção de rajadas de alterações",
            "Avisa quando muitos arquivos existentes mudam rapidamente. O monitor usa polling e pode não observar todas as operações.",
        )
        layout.addWidget(status)
        self.ransomware_status = QLabel("Aguardando alterações nas pastas monitoradas.")
        self.ransomware_status.setObjectName("muted")
        self.ransomware_status.setWordWrap(True)
        layout.addWidget(self.ransomware_status)
        self.ransomware_alerts = QListWidget()
        self.ransomware_alerts.setAccessibleName("Alertas locais de alterações rápidas")
        layout.addWidget(self.ransomware_alerts, 1)
        note = QLabel(
            "Para usar: adicione uma pasta e inicie o monitoramento na página Monitoramento. "
            "Este recurso não bloqueia processos, não restaura arquivos e não detecta todos os ataques. "
            "Use o antivírus nativo do sistema em conjunto. Alertas são salvos localmente."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.stack.addWidget(page)
        self.refresh_ransomware_alerts()

    def refresh_ransomware_alerts(self):
        if not hasattr(self, "ransomware_alerts"):
            return
        self.ransomware_alerts.clear()
        for alert in self.store.recent_security_alerts(50):
            self.ransomware_alerts.addItem(self._format_ransomware_alert(alert))

    @staticmethod
    def _format_ransomware_alert(alert):
        timestamp = alert["created_at"].replace("T", " ").split(".")[0]
        return (
            f"{timestamp} UTC · {alert['event_count']} arquivos diferentes em "
            f"{alert['window_seconds']:g} s · {alert['rule_id']}"
        )

    def _on_monitored_change(self, path):
        self.signals.monitor_event.emit(str(path))
        alert = self.ransomware_detector.record_change(str(path))
        if alert:
            alert["rule_id"] = "LOCAL-CHANGE-BURST"
            alert["id"] = self.store.save_security_alert(alert)
            self.signals.ransomware_alert.emit(alert)

    def show_ransomware_alert(self, alert):
        self.ransomware_status.setText(
            f"Alerta: {alert['event_count']} arquivos diferentes alterados em "
            f"{alert['window_seconds']:g} segundos. Revise a atividade."
        )
        self.ransomware_alerts.insertItem(0, self._format_ransomware_alert(alert))

    def _build_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)
        layout.addWidget(self._title("Configurações", "Preferências locais do GuihGuih Cyber"))

        privacy = self._card(
            "PRIVACIDADE",
            "Seus dados ficam neste dispositivo",
            "Histórico e preferências são salvos localmente em SQLite. O app não envia arquivos ou hashes para serviços externos.",
        )
        privacy.setProperty("class", "settingsCard")
        layout.addWidget(privacy)

        monitor_card = QFrame()
        monitor_card.setObjectName("card")
        form = QFormLayout(monitor_card)
        form.setContentsMargins(18, 16, 18, 16)
        form.setHorizontalSpacing(24)
        form.setVerticalSpacing(12)
        heading = QLabel("Frequência do monitoramento")
        heading.setObjectName("cardTitle")
        form.addRow(heading)
        self.monitor_interval = QComboBox()
        self.monitor_interval.addItem("1 segundo · mais frequente", 1.0)
        self.monitor_interval.addItem("2 segundos · equilibrado", 2.0)
        self.monitor_interval.addItem("5 segundos · menor uso de recursos", 5.0)
        active_interval = self._monitor_interval_preference()
        self.monitor_interval.setCurrentIndex(
            next(i for i in range(self.monitor_interval.count()) if self.monitor_interval.itemData(i) == active_interval)
        )
        form.addRow("Verificar pastas autorizadas a cada", self.monitor_interval)
        self.ransomware_threshold = QComboBox()
        self.ransomware_threshold.addItem("10 arquivos diferentes em 10 s · sensível", 10)
        self.ransomware_threshold.addItem("20 arquivos diferentes em 10 s · equilibrado", 20)
        self.ransomware_threshold.addItem("50 arquivos diferentes em 10 s · menos alertas", 50)
        active_threshold = self._ransomware_threshold_preference()
        self.ransomware_threshold.setCurrentIndex(
            next(i for i in range(self.ransomware_threshold.count()) if self.ransomware_threshold.itemData(i) == active_threshold)
        )
        form.addRow("Alertar a partir de", self.ransomware_threshold)
        self.settings_feedback = QLabel("A preferência é salva neste dispositivo e vale para o monitoramento configurado.")
        self.settings_feedback.setObjectName("muted")
        self.settings_feedback.setWordWrap(True)
        form.addRow(self.settings_feedback)
        save = QPushButton("Salvar preferência")
        save.setObjectName("primary")
        save.clicked.connect(self.save_settings)
        form.addRow(save)
        layout.addWidget(monitor_card)

        limitations = self._card(
            "ESTADO REAL",
            "Recursos ainda em desenvolvimento",
            "A GuihGuih AI não tem modelo treinado. Rede e proteção contra ransomware ainda não estão implementadas. Esta tela não ativa proteção em tempo real.",
        )
        layout.addWidget(limitations)
        layout.addStretch()
        self.stack.addWidget(page)

    def save_settings(self):
        interval = float(self.monitor_interval.currentData())
        self.store.set_preference("monitor_poll_interval", str(interval))
        self.monitor.interval = interval
        self.settings_feedback.setText(
            f"Preferências salvas: polling a cada {self.monitor_interval.currentData():g} s; "
            f"alerta a partir de {self.ransomware_threshold.currentData()} alterações por 10 s."
        )
        self.ransomware_detector.threshold = int(self.ransomware_threshold.currentData())
        self.settings_feedback.setStyleSheet("color:#80ffd1;")
        self.store.set_preference("ransomware_change_threshold", str(self.ransomware_detector.threshold))

    def _logo(self, size):
        label = QLabel()
        label.setFixedSize(size, size)
        label.setAccessibleName("Logo oficial do GuihGuih Cyber")
        label.setPixmap(QPixmap(str(LOGO_PATH)).scaled(
            size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        return label

    def _title(self, title, subtitle):
        box = QWidget(); l = QVBoxLayout(box); l.setContentsMargins(0,0,0,12); h = QLabel(title); h.setObjectName("title"); s = QLabel(subtitle); s.setObjectName("muted"); l.addWidget(h); l.addWidget(s); return box

    def _card(self, kicker, title, detail):
        box = QFrame(); box.setObjectName("card"); l = QVBoxLayout(box); a=QLabel(kicker); a.setObjectName("accent"); b=QLabel(title); b.setObjectName("cardTitle"); c=QLabel(detail); c.setObjectName("muted"); l.addWidget(a); l.addWidget(b); l.addWidget(c); return box

    def _feature_note(self, title):
        notes = {"GuihGuih AI": f"Estado: {MODEL_STATUS}. Extração estática experimental disponível; nenhum modelo foi treinado ou validado, então não há classificação de IA.", "Rede": "Coleta de eventos de serviços autorizados, reputação e bloqueio não implementados.", "Ransomware": "Detecção comportamental e backups versionados não implementados."}
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
        if rows:
            latest = rows[0]
            state = " · cancelada" if latest["cancelled"] else ""
            self.latest_scan.setText(
                f"#{latest['id']} · {latest['files_scanned']} arquivos · {latest['findings']} achados{state}"
            )
        for item in rows:
            row=self.history.rowCount(); self.history.insertRow(row)
            for col, key in enumerate(["id","started_at","root_path","files_scanned","findings"]): self.history.setItem(row,col,QTableWidgetItem(str(item[key])))

    def add_monitor_folder(self):
        path=QFileDialog.getExistingDirectory(self,"Adicionar pasta monitorada")
        if path:
            try: self.monitor.add_folder(path); self.mon_events.addItem(f"Pasta permitida: {path}")
            except (OSError, ValueError) as exc: QMessageBox.warning(self,"Pasta inválida",str(exc))

    def start_monitor(self):
        try:
            self.monitor.start()
            self.mon_status.setText("Ativo · alterações detectadas por polling local")
            self.ransomware_status.setText("Heurística ativa · observando mudanças em arquivos nas pastas escolhidas.")
        except ValueError as exc: QMessageBox.information(self,"Monitoramento",str(exc))

    def stop_monitor(self):
        self.monitor.stop()
        self.mon_status.setText("Desligado")
        self.ransomware_status.setText("Monitoramento desligado; os alertas heurísticos estão pausados.")

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
QWidget { color:#ebf6ff; font-size:14px; }
QMainWindow, QStackedWidget { background:#081320; }
QFrame#sidebar { background:#091a2c; border-right:1px solid #173a53; }
QLabel#brand { font-size:19px; font-weight:800; }
QLabel#sidebarFooter { color:#a1bed2; font-size:11px; padding:10px; border-top:1px solid #23445a; }
QListWidget { background:#0c1d30; border:1px solid #24475d; border-radius:8px; padding:5px; }
QListWidget#navigation { background:transparent; border:0; padding:0; color:#b5cce0; }
QListWidget::item { padding:9px 11px; border-radius:6px; }
QListWidget::item:hover { background:#102e46; }
QListWidget::item:selected { background:#133950; color:#83f1ff; }
QListWidget::item:focus { border:1px solid #29d6ed; }
QLabel#title { font-size:30px; font-weight:800; }
QLabel#muted { color:#b1c8dc; }
QLabel#accent { color:#43e1f2; font-size:11px; font-weight:700; }
QLabel#badge {
    background:#103b39; color:#80ffd1; border:1px solid #22675a; border-radius:9px;
    padding:5px 9px; font-size:11px; font-weight:700;
}
QFrame#hero {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #103450,stop:1 #0a2035);
    border:1px solid #2d7190; border-radius:16px;
}
QLabel#heroTitle { font-size:29px; font-weight:800; }
QFrame#card { background:#102338; border:1px solid #23465f; border-radius:11px; padding:12px; }
QLabel#cardTitle { font-size:18px; font-weight:700; }
QComboBox { background:#0c1d30; color:#ebf6ff; border:1px solid #335b75; border-radius:7px; padding:9px 11px; min-width:270px; }
QComboBox:focus, QComboBox:hover { border-color:#43e1f2; }
QComboBox QAbstractItemView { background:#0c1d30; color:#ebf6ff; selection-background-color:#194961; border:1px solid #335b75; }
QPushButton { background:#15334c; color:#ebf6ff; border:1px solid #335b75; border-radius:8px; padding:10px 13px; }
QPushButton:hover, QPushButton:focus { border-color:#43e1f2; }
QPushButton:pressed { background:#204b62; }
QPushButton#primary { background:#2be0f2; color:#062033; border-color:#2be0f2; font-weight:800; }
QPushButton#primary:hover, QPushButton#primary:focus { background:#a0f9ff; border-color:#a0f9ff; }
QPushButton#shortcut { background:#102338; text-align:left; padding:14px 12px; }
QHeaderView::section { background:#15334c; color:#8defff; padding:8px; border:0; }
QTableWidget { background:#0c1d30; alternate-background-color:#102539; gridline-color:#24475d; border:1px solid #24475d; selection-background-color:#194961; selection-color:#fff; }
QMessageBox { background:#0c1d30; }
"""


def main():
    startup_check = sys.argv[1:] == ["--check-startup"]
    if startup_check:
        environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication([sys.argv[0]] if startup_check else sys.argv)
    app.setApplicationName("GuihGuih Cyber")
    app.setWindowIcon(QIcon(str(LOGO_PATH)))
    if startup_check:
        with TemporaryDirectory(prefix="guihguih-startup-") as directory:
            window = MainWindow(HistoryStore(Path(directory) / "history.sqlite3"))
            window.show()
            app.processEvents()
            if QPixmap(str(LOGO_PATH)).isNull():
                raise SystemExit("Não foi possível carregar a logo oficial.")
            window.close()
        return
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__": main()
