from abc import ABC, abstractmethod
from telegram.ext import Application


class BaseDirector(ABC):
    """
    Base class for building a director.

    Adopts the `Builder` design pattern.
    """

    def __init__(
        self,
        application: Application,
    ):
        self.application = application

    @abstractmethod
    def construct(self):
        pass
