"""
Système de logs pour les importations (HTML et playlists)
"""

import os
import json
import time
from datetime import datetime
import threading

class ImportLogger:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.logs_dir = os.path.join(base_dir, "import_logs")
        self.ensure_logs_dir()
        self.current_session = None
        self.lock = threading.Lock()
    
    def ensure_logs_dir(self):
        """Crée le dossier de logs s'il n'existe pas"""
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
        except Exception as e:
            print(f"Erreur création dossier logs: {e}")
    
    def start_session(self, session_type, source_info):
        """Démarre une nouvelle session de logs"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = f"{session_type}_{timestamp}"
            
            self.current_session = {
                'session_id': session_id,
                'type': session_type,
                'source': source_info,
                'start_time': datetime.now().isoformat(),
                'status': 'running',
                'total_links': 0,
                'processed_links': 0,
                'successful_downloads': 0,
                'failed_downloads': 0,
                'skipped_links': 0,
                'logs': [],
                'processed_urls': [],  # URLs déjà traitées
                'pending_urls': [],    # URLs en attente
                'failed_urls': []      # URLs qui ont échoué
            }
            
            self.log_info(f"Démarrage de la session {session_type}")
            self.log_info(f"Source: {source_info}")
            return session_id
    
    def set_total_links(self, total):
        """Définit le nombre total de liens à traiter"""
        if self.current_session:
            with self.lock:
                self.current_session['total_links'] = total
                self.log_info(f"Total de liens à traiter: {total}")
    
    def set_pending_urls(self, urls):
        """Définit la liste des URLs en attente"""
        if self.current_session:
            with self.lock:
                self.current_session['pending_urls'] = urls.copy()
                self.save_session_state()
    
    def log_info(self, message):
        """Ajoute un log d'information"""
        self._add_log('INFO', message)
    
    def log_warning(self, message):
        """Ajoute un log d'avertissement"""
        self._add_log('WARNING', message)
    
    def log_error(self, message):
        """Ajoute un log d'erreur"""
        self._add_log('ERROR', message)
    
    def log_success(self, message):
        """Ajoute un log de succès"""
        self._add_log('SUCCESS', message)
    
    def _add_log(self, level, message):
        """Ajoute un log avec timestamp"""
        if self.current_session:
            with self.lock:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': level,
                    'message': message
                }
                self.current_session['logs'].append(log_entry)
                print(f"[{level}] {message}")  # Affichage console aussi
    
    def log_url_processed(self, url, title, status, reason=None):
        """Log qu'une URL a été traitée"""
        if self.current_session:
            with self.lock:
                self.current_session['processed_links'] += 1
                
                if status == 'success':
                    self.current_session['successful_downloads'] += 1
                    self.current_session['processed_urls'].append(url)
                    self.log_success(f"✅ Téléchargé: {title}")
                elif status == 'failed':
                    self.current_session['failed_downloads'] += 1
                    self.current_session['failed_urls'].append({'url': url, 'title': title, 'reason': reason})
                    self.log_error(f"❌ Échec: {title} - {reason}")
                elif status == 'skipped':
                    self.current_session['skipped_links'] += 1
                    self.log_warning(f"⚠️ Ignoré: {title} - {reason}")
                
                # Retirer de la liste des URLs en attente
                if url in self.current_session['pending_urls']:
                    self.current_session['pending_urls'].remove(url)
                
                self.save_session_state()
    
    def end_session(self, final_status='completed'):
        """Termine la session courante"""
        if self.current_session:
            with self.lock:
                self.current_session['status'] = final_status
                self.current_session['end_time'] = datetime.now().isoformat()
                
                # Statistiques finales
                total = self.current_session['total_links']
                success = self.current_session['successful_downloads']
                failed = self.current_session['failed_downloads']
                skipped = self.current_session['skipped_links']
                
                self.log_info(f"Session terminée - Statut: {final_status}")
                self.log_info(f"Statistiques: {success} succès, {failed} échecs, {skipped} ignorés sur {total} total")
                
                self.save_session_state()
                self.current_session = None
    
    def save_session_state(self):
        """Sauvegarde l'état de la session courante"""
        if self.current_session:
            try:
                session_file = os.path.join(self.logs_dir, f"{self.current_session['session_id']}.json")
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_session, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erreur sauvegarde session: {e}")
    
    def load_session_state(self, session_id):
        """Charge l'état d'une session"""
        try:
            session_file = os.path.join(self.logs_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur chargement session: {e}")
        return None
    
    def get_recent_sessions(self, limit=10):
        """Récupère les sessions récentes"""
        try:
            sessions = []
            for filename in os.listdir(self.logs_dir):
                if filename.endswith('.json'):
                    session_file = os.path.join(self.logs_dir, filename)
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session = json.load(f)
                            sessions.append(session)
                    except:
                        continue
            
            # Trier par date de début (plus récent en premier)
            sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
            return sessions[:limit]
        except Exception as e:
            print(f"Erreur récupération sessions: {e}")
            return []
    
    def can_resume_session(self, session_id):
        """Vérifie si une session peut être reprise"""
        session = self.load_session_state(session_id)
        if session and session.get('status') == 'running':
            return len(session.get('pending_urls', [])) > 0
        return False
    
    def resume_session(self, session_id):
        """Reprend une session interrompue"""
        session = self.load_session_state(session_id)
        if session:
            with self.lock:
                self.current_session = session
                self.log_info(f"Reprise de la session {session_id}")
                return session.get('pending_urls', [])
        return []

# Instance globale
import_logger = None

def get_import_logger(base_dir):
    """Récupère l'instance globale du logger"""
    global import_logger
    if import_logger is None:
        import_logger = ImportLogger(base_dir)
    return import_logger