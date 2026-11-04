# 🐾 GatosPiuPiu Deluxe v3.0 🔫

*Donde la agilidad felina se encuentra con el caos láser.*

**GatosPiuPiu Deluxe** es un frenético juego de disparos arcade (*top-down shooter*) desarrollado en **Pygame** y portado para ejecutarse en la web mediante **HTML5/Canvas**. Concebido y estructurado con el apoyo del modelo de IA **Claude**, el juego combina mecánicas clásicas de *bullet hell* y *roguelite* con una dirección de arte enfocada en michis armados hasta los dientes.

---

## 📸 Vista Previa y Concepto

En **GatosPiuPiu Deluxe**, tomas el control de uno de los 5 gatos con habilidades únicas para enfrentarte a hordas implacables de ratones, perros, erizos, búhos y colosales jefes finales. Explora biomas, desbloquea armas en el cofre misterioso, mejora tus atributos en el árbol de habilidades y activa la **Fiebre Felina** para desatar la máxima destrucción.

---

## ⚡ Características Principales

- **5 Clases de Gatos Unicas**:
  - 🍊 **Gato Naranja**: *Una Sola Neurona* — Daño x2 durante 5 segundos.
  - 🐈‍⬛ **Gato Negro**: *Mala Suerte* — Invulnerabilidad temporal (3 s).
  - 🐱 **Gato Gordo**: *Pisotón Corporal* — Ataque en área destructivo.
  - 🦲 **Gato Calvo**: *Reflejo Cegador* — Aturde a todos los enemigos cercanos.
  - 😼 **Gato Siamés**: *Súper Salto* — Dash invulnerable de alta velocidad.
- **Arsenal Extenso & Sistema de Rareza**: 10 tipos de armas (Pistola, Subfusil, Escopeta, Ballesta, Láser, Lanzallamas, Bazuca, etc.) en 4 categorías de rareza (**Común, Rara, Épica, Legendaria**) con efectos elementales como *Fuego*, *Hielo* y *Rayo*.
- **Mecánicas Ágiles de Combate**:
  - ⚔️ **Ataque con Katana**: Refleja o barre hordas en un ángulo determinado.
  - 🔄 **Rodada de Esquive**: Otorga fotogramas de invulnerabilidad (*i-frames*).
  - 🧨 **Granadas de Mano**: Control de masas explosivo.
  - 🌈 **Fiebre Felina**: Barra de furia que otorga modos especiales (ataques instantáneos, ondas expansivas o proyectiles extra).
- **Progreso Roguelite**: Sube de nivel derrotando enemigos para gastar puntos en el **Árbol de Habilidades** (Fuerza, Agilidad, Vitalidad, Crítico, Regeneración, Imán, etc.).
- **Variedad de Enemigos y Jefes**: 8 tipos de enemigos estándar (con mecánicas de escudos y embestidas) y 6 **Jefes Colosales** con patrones de ataques complejos (rayos láser, lluvias de espinas, invocaciones).
- **Entornos Dinámicos**: 4 biomas (Jardín, Tundra, Desierto, Volcán) con elementos interactivos como barriles explosivos, charcos de lodo y hielo.

---

## 🕹️ Controles del Juego

| Acción | Tecla / Control |
| :--- | :--- |
| **Movimiento** | `W` `A` `S` `D` o Flechas de dirección |
| **Apuntar y Disparar** | Mouse (Clic izquierdo) |
| **Habilidad Especial del Gato** | `Espacio` |
| **Ataque con Katana** | `Z` |
| **Rodada de Esquive** | `Q` |
| **Lanzar Granada** | `G` |
| **Comprar / Recoger Item** | `E` |
| **Soltar Arma** | `G` (Menú/Suelo) |
| **Árbol de Habilidades** | `Tab` |
| **Menú de Inventario** | `I` |
| **Cambiar Arma** | `1` a `5` o Rueda del Mouse |
| **Pausa** | `Esc` |
| **Pantalla Completa** | `F11` |

---

## 🛠️ Requisitos e Instalación

Este proyecto cuenta con dos implementaciones independientes: la versión autónoma **HTML5/JS Canvas** y el código fuente en **Python / Pygame**.

### 1. Ejecutar la versión Web (HTML)
No requiere instalación.
1. Abre el archivo `GATOSPIUPIU_DELUXE_v3.0..html` en cualquier navegador moderno (Chrome, Firefox, Edge, Safari).
2. ¡Empieza a jugar directamente!

### 2. Ejecutar la versión Python (Pygame)

#### Requisitos previos
- **Python 3.8+** instalado.
- Biblioteca **Pygame**.

#### Pasos para la ejecución

1. Clona este repositorio o descarga los archivos:
   ```bash
   git clone https://github.com/tu-usuario/gatospiupiu-deluxe.git
   cd gatospiupiu-deluxe
   ```

2. Instala Pygame mediante `pip`:
   ```bash
   pip install pygame
   ```

3. Ejecuta el archivo principal:
   ```bash
   python GATOSPIUPIU_codigobase.py
   ```

---

## 📂 Estructura del Proyecto

```
GatosPiuPiu-Deluxe/
├── GATOSPIUPIU_DELUXE_v3.0..html # Versión monolítica para navegador (Canvas + JS + Audio Synthesizer)
├── GATOSPIUPIU_codigobase.py     # Motor en Python con Pygame
└── README.md                     # Documentación oficial
```

---

## 🤖 Créditos y Co-Creación

- **Concepto y Diseño Original**: Creado por amantes de los gatos (Leonardo Peltz Macias) y los shooters retro.
- **Desarrollo y Asistencia de IA**: Co-diseñado con la **Mano de Claude**, optimizando la arquitectura del *game loop*, algoritmos de colisión, patrones de ataque de los jefes e implementación de audio en tiempo real con la Web Audio API.

---

## 📜 Licencia

Este proyecto está bajo la Licencia **MIT**. ¡Siéntete libre de modificarlo, mejorarlo y añadir más michis al caos!
