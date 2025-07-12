import numpy as np


def total_area_normalization(X: np.ndarray, scale_to: float = 100.0) -> np.ndarray:
    """
    Normaliza cada espectro por el área total bajo la curva y escala a un valor específico.

    Parámetros:
    X -- Matriz de espectros con forma (n_muestras, n_puntos)
    scale_to -- Valor al que se escalará el área total (por defecto 100)

    Retorna:
    Matriz normalizada donde cada espectro suma `scale_to`
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    # Calcular suma por muestra (eje 1)
    row_sums = np.sum(X, axis=1)

    # Evitar división por cero (reemplazar ceros por un valor pequeño)
    row_sums[row_sums == 0] = 1e-10

    # Normalizar y escalar
    return (X / row_sums[:, np.newaxis]) * scale_to


def pqn_normalization(X: np.ndarray) -> np.ndarray:
    """
    Implementa la Normalización Probabilística de Cocientes (PQN).

    Parámetros:
    X -- Matriz de espectros con forma (n_muestras, n_puntos)

    Retorna:
    Matriz normalizada usando el método PQN
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    # Calcular espectro de referencia (mediana de todas las muestras)
    referencia = np.median(X, axis=0)

    # Evitar ceros en la referencia
    referencia[referencia == 0] = 1e-10

    # Calcular cocientes para cada punto
    cocientes = X / referencia

    # Calcular factor de normalización (mediana de los cocientes por muestra)
    factores = np.median(cocientes, axis=1)

    # Evitar división por cero
    factores[factores == 0] = 1e-10

    # Aplicar normalización
    return X / factores[:, np.newaxis]


def vector_normalization(X: np.ndarray) -> np.ndarray:
    """
    Normaliza cada espectro por su norma euclidiana (longitud del vector).

    Parámetros:
    X -- Matriz de espectros con forma (n_muestras, n_puntos)

    Retorna:
    Matriz normalizada donde cada espectro tiene norma 1
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    # Calcular norma euclidiana para cada muestra
    normas = np.linalg.norm(X, axis=1)

    # Evitar división por cero
    normas[normas == 0] = 1e-10

    return X / normas[:, np.newaxis]


def internal_standard_normalization(
        X: np.ndarray,
        ppm: np.ndarray,
        ppm_min: float,
        ppm_max: float,
        metodo_integral: str = 'suma'
) -> np.ndarray:
    """
    Normaliza usando un estándar interno en una región específica del espectro.

    Parámetros:
    X -- Matriz de espectros con forma (n_muestras, n_puntos)
    ppm -- Vector de desplazamientos químicos
    ppm_min -- Límite inferior de la región de referencia
    ppm_max -- Límite superior de la región de referencia
    metodo_integral -- Método para calcular el área ('suma' o 'trapezoidal')

    Retorna:
    Matriz normalizada por el área de referencia
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")
    if len(ppm) != X.shape[1]:
        raise ValueError("La longitud de ppm no coincide con la dimensión de los espectros")
    if ppm_min >= ppm_max:
        raise ValueError("ppm_min debe ser menor que ppm_max")

    # Crear máscara para la región de interés
    mascara = (ppm >= ppm_min) & (ppm <= ppm_max)

    if not np.any(mascara):
        raise ValueError(f"No hay puntos en el rango [{ppm_min}, {ppm_max}] ppm")

    # Calcular área de referencia para cada muestra
    areas_ref = np.sum(X[:, mascara], axis=1)

    # Manejar áreas cero o negativas
    areas_ref[areas_ref <= 0] = 1e-10

    return X / areas_ref[:, np.newaxis]


def normalize(
        X: np.ndarray,
        method: str = 'pqn',
        ppm: np.ndarray = None,
        **kwargs
) -> np.ndarray:
    """
    Función unificada para aplicar diferentes métodos de normalización.

    Parámetros:
    X -- Matriz de espectros
    method -- Método a usar: 'total_area', 'pqn', 'vector', 'internal_standard'
    ppm -- Vector ppm (requerido solo para internal_standard)
    kwargs -- Argumentos adicionales específicos del método

    Retorna:
    Matriz normalizada
    """
    method = method.lower()

    if method == 'total_area':
        return total_area_normalization(X, **kwargs)
    elif method == 'pqn':
        return pqn_normalization(X)
    elif method == 'vector':
        return vector_normalization(X)
    elif method == 'internal_standard':
        if ppm is None:
            raise ValueError("Se requiere el vector ppm para normalización por estándar interno")
        return internal_standard_normalization(X, ppm, **kwargs)
    else:
        raise ValueError(f"Método de normalización no reconocido: {method}")
