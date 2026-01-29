import sqlite3
import logging
from rich.console import Console
from rich.table import Table
from models import Zadanie, Bug, Status

logging.basicConfig(filename='system.log', level=logging.INFO, format='%(asctime)s - %(message)s')
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
        logging.info(f'Dodano nowe zadanie/bug: {obiekt.tytul}')

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
        logging.info('Wykonano zapis do bazy danych.')
    
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
        logging.info(f'Wczytano {len(self.lista_zadan)} elementów przy starcie.')
    
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