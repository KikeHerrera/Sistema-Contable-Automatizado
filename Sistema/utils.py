from datetime import date
from .models import PartidaDiaria, LibroMayor

def filtrar_o_crear_partida_diaria():
    # Obtener la fecha actual
    fecha_hoy = date.today()

    # Intentar obtener la partida diaria para el día actual
    partida_diaria = PartidaDiaria.objects.filter(fecha=fecha_hoy).last()

    # Si no existe una partida diaria para hoy, crear una nueva
    if not partida_diaria:
        libro_mayor_actual, created = LibroMayor.objects.get_or_create(id_libro_mayor=1)
        partida_diaria = PartidaDiaria.objects.create(
            fecha=fecha_hoy,
            id_libro_mayor=libro_mayor_actual  # Usa solo el objeto, no la tupla
        )
    
    return partida_diaria
