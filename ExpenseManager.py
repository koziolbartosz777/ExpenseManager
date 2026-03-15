import csv
import os
from datetime import datetime

base_url = r"C:\Users\bkozi\Desktop\Nauka\PYTHON BARTEK\ExpenseManager\expenses.csv"
budget_url = r"C:\Users\bkozi\Desktop\Nauka\PYTHON BARTEK\ExpenseManager\budget.txt"
categories_url = r"C:\Users\bkozi\Desktop\Nauka\PYTHON BARTEK\ExpensesManager\categories.txt"

DEFAULT_CATEGORIES = [
    "Housing", "Food", "Restaurants", "Transport", 
    "Vinted-Inventory", "XTB-Investment", 
    "Health", "Education", "Subscriptions", 
    "Entertainment", "Clothing-Private", "Gifts", "Other"
]

USERS = ["Bartek", "Karolina"]

def load_categories():
    if not os.path.exists(categories_url):
        with open(categories_url, 'w', encoding='utf-8') as f:
            for category in DEFAULT_CATEGORIES:
                f.write(category + "\n")
        return DEFAULT_CATEGORIES.copy()

    with open(categories_url, 'r', encoding='utf-8') as f:
        # readlines czyta z "enterami", więc strip() je usuwa
        return [line.strip() for line in f if line.strip()]

def initialize_file():
    # Sprawdzamy czy folder istnieje, jeśli nie - tworzymy go
    folder = os.path.dirname(base_url)
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    if not os.path.exists(base_url) or os.stat(base_url).st_size == 0:
        with open(base_url, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Description", "Amount", "Payer", "Shared"])
        print("Baza danych została zainicjowana poprawnie.")

def add_expense():
    # --- NOWY SYSTEM DATY ---
    while True:
        is_today = input("Is this expense from today? (Y/N): ").strip().upper()
        
        if is_today == 'Y':
            # Pobieramy dzisiejszą datę
            date = datetime.now().strftime("%Y-%m-%d")
            break
            
        elif is_today == 'N':
            # Pytamy o datę z przeszłości
            custom_date = input("Enter the date (YYYY-MM-DD): ").strip()
            try:
                # Próbujemy przetworzyć wpisany tekst na datę, żeby sprawdzić poprawność
                datetime.strptime(custom_date, "%Y-%m-%d")
                date = custom_date # Jeśli nie było błędu, zapisujemy
                break
            except ValueError:
                # Jeśli ValueError, to znaczy, że format jest zły lub data nie istnieje
                print("[!] Invalid date format. Please use YYYY-MM-DD (e.g., 2023-10-25).")
                
        else:
            print("Please enter 'Y' for Yes or 'N' for No.")
    
    # Wczytujemy z pliku
    categories = load_categories()

    print("\n--- SELECT CATEGORY ---")
    print("0. [DODAJ NOWĄ KATEGORIĘ]") # Nowa super opcja
    for index, name in enumerate(categories, 1):
        print(f"{index}. {name}")
    
    category_name = ""
    while True:
        category_input = input("Choose the category (number) or 0 to add new: ")
        
        # Obsługa dodawania nowej kategorii
        if category_input == "0":
            new_cat = input("Enter new category name: ").strip()
            if new_cat:
                with open(categories_url, 'a', encoding='utf-8') as f:
                    f.write(new_cat + "\n")
                category_name = new_cat
                print(f"[*] Category '{new_cat}' added permanently!")
                break
                
        # Obsługa wyboru istniejącej kategorii
        elif category_input.isdigit():
            idx = int(category_input) - 1
            if 0 <= idx < len(categories):
                category_name = categories[idx]
                break
                
        print(f"Choose 0 or a number between 1 and {len(categories)}")

    while True:
        for index, user in enumerate(USERS):
            print(f"{index+1}. {user}")
        user_input = input("Enter the payer from the list: ")
        if user_input == "1" or user_input.strip().lower() == "bartek":
            payer_name = "Bartek" # Z dużej litery, żeby ładnie wyglądało
            break
        elif user_input == "2" or user_input.strip().lower() == "karolina":
            payer_name = "Karolina"
            break
        else:
            print("Invalid choice, try again.")


    description = input("Enter expense description: ").strip()

    amount = 0.0
    while True:
        try: 
            amount_input = input("Enter the amount (use dot, e.g. 25.50): ")
            amount = float(amount_input)
            break 
        except ValueError:
            print("Error: Amount must be a number")
    
    is_shared = False
    while True:
        shared_input = input("Is this a shared expense? (Y/N): ").upper()
        if shared_input in ['Y', 'N']:
            if shared_input == "Y":
                is_shared = True
            break
        print("Enter 'Y' for Yes or 'N' for No.")

    with open(base_url, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([date, category_name, description, amount, payer_name, is_shared])
    
    print("Expense added successfully!")

def edit_expense():
    if not os.path.exists(base_url):
        print("\n[!] Brak pliku. Nie ma co edytować.")
        return
    
    with open(base_url, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        lines = list(reader)
        
    if not lines:
        print("\n[!] Lista wydatków jest pusta.")
        return
    
    # Kody kolorów (te same co przy usuwaniu)
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    print("\n--- EDIT EXPENSE ---")
    for index, expense in enumerate(lines):
        if expense.get("Shared") == "True":
            tag = f"{GREEN}[WSPÓLNY]{RESET}"
        else:
            tag = f"{YELLOW}[PRYWATNY]{RESET}"
            
        print(f"{index+1}. {tag} {expense['Date']} | {expense['Category']} | {expense['Amount']} PLN | {expense['Description']} | {expense['Payer']}")

    # 1. WYBÓR WYDATKU
    while True:
        choice = input(f"\nEnter the number to edit (1 - {len(lines)}) or '0' to cancel: ")

        if choice == "0":
            print("Canceled")
            return
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(lines):
                expense_to_edit = lines[idx] # Wyciągamy ten konkretny słownik z wydatkiem
                break
            else:
                print("Invalid number. Try again.")
        else:
            print("Please enter a digit.")

    # 2. WYBÓR TEGO, CO CHCEMY ZMIENIĆ
    print("\nWhat do you want to edit?")
    print("1. Date")
    print("2. Category")
    print("3. Description")
    print("4. Amount")
    print("5. Payer")
    print("6. Shared status")
    
    edit_choice = input("Select option (1-6): ")
    
    # 3. PODMIANA DANYCH
    if edit_choice == "1":
        new_date = input("Enter new date (YYYY-MM-DD): ").strip()
        expense_to_edit["Date"] = new_date
    elif edit_choice == "2":
        new_category = input("Enter new category: ").strip()
        expense_to_edit["Category"] = new_category
    elif edit_choice == "3":
        new_desc = input("Enter new description: ").strip()
        expense_to_edit["Description"] = new_desc
    elif edit_choice == "4":
        while True:
            try:
                new_amount = float(input("Enter new amount (e.g. 25.50): "))
                expense_to_edit["Amount"] = new_amount
                break
            except ValueError:
                print("Error: Amount must be a number.")
    elif edit_choice == "5":
        new_payer = input("Enter new payer (Bartek/Karolina): ").strip().capitalize()
        expense_to_edit["Payer"] = new_payer
    elif edit_choice == "6":
        new_shared = input("Is this a shared expense? (Y/N): ").upper()
        if new_shared == "Y":
            expense_to_edit["Shared"] = "True"
        else:
            expense_to_edit["Shared"] = "False"
    else:
        print("Invalid choice, no changes made.")
        return

    # 4. ZAPIS DO PLIKU (Nadpisujemy plik nową, zaktualizowaną listą)
    with open(base_url, 'w', newline='', encoding='utf-8') as file:
        headers = ["Date", "Category", "Description", "Amount", "Payer", "Shared"]
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(lines)
        
    print("\n[*] Expense updated successfully!")

def show_summary():
    if not os.path.exists(base_url):
        print("\n[!] File does not exist yet. Add an expense first.")
        return

    # Struktura: monthly_status["2023-10"]["Shared"]["Food"] = 150.0
    monthly_status = {}
    found_any_data = False

    with open(base_url, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            found_any_data = True
            try:
                month = row["Date"][:7]
                category = row["Category"]
                amount = float(row["Amount"])
                is_shared = row.get("Shared") == "True"
                payer = row.get("Payer", "Unknown")

                # Tworzymy słownik na dany miesiąc, jeśli go nie ma
                if month not in monthly_status:
                    monthly_status[month] = {"Shared": {}, "Bartek": {}, "Karolina": {}}

                # Decydujemy, do której grupy trafi wydatek
                section = "Shared" if is_shared else payer
                
                # Zabezpieczenie, gdyby Payer był wpisany z błędem
                if section not in monthly_status[month]:
                    monthly_status[month][section] = {}

                if category not in monthly_status[month][section]:
                    monthly_status[month][section][category] = 0

                # Dodajemy kwotę
                monthly_status[month][section][category] += amount

            except (KeyError, ValueError, TypeError) as e:
                print(f"[!] Skipping broken row: {row} - Error: {e}")

    if not found_any_data:
        print("\n[!] The file is empty or headers are missing.")
        return

    # WYŚWIETLANIE WYNIKÓW
    for month, data in sorted(monthly_status.items()):
        print(f"\n" + "="*40)
        print(f"  REPORT FOR {month}  ".center(40, "="))
        
        month_total = 0.0

        # Wyświetlamy sekcje po kolei
        for section in ["Shared", "Bartek", "Karolina"]:
            # Jeśli w danej sekcji nie ma wydatków, pomijamy ją
            if not data.get(section): 
                continue

            print(f"\n--- {section.upper()} EXPENSES ---")
            section_total = sum(data[section].values())
            month_total += section_total
            
            max_categ = max(data[section], key=data[section].get)
            print(f"Total {section}: {section_total:.2f} PLN | Most spent: {max_categ} ({data[section][max_categ]:.2f} PLN)")

            # Wyświetlamy kategorie od najwyższej kwoty (sortowanie na żywo)
            for cat, val in sorted(data[section].items(), key=lambda item: item[1], reverse=True):
                print(f" - {cat}: {val:.2f} PLN")

        # BUDŻET
        limit = get_budget()
        print("\n" + "-"*40)
        print(f"TOTAL MONTHLY SPENT: {month_total:.2f} PLN")
        
        if limit:
            print(f"Monthly Budget Limit: {limit:.2f} PLN")
            if month_total <= limit:
                print(f"Status: You have \033[92m{limit - month_total:.2f} PLN left\033[0m")
            else:
                print(f"Status: \033[91m[WARNING] Over budget by {month_total - limit:.2f} PLN\033[0m")
        print("="*40)

def delete_row():
    if not os.path.exists(base_url):
        print("\n[!] Brak pliku. Nie ma co usuwać.")
        return
    
    with open(base_url, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        lines = list(reader)
        
    if not lines:
        print("\n[!] Lista wydatków jest pusta.")
        return
    
    # Definiujemy kolory (kody ANSI)
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m' # To resetuje kolor z powrotem do domyślnego

    # Wyświetlamy wydatki tylko RAZ
    print("\n--- DELETE EXPENSE ---")
    for index, expense in enumerate(lines):
        
        # Sprawdzamy status "Shared" i dodajemy pokolorowany tag
        if expense.get("Shared") == "True":
            tag = f"{GREEN}[WSPÓLNY]{RESET}"
        else:
            tag = f"{YELLOW}[PRYWATNY]{RESET}"
            
        print(f"{index+1}. {tag} {expense['Date']} | {expense['Category']} | {expense['Amount']} PLN | {expense['Description']} | {expense['Payer']}")

    while True:
        choice = input(f"\nEnter the number to delete (1 - {len(lines)}) or '0' to cancel: ")

        if choice == "0":
            print("Canceled")
            return
        
        if choice.isdigit():
            idx = int(choice) - 1
            # Poprawiony znak: 0 <= idx
            if 0 <= idx < len(lines):
                deleted = lines.pop(idx)
                print(f"Deleted {deleted['Amount']} PLN for {deleted['Category']}")
                break
            else:
                print("Invalid number. Try again.")
        else:
            print("Please enter a digit.")

    # Nadpisywanie pliku po usunięciu
    with open(base_url, 'w', newline='', encoding='utf-8') as file:
        headers = ["Date", "Category", "Description", "Amount", "Payer", "Shared"]
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(lines)

def get_budget():
    if os.path.exists(budget_url):
        with open(budget_url, 'r') as file:
            content = file.read().strip()
            if content:
                return float(content)
    return None #return none if the limit has not been set yet 

def set_budget():
    while True:
        try:
            budget_limit = float(input("Enter monthly budget limit: "))
            with open(budget_url, 'w') as file:
                file.write(str(budget_limit))
                break
        except ValueError:
            print("Error: Amount must be a number")

def calculate_settlements():
    if not os.path.exists(base_url):
        print("\n[!] File does not exist yet. Add an expense first.")
        return
    
    bartek_paid=0.0
    karolina_paid=0.0

    with open(base_url, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("Shared") == "True":
                try:
                    amount = float(row["Amount"])
                    if row["Payer"] == "Bartek":
                        bartek_paid+=amount
                    elif row["Payer"] == "Karolina":
                        karolina_paid+=amount
                except ValueError:
                    continue
    
    print("\n--- SETTLEMENTS (ROZLICZENIA) ---")
    print(f"Bartek paid for shared: {bartek_paid:.2f} PLN")
    print(f"Karolina paid for shared: {karolina_paid:.2f} PLN")
    print("-" * 30)

    difference = abs(bartek_paid - karolina_paid)/2

    if bartek_paid > karolina_paid:
        print(f"=> Karolina owes Bartek: {difference:.2f} PLN")
    elif karolina_paid > bartek_paid:
        print(f"=> Bartek owes Karolina: {difference:.2f} PLN")
    else:
        print("=> You are even! (Jesteście kwita!)")

        



def main():
    initialize_file()
    while True:
        print("\n--- EXPENSE MANAGER ---")
        print("1. Add Expense")
        print("2. Show Summary")
        print("3. Edit Expense") 
        print("4. Delete Expense")
        print("5. Set Monthly Budget")
        print("6. Calculate Settlements")
        print("7. Exit")
        choice = input("Select option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            show_summary()
        elif choice == "3":
            edit_expense()
            delete_row()
        elif choice == "5":
            set_budget()
        elif choice == "6":
            calculate_settlements()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()