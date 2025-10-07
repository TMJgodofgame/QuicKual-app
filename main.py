import tkinter as tk
from tkinter import filedialog, messagebox
from bloques import agregar_bloque_texto, mover_botones_abajo
from submenu import abrir_submenu
from export_pdf import export_to_pdf  # ✅ Import correcto

root = tk.Tk()
root.title("QuicKual")

# --- Maximizar según sistema ---
window_system = root.tk.call('tk', 'windowingsystem')
if window_system == 'win32':
    root.state('zoomed')
elif window_system == 'x11':
    try:
        root.attributes('-zoomed', True)
    except tk.TclError:
        root.state('zoomed')
elif window_system == 'aqua':
    root.attributes('-fullscreen', True)

# --- Frame principal con scroll ---
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame, highlightthickness=0, bd=0, bg="#f0f0f0")
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def actualizar_scroll(_=None):
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", actualizar_scroll)
canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))

# --- Frame de botones ---
botones_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
botones_frame.pack(side="top", pady=10)

btn_texto = tk.Button(
    botones_frame, text="Texto", font=("Arial", 14), padx=10, pady=5,
    command=lambda: agregar_bloque_texto(scrollable_frame, botones_frame, canvas)
)
btn_submenu = tk.Button(
    botones_frame, text="+", font=("Arial", 14, "bold"), padx=10, pady=5,
    command=lambda: abrir_submenu(scrollable_frame, botones_frame, canvas)
)

btn_texto.pack(side="left", padx=5)
btn_submenu.pack(side="left", padx=5)

# --- Scroll con rueda del ratón ---
def _on_mousewheel(event):
    if window_system == 'aqua':
        canvas.yview_scroll(-1 * int(event.delta), "units")
    else:
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

# ---- Función para exportar a PDF ----
def exportar_pdf():
    archivo_destino = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf")],
        title="Guardar PDF como..."
    )
    if not archivo_destino:
        return

    try:
        export_to_pdf(scrollable_frame, archivo_destino, title="Mi documento QuicKual")
        messagebox.showinfo(
            "Exportar a PDF",
            f"El documento se ha exportado correctamente como:\n{archivo_destino}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema al exportar:\n{e}")

# ---- Apartado fijo inferior con botón centrado ----
bottom_frame = tk.Frame(root, bg="#f0f0f0", height=60)
bottom_frame.pack(side="bottom", fill="x")
bottom_frame.pack_propagate(False)

export_btn = tk.Button(
    bottom_frame,
    text="Exportar a PDF",
    font=("Arial", 14),
    padx=20,
    pady=6,
    command=exportar_pdf  # ✅ Llamada a la función
)
export_btn.pack(anchor="center", pady=8)

# ------------------------------------------------------------------------------------
root.mainloop()
