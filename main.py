from models import Zadanie, Bug, Szef, Status
from storage import Backlog

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