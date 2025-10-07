import tkinter as tk

def agregar_bloque_texto(scrollable_frame, botones_frame, canvas):
    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)

    # Evitar que el frame cambie de tamaño automáticamente
    bloque.pack_propagate(False)

    # Calcular altura = 1/4 de la ventana principal
    bloque.update_idletasks()
    ventana_altura = bloque.winfo_toplevel().winfo_height()
    if ventana_altura < 100:  # Fallback si la ventana aún no se ha dibujado
        ventana_altura = 600
    bloque.config(height=int(ventana_altura * 0.25))

    # Widget de texto
    text_widget = tk.Text(bloque, wrap="word", font=("Arial", 14), undo=True, borderwidth=0)
    text_widget.pack(fill="both", expand=True, padx=5, pady=5)

    text_widget.focus_set()

    # Actualizar canvas y scroll
    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)

    mover_botones_abajo(botones_frame, canvas)


def mover_botones_abajo(botones_frame, canvas):
    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)
    canvas.update_idletasks()
