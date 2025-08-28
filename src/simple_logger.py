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
        self.logs_dir = os.path.join(base_dir, "import_logs")
        self.ensure_logs_dir()
        self.current_session = None
        self.cancelled = False
        self.paused = False
        self.download_complete_event = threading.Event()
        self.session_thread = None
        self.pause_event = threading.Event()
        self.pause_event.set()  # Initialement non en pause
        self._lock = threading.Lock()  # Sécuriser les écritures fichiers
        
    def ensure_logs_dir(self):
        """Crée le dossier de logs s'il n'existe pas"""
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def start_session(self, source_info, urls=None):
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
            'current_index': 0,
            'pending_urls': urls or [],
            'processed_urls': [],
            'processed_items': [],  # structured list of processed items
            'logs': []
        }
        
        self.cancelled = False
        self.paused = False
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
            # Ne pas imprimer en console pour éviter les doublons pendant les imports massifs
    
    def log_processed(self, url, title, status, reason=None):
        """Log qu'un élément a été traité"""
        if not self.current_session:
            return
            
        # Compteurs
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
        
        # Historique structuré
        self.current_session['processed_urls'].append(url)
        self.current_session['processed_items'].append({
            'url': url,
            'title': title,
            'status': status,
            'reason': reason
        })
        
        # Sauvegardes en temps réel
        self.save()
        try:
            self._write_not_downloaded_report()
        except Exception:
            pass
    
    def end_session(self, status='completed'):
        """Termine la session et génère un rapport JSON des non-téléchargées (hors déjà téléchargées)"""
        if self.current_session:
            self.current_session['status'] = status
            self.current_session['end_time'] = datetime.now().isoformat()
            
            total = self.current_session['total']
            success = self.current_session['success']
            failed = self.current_session['failed']
            skipped = self.current_session['skipped']
            
            # Générer le rapport des non-téléchargées
            try:
                session_id = self.current_session['id']
                self._write_not_downloaded_report()  # écriture finale
                self.log('INFO', f"Rapport non-téléchargées mis à jour pour {session_id}")
            except Exception as e:
                self.log('ERROR', f"Erreur génération rapport: {e}")
            
            self.log("INFO", f"Session terminée: {success} succès, {failed} échecs, {skipped} ignorés sur {total}")
            self.save()
            self.current_session = None

    def _write_not_downloaded_report(self):
        """Écrit/actualise le JSON des non-téléchargées en temps réel (hors "déjà téléchargé")."""
        if not self.current_session:
            return
        session_id = self.current_session['id']
        total = self.current_session['total']
        success = self.current_session['success']
        failed = self.current_session['failed']
        skipped = self.current_session['skipped']
        report_items = []
        for item in self.current_session.get('processed_items', []):
            if item.get('status') in ('failed', 'skipped'):
                reason = (item.get('reason') or '').lower()
                if 'déjà téléchargé' in reason or 'deja telecharge' in reason or 'deja téléchargé' in reason:
                    continue
                report_items.append({
                    'url': item.get('url'),
                    'title': item.get('title'),
                    'status': item.get('status'),
                    'reason': item.get('reason')
                })
        report_path = os.path.join(self.logs_dir, f"not_downloaded_{session_id}.json")
        with self._lock:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'session_id': session_id,
                    'source': self.current_session.get('source'),
                    'generated_at': datetime.now().isoformat(),
                    'total': total,
                    'success': success,
                    'failed': failed,
                    'skipped': skipped,
                    'items': report_items
                }, f, ensure_ascii=False, indent=2)
    
    def cancel_session(self):
        """Annule la session courante"""
        self.cancelled = True
        if self.current_session:
            self.current_session['status'] = 'cancelled'
            self.log("WARNING", "Session annulée par l'utilisateur")
            self.end_session('cancelled')
    
    def pause_session(self):
        """Met en pause la session courante"""
        self.paused = True
        self.pause_event.clear()  # Bloquer les threads en attente
        if self.current_session:
            self.current_session['status'] = 'paused'
            self.log("INFO", "Session mise en pause")
            self.save()
    
    def resume_session(self):
        """Reprend la session courante"""
        self.paused = False
        self.pause_event.set()  # Débloquer les threads en attente
        if self.current_session:
            self.current_session['status'] = 'running'
            self.log("INFO", "Session reprise")
            self.save()
    
    def wait_if_paused(self):
        """Attend si la session est en pause (utilise un événement efficace)"""
        if self.paused:
            print("⏸️ Session en pause, attente...")
            self.pause_event.wait()  # Attente efficace avec événement
            print("▶️ Session reprise")
    
    def is_cancelled(self):
        """Vérifie si la session est annulée"""
        return self.cancelled
    
    def is_paused(self):
        """Vérifie si la session est en pause"""
        return self.paused
    
    def wait_for_download_complete(self):
        """Attend que le téléchargement en cours soit terminé"""
        self.download_complete_event.wait()
        self.download_complete_event.clear()
    
    def signal_download_complete(self):
        """Signale que le téléchargement est terminé"""
        self.download_complete_event.set()
    
    def update_current_index(self, index):
        """Met à jour l'index courant"""
        if self.current_session:
            self.current_session['current_index'] = index
            self.save()
    
    def save(self):
        """Sauvegarde la session"""
        if self.current_session:
            file_path = os.path.join(self.logs_dir, f"{self.current_session['id']}.json")
            try:
                with self._lock:
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
    
    def load_session(self, session_id):
        """Charge une session depuis le fichier"""
        file_path = os.path.join(self.logs_dir, f"{session_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    self.current_session = session
                    self.cancelled = False
                    self.paused = session.get('status') == 'paused'
                    return session
            except Exception as e:
                print(f"Erreur chargement session: {e}")
        return None
    
    def get_resumable_sessions(self):
        """Récupère les sessions qui peuvent être reprises"""
        sessions = []
        try:
            files = [f for f in os.listdir(self.logs_dir) if f.endswith('.json')]
            for file in files:
                file_path = os.path.join(self.logs_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session = json.load(f)
                        status = session.get('status', '')
                        if status in ['paused', 'interrupted'] and session.get('current_index', 0) < session.get('total', 0):
                            sessions.append(session)
                except Exception as e:
                    print(f"Erreur lecture {file}: {e}")
        except Exception as e:
            print(f"Erreur listage sessions: {e}")
        
        return sorted(sessions, key=lambda x: x.get('start_time', ''), reverse=True)

# Instance globale
logger = None

def get_logger(base_dir):
    """Récupère l'instance du logger"""
    global logger
    if logger is None:
        logger = SimpleLogger(base_dir)
    return logger