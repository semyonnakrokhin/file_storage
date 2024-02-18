from abc import ABC, abstractmethod
from typing import Dict, Generic

from fastapi_app.src.app_types import D, E, M


class AbstractDomainEntityMapper(ABC, Generic[D, E]):
    """AbstractDomainEntityMapper is an abstract class providing a base
    interface for mappers that transform data between domain models and
    entities."""

    @abstractmethod
    def to_entity(self, domain_obj: D) -> E:
        """Abstract method for mapping data from a domain model object to an
        entity object.

        Args:
            domain_obj (D): The domain model object to be mapped.

        Returns:
            E: The entity object.
        """
        pass

    @abstractmethod
    def to_domain(self, entity_obj: E) -> D:
        """Abstract method for mapping data from an entity object to a domain
        model object.

        Args:
            entity_obj (E): The entity object to be mapped.

        Returns:
            D: The domain model object.
        """
        pass


class AbstractModelDictMapper(ABC, Generic[M]):
    @abstractmethod
    def to_dict(self, model_obj: M) -> Dict:
        pass

    @abstractmethod
    def to_model(self, dict_obj: Dict) -> M:
        pass
