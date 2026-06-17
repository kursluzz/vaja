from dataclasses import dataclass

from fastapi import APIRouter


@dataclass
class VajaModule:
    name: str
    display_name: str
    router: APIRouter


REGISTRY: list[VajaModule] = []


def register(module: VajaModule) -> None:
    REGISTRY.append(module)
