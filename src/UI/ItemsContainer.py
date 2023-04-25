from dataclasses import dataclass, field, fields


@dataclass()
class ItemsContainer:
    """dataclass для хранения объектов интерфейса для каждого из сценариев"""

    start_window: list = field(default_factory=list)
    create_client_window: list = field(default_factory=list)
    create_bank_window: list = field(default_factory=list)
    client_account: list = field(default_factory=list)
    client_transaction: list = field(default_factory=list)
    bank_manager_account: list = field(default_factory=list)
    new_bank_account: list = field(default_factory=list)
    top_up: list = field(default_factory=list)
    transfer: list = field(default_factory=list)

    def __iter__(self):
        return (getattr(self, fi.name) for fi in fields(self))