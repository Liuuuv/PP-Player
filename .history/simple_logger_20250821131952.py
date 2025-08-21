"""
Système de logs simplifié pour les importations
"""

import os
import json
import time
from datetime import datetime
import threading

class SimpleLogger:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.logs_dir = os.path.join(base_dir, "logs")
        self.ensure_logs_dir()
        self.current_session = None
        self.cancelled = False
        self.paused = False
        self.download_complete_event = threading.Event()
        self.session_thread = None
        
    def ensure_logs_dir(self):
        """Crée le dossier de logs s'il n'existe pas"""
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def start_session(self, source_info):
        """Démarre une nouvelle session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"import_{timestamp}"
        
        self.current_session = {
            'id': session_id,
            'source': source_info,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'total': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'logs': []
        }
        
        self.cancelled = False
        self.log("INFO", f"Session démarrée: {source_info}")
        self.save()
        return session_id
    
    def set_total(self, total):
        """Définit le nombre total d'éléments"""
        if self.current_session:
            self.current_session['total'] = total
            self.log("INFO", f"Total: {total} éléments")
            self.save()
    
    def log(self, level, message):
        """Ajoute un log"""
        if self.current_session:
            log_entry = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'level': level,
                'message': message
            }
            self.current_session['logs'].append(log_entry)
            print(f"[{level}] {message}")
    
    def log_processed(self, url, title, status, reason=None):
        """Log qu'un élément a été traité"""
        if not self.current_session:
            return
            
        self.current_session['processed'] += 1
        
        if status == 'success':
            self.current_session['success'] += 1
            self.log("SUCCESS", f"✅ {title}")
        elif status == 'failed':
            self.current_session['failed'] += 1
            self.log("ERROR", f"❌ {title} - {reason}")
        elif status == 'skipped':
            self.current_session['skipped'] += 1
            self.log("WARNING", f"⚠️ {title} - {reason}")
        
        self.save()
    
    def end_session(self, status='completed'):
        """Termine la session"""
        if self.current_session:
            self.current_session['status'] = status
            self.current_session['end_time'] = datetime.now().isoformat()
            
            total = self.current_session['total']
            success = self.current_session['success']
            failed = self.current_session['failed']
            skipped = self.current_session['skipped']
            
            self.log("INFO", f"Session terminée: {success} succès, {failed} échecs, {skipped} ignorés sur {total}")
            self.save()
            self.current_session = None
    
    def cancel_session(self):
        """Annule la session courante"""
        self.cancelled = True
        if self.current_session:
            self.current_session['status'] = 'cancelled'
            self.log("WARNING", "Session annulée par l'utilisateur")
            self.end_session('cancelled')
    
    def is_cancelled(self):
        """Vérifie si la session est annulée"""
        return self.cancelled
    
    def save(self):
        """Sauvegarde la session"""
        if self.current_session:
            file_path = os.path.join(self.logs_dir, f"{self.current_session['id']}.json")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_session, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erreur sauvegarde: {e}")
    
    def get_recent_sessions(self, limit=20):
        """Récupère les sessions récentes"""
        sessions = []
        try:
            files = [f for f in os.listdir(self.logs_dir) if f.endswith('.json')]
            files.sort(reverse=True)  # Plus récent en premier
            
            for file in files[:limit]:
                file_path = os.path.join(self.logs_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session = json.load(f)
                        sessions.append(session)
                except Exception as e:
                    print(f"Erreur lecture {file}: {e}")
        except Exception as e:
            print(f"Erreur listage logs: {e}")
        
        return sessions
    
    def delete_session(self, session_id):
        """Supprime une session"""
        file_path = os.path.join(self.logs_dir, f"{session_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"Session {session_id} non trouvée")

# Instance globale
logger = None

def get_logger(base_dir):
    """Récupère l'instance du logger"""
    global logger
    if logger is None:
        logger = SimpleLogger(base_dir)
    return logger