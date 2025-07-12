import numpy as np


def log_transform(X: np.ndarray, epsilon: float = 1e-6, base: str = 'e') -> np.ndarray:
    """
    Aplica transformación logarítmica a los datos.

    Parámetros:
    X -- Matriz de datos con forma (n_muestras, n_características)
    epsilon -- Valor pequeño para evitar log(0) (por defecto 1e-6)
    base -- Base del logaritmo: 'e' (natural), '2' (binario), '10' (decimal)

    Retorna:
    Matriz transformada
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")
    if epsilon <= 0:
        raise ValueError("epsilon debe ser mayor que cero")

    # Aplicar desplazamiento para evitar valores <= 0
    X_shifted = X.copy()
    min_val = np.min(X)
    if min_val <= 0:
        X_shifted = X_shifted - min_val + epsilon

    # Seleccionar base logarítmica
    if base == 'e':
        return np.log(X_shifted)
    elif base == '2':
        return np.log2(X_shifted)
    elif base == '10':
        return np.log10(X_shifted)
    else:
        raise ValueError(f"Base logarítmica no soportada: {base}")


def glog_transform(
        X: np.ndarray,
        lambda_val: float = 1.0,
        epsilon: float = 1e-6
) -> np.ndarray:
    """
    Aplica la transformación logarítmica generalizada (glog).

    La transformación glog se define como:
        glog(x) = log((x + sqrt(x² + lambda²)) / 2)

    Es equivalente a arcsinh(x/lambda)/log(2) pero más estable numéricamente.

    Parámetros:
    X -- Matriz de datos
    lambda_val -- Parámetro de transformación (por defecto 1.0)
    epsilon -- Valor pequeño para estabilizar (por defecto 1e-6)

    Retorna:
    Matriz transformada
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")
    if lambda_val <= 0:
        raise ValueError("lambda_val debe ser mayor que cero")

    # Calcular el término dentro de la raíz cuadrada
    X_sq = X ** 2
    lambda_sq = lambda_val ** 2

    # Evitar problemas numéricos con valores muy pequeños
    inside_sqrt = X_sq + lambda_sq + epsilon

    # Calcular la transformación glog
    return np.log((X + np.sqrt(inside_sqrt)) / (2 * lambda_val))


def sqrt_transform(X: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    """
    Aplica transformación raíz cuadrada a los datos.

    Parámetros:
    X -- Matriz de datos
    epsilon -- Valor pequeño para estabilizar (por defecto 1e-6)

    Retorna:
    Matriz transformada
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    # Manejar valores negativos
    X_shifted = X.copy()
    min_val = np.min(X)
    if min_val < 0:
        X_shifted = X_shifted - min_val + epsilon

    return np.sqrt(X_shifted)


def transform(
        X: np.ndarray,
        method: str = 'glog',
        **kwargs
) -> np.ndarray:
    """
    Función unificada para aplicar diferentes transformaciones.

    Parámetros:
    X -- Matriz de datos
    method -- Método a usar: 'log', 'glog', 'sqrt', o 'none'
    kwargs -- Argumentos adicionales específicos del método

    Retorna:
    Matriz transformada
    """
    method = method.lower()

    if method == 'none' or method is None:
        return X.copy()
    elif method == 'log':
        return log_transform(X, **kwargs)
    elif method == 'glog':
        return glog_transform(X, **kwargs)
    elif method == 'sqrt':
        return sqrt_transform(X, **kwargs)
    else:
        raise ValueError(f"Método de transformación no reconocido: {method}")
