from typing import Tuple, Optional, List
import pandas as pd
import numpy as np
import os


def load_nmr_data(file_path: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Carga datos de espectros NMR desde un archivo CSV con estructura específica.

    Parámetros:
    file_path -- Ruta al archivo CSV

    Retorna:
    ppm -- Vector de desplazamientos químicos (1D array)
    data -- Matriz de espectros (muestras x puntos ppm)
    sample_names -- Lista de nombres de muestras

    Estructura esperada:
    - Primera columna: valores ppm (a partir de la segunda fila)
    - Primera fila: nombres de muestras (a partir de la segunda columna)
    - Segunda fila en adelante: datos de intensidad
    """
    try:
        # Leer el archivo manteniendo los encabezados y el índice
        df = pd.read_csv(file_path, header=0, index_col=None)

        # Extraer componentes
        ppm = df.iloc[1:, 0].values.astype(float)
        sample_names = df.columns[1:].tolist()
        spectra = df.iloc[1:, 1:].values.astype(float).T

        return ppm, spectra, sample_names

    except Exception as e:
        raise IOError(f"Error al cargar el archivo {file_path}: {str(e)}")


def save_processed_data(
        output_path: str,
        ppm: np.ndarray,
        processed_data: np.ndarray,
        sample_names: List[str],
        original_file_path: Optional[str] = None
) -> None:
    """
    Guarda los datos procesados en un archivo CSV manteniendo la estructura original.

    Parámetros:
    output_path -- Ruta de salida para el archivo CSV
    ppm -- Vector de desplazamientos químicos
    processed_data -- Matriz de datos procesados (muestras x puntos ppm)
    sample_names -- Lista de nombres de muestras
    original_file_path -- Ruta opcional al archivo original (para mantener metadatos)
    """
    try:
        # Transponer los datos procesados para que coincidan con la estructura de salida
        # (puntos ppm x muestras)
        data_to_save = processed_data.T

        # Crear una lista de listas para los datos
        # Primera fila: vacío + nombres de muestra
        data_list = [[''] + sample_names]

        # Para cada punto ppm, crear una fila: [ppm] + [valores para cada muestra]
        for i in range(len(ppm)):
            row = [ppm[i]] + data_to_save[i].tolist()
            data_list.append(row)

        # Convertir a DataFrame y guardar
        df_output = pd.DataFrame(data_list)
        df_output.to_csv(output_path, index=False, header=False)

        print(f"Datos procesados guardados en: {output_path}")

    except Exception as e:
        raise IOError(f"Error al guardar el archivo {output_path}: {str(e)}")


def validate_nmr_data(ppm: np.ndarray, data: np.ndarray, sample_names: list) -> None:
    """
    Valida la consistencia de los datos cargados.

    Parámetros:
    ppm -- Vector de desplazamientos químicos
    data -- Matriz de espectros
    sample_names -- Lista de nombres de muestras

    Lanza excepciones si se encuentran inconsistencias.
    """
    if len(ppm) == 0:
        raise ValueError("El vector ppm está vacío")

    if data.size == 0:
        raise ValueError("La matriz de datos está vacía")

    if len(sample_names) == 0:
        raise ValueError("No se encontraron nombres de muestra")

    if len(ppm) != data.shape[1]:
        raise ValueError(f"Dimensiones inconsistentes: "
                         f"ppm tiene {len(ppm)} puntos, "
                         f"pero los datos tienen {data.shape[1]} columnas")

    if len(sample_names) != data.shape[0]:
        raise ValueError(f"Dimensiones inconsistentes: "
                         f"{len(sample_names)} nombres de muestra, "
                         f"pero {data.shape[0]} filas en los datos")


def generate_output_filename(input_path: str, suffix: str = "_processed") -> str:
    """
    Genera un nombre de archivo de salida basado en el archivo de entrada.

    Parámetros:
    input_path -- Ruta al archivo de entrada
    suffix -- Sufijo para agregar al nombre del archivo

    Retorna:
    Ruta de archivo de salida
    """
    dir_name, file_name = os.path.split(input_path)
    base_name, ext = os.path.splitext(file_name)
    new_name = base_name + suffix + ext
    return os.path.join(dir_name, new_name)
