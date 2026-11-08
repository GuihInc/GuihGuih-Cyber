"""Desktop UI entry point using only Python's standard library."""

import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .scanner import scan_path
from .storage import HistoryStore


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("GuihGuih Cyber · Scanner local")
        self.root.geometry("900x620")
        self.root.configure(bg="#080f18")
        self.store = HistoryStore()
        self.cancel = threading.Event()
        self._build()
        self._history()

    def _build(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#101b29", foreground="#e8f0f7", fieldbackground="#101b29", rowheight=29, borderwidth=0)
        style.configure("Treeview.Heading", background="#18283a", foreground="#78e7b0", font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#174333")])
        shell = tk.Frame(self.root, bg="#080f18"); shell.pack(fill="both", expand=True)
        nav = tk.Frame(shell, bg="#0b1420", width=205); nav.pack(side="left", fill="y"); nav.pack_propagate(False)
        tk.Label(nav, text="GUIHGUIH", fg="#e9f4fb", bg="#0b1420", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20, pady=(25, 0))
        tk.Label(nav, text="CYBER  /  DESKTOP", fg="#78e7b0", bg="#0b1420", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(2, 24))
        for item in ("▦   Visão geral", "◉   Verificação", "◷   Monitoramento", "⬡   Quarentena", "☷   Histórico", "✳   GuihGuih AI", "⌁   Rede", "⚙   Configurações"):
            tk.Label(nav, text=item, fg="#a8bacb" if item.startswith(("▦", "◉", "◷", "⬡", "☷")) else "#60768a", bg="#0b1420", font=("Segoe UI", 10), padx=18, pady=11, anchor="w").pack(fill="x", padx=8)
        content = tk.Frame(shell, bg="#080f18", padx=28, pady=22); content.pack(side="left", fill="both", expand=True)
        top = tk.Frame(content, bg="#080f18"); top.pack(fill="x")
        tk.Label(top, text="PAINEL DE SEGURANÇA", fg="#78e7b0", bg="#080f18", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(top, text="Visão geral", fg="#f0f6fb", bg="#080f18", font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(3, 13))
        status = tk.Frame(content, bg="#12271f", highlightbackground="#24513c", highlightthickness=1, padx=16, pady=13); status.pack(fill="x", pady=(0, 16))
        tk.Label(status, text="●", fg="#78e7b0", bg="#12271f", font=("Segoe UI", 16)).pack(side="left", padx=(0, 11))
        status_text = tk.Frame(status, bg="#12271f"); status_text.pack(side="left")
        tk.Label(status_text, text="SCANNER LOCAL DISPONÍVEL", fg="#78e7b0", bg="#12271f", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(status_text, text="Verificação manual · sem proteção em tempo real", fg="#c2d0db", bg="#12271f", font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 0))
        cards = tk.Frame(content, bg="#080f18"); cards.pack(fill="x", pady=(0, 16))
        for title, value, caption in (("ÚLTIMA VERIFICAÇÃO", "—", "Nenhuma nesta sessão"), ("ARQUIVOS ANALISADOS", "0", "Aguardando verificação"), ("AMEAÇAS DETECTADAS", "0", "Regras locais explicáveis")):
            card = tk.Frame(cards, bg="#101b29", highlightbackground="#203044", highlightthickness=1, padx=14, pady=12); card.pack(side="left", fill="both", expand=True, padx=(0, 9))
            tk.Label(card, text=title, fg="#8499ae", bg="#101b29", font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(card, text=value, fg="#e8f0f7", bg="#101b29", font=("Segoe UI", 21, "bold")).pack(anchor="w", pady=(4, 0))
            tk.Label(card, text=caption, fg="#8499ae", bg="#101b29", font=("Segoe UI", 8)).pack(anchor="w")
        bar = tk.Frame(content, bg="#080f18"); bar.pack(fill="x", pady=(0, 10))
        style.configure("Accent.TButton", background="#78e7b0", foreground="#07130f", font=("Segoe UI", 10, "bold"), padding=(14, 10))
        style.map("Accent.TButton", background=[("active", "#9af3c7")])
        ttk.Button(bar, text="Verificação rápida", style="Accent.TButton", command=self.scan_folder).pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="Verificação completa", command=self.scan_home).pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="Personalizada…", command=self.scan_file).pack(side="left", padx=(0, 8))
        ttk.Button(bar, text="Cancelar", command=self.cancel.set).pack(side="left")
        self.status = tk.Label(content, text="Aguardando verificação", fg="#9db0c4", bg="#080f18", anchor="w"); self.status.pack(fill="x", pady=(2, 6))
        tk.Label(content, text="RESULTADOS DA VERIFICAÇÃO", fg="#8499ae", bg="#080f18", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(6, 7))
        cols = ("status", "path", "sha", "reason")
        self.table = ttk.Treeview(content, columns=cols, show="headings")
        for col, title, width in (("status", "Estado", 120), ("path", "Arquivo", 250), ("sha", "SHA-256", 250), ("reason", "Regra / explicação", 270)):
            self.table.heading(col, text=title); self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True)
        tk.Label(content, text="Detecções baseadas em regras locais. Sem achados não prova que o arquivo seja seguro. Microsoft Defender permanece ativo.", fg="#8295aa", bg="#080f18", pady=10, anchor="w").pack(fill="x")

    def scan_home(self):
        self._start(__import__("pathlib").Path.home())

    def _start(self, path):
        self.cancel.clear(); self.status.config(text="Varrendo…")
        for item in self.table.get_children(): self.table.delete(item)
        threading.Thread(target=self._work, args=(path,), daemon=True).start()

    def _work(self, path):
        report = scan_path(path, self.cancel)
        scan_id = self.store.save_scan(report)
        self.root.after(0, lambda: self._show(report, scan_id))

    def _show(self, report, scan_id):
        for item in report["files"]:
            reason = "; ".join(f["rule_id"] + ": " + f["explanation"] for f in item["findings"])
            self.table.insert("", "end", values=(item["status"], item["path"], item["sha256"] or "—", reason or item["error"] or "Nenhuma regra acionada"))
        self.status.config(text=f"Varredura #{scan_id}: {report['files_scanned']} arquivos · {report['finding_count']} achados · {report['error_count']} erros" + (" · cancelada" if report["cancelled"] else ""))
        self._history()

    def _history(self):
        rows = self.store.recent_scans(1)
        self.root.title("GuihGuih Cyber · Scanner local" + (f" · última #{rows[0]['id']}" if rows else ""))

    def scan_file(self):
        path = filedialog.askopenfilename()
        if path: self._start(path)

    def scan_folder(self):
        path = filedialog.askdirectory()
        if path: self._start(path)


def main():
    root = tk.Tk(); App(root); root.mainloop()


if __name__ == "__main__":
    main()

