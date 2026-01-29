import sqlite3
from enum import Enum
from rich.console import Console
from rich.table import Table

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
            raise ValueError(f"BŁĄD: Dział '{dzial}' nie istnieje! Dostępne: {self.DOZWOLONE_DZIALY}")
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
    
    def generuj_przykladowe_dane(self):
        print("Generowanie przykładowych zadań...")
        z1 = Zadanie("Analiza wymagań SAP", 8, "Gotowe") 
        z2 = Zadanie("Implementacja Klasy Kontrahenta", 16, "W Toku")
        b1 = Bug("Dump przy księgowaniu faktury", 4, 10, "Nowe")
        
        self.dodaj_zadanie(z1)
        self.dodaj_zadanie(z2)
        self.dodaj_zadanie(b1)
    
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
    
class Backlog():
    def __init__(self):
        self.lista_zadan = []
        self.plik_db = 'jira.db'
        self._utworz_tabele()

    def _utworz_tabele(self):
        conn = sqlite3.connect(self.plik_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zadania (
                tytul TEXT,
                czas_h INTEGER,
                priorytet INTEGER,
                typ TEXT,
                status TEXT,
                zlecajacy TEXT
            )
        ''')
        conn.commit()
        conn.close()


    def dodaj_zadanie(self, obiekt : 'Zadanie') -> None:
        self.lista_zadan.append(obiekt)

    def zapisz(self):
        conn = sqlite3.connect(self.plik_db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM zadania')
        for zadanie in self.lista_zadan:
            if isinstance(zadanie, Bug):
                typ = 'Bug'
                prio = zadanie.priorytet
            else:
                typ = 'zadanie'
                prio = 0
            cursor.execute('INSERT INTO zadania VALUES (?, ?, ?, ?, ?, ?)', (zadanie.tytul, zadanie.czas_h, prio, typ, zadanie.status.value, zadanie.zlecajacy_info))
        conn.commit()
        conn.close()
        print('Zapisano do bazy SQL')
    
    def wczytaj(self):
        conn = sqlite3.connect(self.plik_db)
        cursor = conn.cursor()
        cursor.execute('SELECT tytul, czas_h, priorytet, typ, status, zlecajacy FROM zadania')
        wiersze = cursor.fetchall()
        self.lista_zadan = []
        for w in wiersze:
            tytul, czas, prio, typ, status_txt, zlecajacy = w
            if typ =='Bug':                                                     
                obj = Bug(tytul, czas, zlecajacy, prio, status_txt)
                obj.status = Status(status_txt)
            else:
                obj = Zadanie(tytul, czas, zlecajacy, status_txt)
            self.lista_zadan.append(obj)
        conn.close()
    
    def pokaz_posortowane(self):
        self.lista_zadan.sort()
        console = Console()
        table = Table(title='Jira Backlog', show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Typ", justify="center")
        table.add_column("Tytuł", style="cyan", no_wrap=True)
        table.add_column("Czas", justify="right")
        table.add_column("Priorytet", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Zlecający", style="italic green")
        for i, z in enumerate(self.lista_zadan):
            if hasattr(z, 'priorytet'): 
                typ_icon = "🐛 BUG"
                prio_txt = f"[bold red]{z.priorytet}[/bold red]" 
            else:
                typ_icon = "📄 TASK"
                prio_txt = "-"

            status_style = "white"
            if z.status.value == "Nowe":
                status_style = "red"
            elif z.status.value == "W Toku":
                status_style = "yellow"
            elif z.status.value == "Zakończone":
                status_style = "green"
            status_formatted = f"[{status_style}]{z.status.value}[/{status_style}]"
            table.add_row(
                str(i),          
                typ_icon,        
                z.tytul,         
                f"{z.czas_h}h",  
                prio_txt,        
                status_formatted,
                z.zlecajacy_info 
            )
        console.print(table)            


def main():
    zalogowany_szef = Szef("Jan", "Kowalski", 999, "IT")
    b = Backlog()
    b.wczytaj()
    
    while True:
        print(f"\n--- SYSTEM ZADAŃ (Zalogowany: {zalogowany_szef}) ---")
        print("1. 📋 Pokaż zadania")
        print("2. ➕ Dodaj Zadanie")
        print("3. 🐛 Zgłoś Buga")
        print("4. 💾 Zapisz i Wyjdź")
        print("5. 🔄 Zmień status")
        
        wybor = input("Wybierz opcję: ")
        
        if wybor == "1":
            print("\n--- LISTA ZADAŃ ---")
            b.pokaz_posortowane()
            
        elif wybor == "2":
            tytul = input("Podaj tytuł: ")
            try:
                czas = int(input("Ile godzin: "))
                nowe_zadanie = Zadanie(tytul, czas, zlecajacy=zalogowany_szef)
                
                b.dodaj_zadanie(nowe_zadanie)
                print("✅ Dodano zadanie!")
            except ValueError:
                print("❌ Błąd: Czas musi być liczbą całkowitą.")
            
        elif wybor == "3":
            tytul = input("Opis błędu: ")
            try:
                czas = int(input("Ile godzin: "))
                prio = int(input("Priorytet (1-10): "))
                nowy_bug = Bug(tytul, czas, zlecajacy=zalogowany_szef, priorytet=prio)
                
                b.dodaj_zadanie(nowy_bug)
                print("🐛 Zgłoszono buga!")
            except ValueError:
                print("❌ Błąd: Czas i Priorytet muszą być liczbami.")
            
        elif wybor == "4":
            b.zapisz()
            print("💾 Zapisano zmiany. Do widzenia!")
            break
            
        elif wybor == "5":
            print("\n--- ZMIANA STATUSU ---")
            if not b.lista_zadan:
                print("Lista jest pusta.")
                continue

            for i, zadanie in enumerate(b.lista_zadan):
                print(f"{i}. {zadanie}")
            
            try:
                idx = int(input("Podaj numer zadania: "))
                if idx < 0 or idx >= len(b.lista_zadan):
                    print("❌ Nie ma takiego numeru.")
                    continue
                    
                wybrane = b.lista_zadan[idx]
                
                print("Dostępne statusy: 1. Nowe | 2. W Toku | 3. Zakończone")
                s = input("Wybierz status: ")
                
                if s == "2":
                    wybrane.zmien_status(Status.W_TOKU)
                elif s == "3":
                    wybrane.zmien_status(Status.GOTOWE)
                else:
                    wybrane.zmien_status(Status.NOWE)
                    
            except ValueError:
                print("❌ Błąd: Wpisz numer.")

if __name__ == "__main__":
    main()