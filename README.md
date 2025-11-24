# Bond Portfolio Analysis Tool

Herramienta de análisis y gestión de carteras de renta fija, diseñada para valorar bonos, calcular métricas de riesgo (Duración, Convexidad, VaR) y construir carteras optimizadas bajo mandatos específicos.

## Instalación y Requisitos

Este proyecto requiere **Python 3.8+**.

Si encuentras errores de importación al ejecutar las celdas del notebook, asegúrate de instalar las siguientes librerías. Puedes hacerlo ejecutando el siguiente comando en tu terminal o en una celda del notebook (añadiendo `%` al principio):

```bash
pip install pandas numpy scipy matplotlib
```

## Estructura de Datos

El proyecto espera que los archivos de datos se encuentren en la carpeta `data/` con el siguiente formato específico.

### Configuración General de CSVs
*   **Separador de columnas:** `;` (punto y coma)
*   **Separador decimal:** `.` (punto)
*   **Formato de Fechas:** `DD/MM/YYYY`

### Especificación de Archivos

#### 1. `data/universo.csv`
Contiene la información estática y de mercado actual de los bonos.

*   **Columnas:**
    *   `ISIN` (Texto): Identificador único.
    *   `Description` (Texto): Nombre del bono.
    *   `Ccy` (Texto): Moneda (ej. EUR).
    *   `Price` (Decimal): Precio sucio/limpio de mercado actual.
    *   `Issuer` (Texto): Emisor.
    *   `Industry Sector` (Texto): Sector industrial.
    *   `Maturity` (Fecha): Fecha de vencimiento.
    *   `Coupon` (Decimal): Cupón anual (%).
    *   `Rating` (Texto): Calificación crediticia (ej. BBB+).
    *   `PD 1YR` (Decimal): Probabilidad de default a 1 año (puede estar en notación científica).
    *   `Outstanding Amount` (Entero/Decimal): Monto en circulación.
    *   `Callable` (Texto): 'Y' o 'N'.
    *   `Next Call Date` (Fecha): Próxima fecha de call (puede estar vacío).
    *   `Seniority` (Texto): Prelación (ej. Sr Unsecured).
    *   `Coupon Frequency` (Entero): Frecuencia de cupón.
    *   `Coupon Type` (Texto): Tipo de cupón (ej. FIXED).
    *   `First Coupon Date` (Fecha)
    *   `Penultimate Coupon Date` (Fecha)
    *   `Issue date` (Fecha)
    *   `Bid Price` (Decimal)
    *   `Ask Price` (Decimal)

#### 2. `data/precios_historicos_universo.csv`
Matriz de precios históricos de los bonos para análisis de volatilidad y backtesting.

*   **Estructura:**
    *   **Fila 1 (Cabecera):** Fechas en formato `DD/MM/YYYY`. La primera celda suele estar vacía o ser un identificador.
    *   **Filas siguientes:**
        *   **Columna 1:** Identificador del bono (ISIN + Ticker).
        *   **Columnas siguientes:** Precio del bono (Decimal) correspondiente a la fecha de la cabecera.
    *   **Valores nulos:** Representados como `#N/D`.

#### 3. `data/curvaESTR.csv`
Curva de tipos de interés libre de riesgo (Euro Short-Term Rate) para descuento de flujos.

*   **Columnas:**
    *   `Date` (Fecha): Fecha del nodo de la curva.
    *   `Market Rate` (Decimal): Tipo de mercado.
    *   `Zero Rate` (Decimal): Tipo cupón cero interpolado.
    *   `Discount` (Decimal): Factor de descuento.

#### 4. `data/precios_historicos_varios.csv`
Histórico de precios de índices de crédito y futuros de bonos gubernamentales para coberturas y benchmarking.

*   **Estructura:**
    *   **Fila 1 (Cabecera):** Nombres de los índices/activos.
        *   Ejemplos: `ITRX EUR CDSI GEN 5Y Corp`, `ITRX XOVER CDSI GEN 5Y Corp`, `DU1 Comdty` (Schatz), `OE1 Comdty` (Bobl), `RX1 Comdty` (Bund), `RECMTREU Index`.
    *   **Filas siguientes:**
        *   **Columna 1:** Fecha (`DD/MM/YYYY`).
        *   **Columnas siguientes:** Valor de cierre (Decimal).

## Uso

1.  Abre el notebook `src/TallerRF_AnálisisCartera_Enunciado.ipynb`.
2.  Asegúrate de que la carpeta `data/` contiene los archivos CSV descritos.
3.  Ejecuta las celdas secuencialmente para cargar datos, valorar bonos y generar la cartera.