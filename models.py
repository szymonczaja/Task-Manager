from enum import Enum

class Status(Enum):
    NOWE = 'Nowe'
    W_TOKU = 'W Toku'
    GOTOWE = 'Zakończone'

class Pracownik():
    def __init__(self, imie, nazwisko, id_pracownika):
        self.imie = imie
        self.nazwisko = nazwisko 
        self.id = id_pracownika

    def __str__(self):
        return f'[{self.id}] {self.imie} {self.nazwisko}'

class Szef(Pracownik):
    DZIALY = ["IT", "HR", "Finanse", "Zarząd"]

    def __init__(self, imie, nazwisko, id_pracownika, dzial):
        if dzial not in self.DZIALY:
            raise ValueError(f"BŁĄD: Dział '{dzial}' nie istnieje! Dostępne: {self.DZIALY}")
        super().__init__(imie, nazwisko, id_pracownika)
        self.dzial = dzial

    def __str__(self):
        return f'Szef {super().__str__()} (Dział: {self.dzial})'
    
class Zadanie():
    def __init__(self, tytul, czas_h, zlecajacy, status_str='Nowe'):
        self.tytul = tytul 
        assert isinstance(czas_h, int) and czas_h >= 1
        self.czas_h = czas_h
        self.status = Status(status_str)
        if hasattr(zlecajacy, 'imie'):
            self.zlecajacy_info = f'{zlecajacy.imie} {zlecajacy.nazwisko}'
        else:
            self.zlecajacy_info = str(zlecajacy)

    def zmien_status(self, nowy_status : Status):
        self.status = nowy_status
        print(f"Status zadania '{self.tytul}' zmieniony na: {self.status.value}")

    def __str__(self):
        icon = "✅" if self.status == Status.GOTOWE else "⏳" if self.status == Status.W_TOKU else "🆕"
        return f'{icon} [{self.status.value}] Zadanie: {self.tytul} ({self.czas_h}h | zlecone przez [{self.zlecajacy_info}])'
    
    def __lt__(self, other):
        return self.czas_h < other.czas_h
    
    def __add__(self, other):
        return self.czas_h + other.czas_h
    
    def to_dict(self):
        slownik = {}
        slownik['tytul'] = self.tytul
        slownik['czas_h'] = self.czas_h
        return slownik 
    
class Bug(Zadanie):
    def __init__(self, tytul, czas_h, zlecajacy, priorytet, status_str='Nowe'):
        super().__init__(tytul, czas_h, zlecajacy, status_str)
        assert isinstance(priorytet, int) and 1 <= priorytet <= 10
        self.priorytet = priorytet

    def __str__(self):
        base = super().__str__()
        return base.replace(f"] {self.tytul}", f"] 🐛 BUG: {self.tytul} [Prio: {self.priorytet}]")
    
    def to_dict(self):
        slownik = super().to_dict()
        slownik['priorytet'] = self.priorytet
        return slownik