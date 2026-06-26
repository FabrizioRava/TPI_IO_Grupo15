from dataclasses import dataclass
from typing import Optional

@dataclass
class Articulo:
    """Modelo para un artículo de inventario"""
    id: Optional[int] = None
    sku: str = ""
    nombre: str = ""
    demanda: int = 0
    costo_unitario: float = 0.0