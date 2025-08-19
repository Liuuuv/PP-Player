from __init__ import *


def show_output_menu(self):
    """Affiche un menu déroulant pour choisir le périphérique de sortie audio"""
    try:
        # Obtenir la liste des périphériques audio
        import pygame._sdl2.audio
        devices = pygame._sdl2.audio.get_audio_device_names()
        
        if not devices:
            messagebox.showinfo("Périphériques audio", "Aucun périphérique audio trouvé")
            return
        
        # Créer le menu déroulant
        output_menu = tk.Menu(self.root, tearoff=0, bg='white', fg='black', 
                                activebackground='#4a8fe7', activeforeground='white',
                                relief='flat', bd=1)
        
        # Ajouter un titre
        output_menu.add_command(label="Périphériques de sortie", state='disabled')
        output_menu.add_separator()
        
        # Variable partagée pour les radiobuttons
        if not hasattr(self, 'audio_device_var'):
            self.audio_device_var = tk.StringVar(value=self.current_audio_device or "")
        else:
            self.audio_device_var.set(self.current_audio_device or "")
        
        # Ajouter chaque périphérique comme radiobutton
        for device in devices:
            device_name = device.decode('utf-8') if isinstance(device, bytes) else device
            
            output_menu.add_radiobutton(
                label=device_name,
                variable=self.audio_device_var,
                value=device_name,
                command=lambda d=device, name=device_name: self.change_output_device(d, name)
            )
        
        # Afficher le menu à la position du bouton
        try:
            x = self.output_button.winfo_rootx()
            y = self.output_button.winfo_rooty() + self.output_button.winfo_height()
            output_menu.post(x, y)
        except:
            # Si erreur de positionnement, afficher au curseur
            output_menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
            
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'accéder aux périphériques audio:\n{str(e)}")