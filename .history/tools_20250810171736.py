def colorize_ttk_frames(self, widget, colors=("red", "green", "blue", "yellow", "cyan", "magenta")):
        style = ttk.Style()
        color_index = 0

        for child in widget.winfo_children():
            # Si c'est un ttk.Frame → appliquer un style
            if isinstance(child, ttk.Frame):
                style_name = f"Debug.TFrame{color_index}"
                style.layout(style_name, style.layout("TFrame"))
                style.configure(style_name, background=colors[color_index % len(colors)])
                child.configure(style=style_name)
                color_index += 1

            # Si c'est un tk.Frame → appliquer une couleur directement
            elif isinstance(child, tk.Frame):
                child.configure(bg=colors[color_index % len(colors)])
                color_index += 1

            # Récursif sur les enfants
            self.colorize_ttk_frames(child, colors)