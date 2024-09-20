"""A module that contains the representation of the holy mass and a calendar day."""

from app.altar_server.altar_server import AltarServer

from app.events.event import Event


class HolyMass:
    """The representation of a holy mass."""

    def __init__(self: "HolyMass", event: Event) -> None:
        """Create a holy mass object.

        :param event: The event object associated with this holy mass.
        """
        self.servers = []
        self.event = event
        self.day = None

    def add_server(self: "HolyMass", server: AltarServer) -> None:
        """Add a server to the holy mass.

        :param server: The server to add.
        """
        self.servers.append(server)

    def __str__(self: "HolyMass") -> str:
        """Return a string representation of the holy mass."""
        return f"{self.event} - {self.servers}"

    def __repr__(self: "HolyMass") -> str:
        """Return a string representation of the holy mass."""
        return self.__str__()
