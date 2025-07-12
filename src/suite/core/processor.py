import pandas as pd
import numpy as np


class RMNProcessor:
    def __init__(self):
        self.df = None
        self.integrales_df = pd.DataFrame()
        self.val_x = None
        self.val_y = None
        self.muestras = None
        self.prom_y = None
        self.integrales_totales = None  # Nuevo: almacenará integrales totales por muestra

    def load_file(self, ruta):
        extension = ruta.split('.')[-1].lower()

        if extension == 'csv':
            df = pd.read_csv(ruta, header=None, low_memory=False)
        elif extension == 'txt':
            df = pd.read_csv(ruta, delimiter=',', header=None, low_memory=False)
        else:
            raise ValueError("Formato no soportado. Use archivos .csv o .txt")

        self.df = df.T
        self._process_data()
        return self.df

    def _process_data(self):
        if self.df is not None:
            self.val_x = self.df.iloc[0, 1:].values.astype(float)
            self.val_y = self.df.iloc[1:, 1:].values.astype(float)
            self.muestras = self.df.iloc[1:, 0].tolist()
            self.prom_y = np.mean(self.val_y, axis=0)
            # Calcular integrales totales para cada muestra
            self.integrales_totales = np.sum(self.val_y, axis=1)

    def calculate_integral(self, x1, x2):
        x1, x2 = sorted([x1, x2])
        region_df = self.val_y[:, x1:x2 + 1]

        # Calcular integrales
        integral_values = np.sum(region_df, axis=1)

        # Actualizar DataFrame de integrales
        col_name = f"{self.val_x[x1]:.4f} - {self.val_x[x2]:.4f}"
        self.integrales_df[col_name] = integral_values
        self.integrales_df.index = self.muestras

        # Datos para visualización
        y_integral = np.cumsum(self.prom_y[x1:x2 + 1])
        if len(y_integral) > 0 and max(y_integral) > 0:
            y_integral = (y_integral / max(y_integral)) * np.max(region_df, axis=0).max()
        else:
            y_integral = np.zeros_like(y_integral)

        return self.val_x[x1], self.val_x[x2], self.val_x[x1:x2 + 1], y_integral

    def get_plot_data(self):
        if self.df is None:
            return None
        return {
            'val_x': self.val_x,
            'prom_y': self.prom_y,
            'lim_inf': min(self.val_x),
            'lim_sup': max(self.val_x)
        }

    def get_integrales(self):
        return self.integrales_df.copy()

    def reset(self):
        self.df = None
        self.integrales_df = pd.DataFrame()
        self.val_x = None
        self.val_y = None
        self.muestras = None
        self.prom_y = None
        self.integrales_totales = None

    def calcular_integrales_relativas(self):
        """Calcula las integrales relativas respecto al total de cada muestra"""
        if self.integrales_df.empty or self.integrales_totales is None:
            return pd.DataFrame()

        # Crear copia del DataFrame de integrales
        relativas_df = self.integrales_df.copy()

        # Calcular valores relativos (cada integral / integral total de su muestra)
        for col in relativas_df.columns:
            relativas_df[col] = relativas_df[col] / self.integrales_totales

        # Redondear a 4 decimales
        return relativas_df.round(9)

    def get_integrales_totales(self):
        """Devuelve las integrales totales de cada muestra"""
        if self.integrales_totales is None:
            return None
        return pd.Series(self.integrales_totales, index=self.muestras, name="Integral Total")
