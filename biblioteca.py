from dataclasses import dataclass, replace
from typing import Protocol


# Representa un libro del catálogo.
@dataclass(frozen=True)
class Libro:
    codigo: str
    disponibles: int


# Errores específicos de las reservas.
class LibroInexistente(Exception):
    pass


class LibroNoDisponible(Exception):
    pass


# Define las operaciones del repositorio.
class RepositorioLibros(Protocol):

    def buscar(self, codigo: str) -> Libro | None:
        ...

    def guardar(self, libro: Libro) -> None:
        ...


# Almacena libros en memoria para las pruebas.
class RepositorioEnMemoria:

    def __init__(self, libros: list[Libro]):
        self._libros = {libro.codigo: libro for libro in libros}

    def buscar(self, codigo: str) -> Libro | None:
        return self._libros.get(codigo)

    def guardar(self, libro: Libro) -> None:
        self._libros[libro.codigo] = libro


# Aplica las reglas de negocio de las reservas.
class ServicioReservas:

    def __init__(self, repositorio: RepositorioLibros):
        self._repositorio = repositorio

    def reservar(self, codigo: str) -> int:

        if not isinstance(codigo, str) or not codigo.strip():
            raise ValueError("El código del libro es obligatorio")

        libro = self._repositorio.buscar(codigo)

        if libro is None:
            raise LibroInexistente("El libro no existe")

        if libro.disponibles <= 0:
            raise LibroNoDisponible("No hay ejemplares disponibles")

        actualizado = replace(
            libro,
            disponibles=libro.disponibles - 1
        )

        self._repositorio.guardar(actualizado)

        return actualizado.disponibles
