"""
Interface simplifiée pour visualiser les logs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import threading

class SimpleLogsViewer:
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        self.window = None
        self.current_session = None
        self.auto_refresh_active = False
        self.refresh_job = None
    
    def show_window(self):
        """Affiche la fenêtre des logs"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Logs d'importation")
        self.window.geometry("1000x700")
        self.window.configure(bg='#2d2d2d')
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
        self.load_sessions()
        self.start_auto_refresh()
    
    def create_widgets(self):
        """Crée l'interface"""
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#2d2d2d')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="📋 Logs d'importation",
            font=("Arial", 16, "bold"),
            bg='#2d2d2d',
            fg='white'
        )
        title_label.pack(pady=(0, 10))
        
        # Frame sessions
        sessions_frame = tk.LabelFrame(
            main_frame,
            text="Sessions récentes",
            bg='#2d2d2d',
            fg='white',
            font=("Arial", 10, "bold")
        )
        sessions_frame.pack(fill='x', pady=(0, 10))
        
        # Liste des sessions
        columns = ('Date', 'Source', 'Statut', 'Progression', 'Succès', 'Échecs')
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.sessions_tree.heading(col, text=col)
        
        self.sessions_tree.column('Date', width=120)
        self.sessions_tree.column('Source', width=300)
        self.sessions_tree.column('Statut', width=80)
        self.sessions_tree.column('Progression', width=100)
        self.sessions_tree.column('Succès', width=60)
        self.sessions_tree.column('Échecs', width=60)
        
        scrollbar = ttk.Scrollbar(sessions_frame, orient='vertical', command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sessions_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.sessions_tree.bind('<<TreeviewSelect>>', self.on_session_select)
        
        # Boutons
        buttons_frame = tk.Frame(main_frame, bg='#2d2d2d')
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        tk.Button(
            buttons_frame,
            text="🔄 Actualiser",
            command=self.load_sessions,
            bg='#4a8fe7',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5
        ).pack(side='left', padx=(0, 10))
        
        self.delete_btn = tk.Button(
            buttons_frame,
            text="🗑️ Supprimer",
            command=self.delete_session,
            bg='#dc3545',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.delete_btn.pack(side='left', padx=(0, 10))
        
        self.pause_btn = tk.Button(
            buttons_frame,
            text="⏸️ Pause",
            command=self.pause_session,
            bg='#ffc107',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.pause_btn.pack(side='left', padx=(0, 10))
        
        self.resume_btn = tk.Button(
            buttons_frame,
            text="▶️ Reprendre",
            command=self.resume_session,
            bg='#28a745',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.resume_btn.pack(side='left', padx=(0, 10))
        
        self.cancel_btn = tk.Button(
            buttons_frame,
            text="⏹️ Annuler",
            command=self.cancel_session,
            bg='#dc3545',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.cancel_btn.pack(side='left', padx=(0, 10))
        
        # Auto-refresh (activé par défaut)
        self.auto_refresh_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            buttons_frame,
            text="🔄 Mise à jour auto",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            font=("Arial", 9)
        ).pack(side='right')
        
        # Zone de logs
        logs_frame = tk.LabelFrame(
            main_frame,
            text="Logs détaillés",
            bg='#2d2d2d',
            fg='white',
            font=("Arial", 10, "bold")
        )
        logs_frame.pack(fill='both', expand=True)
        
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            bg='#1e1e1e',
            fg='white',
            font=("Consolas", 9),
            wrap='word',
            state='disabled'
        )
        self.logs_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Couleurs pour les logs
        self.logs_text.tag_configure('INFO', foreground='#87CEEB')
        self.logs_text.tag_configure('SUCCESS', foreground='#90EE90')
        self.logs_text.tag_configure('WARNING', foreground='#FFD700')
        self.logs_text.tag_configure('ERROR', foreground='#FF6B6B')
    
    def load_sessions(self):
        """Charge les sessions"""
        # Vider la liste
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
        
        # Charger les sessions
        sessions = self.logger.get_recent_sessions(20)
        
        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session.get('start_time', ''))
                date_str = start_time.strftime('%d/%m %H:%M')
            except:
                date_str = 'N/A'
            
            source = session.get('source', 'N/A')
            if len(source) > 40:
                source = source[:37] + '...'
            
            status = session.get('status', 'N/A')
            total = session.get('total', 0)
            processed = session.get('processed', 0)
            success = session.get('success', 0)
            failed = session.get('failed', 0)
            
            progression = f"{processed}/{total}" if total > 0 else "0/0"
            
            # Couleur selon le statut
            tags = ()
            if status == 'running':
                tags = ('running',)
            elif status == 'completed':
                tags = ('completed',)
            elif status == 'cancelled':
                tags = ('cancelled',)
            elif status == 'paused':
                tags = ('paused',)
            elif status == 'interrupted':
                tags = ('interrupted',)
            
            self.sessions_tree.insert('', 'end', values=(
                date_str, source, status, progression, success, failed
            ), tags=tags)
        
        # Couleurs
        self.sessions_tree.tag_configure('running', background='#FFF3CD')
        self.sessions_tree.tag_configure('completed', background='#D4EDDA')
        self.sessions_tree.tag_configure('cancelled', background='#E2E3E5')
        self.sessions_tree.tag_configure('paused', background='#FCE4EC')
        self.sessions_tree.tag_configure('interrupted', background='#FFEBEE')
    
    def on_session_select(self, event):
        """Session sélectionnée"""
        selection = self.sessions_tree.selection()
        if not selection:
            self.delete_btn.config(state='disabled')
            self.cancel_btn.config(state='disabled')
            self.current_session = None
            return
        
        # Trouver la session
        item = selection[0]
        values = self.sessions_tree.item(item, 'values')
        
        sessions = self.logger.get_recent_sessions(20)
        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session.get('start_time', ''))
                date_str = start_time.strftime('%d/%m %H:%M')
                if date_str == values[0]:
                    self.current_session = session
                    
                    # Configurer les boutons
                    status = session.get('status', '')
                    if status == 'running':
                        self.delete_btn.config(state='disabled')
                        self.pause_btn.config(state='normal')
                        self.resume_btn.config(state='disabled')
                        self.cancel_btn.config(state='normal')
                    elif status == 'paused':
                        self.delete_btn.config(state='normal')
                        self.pause_btn.config(state='disabled')
                        self.resume_btn.config(state='normal')
                        self.cancel_btn.config(state='normal')
                    else:
                        self.delete_btn.config(state='normal')
                        self.pause_btn.config(state='disabled')
                        self.resume_btn.config(state='disabled')
                        self.cancel_btn.config(state='disabled')
                    
                    # Afficher les logs
                    self.display_logs(session)
                    break
            except:
                continue
    
    def display_logs(self, session):
        """Affiche les logs d'une session"""
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        
        # En-tête
        header = f"=== {session.get('id', 'N/A')} ===\n"
        header += f"Source: {session.get('source', 'N/A')}\n"
        header += f"Début: {session.get('start_time', 'N/A')}\n"
        header += f"Statut: {session.get('status', 'N/A')}\n"
        header += f"Progression: {session.get('processed', 0)}/{session.get('total', 0)}\n"
        header += "=" * 50 + "\n\n"
        
        self.logs_text.insert(tk.END, header, 'INFO')
        
        # Logs
        for log_entry in session.get('logs', []):
            time_str = log_entry.get('time', '')
            level = log_entry.get('level', 'INFO')
            message = log_entry.get('message', '')
            
            log_line = f"[{time_str}] {message}\n"
            self.logs_text.insert(tk.END, log_line, level)
        
        self.logs_text.config(state='disabled')
        self.logs_text.see(tk.END)
    
    def delete_session(self):
        """Supprime la session sélectionnée"""
        if not self.current_session:
            return
        
        session_id = self.current_session.get('id')
        result = messagebox.askyesno(
            "Supprimer session",
            f"Supprimer la session {session_id} ?\n\nCette action est irréversible."
        )
        
        if result:
            try:
                self.logger.delete_session(session_id)
                messagebox.showinfo("Succès", "Session supprimée")
                self.load_sessions()
                self.logs_text.config(state='normal')
                self.logs_text.delete(1.0, tk.END)
                self.logs_text.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def cancel_session(self):
        """Annule la session en cours"""
        if not self.current_session:
            return
        
        session_id = self.current_session.get('id')
        result = messagebox.askyesno(
            "Annuler session",
            f"Annuler la session {session_id} ?\n\nLe processus sera interrompu."
        )
        
        if result:
            try:
                self.logger.cancel_session()
                messagebox.showinfo("Succès", "Session annulée")
                self.load_sessions()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def toggle_auto_refresh(self):
        """Active/désactive l'auto-refresh"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Démarre l'auto-refresh"""
        if not self.auto_refresh_active:
            self.auto_refresh_active = True
            self.auto_refresh()
    
    def stop_auto_refresh(self):
        """Arrête l'auto-refresh"""
        self.auto_refresh_active = False
        if self.refresh_job:
            self.window.after_cancel(self.refresh_job)
            self.refresh_job = None
    
    def auto_refresh(self):
        """Fonction d'auto-refresh"""
        if not self.auto_refresh_active or not self.window or not self.window.winfo_exists():
            return
        
        # Sauvegarder la sélection
        current_session_id = None
        if self.current_session:
            current_session_id = self.current_session.get('id')
        
        # Recharger
        self.load_sessions()
        
        # Restaurer la sélection et mettre à jour les logs
        if current_session_id:
            sessions = self.logger.get_recent_sessions(20)
            for i, session in enumerate(sessions):
                if session.get('id') == current_session_id:
                    items = self.sessions_tree.get_children()
                    if i < len(items):
                        self.sessions_tree.selection_set(items[i])
                        self.current_session = session
                        self.display_logs(session)
                    break
        
        # Programmer la prochaine mise à jour
        self.refresh_job = self.window.after(2000, self.auto_refresh)
    
    def on_close(self):
        """Fermeture de la fenêtre"""
        self.stop_auto_refresh()
        self.window.destroy()