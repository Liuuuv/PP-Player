"""
Interface pour visualiser les logs d'importation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import json

class LogsViewer:
    def __init__(self, parent, import_logger):
        self.parent = parent
        self.import_logger = import_logger
        self.window = None
        self.current_session = None
        self.auto_refresh_job = None
        self.is_auto_refreshing = False
    
    def show_logs_window(self):
        """Affiche la fenêtre des logs"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Logs d'importation")
        self.window.geometry("900x700")
        self.window.configure(bg='#2d2d2d')
        
        # Centrer la fenêtre
        self.window.transient(self.parent)
        
        # Gérer la fermeture de la fenêtre
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.create_widgets()
        self.load_sessions()
    
    def create_widgets(self):
        """Crée les widgets de l'interface"""
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
        
        # Frame pour la liste des sessions
        sessions_frame = tk.LabelFrame(
            main_frame,
            text="Sessions récentes",
            bg='#2d2d2d',
            fg='white',
            font=("Arial", 10, "bold")
        )
        sessions_frame.pack(fill='x', pady=(0, 10))
        
        # Treeview pour les sessions
        columns = ('Date', 'Type', 'Source', 'Statut', 'Succès', 'Échecs', 'Ignorés')
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=columns, show='headings', height=6)
        
        # Configuration des colonnes
        self.sessions_tree.heading('Date', text='Date')
        self.sessions_tree.heading('Type', text='Type')
        self.sessions_tree.heading('Source', text='Source')
        self.sessions_tree.heading('Statut', text='Statut')
        self.sessions_tree.heading('Succès', text='Succès')
        self.sessions_tree.heading('Échecs', text='Échecs')
        self.sessions_tree.heading('Ignorés', text='Ignorés')
        
        self.sessions_tree.column('Date', width=120)
        self.sessions_tree.column('Type', width=80)
        self.sessions_tree.column('Source', width=200)
        self.sessions_tree.column('Statut', width=80)
        self.sessions_tree.column('Succès', width=60)
        self.sessions_tree.column('Échecs', width=60)
        self.sessions_tree.column('Ignorés', width=60)
        
        # Scrollbar pour la treeview
        sessions_scrollbar = ttk.Scrollbar(sessions_frame, orient='vertical', command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar.set)
        
        self.sessions_tree.pack(side='left', fill='both', expand=True)
        sessions_scrollbar.pack(side='right', fill='y')
        
        # Bind pour sélection
        self.sessions_tree.bind('<<TreeviewSelect>>', self.on_session_select)
        
        # Frame pour les boutons
        buttons_frame = tk.Frame(main_frame, bg='#2d2d2d')
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        # Bouton rafraîchir
        refresh_btn = tk.Button(
            buttons_frame,
            text="🔄 Rafraîchir",
            command=self.load_sessions,
            bg='#4a8fe7',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        # Bouton reprendre session
        self.resume_btn = tk.Button(
            buttons_frame,
            text="▶️ Reprendre session",
            command=self.resume_selected_session,
            bg='#28a745',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.resume_btn.pack(side='left', padx=(0, 10))
        
        # Bouton supprimer session
        self.delete_btn = tk.Button(
            buttons_frame,
            text="🗑️ Supprimer session",
            command=self.delete_selected_session,
            bg='#dc3545',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.delete_btn.pack(side='left', padx=(0, 10))
        
        # Bouton annuler session (pour les sessions en cours)
        self.cancel_btn = tk.Button(
            buttons_frame,
            text="⏹️ Annuler session",
            command=self.cancel_selected_session,
            bg='#fd7e14',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            padx=15,
            pady=5,
            state='disabled'
        )
        self.cancel_btn.pack(side='left', padx=(0, 10))
        
        # Checkbox pour auto-refresh
        self.auto_refresh_var = tk.BooleanVar()
        self.auto_refresh_check = tk.Checkbutton(
            buttons_frame,
            text="🔄 Mise à jour automatique",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            font=("Arial", 9)
        )
        self.auto_refresh_check.pack(side='right')
        
        # Frame pour les logs détaillés
        logs_frame = tk.LabelFrame(
            main_frame,
            text="Logs détaillés",
            bg='#2d2d2d',
            fg='white',
            font=("Arial", 10, "bold")
        )
        logs_frame.pack(fill='both', expand=True)
        
        # Zone de texte pour les logs
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            bg='#1e1e1e',
            fg='white',
            font=("Consolas", 9),
            wrap='word',
            state='disabled'
        )
        self.logs_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configuration des couleurs pour les différents niveaux de logs
        self.logs_text.tag_configure('INFO', foreground='#87CEEB')
        self.logs_text.tag_configure('SUCCESS', foreground='#90EE90')
        self.logs_text.tag_configure('WARNING', foreground='#FFD700')
        self.logs_text.tag_configure('ERROR', foreground='#FF6B6B')
    
    def load_sessions(self):
        """Charge les sessions récentes"""
        # Vider la treeview
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
        
        # Charger les sessions
        sessions = self.import_logger.get_recent_sessions(20)
        
        for session in sessions:
            # Formater la date
            try:
                start_time = datetime.fromisoformat(session.get('start_time', ''))
                date_str = start_time.strftime('%d/%m %H:%M')
            except:
                date_str = 'N/A'
            
            # Informations de la session
            session_type = session.get('type', 'N/A')
            source = session.get('source', 'N/A')
            if len(source) > 30:
                source = source[:27] + '...'
            
            status = session.get('status', 'N/A')
            success = session.get('successful_downloads', 0)
            failed = session.get('failed_downloads', 0)
            skipped = session.get('skipped_links', 0)
            
            # Couleur selon le statut
            tags = ()
            if status == 'running':
                tags = ('running',)
            elif status == 'completed':
                tags = ('completed',)
            elif status == 'interrupted':
                tags = ('interrupted',)
            
            self.sessions_tree.insert('', 'end', values=(
                date_str, session_type, source, status, success, failed, skipped
            ), tags=tags)
        
        # Configuration des couleurs
        self.sessions_tree.tag_configure('running', background='#FFF3CD')
        self.sessions_tree.tag_configure('completed', background='#D4EDDA')
        self.sessions_tree.tag_configure('interrupted', background='#F8D7DA')
    
    def on_session_select(self, event):
        """Appelé quand une session est sélectionnée"""
        selection = self.sessions_tree.selection()
        if not selection:
            self.resume_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            self.cancel_btn.config(state='disabled')
            self.current_session = None
            return
        
        # Récupérer la session sélectionnée
        item = selection[0]
        values = self.sessions_tree.item(item, 'values')
        
        if len(values) >= 4:
            status = values[3]  # Statut
            
            # Trouver la session correspondante
            sessions = self.import_logger.get_recent_sessions(20)
            for session in sessions:
                try:
                    start_time = datetime.fromisoformat(session.get('start_time', ''))
                    date_str = start_time.strftime('%d/%m %H:%M')
                    if date_str == values[0]:  # Même date
                        self.current_session = session
                        session_id = session.get('session_id')
                        
                        # Configurer les boutons selon le statut
                        if status == 'running':
                            # Session en cours
                            self.resume_btn.config(state='disabled')
                            self.cancel_btn.config(state='normal')
                            self.delete_btn.config(state='disabled')
                        elif self.import_logger.can_resume_session(session_id):
                            # Session interrompue, peut être reprise
                            self.resume_btn.config(state='normal')
                            self.cancel_btn.config(state='disabled')
                            self.delete_btn.config(state='normal')
                        else:
                            # Session terminée
                            self.resume_btn.config(state='disabled')
                            self.cancel_btn.config(state='disabled')
                            self.delete_btn.config(state='normal')
                        
                        # Afficher les logs de cette session
                        self.display_session_logs(session)
                        break
                except:
                    continue
    
    def display_session_logs(self, session):
        """Affiche les logs d'une session"""
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        
        # En-tête de session
        header = f"=== Session {session.get('session_id', 'N/A')} ===\n"
        header += f"Type: {session.get('type', 'N/A')}\n"
        header += f"Source: {session.get('source', 'N/A')}\n"
        header += f"Début: {session.get('start_time', 'N/A')}\n"
        header += f"Statut: {session.get('status', 'N/A')}\n"
        header += f"Progression: {session.get('processed_links', 0)}/{session.get('total_links', 0)}\n"
        header += "=" * 50 + "\n\n"
        
        self.logs_text.insert(tk.END, header, 'INFO')
        
        # Logs détaillés
        logs = session.get('logs', [])
        for log_entry in logs:
            timestamp = log_entry.get('timestamp', '')
            level = log_entry.get('level', 'INFO')
            message = log_entry.get('message', '')
            
            # Formater le timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = timestamp
            
            log_line = f"[{time_str}] {message}\n"
            self.logs_text.insert(tk.END, log_line, level)
        
        self.logs_text.config(state='disabled')
        self.logs_text.see(tk.END)
    
    def resume_selected_session(self):
        """Reprend la session sélectionnée"""
        selection = self.sessions_tree.selection()
        if not selection:
            return
        
        # Trouver la session correspondante
        item = selection[0]
        values = self.sessions_tree.item(item, 'values')
        
        sessions = self.import_logger.get_recent_sessions(20)
        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session.get('start_time', ''))
                date_str = start_time.strftime('%d/%m %H:%M')
                if date_str == values[0]:
                    session_id = session.get('session_id')
                    
                    # Confirmer la reprise
                    pending_count = len(session.get('pending_urls', []))
                    result = messagebox.askyesno(
                        "Reprendre session",
                        f"Reprendre la session avec {pending_count} liens en attente ?\n\n"
                        f"Session: {session_id}\n"
                        f"Type: {session.get('type', 'N/A')}\n"
                        f"Source: {session.get('source', 'N/A')}"
                    )
                    
                    if result:
                        # TODO: Implémenter la reprise dans le music player
                        messagebox.showinfo("Info", "Fonctionnalité de reprise en cours d'implémentation")
                    break
            except:
                continue