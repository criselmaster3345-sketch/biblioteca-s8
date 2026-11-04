
import pytest

from biblioteca import (
    Libro,
    LibroInexistente,
    LibroNoDisponible,
    RepositorioEnMemoria,
    ServicioReservas,
)


# PRUEBA 1: Reserva exitosa.
def test_reserva_exitosa_resta_un_ejemplar():
    repo = RepositorioEnMemoria([Libro("LIB-001", 3)])

    disponibles = ServicioReservas(repo).reservar("LIB-001")

    assert disponibles == 2
    assert repo.buscar("LIB-001").disponibles == 2


# PRUEBA 2: Reserva sin existencias.
def test_sin_stock_impide_reserva_y_conserva_existencias():
    repo = RepositorioEnMemoria([Libro("LIB-001", 0)])

    with pytest.raises(LibroNoDisponible):
        ServicioReservas(repo).reservar("LIB-001")

    assert repo.buscar("LIB-001").disponibles == 0


# PRUEBA 3: Libro inexistente.
def test_libro_inexistente_muestra_error_de_dominio():
    repo = RepositorioEnMemoria([])

    with pytest.raises(LibroInexistente):
        ServicioReservas(repo).reservar("NO-EXISTE")


# PRUEBAS 4, 5, 6 y 7: Códigos inválidos.
@pytest.mark.parametrize("codigo", ["", "  ", None, 123])
def test_codigo_invalido_es_rechazado(codigo):
    repo = RepositorioEnMemoria([Libro("LIB-001", 2)])

    with pytest.raises(ValueError):
        ServicioReservas(repo).reservar(codigo)

    assert repo.buscar("LIB-001").disponibles == 2


# PRUEBA 8: Última copia disponible.
def test_ultima_copia_no_puede_reservarse_dos_veces():
    repo = RepositorioEnMemoria([Libro("LIB-001", 1)])
    servicio = ServicioReservas(repo)

    assert servicio.reservar("LIB-001") == 0

    with pytest.raises(LibroNoDisponible):
        servicio.reservar("LIB-001")


# PRUEBA 9: Independencia entre libros.
def test_reservar_un_libro_no_afecta_otro():
    repo = RepositorioEnMemoria([
        Libro("A", 2),
        Libro("B", 5)
    ])

    ServicioReservas(repo).reservar("A")

    assert repo.buscar("A").disponibles == 1
    assert repo.buscar("B").disponibles == 5


# PRUEBA 10: Inmutabilidad del libro original.
def test_reserva_conserva_el_libro_original():
    original = Libro("L001", 2)
    repositorio = RepositorioEnMemoria([original])
    servicio = ServicioReservas(repositorio)

    restantes = servicio.reservar("L001")

    assert restantes == 1
    assert original.disponibles == 2
    assert repositorio.buscar("L001").disponibles == 1
    assert repositorio.buscar("L001") is not original


# PRUEBA 11: Inversión de dependencias (DIP).
def test_servicio_funciona_con_otro_repositorio():

    class RepositorioFalso:
        def __init__(self):
            self.libro = Libro("L001", 2)
            self.guardado = None

        def buscar(self, codigo):
            return self.libro if codigo == "L001" else None

        def guardar(self, libro):
            self.guardado = libro

    repositorio = RepositorioFalso()
    servicio = ServicioReservas(repositorio)

    restantes = servicio.reservar("L001")

    assert restantes == 1
    assert repositorio.guardado.disponibles == 1


# PRUEBA 12: Un error no debe guardar cambios.
def test_reserva_sin_stock_no_guarda_cambios():

    class RepositorioFalso:
        def __init__(self):
            self.guardados = 0

        def buscar(self, codigo):
            return Libro("L001", 0)

        def guardar(self, libro):
            self.guardados += 1

    repositorio = RepositorioFalso()
    servicio = ServicioReservas(repositorio)

    with pytest.raises(LibroNoDisponible):
        servicio.reservar("L001")

    assert repositorio.guardados == 0
