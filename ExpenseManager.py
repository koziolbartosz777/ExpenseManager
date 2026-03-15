import csv
import os
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- FILE PATHS ---
base_url = r"C:\Users\bkozi\Desktop\Nauka\PYTHON BARTEK\ExpenseManager\expenses.csv"
budget_url = r"C:\Users\bkozi\Desktop\Nauka\PYTHON BARTEK\ExpenseManager\budget.txt"
categories_url = r"C:\Users\bkozi\Desktop\Nauka\PYTHON BARTEK\ExpenseManager\categories.txt"

# EXTENDED ENGLISH CATEGORIES
DEFAULT_CATEGORIES = [
    "Housing", "Utilities", "Groceries", "Dining Out", "Transport", 
    "Healthcare", "Personal Care", "Education", "Subscriptions", 
    "Entertainment", "Clothing", "Pets", "Home Supplies", 
    "Investments", "Vacation", "Gifts", "Other"
]

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Plot style for Dark Mode
plt.style.use('dark_background')

class ExpenseManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Expense Manager")
        self.geometry("1000x750") 
        
        self.initialize_files()
        self.categories = self.load_categories()

        # --- MAIN GRID ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- SIDEBAR (MENU) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Expense\nManager", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_add = ctk.CTkButton(self.sidebar_frame, text="Add Expense", command=self.show_add_frame)
        self.btn_add.grid(row=1, column=0, padx=20, pady=10)

        self.btn_manage = ctk.CTkButton(self.sidebar_frame, text="Manage", command=self.show_manage_frame)
        self.btn_manage.grid(row=2, column=0, padx=20, pady=10)

        self.btn_search = ctk.CTkButton(self.sidebar_frame, text="Search", command=self.show_search_frame)
        self.btn_search.grid(row=3, column=0, padx=20, pady=10)

        self.btn_summary = ctk.CTkButton(self.sidebar_frame, text="Summary", command=self.show_summary_frame)
        self.btn_summary.grid(row=4, column=0, padx=20, pady=10)

        self.btn_analytics = ctk.CTkButton(self.sidebar_frame, text="Analytics", command=self.show_analytics_frame)
        self.btn_analytics.grid(row=5, column=0, padx=20, pady=10)

        self.btn_settlements = ctk.CTkButton(self.sidebar_frame, text="Settlements", command=self.show_settlements_frame)
        self.btn_settlements.grid(row=6, column=0, padx=20, pady=10)

        self.btn_budget = ctk.CTkButton(self.sidebar_frame, text="Budget", command=self.show_budget_frame)
        self.btn_budget.grid(row=7, column=0, padx=20, pady=10)

        # --- MAIN FRAMES ---
        self.add_frame = ctk.CTkFrame(self, corner_radius=10)
        self.manage_frame = ctk.CTkFrame(self, corner_radius=10)
        self.search_frame = ctk.CTkFrame(self, corner_radius=10)
        self.summary_frame = ctk.CTkFrame(self, corner_radius=10)
        self.analytics_frame = ctk.CTkFrame(self, corner_radius=10)
        self.settlements_frame = ctk.CTkFrame(self, corner_radius=10)
        self.budget_frame = ctk.CTkFrame(self, corner_radius=10)

        self.setup_add_frame()
        self.setup_manage_frame()
        self.setup_search_frame()
        self.setup_summary_frame()
        self.setup_analytics_frame()
        self.setup_settlements_frame()
        self.setup_budget_frame()

        self.show_add_frame()

    def destroy(self):
        # This function is called when the window is closed
        # First close all matplotlib plots to clear memory
        plt.close('all')
        # Then destroy the main window
        super().destroy()

    # ==========================================
    # FILE LOGIC
    # ==========================================
    def initialize_files(self):
        # Create folder if it doesn't exist
        folder = os.path.dirname(base_url)
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Initialize CSV file with headers if it's new or empty
        if not os.path.exists(base_url) or os.stat(base_url).st_size == 0:
            with open(base_url, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Category", "Description", "Amount", "Payer", "Shared"])

    def load_categories(self):
        # Create categories file if missing
        if not os.path.exists(categories_url):
            with open(categories_url, 'w', encoding='utf-8') as f:
                for category in DEFAULT_CATEGORIES:
                    f.write(category + "\n")
            return DEFAULT_CATEGORIES.copy()
        
        # Load existing categories
        with open(categories_url, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

    def get_budget(self):
        # Read budget limit from file
        if os.path.exists(budget_url):
            with open(budget_url, 'r') as file:
                content = file.read().strip()
                if content:
                    return float(content)
        return None

    def read_csv_lines(self):
        # Helper to read all expenses as a list of dictionaries
        if not os.path.exists(base_url): return []
        with open(base_url, 'r', encoding='utf-8') as file:
            return list(csv.DictReader(file))

    # ==========================================
    # VIEW SWITCHING
    # ==========================================
    def hide_all_frames(self):
        # Hide all main content frames
        for frame in [self.add_frame, self.manage_frame, self.search_frame, self.summary_frame, self.analytics_frame, self.settlements_frame, self.budget_frame]:
            frame.grid_forget()

    def show_add_frame(self):
        self.hide_all_frames()
        self.add_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def show_manage_frame(self):
        self.hide_all_frames()
        self.manage_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.refresh_manage_list()

    def show_search_frame(self):
        self.hide_all_frames()
        self.search_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def show_summary_frame(self):
        self.hide_all_frames()
        self.summary_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.update_month_list()

    def show_analytics_frame(self):
        self.hide_all_frames()
        self.analytics_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        # Refresh chart when entering the tab
        self.draw_chart()

    def show_settlements_frame(self):
        self.hide_all_frames()
        self.settlements_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.generate_settlements()

    def show_budget_frame(self):
        self.hide_all_frames()
        self.budget_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.refresh_budget_view()

    # ==========================================
    # 1. ADD EXPENSE
    # ==========================================
    def setup_add_frame(self):
        ctk.CTkLabel(self.add_frame, text="Add New Expense", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 20))
        
        self.date_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Date (YYYY-MM-DD)", width=300)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=10)
        
        self.category_var = ctk.StringVar(value=self.categories[0])
        self.category_menu = ctk.CTkOptionMenu(self.add_frame, values=self.categories, variable=self.category_var, width=300)
        self.category_menu.pack(pady=10)
        
        self.desc_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Description (e.g., Walmart)", width=300)
        self.desc_entry.pack(pady=10)
        
        self.amount_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Amount (e.g., 25.50)", width=300)
        self.amount_entry.pack(pady=10)
        
        self.payer_var = ctk.StringVar(value="Bartek")
        self.payer_menu = ctk.CTkOptionMenu(self.add_frame, values=["Bartek", "Karolina"], variable=self.payer_var, width=300)
        self.payer_menu.pack(pady=10)
        
        self.shared_var = ctk.StringVar(value="False")
        self.shared_switch = ctk.CTkSwitch(self.add_frame, text="Shared Expense?", variable=self.shared_var, onvalue="True", offvalue="False")
        self.shared_switch.pack(pady=10)
        
        self.btn_save = ctk.CTkButton(self.add_frame, text="Save Expense", command=self.save_expense, width=300, fg_color="#28a745", hover_color="#218838")
        self.btn_save.pack(pady=30)

    def save_expense(self):
        date = self.date_entry.get().strip()
        category = self.category_var.get()
        desc = self.desc_entry.get().strip()
        amount_str = self.amount_entry.get().replace(",", ".")
        payer = self.payer_var.get()
        is_shared = self.shared_var.get()

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except:
            return messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
        
        # Check description
        if not desc:
            return messagebox.showerror("Error", "Description cannot be empty!")
        
        # Validate amount
        try:
            amount = float(amount_str)
        except:
            return messagebox.showerror("Error", "Amount must be a number!")

        # Save to file
        with open(base_url, 'a', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow([date, category, desc, amount, payer, is_shared])
        
        messagebox.showinfo("Success", "Expense saved successfully!")
        self.desc_entry.delete(0, 'end')
        self.amount_entry.delete(0, 'end')

    # ==========================================
    # 2. MANAGE (DELETE / EDIT)
    # ==========================================
    def setup_manage_frame(self):
        ctk.CTkLabel(self.manage_frame, text="Manage Expenses", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))
        self.scrollable_manage_frame = ctk.CTkScrollableFrame(self.manage_frame, width=600, height=450)
        self.scrollable_manage_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def refresh_manage_list(self):
        # Clear current list widgets
        for widget in self.scrollable_manage_frame.winfo_children(): widget.destroy()
        self.lines = self.read_csv_lines()

        # Show expenses in reverse order (newest on top)
        for index, row in reversed(list(enumerate(self.lines))):
            row_frame = ctk.CTkFrame(self.scrollable_manage_frame)
            row_frame.pack(fill="x", pady=2, padx=5)

            text_info = f"{row['Date']} | {row['Category']} | {row['Amount']} PLN | {row['Payer']}  "
            ctk.CTkLabel(row_frame, text=text_info, anchor="w").pack(side="left", padx=(10, 0), pady=5)

            # Labels for Shared vs Private status
            is_shared = row.get("Shared") == "True"
            tag_text = " Shared " if is_shared else " Private "
            tag_bg_color = "#198754" if is_shared else "#ffc107" 
            tag_text_color = "white" if is_shared else "black"

            ctk.CTkLabel(row_frame, text=tag_text, fg_color=tag_bg_color, text_color=tag_text_color, corner_radius=6, height=22).pack(side="left", padx=5, pady=5)

            # Delete and Edit buttons
            ctk.CTkButton(row_frame, text="Delete", width=60, fg_color="#dc3545", hover_color="#c82333", command=lambda i=index: self.delete_expense(i)).pack(side="right", padx=5, pady=5)
            ctk.CTkButton(row_frame, text="Edit", width=60, fg_color="#007bff", hover_color="#0056b3", command=lambda i=index: self.open_edit_window(i)).pack(side="right", padx=5, pady=5)

    def delete_expense(self, index):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            self.lines.pop(index)
            self.save_all_lines()
            self.refresh_manage_list()

    def open_edit_window(self, index):
        expense = self.lines[index]
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Expense")
        edit_window.geometry("300x300")
        edit_window.attributes('-topmost', True)

        entry_date = ctk.CTkEntry(edit_window, width=200); entry_date.insert(0, expense["Date"]); entry_date.pack(pady=5)
        entry_amount = ctk.CTkEntry(edit_window, width=200); entry_amount.insert(0, expense["Amount"]); entry_amount.pack(pady=5)
        entry_desc = ctk.CTkEntry(edit_window, width=200); entry_desc.insert(0, expense["Description"]); entry_desc.pack(pady=5)

        def save_edits():
            try:
                float(entry_amount.get().replace(",", "."))
            except:
                return messagebox.showerror("Error", "Amount must be a number!")
            
            self.lines[index].update({
                "Date": entry_date.get(), 
                "Amount": entry_amount.get().replace(",", "."), 
                "Description": entry_desc.get()
            })
            self.save_all_lines()
            edit_window.destroy()
            self.refresh_manage_list()

        ctk.CTkButton(edit_window, text="Save Changes", command=save_edits).pack(pady=20)

    def save_all_lines(self):
        # Overwrite file with current data
        with open(base_url, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Date", "Category", "Description", "Amount", "Payer", "Shared"])
            writer.writeheader()
            writer.writerows(self.lines)

    # ==========================================
    # 3. SEARCH
    # ==========================================
    def setup_search_frame(self):
        ctk.CTkLabel(self.search_frame, text="Search Expenses", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))
        
        search_top_frame = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        search_top_frame.pack(pady=10)

        self.search_entry = ctk.CTkEntry(search_top_frame, placeholder_text="Type keyword...", width=300)
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(search_top_frame, text="Search", command=self.perform_search).pack(side="left")

        self.search_results_frame = ctk.CTkScrollableFrame(self.search_frame, width=600, height=400)
        self.search_results_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def perform_search(self):
        for widget in self.search_results_frame.winfo_children(): widget.destroy()
        keyword = self.search_entry.get().lower()
        if not keyword: return

        lines = self.read_csv_lines()
        found = False

        for row in reversed(lines):
            # Check if keyword matches description, category or amount
            if keyword in row["Description"].lower() or keyword in row["Category"].lower() or keyword in row["Amount"]:
                found = True
                row_frame = ctk.CTkFrame(self.search_results_frame)
                row_frame.pack(fill="x", pady=2, padx=5)

                is_shared = row.get("Shared") == "True"
                tag_text = " Shared " if is_shared else " Private "
                tag_bg = "#198754" if is_shared else "#ffc107"
                tag_fg = "white" if is_shared else "black"

                text_info = f"{row['Date']} | {row['Category']} | {row['Amount']} PLN | {row['Description']} "
                ctk.CTkLabel(row_frame, text=text_info, anchor="w").pack(side="left", padx=(10, 5), pady=5)
                ctk.CTkLabel(row_frame, text=tag_text, fg_color=tag_bg, text_color=tag_fg, corner_radius=6, height=22).pack(side="left", padx=5)

        if not found:
            ctk.CTkLabel(self.search_results_frame, text="No results found.", text_color="gray").pack(pady=20)


    # ==========================================
    # 4. SUMMARY
    # ==========================================
    def setup_summary_frame(self):
        ctk.CTkLabel(self.summary_frame, text="Monthly Summary", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))
        
        self.month_var = ctk.StringVar(value="All")
        self.month_menu = ctk.CTkOptionMenu(self.summary_frame, values=["All"], variable=self.month_var, command=self.generate_summary)
        self.month_menu.pack(pady=10)
        
        self.summary_text = ctk.CTkTextbox(self.summary_frame, width=600, height=400)
        self.summary_text.pack(pady=10, padx=20, fill="both", expand=True)

    def update_month_list(self):
        # Update dropdown with months found in data
        lines = self.read_csv_lines()
        months = set([row["Date"][:7] for row in lines if row.get("Date")])
        sorted_months = ["All"] + sorted(list(months), reverse=True)
        
        self.month_menu.configure(values=sorted_months)
        if self.month_var.get() not in sorted_months:
            self.month_var.set(sorted_months[0])
            
        self.generate_summary()

    def generate_summary(self, choice=None):
        self.summary_text.delete("1.0", "end")
        selected_month = self.month_var.get()
        lines = self.read_csv_lines()

        monthly_status = {"Shared": {}, "Bartek": {}, "Karolina": {}}
        month_total = 0.0

        for row in lines:
            month = row["Date"][:7]
            if selected_month != "All" and month != selected_month:
                continue

            try:
                category = row["Category"]
                amount = float(row["Amount"])
                section = "Shared" if row.get("Shared") == "True" else row.get("Payer", "Unknown")
                
                if category not in monthly_status[section]: 
                    monthly_status[section][category] = 0
                
                monthly_status[section][category] += amount
                month_total += amount
            except: 
                continue

        report = f"REPORT FOR: {selected_month}\n"
        report += f"========================================\n"

        for section in ["Shared", "Bartek", "Karolina"]:
            if not monthly_status[section]: continue
            section_total = sum(monthly_status[section].values())
            
            report += f"\n--- {section.upper()} EXPENSES ---\n"
            for cat, val in sorted(monthly_status[section].items(), key=lambda i: i[1], reverse=True):
                report += f" • {cat}: {val:.2f} PLN\n"
            report += f"Total for {section}: {section_total:.2f} PLN\n"
        
        budget_limit = self.get_budget()
        report += f"\n----------------------------------------\n"
        report += f"TOTAL EXPENSES: {month_total:.2f} PLN\n"
        
        if budget_limit and selected_month != "All": 
            report += f"Your monthly budget: {budget_limit:.2f} PLN\n"
            if month_total <= budget_limit:
                report += f"STATUS: You have {budget_limit - month_total:.2f} PLN left.\n"
            else:
                report += f"STATUS: [WARNING] OVER BUDGET BY {month_total - budget_limit:.2f} PLN!\n"

        self.summary_text.insert("end", report)

    # ==========================================
    # 5. ANALYTICS (PIE CHART)
    # ==========================================
    def setup_analytics_frame(self):
        ctk.CTkLabel(self.analytics_frame, text="Analytics (Pie Chart)", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        # Filter switcher
        self.analysis_filter_var = ctk.StringVar(value="All")
        filter_seg = ctk.CTkSegmentedButton(self.analytics_frame, variable=self.analysis_filter_var, 
                                            values=["All", "Shared", "Bartek", "Karolina"], 
                                            command=self.draw_chart)
        filter_seg.pack(pady=10)

        self.chart_frame = ctk.CTkFrame(self.analytics_frame, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def draw_chart(self, value=None):
        # Clear existing widgets and close plots
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        plt.close('all') 

        lines = self.read_csv_lines()
        if not lines:
            ctk.CTkLabel(self.chart_frame, text="No data to display.", font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        filter_choice = self.analysis_filter_var.get()

        # Filter data based on selection
        filtered_lines = []
        for row in lines:
            try:
                is_shared = row.get("Shared") == "True"
                payer = row.get("Payer")
                if filter_choice == "Shared" and not is_shared: continue
                if filter_choice == "Bartek" and (is_shared or payer != "Bartek"): continue
                if filter_choice == "Karolina" and (is_shared or payer != "Karolina"): continue
                filtered_lines.append(row)
            except: continue

        if not filtered_lines:
            ctk.CTkLabel(self.chart_frame, text="No data for this filter.", font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        # Initialize Plot
        fig, ax = plt.subplots(figsize=(7, 5))
        fig.patch.set_facecolor('#2b2b2b') 
        ax.set_facecolor('#2b2b2b')

        # Aggregate sums per category
        categories_sum = {}
        for row in filtered_lines:
            try:
                cat = row["Category"]
                amt = float(row["Amount"])
                if cat not in categories_sum: categories_sum[cat] = 0
                categories_sum[cat] += amt
            except: continue

        if not categories_sum:
            ctk.CTkLabel(self.chart_frame, text="No categorized data.").pack(pady=50)
            return

        sorted_cats = sorted(categories_sum.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_cats]
        sizes = [item[1] for item in sorted_cats]

        # Draw the chart
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                textprops=dict(color="white", fontsize=11, weight="bold"))
        
        ax.axis('equal') 

        # Display in UI
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ==========================================
    # 6. SETTLEMENTS & BUDGET
    # ==========================================
    def setup_settlements_frame(self):
        ctk.CTkLabel(self.settlements_frame, text="Who owes whom?", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 30))
        self.settlement_label = ctk.CTkLabel(self.settlements_frame, text="", font=ctk.CTkFont(size=18))
        self.settlement_label.pack(pady=20)
        self.result_label = ctk.CTkLabel(self.settlements_frame, text="", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffcc00")
        self.result_label.pack(pady=20)

    def generate_settlements(self):
        bartek_paid, karolina_paid = 0.0, 0.0
        for row in self.read_csv_lines():
            if row.get("Shared") == "True":
                try:
                    if row["Payer"] == "Bartek": bartek_paid += float(row["Amount"])
                    elif row["Payer"] == "Karolina": karolina_paid += float(row["Amount"])
                except: continue

        self.settlement_label.configure(text=f"Bartek paid for shared: {bartek_paid:.2f} PLN\nKarolina paid for shared: {karolina_paid:.2f} PLN")
        diff = abs(bartek_paid - karolina_paid) / 2
        
        if bartek_paid > karolina_paid: 
            self.result_label.configure(text=f"=> Karolina owes Bartek: {diff:.2f} PLN")
        elif karolina_paid > bartek_paid: 
            self.result_label.configure(text=f"=> Bartek owes Karolina: {diff:.2f} PLN")
        else: 
            self.result_label.configure(text="=> You are even! (0.00 PLN)")

    def setup_budget_frame(self):
        ctk.CTkLabel(self.budget_frame, text="Budget Settings", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 30))
        self.current_budget_lbl = ctk.CTkLabel(self.budget_frame, text="", font=ctk.CTkFont(size=16))
        self.current_budget_lbl.pack(pady=10)
        self.budget_entry = ctk.CTkEntry(self.budget_frame, placeholder_text="New limit (e.g., 3000)", width=200)
        self.budget_entry.pack(pady=10)
        ctk.CTkButton(self.budget_frame, text="Save Budget", command=self.save_budget, fg_color="#17a2b8", hover_color="#138496").pack(pady=20)

    def refresh_budget_view(self):
        limit = self.get_budget()
        self.current_budget_lbl.configure(text=f"Current monthly budget: {limit:.2f} PLN" if limit else "You haven't set a budget yet.")

    def save_budget(self):
        try:
            limit = float(self.budget_entry.get().replace(",", "."))
            with open(budget_url, 'w') as file: file.write(str(limit))
            messagebox.showinfo("Success", "Budget updated successfully!")
            self.budget_entry.delete(0, 'end')
            self.refresh_budget_view()
        except: 
            messagebox.showerror("Error", "Budget must be a number!")

if __name__ == "__main__":
    app = ExpenseManagerApp()
    app.mainloop()