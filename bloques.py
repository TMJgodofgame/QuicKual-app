import tkinter as tk

# Emoji para el botón de borrar. Si en tu sistema no se ve bien, cambia por "X" o "[borrar]".
TRASH_EMOJI = "🗑️"


def _add_header_with_trash(parent_block: tk.Frame, botones_frame: tk.Frame, canvas: tk.Canvas) -> tk.Frame:
    """
    Añade una cabecera superior con un botón de papelera al bloque indicado y
    devuelve un frame 'content' donde debes colocar el contenido real
    (Text o la tabla de Entry/Label).

    Al pulsar la papelera, se elimina el bloque completo y se recolocan los
    botones principales (Texto/+).
    """
    # Cabecera
    header = tk.Frame(parent_block, bg="#f7f7f7")
    header.pack(fill="x")

    # Espaciador izquierdo (por si en el futuro quieres poner un título a la izquierda)
    tk.Label(header, text="", bg="#f7f7f7").pack(side="left", padx=4, pady=2)

    def _delete_block():
        # Destruye el bloque completo y recoloca los botones
        parent_block.destroy()
        mover_botones_abajo(botones_frame, canvas)

    trash_btn = tk.Button(
        header,
        text=TRASH_EMOJI,
        font=("Arial", 10),
        width=2,
        relief="flat",
        cursor="hand2",
        command=_delete_block
    )
    trash_btn.pack(side="right", padx=4, pady=2)

    # Contenedor de contenido real del bloque
    content = tk.Frame(parent_block, bg="white")
    content.pack(fill="both", expand=True)

    return content


def agregar_bloque_texto(scrollable_frame: tk.Frame, botones_frame: tk.Frame, canvas: tk.Canvas) -> None:
    """
    Crea un bloque de texto con cabecera de papelera.
    """
    bloque = tk.Frame(scrollable_frame, bd=3, relief="groove", bg="white")
    bloque.pack(side="top", fill="x", pady=5)
    bloque.pack_propagate(False)

    # Altura aproximada (1/4 de la ventana) con fallback
    bloque.update_idletasks()
    ventana_altura = bloque.winfo_toplevel().winfo_height()
    if ventana_altura < 100:  # Fallback si aún no se dibujó
        ventana_altura = 600
    bloque.config(height=int(ventana_altura * 0.25))

    # Cabecera + contenedor
    content = _add_header_with_trash(bloque, botones_frame, canvas)

    # Text widget
    text_widget = tk.Text(content, wrap="word", font=("Arial", 14), undo=True, borderwidth=0, bg="white")
    text_widget.pack(fill="both", expand=True, padx=5, pady=5)
    text_widget.focus_set()

    # Ajuste de scroll y recolocar botones
    bloque.update_idletasks()
    canvas.update_idletasks()
    canvas.yview_moveto(1.0)
    mover_botones_abajo(botones_frame, canvas)


def mover_botones_abajo(botones_frame: tk.Frame, canvas: tk.Canvas) -> None:
    """
    Recoloca el frame de botones principales para que quede después del último bloque.
    """
    botones_frame.pack_forget()
    botones_frame.pack(side="top", pady=10)
    canvas.update_idletasks()