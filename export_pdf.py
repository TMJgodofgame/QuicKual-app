import tkinter as tk
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from typing import List, Dict, Any


def extract_document_structure(scrollable_frame: tk.Frame) -> List[Dict[str, Any]]:
    blocks = []
    for child in scrollable_frame.winfo_children():
        children = child.winfo_children()
        if not children:
            continue

        # Ignorar frames que solo contienen botones
        if any(isinstance(w, tk.Button) for w in children):
            continue

        # Bloques de texto
        text_widgets = [w for w in children if isinstance(w, tk.Text)]
        if text_widgets:
            text_widget = text_widgets[0]
            text = text_widget.get("1.0", "end-1c")
            blocks.append({'type': 'text', 'content': text})
            continue

        # Bloques de tabla
        cell_widgets = []
        max_row = -1
        max_col = -1
        for w in children:
            try:
                gi = w.grid_info()
            except Exception:
                gi = {}
            if gi:
                try:
                    r = int(gi.get('row', 0))
                    c = int(gi.get('column', 0))
                except Exception:
                    r, c = 0, 0
                cell_widgets.append((r, c, w))
                if r > max_row:
                    max_row = r
                if c > max_col:
                    max_col = c

        if cell_widgets:
            rows = max_row + 1
            cols = max_col + 1
            matrix = [['' for _ in range(cols)] for _ in range(rows)]
            is_division = False
            is_suma = False
            is_resta = False
            is_factorial = False  # Nueva bandera

            # Detectar división: tabla de 2 columnas y fila 0 con números
            if cols == 2 and len(children) > 2:
                c0_text = ''
                c1_text = ''
                for r, c, w in cell_widgets:
                    try:
                        txt = w.get() if isinstance(w, tk.Entry) else ''
                    except:
                        txt = ''
                    if r == 0 and c == 0:
                        c0_text = txt
                    if r == 0 and c == 1:
                        c1_text = txt
                if c0_text.isdigit() and c1_text.isdigit():
                    is_division = True

            # Detectar suma / resta / factorial
            for r, c, w in cell_widgets:
                try:
                    txt = ''
                    if isinstance(w, tk.Entry):
                        txt = w.get()
                    elif isinstance(w, tk.Label):
                        txt = w.cget('text')
                    else:
                        for sub in w.winfo_children():
                            if isinstance(sub, tk.Label):
                                txt += sub.cget('text')
                            elif isinstance(sub, tk.Entry):
                                try:
                                    txt += sub.get()
                                except:
                                    pass
                            elif isinstance(sub, tk.Text):
                                try:
                                    txt += sub.get("1.0", "end-1c")
                                except:
                                    pass
                    matrix[r][c] = txt
                    if txt.strip().startswith('+') and r == 2:
                        is_suma = True
                    if txt.strip().startswith('-') and r == 2:
                        is_resta = True
                    if '!' in txt:  # Detecta factorial
                        is_factorial = True
                except:
                    matrix[r][c] = ''

            blocks.append({
                'type': 'table',
                'content': matrix,
                'division': is_division,
                'suma': is_suma,
                'resta': is_resta,
                'factorial': is_factorial
            })
            continue

    return blocks


def export_to_pdf(scrollable_frame: tk.Frame, output_path: str = "document.pdf", title: str = None,
                  page_size=letter):
    blocks = extract_document_structure(scrollable_frame)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontName = "Helvetica"
    normal.fontSize = 12
    normal.leading = 14

    story = []

    if title:
        title_style = styles.get("Title", normal)
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 8))

    for block in blocks:
        if block['type'] == 'text':
            text = block['content'].strip()
            if not text:
                continue
            para = Paragraph(text.replace('\n', '<br/>'), normal)
            story.append(para)
            story.append(Spacer(1, 10))

        elif block['type'] == 'table':
            data = block['content']
            if not data:
                continue

            is_division = block.get('division', False)
            is_suma = block.get('suma', False)
            is_resta = block.get('resta', False)
            is_factorial = block.get('factorial', False)
            is_raiz = block.get('raiz', False)
            is_multiplicacion = any('X' in row for row in data)

            table_data = [[("" if cell is None else str(cell)) for cell in row] for row in data]

            usable_width = page_size[0] - 40 * mm
            num_cols = len(table_data[0])
            num_rows = len(table_data)

            # --- División ---
            if is_division:
                half_width = usable_width / 2.0
                col_widths = [half_width, half_width]

                table = Table(table_data, colWidths=col_widths, hAlign='CENTER')
                table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0, colors.white),
                    ('LINEAFTER', (0, 0), (0, 0), 1.2, colors.black),
                    ('LINEBELOW', (1, 0), (1, 0), 1.2, colors.black),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                ]))

            # --- Suma / Resta ---
            elif is_suma or is_resta:
                table = Table(table_data, colWidths=[usable_width / num_cols] * num_cols, hAlign='CENTER')
                table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0, colors.white),
                    ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                ]))

            # --- Multiplicación ---
            elif is_multiplicacion:
                table = Table(table_data, colWidths=[usable_width / num_cols] * num_cols, hAlign='CENTER')
                table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0, colors.white),
                    ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),
                    ('LINEABOVE', (0, num_rows - 1), (-1, num_rows - 1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                ]))

            # --- Factorial ---
            elif is_factorial:
                table = Table(table_data, colWidths=[usable_width / num_cols] * num_cols, hAlign='CENTER')
                table.setStyle(TableStyle([
                    ('BOX', (0, 0), (-1, -1), 0, colors.white),
                    ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
                    ('LINEBELOW', (0, num_rows - 1), (-1, num_rows - 1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                ]))

            # --- Raíz ---
                        # --- Raíz ---
            elif is_raiz:
                table_data_blank = [['' for _ in range(num_cols)] for _ in range(num_rows)]
                table = Table(table_data_blank, colWidths=[usable_width / num_cols] * num_cols, hAlign='CENTER')
                table.setStyle(TableStyle([
                    # Quitar todos los bordes
                    ('BOX', (0, 0), (-1, -1), 0, colors.white),
                    ('GRID', (0, 0), (-1, -1), 0, colors.white),
            
                    # Solo borde derecho de la celda (0,0)
                    ('LINEAFTER', (0, 0), (0, 0), 1.2, colors.black),
            
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                ]))
            
            
            # --- Tablas normales ---
            else:
                table = Table(table_data, colWidths=[usable_width / num_cols] * num_cols, hAlign='CENTER')
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
                ]))

            story.append(table)
            story.append(Spacer(1, 10))

    doc.build(story)
