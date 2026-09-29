# OCR con IA desde Google Colab

OCR de PDFs con **PaddleOCR-VL**, corriendo gratis en Google Colab. Funciona bien con tablas y soporta español.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NikoSwami/orc-con-ia-desde-google-colab/blob/main/OCR_con_IA.ipynb)

## Uso

1. Abrí el notebook con el botón de arriba.
2. `Entorno de ejecución` → `Cambiar tipo de entorno` → **GPU (T4)**.
3. Elegí dónde guardar (celda 1, ver abajo).
4. Corré las celdas en orden.
5. Subí tus PDFs cuando la celda 4 abra el diálogo. Podés marcar varios con Ctrl+click.

El resultado sale en Markdown, con las tablas ya armadas.

## Las dos formas de usarlo

En la celda 1 hay una sola opción que cambiar:

### `USAR_DRIVE = False` — todo en la máquina virtual

No pide permisos de Google Drive. Todo vive en el disco temporal de Colab.

Al cerrar o reiniciar el entorno se borra, así que la próxima vez vuelve a descargar ~3 GB entre librerías y modelo (5–10 minutos).

Conviene si vas a probar una vez, o si no querés dar acceso a tu Drive.

### `USAR_DRIVE = True` — guardar todo en Drive

Pide permiso para montar tu Drive y crea esta estructura:

```
MyDrive/ocr_ia/
  paquetes/      librerías instaladas
  pip_cache/     descargas de pip
  huggingface/   pesos del modelo
  paddlex/       modelos de layout
  resultados/    los .md de cada corrida
```

La primera vez tarda igual. De ahí en más arranca en **~1 minuto** porque no descarga nada.

Ocupa unos 4 GB en tu Drive. Conviene si vas a usarlo seguido.

## El modelo

[`PaddlePaddle/PaddleOCR-VL`](https://huggingface.co/PaddlePaddle/PaddleOCR-VL) — 0.9B parámetros, encoder visual NaViT + ERNIE-4.5-0.3B.

- 109 idiomas, español nativo
- Tablas, fórmulas y gráficos como tareas propias
- Menos de 1 GB de VRAM en reposo, ~2.5 GB de pico

Es chico a propósito: entra en una placa de 4 GB, así que si después querés bajarlo a tu máquina, corre.

## Opciones

| Variable | Celda | Qué hace |
|---|---|---|
| `USAR_DRIVE` | 1 | Guardar en Drive o solo en la VM |
| `CARPETA_DRIVE` | 1 | Dónde guardar dentro de tu Drive |
| `PAGINAS_MAX` | 1 | Páginas por PDF. `0` procesa el documento completo |

## Problemas conocidos

**La instalación de Paddle se corta con `ReadTimeoutError`.** La versión GPU no está en PyPI: sale de un CDN de Baidu que desde fuera de China corta la descarga del wheel de 565 MB. El notebook ya reintenta tres veces con timeouts largos y pip reanuda lo que quedó a medias. Si aun así falla, cae solo a Paddle CPU: el OCR funciona igual, más lento.

**Un PDF rompe el proceso.** No corta el lote. Se anota el error y sigue con el siguiente.

**Las descargas múltiples no llegan.** Los navegadores bloquean descargas seguidas. Con más de un PDF, el notebook baja un zip único.

## Licencia

MIT
