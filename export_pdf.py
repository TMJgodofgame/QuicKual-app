"""
Módulo para exportar el contenido de QuicKual a PDF usando ReportLab.
Extrae bloques de texto y tablas del frame de Tkinter y los renderiza con estilos específicos.
"""

import tkinter as tk
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from typing import List, Dict, Any


def _safe_get_text(widget: tk.Widget) -> str:
    """
    Extrae texto de Entry, Label o busca recursivamente en subwidgets.
    """
    try:
        if isinstance(widget, tk.Entry):
            return widget.get()
        if isinstance(widget, tk.Label):
            return widget.cget('text')
        # Buscar recursivamente en hijos
        text = ""
        for sub in widget.winfo_children():
            text += _safe_get_text(sub)
        return text
    except Exception:
        return ""


def extract_document_structure(scrollable_frame: tk.Frame) -> List[Dict[str, Any]]:
    """
    Extrae la estructura del documento desde el frame scrollable de Tkinter.

    Args:
        scrollable_frame: Frame de Tkinter que contiene los bloques del documento.

    Returns:
        Lista de diccionarios representando cada bloque (texto o tabla).
    """
    blocks: List[Dict[str, Any]] = []

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

        # Bloques de tabla: buscar widgets en grid (incluyendo subwidgets)
        cell_widgets = []
        max_row = -1
        max_col = -1

        for w in children:
            # Buscar en subwidgets (para capturar el frame "content")
            if w.winfo_children():
                for sw in w.winfo_children():
                    try:
                        gi = sw.grid_info()
                    except Exception:
                        gi = {}

                    if gi:
                        try:
                            r = int(gi.get('row', 0))
                            c = int(gi.get('column', 0))
                        except Exception:
                            r, c = 0, 0

                        cell_widgets.append((r, c, sw))
                        max_row = max(max_row, r)
                        max_col = max(max_col, c)

            # También intentar con el widget mismo
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
                max_row = max(max_row, r)
                max_col = max(max_col, c)

        if not cell_widgets:
            # Si no hay grid, intentar extraer texto plano
            text = "".join(_safe_get_text(w) for w in children).strip()
            if text:
                blocks.append({'type': 'text', 'content': text})
            continue

        rows = max_row + 1
        cols = max_col + 1
        matrix = [['' for _ in range(cols)] for _ in range(rows)]

        # Heurísticas de detección (reiniciar flags)
        is_division = False
        is_suma = False
        is_resta = False
        is_factorial = False
        is_raiz = False
        is_binario = False
        is_multiplicacion = False

        # Rellenar matriz
        for r, c, w in cell_widgets:
            txt = _safe_get_text(w)
            matrix[r][c] = txt

        # Utilidades
        def is_int_str(s: str) -> bool:
            s = s.strip()
            if not s:
                return False
            if s.startswith('-'):
                s = s[1:]
            return s.isdigit()

        def digits_only(s: str) -> str:
            return ''.join(ch for ch in s if ch.isdigit())

        # Conteos útiles
        flat = [str(matrix[r][c]).strip() for r in range(rows) for c in range(cols)]
        count_twos = sum(1 for v in flat if v == '2')
        has_sqrt_symbol = any('√' in v for v in flat)

        # División: 2 columnas y primera fila con números
        if cols == 2 and rows >= 1:
            c0_text = matrix[0][0].strip()
            c1_text = matrix[0][1].strip()
            if is_int_str(c0_text) and is_int_str(c1_text):
                is_division = True

        # Suma/Resta: símbolo en primera col (± en primeras filas)
        for r in range(min(rows, 4)):
            sym = matrix[r][0].strip() if cols > 0 else ""
            if sym == "+":
                is_suma = True
            if sym == "-":
                is_resta = True

        # Multiplicación: 'X' o 'x' en primera columna
        for r in range(rows):
            if cols > 0 and ('X' in str(matrix[r][0]) or 'x' in str(matrix[r][0])):
                is_multiplicacion = True
                break

        # Factorial: cualquier '!'
        is_factorial = any('!' in v for v in flat)

        # BINARIO - detección fuerte
        first_row_is_int = cols > 0 and rows > 0 and is_int_str(matrix[0][0])
        rows_with_two = {r for r in range(rows) if any((str(matrix[r][c]).strip() == '2') for c in range(cols))}
        first_row_col1_is_two_or_empty = (cols > 1 and (matrix[0][1].strip() in ('', '2'))) or (cols == 1)
        binario_strong = (first_row_is_int and count_twos >= 2 and len(rows_with_two) >= 2 and first_row_col1_is_two_or_empty)

        # RAÍZ - detección estricta si no hay símbolo √
        raiz_strict = False
        if not has_sqrt_symbol:
            if cols >= 3 and rows >= 1:
                c00_digits = digits_only(matrix[0][0])
                c01_digits = digits_only(matrix[0][1]) if cols > 1 else ''
                looks_like_index = 1 <= len(c00_digits) <= 2
                looks_like_radicand = len(c01_digits) >= 1
                # verificar "barra vertical" en col 2: contenido no vacío en ≥2 filas contiguas
                streak = 0
                max_streak = 0
                for rr in range(rows):
                    if matrix[rr][2].strip() != '':
                        streak += 1
                        max_streak = max(max_streak, streak)
                    else:
                        streak = 0
                has_vertical_bar = max_streak >= 2
                raiz_strict = looks_like_index and looks_like_radicand and has_vertical_bar

        # Prioridad y decisión final
        if has_sqrt_symbol and not binario_strong:
            is_raiz = True
        elif binario_strong:
            is_binario = True
        elif raiz_strict:
            is_raiz = True

        blocks.append({
            'type': 'table',
            'content': matrix,
            'division': is_division,
            'suma': is_suma,
            'resta': is_resta,
            'factorial': is_factorial,
            'raiz': is_raiz,
            'binario': is_binario,
            'multiplicacion': is_multiplicacion
        })

    return blocks


def export_to_pdf(scrollable_frame: tk.Frame, output_path: str = "document.pdf",
                  title: str = None, page_size=letter) -> None:
    """
    Exporta el contenido del frame scrollable a un archivo PDF.

    Args:
        scrollable_frame: Frame de Tkinter con el contenido a exportar.
        output_path: Ruta del archivo PDF de salida.
        title: Título opcional del documento.
        page_size: Tamaño de página (por defecto letter).
    """
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
            continue

        if block['type'] != 'table':
            continue

        data = block['content'] or []
        if not data:
            continue

        is_division = block.get('division', False)
        is_suma = block.get('suma', False)
        is_resta = block.get('resta', False)
        is_factorial = block.get('factorial', False)
        is_raiz = block.get('raiz', False)
        is_binario = block.get('binario', False)
        is_multiplicacion = block.get('multiplicacion', False)

        # Asegurar strings
        table_data = [[("" if cell is None else str(cell)) for cell in row] for row in data]

        usable_width = page_size[0] - 40 * mm
        num_cols = max(1, len(table_data[0]))
        num_rows = len(table_data)

        def col_widths(nc: int):
            w = usable_width / nc
            return [w] * nc

        # División
        if is_division:
            colw = [usable_width / 2.0, usable_width / 2.0]
            table = Table(table_data, colWidths=colw, hAlign='CENTER')
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
        # Suma/Resta
        elif is_suma or is_resta:
            table = Table(table_data, colWidths=col_widths(num_cols), hAlign='CENTER')
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
        # Multiplicación
        elif is_multiplicacion:
            table = Table(table_data, colWidths=col_widths(num_cols), hAlign='CENTER')
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
        # Factorial
        elif is_factorial:
            table = Table(table_data, colWidths=col_widths(num_cols), hAlign='CENTER')
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
        # Raíz
        elif is_raiz:
            table = Table(table_data, colWidths=col_widths(num_cols), hAlign='CENTER')
            table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0, colors.white),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEABOVE', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBEFORE', (0, 0), (-1, -1), 0, colors.white),
                ('LINEAFTER', (0, 0), (-1, -1), 0, colors.white),

                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),

                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),

                ('LINEAFTER', (0, 0), (0, 0), 1.2, colors.black),
                ('LINEABOVE', (1, 0), (1, 0), 1.2, colors.black),
                ('LINEBEFORE', (2, 0), (2, -1), 1.2, colors.black),
            ]))
        # Binario: sin ningún borde (Paso 1)
        # --- Binario: solo borde inferior en celdas con "2" (dividendo) ---
        # --- Binario: borde inferior en celdas "2" y borde derecho en la celda de su izquierda ---
        elif is_binario:
            table = Table(table_data, colWidths=col_widths(num_cols), hAlign='CENTER')

            base_styles = [
                # Sin bordes globales
                ('BOX', (0, 0), (-1, -1), 0, colors.white),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEABOVE', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBEFORE', (0, 0), (-1, -1), 0, colors.white),
                ('LINEAFTER', (0, 0), (-1, -1), 0, colors.white),

                # Tipografía y alineación
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),

                # Paddings compactos
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]

            line_width = 1.0
            line_color = colors.black

            for r in range(num_rows):
                for c in range(num_cols):
                    if str(table_data[r][c]).strip() == '2':
                        # 1) Línea inferior en la celda del "2"
                        base_styles.append(('LINEBELOW', (c, r), (c, r), line_width, line_color))
                        # 2) Borde derecho en la celda a la izquierda (si existe)
                        left_c = c - 1
                        if left_c >= 0:
                            base_styles.append(('LINEAFTER', (left_c, r), (left_c, r), line_width, line_color))

            table.setStyle(TableStyle(base_styles))
        # Tabla normal (fallback)
        else:
            table = Table(table_data, colWidths=col_widths(num_cols), hAlign='CENTER')
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