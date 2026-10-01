"""Convierte la salida de PaddleOCR-VL a Markdown puro."""

from __future__ import annotations

import html
import os
import re

RE_TABLA = re.compile(r'<table\b.*?</table>', re.S | re.I)
RE_FILA = re.compile(r'<tr\b[^>]*>(.*?)</tr>', re.S | re.I)
RE_CELDA = re.compile(r'<(t[hd])\b([^>]*)>(.*?)</\1>', re.S | re.I)
RE_COLSPAN = re.compile(r'colspan\s*=\s*["\']?(\d+)', re.I)
RE_IMAGEN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
RE_BR = re.compile(r'<br\s*/?>', re.I)
RE_SOBRAS = re.compile(
    r'</?(div|span|p|font|b|i|u|em|strong|sup|sub|center|a)\b[^>]*>', re.I)


def _limpiar(bruto):
    texto = RE_BR.sub(' ', bruto)
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = html.unescape(texto)
    return ' '.join(texto.split()).replace('|', r'\|')


def _celdas(fila):
    salida = []
    for etiqueta, atributos, contenido in RE_CELDA.findall(fila):
        ancho = RE_COLSPAN.search(atributos)
        salida.append(_limpiar(contenido))
        for _ in range(int(ancho.group(1)) - 1 if ancho else 0):
            salida.append('')
    return salida


def tabla_a_pipes(bloque):
    """Pasa una tabla HTML a una tabla Markdown de pipes."""
    filas = [c for c in (_celdas(f) for f in RE_FILA.findall(bloque)) if c]
    if not filas:
        return ''
    ancho = max(len(f) for f in filas)
    filas = [f + [''] * (ancho - len(f)) for f in filas]
    if not any(c.strip() for c in filas[0]):
        filas[0] = [f'col {i + 1}' for i in range(ancho)]
    lineas = ['| ' + ' | '.join(filas[0]) + ' |', '|' + ' --- |' * ancho]
    lineas += ['| ' + ' | '.join(f) + ' |' for f in filas[1:]]
    return '\n'.join(lineas)


def reubicar_imagenes(texto, base_pieza, base_destino):
    """Reescribe los `![](imgs/...)` para que apunten bien desde el destino."""
    def cambiar(m):
        destino = m.group(2).strip()
        if destino.startswith(('http://', 'https://', 'data:', '/')):
            return m.group(0)
        absoluta = os.path.normpath(os.path.join(base_pieza, destino))
        relativa = os.path.relpath(absoluta, base_destino).replace(os.sep, '/')
        return f'![{m.group(1)}]({relativa})'
    return RE_IMAGEN.sub(cambiar, texto)


def a_markdown(texto, imagenes=True):
    """Deja Markdown puro: tablas de pipes, sin HTML suelto."""
    texto = RE_TABLA.sub(lambda m: '\n' + tabla_a_pipes(m.group(0)) + '\n', texto)
    if not imagenes:
        texto = RE_IMAGEN.sub('', texto)
    texto = RE_BR.sub('\n', texto)
    texto = RE_SOBRAS.sub('', texto)
    texto = html.unescape(texto)
    texto = re.sub(r'[ \t]+\n', '\n', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()


def contar_filas(texto):
    return sum(1 for l in texto.splitlines()
               if l.lstrip().startswith('|') and not set(l) <= set('| -'))
