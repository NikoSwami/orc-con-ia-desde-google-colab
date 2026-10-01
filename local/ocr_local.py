"""OCR de PDFs e imagenes con PaddleOCR-VL, en local."""

from __future__ import annotations

import argparse
import glob
import os
import sys
import time

import a_markdown

EXTENSIONES = ('.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp')


def juntar_entradas(entradas, recursivo):
    rutas = []
    for entrada in entradas:
        if os.path.isdir(entrada):
            patron = '**/*' if recursivo else '*'
            for p in sorted(glob.glob(os.path.join(entrada, patron), recursive=recursivo)):
                if p.lower().endswith(EXTENSIONES):
                    rutas.append(p)
        elif os.path.isfile(entrada):
            rutas.append(entrada)
        else:
            for p in sorted(glob.glob(entrada)):
                if p.lower().endswith(EXTENSIONES):
                    rutas.append(p)
    vistos, unicas = set(), []
    for r in rutas:
        clave = os.path.abspath(r)
        if clave not in vistos:
            vistos.add(clave)
            unicas.append(r)
    return unicas


def recortar_pdf(ruta, maximo, destino):
    if not maximo or not ruta.lower().endswith('.pdf'):
        return ruta, None
    from pypdf import PdfReader, PdfWriter

    lector = PdfReader(ruta)
    total = len(lector.pages)
    if total <= maximo:
        return ruta, total
    escritor = PdfWriter()
    for pagina in lector.pages[:maximo]:
        escritor.add_page(pagina)
    corto = os.path.join(destino, f'_recorte_{os.path.basename(ruta)}')
    with open(corto, 'wb') as f:
        escritor.write(f)
    return corto, total


def cargar_pipeline(version, dispositivo):
    from paddleocr import PaddleOCRVL

    intentos = [{'pipeline_version': version, 'device': dispositivo}]
    if dispositivo is None:
        intentos = [{'pipeline_version': version}]
    intentos.append({'pipeline_version': version})
    ultimo = None
    for kwargs in intentos:
        try:
            return PaddleOCRVL(**kwargs)
        except TypeError as e:
            ultimo = e
    raise ultimo


def consolidar(carpeta, ruta_original, version, destino_md,
               formato='md', imagenes=True):
    piezas = sorted(glob.glob(os.path.join(carpeta, '**', '*.md'), recursive=True))
    if not piezas:
        return None, 0, 0
    cabecera = [
        f'# OCR de {os.path.basename(ruta_original)}',
        '',
        f'- Modelo: PaddleOCR-VL {version}',
        f'- Fecha: {time.strftime("%Y-%m-%d %H:%M")}',
        f'- Origen: `{os.path.abspath(ruta_original)}`',
        '',
        '---',
        '',
    ]
    base_destino = os.path.dirname(os.path.abspath(destino_md))
    cuerpo = []
    for pieza in piezas:
        trozo = open(pieza, encoding='utf-8').read().strip()
        if formato == 'md':
            trozo = a_markdown.reubicar_imagenes(
                trozo, os.path.dirname(os.path.abspath(pieza)), base_destino)
            trozo = a_markdown.a_markdown(trozo, imagenes)
        cuerpo.append(trozo)
    texto = '\n'.join(cabecera + cuerpo)
    with open(destino_md, 'w', encoding='utf-8') as f:
        f.write(texto)
    return destino_md, len(texto), a_markdown.contar_filas(texto)


def main():
    parser = argparse.ArgumentParser(
        description='OCR de PDFs e imagenes con PaddleOCR-VL, en local.')
    parser.add_argument('entradas', nargs='+',
                        help='Archivos, carpetas o comodines a procesar.')
    parser.add_argument('-s', '--salida', default='salida_ocr',
                        help='Carpeta donde escribir los resultados.')
    parser.add_argument('-p', '--paginas', type=int, default=0,
                        help='Maximo de paginas por PDF. 0 = todas.')
    parser.add_argument('-v', '--version', default='v1.5',
                        help='Version del pipeline: v1, v1.5, v1.6.')
    parser.add_argument('-d', '--dispositivo', choices=['gpu', 'cpu'], default=None,
                        help='Forzar GPU o CPU. Por defecto lo decide Paddle.')
    parser.add_argument('-r', '--recursivo', action='store_true',
                        help='Entrar en subcarpetas.')
    parser.add_argument('-f', '--formato', choices=['md', 'crudo'], default='md',
                        help='md = Markdown puro (tablas de pipes, sin HTML). '
                             'crudo = tal cual lo devuelve el modelo.')
    parser.add_argument('--sin-imagenes', action='store_true',
                        help='Quitar los recortes de imagen del .md final.')
    parser.add_argument('--json', action='store_true',
                        help='Guardar tambien el JSON de layout.')
    args = parser.parse_args()

    rutas = juntar_entradas(args.entradas, args.recursivo)
    if not rutas:
        print('No se encontro ningun archivo procesable.', file=sys.stderr)
        return 2

    os.makedirs(args.salida, exist_ok=True)
    print(f'Archivos a procesar: {len(rutas)}')
    print(f'Formato de salida: {args.formato}')
    print(f'Cargando PaddleOCR-VL {args.version}...')

    inicio_carga = time.time()
    pipeline = cargar_pipeline(args.version, args.dispositivo)
    print(f'Modelo listo en {time.time() - inicio_carga:.1f}s\n')

    resumen, fallidos = [], []
    inicio_lote = time.time()

    for i, ruta in enumerate(rutas, 1):
        nombre = os.path.basename(ruta)
        base = os.path.splitext(nombre)[0]
        print(f'[{i}/{len(rutas)}] {nombre}')
        try:
            carpeta = os.path.join(args.salida, base)
            os.makedirs(carpeta, exist_ok=True)
            entrada, total = recortar_pdf(ruta, args.paginas, carpeta)
            if total and args.paginas and total > args.paginas:
                print(f'        recortado a {args.paginas} de {total} paginas')

            t0 = time.time()
            for resultado in pipeline.predict(entrada):
                resultado.save_to_markdown(save_path=carpeta)
                if args.json:
                    resultado.save_to_json(save_path=carpeta)
            duracion = time.time() - t0

            destino_md = os.path.join(args.salida, base + '_ocr.md')
            md, chars, filas = consolidar(carpeta, ruta, args.version, destino_md,
                                          args.formato, not args.sin_imagenes)
            if md is None:
                raise RuntimeError('el modelo no devolvio texto')

            resumen.append((nombre, total or '-', f'{duracion:.1f}s', chars, filas))
            print(f'        ok en {duracion:.1f}s | {chars} chars | {filas} filas de tabla')
            print(f'        -> {md}')
        except Exception as e:
            fallidos.append((nombre, f'{type(e).__name__}: {e}'))
            resumen.append((nombre, '-', 'FALLO', 0, 0))
            print(f'        FALLO: {type(e).__name__}: {e}', file=sys.stderr)

    ok = len(rutas) - len(fallidos)
    print('\n' + '=' * 78)
    print(f'TERMINADO en {time.time() - inicio_lote:.1f}s | {ok} ok, {len(fallidos)} con error')
    print('=' * 78)
    print(f'{"archivo":<38} {"pags":>5} {"tiempo":>8} {"chars":>8} {"tablas":>7}')
    print('-' * 78)
    for fila in resumen:
        print(f'{str(fila[0])[:38]:<38} {str(fila[1]):>5} {str(fila[2]):>8} '
              f'{fila[3]:>8} {fila[4]:>7}')

    if fallidos:
        print('\nCon error:')
        for nombre, error in fallidos:
            print(f'  {nombre}: {error}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
