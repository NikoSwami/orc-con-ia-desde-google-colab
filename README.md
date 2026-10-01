# OCR con IA desde Google Colab

OCR de PDFs con **PaddleOCR-VL-1.5**, corriendo gratis en Google Colab. Funciona bien con tablas y soporta español.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NikoSwami/orc-con-ia-desde-google-colab/blob/main/OCR_con_IA.ipynb)

## Uso

1. Abrí el notebook con el botón de arriba.
2. `Entorno de ejecución` → `Cambiar tipo de entorno` → **GPU (T4)**.
3. Elegí dónde guardar (celda 1, ver abajo).
4. Corré las celdas en orden.
5. Subí tus PDFs cuando la celda 4 abra el diálogo. Podés marcar varios con Ctrl+click.

El resultado sale en Markdown, con las tablas ya armadas.

## Formato de salida

El modelo devuelve las tablas como bloques `<table><tr><td>` y deja `<div>` y
`<br>` sueltos. Eso no es Markdown, es HTML dentro de un `.md`.

| Valor | Que sale |
|---|---|
| `md` (por defecto) | Markdown puro: tablas de pipes, sin HTML, entidades ya resueltas (`N&deg;` queda `N°`) |
| `crudo` | La salida del modelo tal cual, con las tablas en HTML |

En el notebook se elige con `FORMATO` en la celda 1. En el script local, con
`-f md` o `-f crudo`.

Con `md` los `![](imgs/...)` tambien se reescriben para que apunten bien desde
el archivo final, que queda un nivel arriba de donde el modelo dejo los recortes.

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

[`PaddlePaddle/PaddleOCR-VL-1.5`](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.5) — 0.9B parámetros, encoder visual NaViT + ERNIE-4.5-0.3B.

- **94.5% en OmniDocBench v1.5**
- 109 idiomas, español nativo
- Tablas, fórmulas, gráficos, sellos y text spotting como tareas propias
- Menos de 1 GB de VRAM en reposo, ~2.5 GB de pico

Es chico a propósito: entra en una placa de 4 GB, así que si después querés bajarlo a tu máquina, corre.

Se selecciona con `pipeline_version='v1.5'` en la celda 3. Ya existe una **1.6**; para usarla, cambiá ese valor.

## Correrlo en tu PC

En `local/` hay un script de linea de comandos con el mismo modelo, sin Colab.
La conversion a Markdown vive aparte, en `local/a_markdown.py`.

### Instalar

Windows:

```powershell
cd local
.\instalar.ps1
```

Linux o macOS:

```bash
cd local
bash instalar.sh
```

Sin GPU, agregale `-Cpu` en Windows o `--cpu` en Linux/macOS.

Requiere Python 3.9 a 3.13 (64 bits). El script crea un entorno virtual en
`local/.venv` e instala todo ahi.

### Usar

```bash
python ocr_local.py mis_pdfs/
```

Acepta archivos sueltos, carpetas y comodines. Por cada entrada deja un
`<nombre>_ocr.md` en la carpeta de salida, y al final imprime una tabla con
tiempo, caracteres y filas de tabla de cada uno.

| Opcion | Que hace |
|---|---|
| `-s`, `--salida` | Carpeta de resultados. Por defecto `salida_ocr` |
| `-p`, `--paginas` | Maximo de paginas por PDF. `0` = todas |
| `-v`, `--version` | Version del pipeline: `v1`, `v1.5`, `v1.6` |
| `-d`, `--dispositivo` | Forzar `gpu` o `cpu` |
| `-r`, `--recursivo` | Entrar en subcarpetas |
| `-f`, `--formato` | `md` (por defecto) o `crudo`. Ver arriba |
| `--sin-imagenes` | Quitar los recortes de imagen del `.md` final |
| `--json` | Guardar tambien el JSON de layout |

Ejemplos:

```bash
python ocr_local.py escaneos/ -r -s resultados
python ocr_local.py boletin.pdf -p 3
python ocr_local.py "facturas/*.pdf" -d cpu
python ocr_local.py acta.pdf -f crudo
python ocr_local.py acta.pdf --sin-imagenes
```

Si un archivo falla, se anota y sigue con el siguiente. El script termina con
codigo 1 si hubo algun error, asi se puede encadenar en un script mayor.

Formatos que acepta: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp`.

## Opciones del notebook

| Variable | Celda | Qué hace |
|---|---|---|
| `USAR_DRIVE` | 1 | Guardar en Drive o solo en la VM |
| `CARPETA_DRIVE` | 1 | Dónde guardar dentro de tu Drive |
| `PAGINAS_MAX` | 1 | Páginas por PDF. `0` procesa el documento completo |
| `FORMATO` | 1 | `md` o `crudo` |

## Problemas conocidos

**La instalación de Paddle se corta con `ReadTimeoutError`.** La versión GPU no está en PyPI: sale de un CDN de Baidu que desde fuera de China corta la descarga del wheel de 565 MB. El notebook ya reintenta tres veces con timeouts largos y pip reanuda lo que quedó a medias. Si aun así falla, cae solo a Paddle CPU: el OCR funciona igual, más lento.

**Un PDF rompe el proceso.** No corta el lote. Se anota el error y sigue con el siguiente.

**Las descargas múltiples no llegan.** Los navegadores bloquean descargas seguidas. Con más de un PDF, el notebook baja un zip único.

**Cambiaste de versión del modelo y sigue usando la vieja.** Con `USAR_DRIVE = True`, borrá `MyDrive/ocr_ia/paquetes/.ok` para que reinstale.

## Licencia

MIT
