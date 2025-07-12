from typing import Tuple, Optional
import numpy as np


def autoscaling(X: np.ndarray) -> np.ndarray:
    """
    Aplica autoescalado (z-score) a los datos.

    Parámetros:
    X -- Matriz de datos con forma (n_muestras, n_características)

    Retorna:
    Matriz escalada donde cada característica tiene media 0 y desviación estándar 1
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    # Calcular media y desviación estándar por característica
    means = np.mean(X, axis=0)
    stds = np.std(X, axis=0)

    # Manejar desviaciones estándar cero
    stds[stds == 0] = 1.0

    return (X - means) / stds


def pareto_scaling(X: np.ndarray) -> np.ndarray:
    """
    Aplica escalado Pareto a los datos.

    Parámetros:
    X -- Matriz de datos con forma (n_muestras, n_características)

    Retorna:
    Matriz escalada donde cada característica está centrada y dividida por sqrt(std)
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    means = np.mean(X, axis=0)
    stds = np.std(X, axis=0)

    # Manejar desviaciones estándar cero
    stds[stds == 0] = 1.0

    return (X - means) / np.sqrt(stds)


def range_scaling(
        X: np.ndarray,
        feature_range: Tuple[float, float] = (0, 1)
) -> np.ndarray:
    """
    Escala los datos a un rango específico.

    Parámetros:
    X -- Matriz de datos con forma (n_muestras, n_características)
    feature_range -- Tupla (min, max) del rango deseado (por defecto (0,1))

    Retorna:
    Matriz escalada al rango especificado
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    min_vals = np.min(X, axis=0)
    max_vals = np.max(X, axis=0)
    data_range = max_vals - min_vals

    # Manejar rangos cero
    data_range[data_range == 0] = 1.0

    # Escalar primero a [0,1]
    X_scaled = (X - min_vals) / data_range

    # Escalar al rango deseado
    min_target, max_target = feature_range
    target_range = max_target - min_target
    return X_scaled * target_range + min_target


def mean_centering(X: np.ndarray) -> np.ndarray:
    """
    Centra los datos restando la media.

    Parámetros:
    X -- Matriz de datos con forma (n_muestras, n_características)

    Retorna:
    Matriz centrada (media 0)
    """
    if X.size == 0:
        raise ValueError("La matriz de entrada está vacía")

    means = np.mean(X, axis=0)
    return X - means


def scale(
        X: np.ndarray,
        method: str = 'auto',
        **kwargs
) -> np.ndarray:
    """
    Función unificada para aplicar diferentes métodos de escalado.

    Parámetros:
    X -- Matriz de datos
    method -- Método a usar: 'auto', 'pareto', 'range', 'center'
    kwargs -- Argumentos adicionales específicos del método

    Retorna:
    Matriz escalada
    """
    method = method.lower()

    if method == 'auto':
        return autoscaling(X)
    elif method == 'pareto':
        return pareto_scaling(X)
    elif method == 'range':
        return range_scaling(X, **kwargs)
    elif method == 'center':
        return mean_centering(X)
    else:
        raise ValueError(f"Método de escalado no reconocido: {method}")