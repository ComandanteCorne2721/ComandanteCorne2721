# Progreso DragonToys — formato estándar (actualizado por Claude Code en la nube)

Estándar aplicado (referencia: Marvel 2 Parte 20, pág 2):
- Individual: figura grande en el arco (marco top 243.58, alto 728.42), SOLO el nombre
  en negrita, tamaño 56, centrado, top 983 (nombres largos: 2 líneas, line_height 0.85, top 972).
- Grillas: arco blanco por figura, foto limpia, sin rótulos.

## Hecho
- Marvel 2 Parte 20 (DAHXGs1WF0w): 24 nombres a 56 — COMPLETO, guardado.
- Star Wars 1 Parte 1 (DAHOWIqoenU): nombres a 56 en págs 2-10, 12, 14 — guardado.

## Hallazgos del barrido (46 diseños en carpeta Star Wars FAHOWIkNLqs)
- Ya con marco estándar y nombre autoajustado (hay que llevar a 56):
  SW1 P1 (págs 2-30), SW1 P10 (págs 2-30), "Star Wars - Varios 2026" (11 págs), "Varios 2026 (Parte 2)".
- Formato anterior (marco 266-913, nombre "ultrabold" en y=915, rótulos del proveedor en la foto):
  resto de SW1/SW2/SW3/Stormtrooper (~34 diseños). Requieren reencuadre + limpieza de rótulos.
- Faltantes / Faltantes 2: solo imágenes sin texto (no son catálogo).
- Lightsaber (47.º diseño): no está en la carpeta Star Wars; pendiente de ubicar.
- Stormtrooper Partes 11-14: no se pudieron leer (límite de transacciones de Canva); repetir.
- Límite de Canva: "too many requests" al abrir muchas transacciones de lectura a la vez.

## Scripts
- scripts/fit_figure.py: detecta la figura en la miniatura y calcula marco/imageBox estándar y parches.

## Actualización (Canva se desconectó, pide reautorizar)
Guardado en Canva:
- Marvel 2 P20: 24 nombres a 56.
- SW1 P1 (DAHOWIqoenU): nombres a 56 en págs 2-10, 12, 14-30 (todas las de marco estándar).
SIN guardar (se perdió con la transacción): págs 32 y 33 de SW1 P1 (limpieza de foto + parche).
Pendiente SW1 P1: págs 13, 31-40 (formato antiguo: foto con rótulo WMxxx, nombre en y=915) y grillas 1, 11, 21, 31.

## Receta que funcionó (formato antiguo -> estándar)
1. remove-background sobre la foto (mediaId del marco) -> imagen limpia (quita rótulo; deja recuadros de accesorio).
2. update_fill del marco con la imagen nueva; marco left 230-250, ancho ~600-620, top 243.58, alto 728.42.
3. insert_shape rect blanco (192,640,696x440) detrás para tapar la marca tenue "XXXX"; layer_element front a foto y nombre.
4. crop_media explícito (resize no escala la imagen): top 0..40, left 0..6, ancho/alto = marco.
5. Recuadros de accesorios (Rey, Kylo, Drak Rey, Palpatine con rótulo): parche blanco con scripts/arch_patch.py (recortado al arco).
6. Nombre: 56 bold, left 160, ancho 760, top 983.
Límite Canva: "too many requests" si se abren >~10 transacciones de lectura seguidas.
