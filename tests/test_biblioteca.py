
import pytest

from biblioteca import (
    Libro,
    LibroInexistente,
    LibroNoDisponible,
    RepositorioEnMemoria,
    ServicioReservas,
)


def test_reserva_exitosa_resta_un_ejemplar():
    repo = RepositorioEnMemoria([Libro("LIB-001", 3)])

    disponibles = ServicioReservas(repo).reservar("LIB-001")

    assert disponibles == 2
    assert repo.buscar("LIB-001").disponibles == 2


def test_sin_stock_impide_reserva_y_conserva_existencias():
    repo = RepositorioEnMemoria([Libro("LIB-001", 0)])

    with pytest.raises(LibroNoDisponible):
        ServicioReservas(repo).reservar("LIB-001")

    assert repo.buscar("LIB-001").disponibles == 0


def test_libro_inexistente_muestra_error_de_dominio():
    repo = RepositorioEnMemoria([])

    with pytest.raises(LibroInexistente):
        ServicioReservas(repo).reservar("NO-EXISTE")


@pytest.mark.parametrize("codigo", ["", "  ", None])
def test_codigo_invalido_es_rechazado(codigo):
    repo = RepositorioEnMemoria([Libro("LIB-001", 2)])

    with pytest.raises(ValueError):
        ServicioReservas(repo).reservar(codigo)

    assert repo.buscar("LIB-001").disponibles == 2


def test_ultima_copia_no_puede_reservarse_dos_veces():
    repo = RepositorioEnMemoria([Libro("LIB-001", 1)])
    servicio = ServicioReservas(repo)

    assert servicio.reservar("LIB-001") == 0

    with pytest.raises(LibroNoDisponible):
        servicio.reservar("LIB-001")


def test_reservar_un_libro_no_afecta_otro():
    repo = RepositorioEnMemoria([
        Libro("A", 2),
        Libro("B", 5)
    ])

    ServicioReservas(repo).reservar("A")

    assert repo.buscar("A").disponibles == 1
    assert repo.buscar("B").disponibles == 5
