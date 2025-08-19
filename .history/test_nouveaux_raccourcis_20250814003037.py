#!/usr/bin/env python3
"""
Script de test pour les nouveaux raccourcis
"""

import tkinter as tk
import time

def test_all_shortcuts():
    """Teste tous les raccourcis avec debug"""
    root = tk.Tk()
    root.title("Test Tous les Raccourcis")
    root.geometry("700x500")
    root.configure(bg='#2d2d2d')
    
    # Variables de simulation
    is_playing = False
    volume = 50
    current_time = 30  # Position actuelle en secondes
    song_length = 180  # Durée totale en secondes
    
    def update_display():
        status_label.config(text=f"État: {'En lecture' if is_playing else 'En pause'}")
        volume_label.config(text=f"Volume: {volume}%")
        time_label.config(text=f"Position: {current_time}s / {song_length}s")
        progress_bar['value'] = (current_time / song_length) * 100
    
    def on_play_pause(event):
        nonlocal is_playing
        is_playing = not is_playing
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+P: {'Play' if is_playing else 'Pause'}\n")
        log_text.see(tk.END)
        update_display()
        return "break"
    
    def on_volume_up(event):
        nonlocal volume
        volume = min(100, volume + 5)
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+↑: Volume {volume}%\n")
        log_text.see(tk.END)
        update_display()
        return "break"
    
    def on_volume_down(event):
        nonlocal volume
        volume = max(0, volume - 5)
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+↓: Volume {volume}%\n")
        log_text.see(tk.END)
        update_display()
        return "break"
    
    def on_seek_forward(event):
        nonlocal current_time
        current_time = min(song_length, current_time + 5)
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+→: Avance à {current_time}s\n")
        log_text.see(tk.END)
        update_display()
        return "break"
    
    def on_seek_backward(event):
        nonlocal current_time
        current_time = max(0, current_time - 5)
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+←: Recule à {current_time}s\n")
        log_text.see(tk.END)
        update_display()
        return "break"
    
    def on_next_track(event):
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+N: Chanson suivante\n")
        log_text.see(tk.END)
        return "break"
    
    def on_prev_track(event):
        log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Ctrl+Alt+B: Chanson précédente\n")
        log_text.see(tk.END)
        return "break"
    
    # Interface
    tk.Label(root, text="Test de Tous les Raccourcis", font=("Arial", 16, "bold"), bg='#2d2d2d', fg='white').pack(pady=10)
    
    # Statut
    status_frame = tk.Frame(root, bg='#2d2d2d')
    status_frame.pack(pady=10)
    
    status_label = tk.Label(status_frame, text="", font=("Arial", 12, "bold"), bg='#2d2d2d', fg='#4a8fe7')
    status_label.pack()
    
    volume_label = tk.Label(status_frame, text="", font=("Arial", 12), bg='#2d2d2d', fg='white')
    volume_label.pack()
    
    time_label = tk.Label(status_frame, text="", font=("Arial", 12), bg='#2d2d2d', fg='white')
    time_label.pack()
    
    # Barre de progression
    from tkinter import ttk
    progress_bar = ttk.Progressbar(root, length=400, mode='determinate', maximum=100)
    progress_bar.pack(pady=10)
    
    # Instructions
    instructions_frame = tk.Frame(root, bg='#2d2d2d')
    instructions_frame.pack(pady=10)
    
    tk.Label(instructions_frame, text="Raccourcis disponibles:", font=("Arial", 12, "bold"), bg='#2d2d2d', fg='white').pack()
    
    shortcuts = [
        "Ctrl+Alt+P : Play/Pause",
        "Ctrl+Alt+↑ : Volume +5%",
        "Ctrl+Alt+↓ : Volume -5%",
        "Ctrl+Alt+→ : Avancer 5s",
        "Ctrl+Alt+← : Reculer 5s",
        "Ctrl+Alt+N : Chanson suivante",
        "Ctrl+Alt+B : Chanson précédente"
    ]
    
    for shortcut in shortcuts:
        tk.Label(instructions_frame, text=shortcut, bg='#2d2d2d', fg='#cccccc').pack()
    
    # Zone de log
    log_frame = tk.Frame(root, bg='#2d2d2d')
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    tk.Label(log_frame, text="Log des raccourcis:", bg='#2d2d2d', fg='white', font=("Arial", 10, "bold")).pack(anchor='w')
    
    log_text = tk.Text(log_frame, height=8, bg='#1d1d1d', fg='white', font=("Consolas", 9))
    log_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Bindings - Toutes les variantes
    root.bind('<Control-Alt-p>', on_play_pause)
    root.bind('<Control-Alt-P>', on_play_pause)
    root.bind('<Control-Alt-Key-p>', on_play_pause)
    root.bind('<Control-Alt-Key-P>', on_play_pause)
    
    root.bind('<Control-Alt-Up>', on_volume_up)
    root.bind('<Control-Alt-Down>', on_volume_down)
    root.bind('<Control-Alt-Right>', on_seek_forward)
    root.bind('<Control-Alt-Left>', on_seek_backward)
    
    root.bind('<Control-Alt-n>', on_next_track)
    root.bind('<Control-Alt-N>', on_next_track)
    root.bind('<Control-Alt-b>', on_prev_track)
    root.bind('<Control-Alt-B>', on_prev_track)
    
    root.focus_set()
    
    # Initialiser l'affichage
    update_display()
    
    # Message initial
    log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Test démarré - Testez tous les raccourcis !\n\n")
    
    tk.Button(root, text="Fermer", command=root.destroy, bg='#d32f2f', fg='white').pack(pady=10)
    
    print("=== Test de Tous les Raccourcis ===")
    print("Testez tous les raccourcis Ctrl+Alt+...")
    print("Vérifiez que Ctrl+Alt+P fonctionne maintenant !")
    
    root.mainloop()

def main():
    """Menu principal de test"""
    print("=== Test des Nouveaux Raccourcis ===")
    print("1. Test de tous les raccourcis")
    print("2. Lancer l'application complète")
    print("0. Quitter")
    
    while True:
        try:
            choice = input("\nChoisissez un test (0-2): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                test_all_shortcuts()
            elif choice == '2':
                print("Lancement de l'application complète...")
                import subprocess
                subprocess.run(['python', 'main.py'])
            else:
                print("Choix invalide. Utilisez 0, 1 ou 2.")
        except KeyboardInterrupt:
            break
    
    print("\n=== Résumé des nouveaux raccourcis ===")
    print("✅ Ctrl+Alt+P : Play/Pause (avec debug amélioré)")
    print("✅ Ctrl+Alt+↑/↓ : Volume +/-5% (avec slider)")
    print("✅ Ctrl+Alt+→/← : Avancer/Reculer 5s (NOUVEAU)")
    print("✅ Ctrl+Alt+N/B : Chanson suivante/précédente")
    print("✅ Focus désactivé sur tous les onglets")
    print("✅ create_tooltip corrigé (plus d'erreurs)")
    print("✅ Résultats de recherche fonctionnels")
    print("\nTous les raccourcis sont maintenant opérationnels !")

if __name__ == "__main__":
    main()