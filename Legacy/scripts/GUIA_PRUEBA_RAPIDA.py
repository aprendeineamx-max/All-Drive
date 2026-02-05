#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUÍA DE PRUEBA RÁPIDA - Desmontar Específico por Letra
========================================================

Sigue estos pasos para verificar que todo funciona correctamente:
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    🧪 GUÍA DE PRUEBA RÁPIDA                              ║
║                  Desmontar Específico por Letra                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 PRUEBA 1: Desmontar Botón Naranja (Específico)
════════════════════════════════════════════════════════════════════════════

1. Abre la app: py app.py
2. Ve a la pestaña "Montar Disco"
3. Click en "🔍 Detectar Unidades Montadas"
4. Deberías ver botones naranjas (ej: 🗑️ Desmontar V:, W:, Y:)

PRUEBA:
  ✅ Click en 🗑️ Desmontar V:
  ✅ Verifica que SOLO V se desmonta
  ✅ W: y Y: siguen en la lista (si estaban montadas)
  ✅ El botón naranja de V: DESAPARECE
  ✅ Los botones de W: y Y: PERMANECEN

RESULTADO ESPERADO:
  ┌────────────────────────────────┐
  │ 🎯 Desmontar Unidades Específicas: │
  │ (Solo se ven W: y Y:)           │
  │ 🗑️ Desmontar W:                 │
  │ 🗑️ Desmontar Y:                 │
  └────────────────────────────────┘


📋 PRUEBA 2: Sincronización de Botones al Cambiar Letra
════════════════════════════════════════════════════════════════════════════

1. En "Configuración de Montaje", tienes un ComboBox de letra
2. Actualmente seleccionada: V (o la que esté)

PRUEBA:
  ✅ Si V: está montada → 🔌 Desmontar Unidad = AZUL (habilitado)
  ✅ Si cambias a W: → busca si W está montada
  ✅ Si W: está montada → 🔌 Desmontar Unidad = AZUL (habilitado)
  ✅ Si cambias a Z: (no montada) → 🔌 Desmontar Unidad = GRIS (deshabilitado)

RESULTADO ESPERADO:
  ┌────────────────────────────────┐
  │ Letra de Unidad: V ▼           │
  │ ✅ Unidad V: está montada       │
  │ 🔗 Montar como Unidad (gris)   │
  │ 🔌 Desmontar Unidad (azul)     │
  │                                │
  │ (cambias a Z)                  │
  │ Letra de Unidad: Z ▼           │
  │ ⭕ Unidad Z: no está montada    │
  │ 🔗 Montar como Unidad (verde)  │
  │ 🔌 Desmontar Unidad (gris)     │
  └────────────────────────────────┘


📋 PRUEBA 3: Botón "Desmontar Unidad" - Específico
════════════════════════════════════════════════════════════════════════════

Supón que tienes:
  - V: montada
  - W: montada
  - X: disponible (no montada)

PRUEBA:
  1. Selecciona W: en el ComboBox
  2. Verifica que 🔌 Desmontar Unidad está HABILITADO (azul)
  3. Click en 🔌 Desmontar Unidad
  4. Deberías ver: "🔄 Desmontando unidad W:..."
  5. Después de 2 segundos:
     ✅ W: está DESMONTADA
     ✅ V: SIGUE MONTADA
     ✅ El botón en la lista de detectados DESAPARECE
     ✅ El botón 🔌 Desmontar Unidad se pone GRIS (deshabilitado)
     ✅ El botón 🔗 Montar como Unidad se pone VERDE (habilitado)

RESULTADO ESPERADO:
  Antes:
  ┌────────────────────────────────┐
  │ W: está montada        ✅       │
  │ 🔗 Montar (gris)               │
  │ 🔌 Desmontar (azul)            │
  │ 🗑️ Desmontar W: (naranja)      │ ← En lista de detectados
  └────────────────────────────────┘

  Después de desmontar:
  ┌────────────────────────────────┐
  │ W: no está montada     ⭕       │
  │ 🔗 Montar (verde)              │
  │ 🔌 Desmontar (gris)            │
  │ (botón naranja desaparece)     │
  └────────────────────────────────┘


📋 PRUEBA 4: Sin Interferencias - Desmontar No Afecta Otras Unidades
════════════════════════════════════════════════════════════════════════════

ESCENARIO:
  - V: montada con bucket "backups"
  - W: montada con bucket "documentos"
  - Y: montada con bucket "fotos"

PRUEBA:
  1. Detecta las tres unidades
  2. Ves tres botones naranjas
  3. Click en 🗑️ Desmontar V:
  4. Espera 2 segundos

RESULTADO ESPERADO:
  ✅ V: se desmonta
  ✅ W: SIGUE montada (con sus archivos accesibles)
  ✅ Y: SIGUE montada (con sus archivos accesibles)
  ✅ Solo desaparece el botón naranja de V
  ✅ Botones de W y Y permanecen


📋 PRUEBA 5: Remonta la Unidad Desmontada
════════════════════════════════════════════════════════════════════════════

Después de desmontar V:

PRUEBA:
  1. Selecciona V: en "Configuración de Montaje"
  2. Verifica que 🔌 Desmontar está GRIS
  3. Verifica que 🔗 Montar está VERDE
  4. Click en 🔗 Montar como Unidad
  5. Espera 5 segundos para que se monte

RESULTADO ESPERADO:
  ✅ V: se monta nuevamente
  ✅ Después de 3 segundos:
  ✅ El botón naranja de V: reaparece en la lista
  ✅ El botón 🔌 Desmontar se pone AZUL
  ✅ El botón 🔗 Montar se pone GRIS


╔════════════════════════════════════════════════════════════════════════════╗
║                           🎯 CHECKLIST FINAL                              ║
╚════════════════════════════════════════════════════════════════════════════╝

Marca los que funcionan:

□ Botón naranja solo desmonta ESA letra, no las demás
□ Al cambiar de letra en ComboBox, botones se actualizan
□ Si letra está montada → Desmontar Unidad = AZUL (habilitado)
□ Si letra NO está montada → Desmontar Unidad = GRIS (deshabilitado)
□ Presionar "Desmontar Unidad" desmonta SOLO esa letra
□ Después de desmontar, botón naranja desaparece de lista
□ Las demás unidades siguen funcionando sin interferencia
□ Se puede remonta la misma letra sin reiniciar


═══════════════════════════════════════════════════════════════════════════════

🚀 Si TODO funciona: ¡La sincronización está PERFECTA! ✅
""")
