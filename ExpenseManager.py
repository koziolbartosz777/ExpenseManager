import flet as ft
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
CREDENTIALS_FILE = "credentials.json"
SHEET_NAME = "ExpenseManagerSpreadsheet"

# EXTENDED ENGLISH CATEGORIES
DEFAULT_CATEGORIES = [
    "Housing", "Utilities", "Groceries", "Dining Out", "Transport",
    "Healthcare", "Personal Care", "Education", "Subscriptions",
    "Entertainment", "Clothing", "Pets", "Home Supplies",
    "Investments", "Vacation", "Gifts", "Other"
]

# --- DESKTOP UI CONSTANTS ---
PAGE_PADDING = 24
CARD_MAX_WIDTH = 520
LIST_MAX_WIDTH = 680
CARD_PADDING = 28
SECTION_SPACING = 20
FIELD_SPACING = 16

# Colors for analytics bars (one per category, cycle if needed)
CHART_COLORS = [
    ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.AMBER_400,
    ft.Colors.PURPLE_400, ft.Colors.CYAN_400, ft.Colors.ORANGE_400,
    ft.Colors.PINK_400, ft.Colors.TEAL_400, ft.Colors.INDIGO_400,
    ft.Colors.LIME_400, ft.Colors.DEEP_ORANGE_400, ft.Colors.BROWN_400,
]

def _card(content, width=None):
    """Wrap content in a centered card for desktop-friendly layout."""
    w = width or CARD_MAX_WIDTH
    return ft.Container(
        content=content,
        width=w,
        padding=CARD_PADDING,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
    )

class ExpenseManagerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Expense Manager"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.categories = DEFAULT_CATEGORIES
        self.lines = []
        self.expenses_sheet = None
        self.budget_sheet = None

        # Connect to Google Sheets
        self.connect_to_sheets()

        # --- NAVIGATION BAR (desktop & mobile) ---
        self.page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=self.handle_nav_change,
            elevation=8,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            indicator_color=ft.Colors.PRIMARY_CONTAINER,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.ADD, label="Add"),
                ft.NavigationBarDestination(icon=ft.Icons.EDIT, label="Manage"),
                ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
                ft.NavigationBarDestination(icon=ft.Icons.ARTICLE, label="Summary"),
                ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART, label="Analytics"),
                ft.NavigationBarDestination(icon=ft.Icons.ACCOUNT_BALANCE, label="Settles"),
                ft.NavigationBarDestination(icon=ft.Icons.SAVINGS, label="Budget"),
            ]
        )

        # --- MAIN FRAMES ---
        self.add_frame = ft.Container(visible=False, expand=True)
        self.manage_frame = ft.Container(visible=False, expand=True)
        self.search_frame = ft.Container(visible=False, expand=True)
        self.summary_frame = ft.Container(visible=False, expand=True)
        self.analytics_frame = ft.Container(visible=False, expand=True)
        self.settlements_frame = ft.Container(visible=False, expand=True)
        self.budget_frame = ft.Container(visible=False, expand=True)

        self.main_content = ft.Container(
            content=ft.Column(
                controls=[
                    self.add_frame, self.manage_frame, self.search_frame,
                    self.summary_frame, self.analytics_frame,
                    self.settlements_frame, self.budget_frame
                ],
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=PAGE_PADDING,
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
        )
        self.page.add(self.main_content)

        # Initialize all views
        self.setup_add_frame()
        self.setup_manage_frame()
        self.setup_search_frame()
        self.setup_summary_frame()
        self.setup_analytics_frame()
        self.setup_settlements_frame()
        self.setup_budget_frame()

        # Show default view
        self.show_add_frame()

    # ==========================================
    # GOOGLE SHEETS LOGIC
    # ==========================================
    def connect_to_sheets(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
            client = gspread.authorize(creds)
            self.spreadsheet = client.open(SHEET_NAME)
            
            # Setup Expenses sheet
            self.expenses_sheet = self.spreadsheet.sheet1
            if not self.expenses_sheet.get_all_values():
                self.expenses_sheet.append_row(["Date", "Category", "Description", "Amount", "Payer", "Shared"])

            # Setup Budget sheet (creates a new tab in your Google Sheet)
            try:
                self.budget_sheet = self.spreadsheet.worksheet("Budget")
            except gspread.exceptions.WorksheetNotFound:
                self.budget_sheet = self.spreadsheet.add_worksheet("Budget", rows=10, cols=2)
                self.budget_sheet.update_acell("A1", "Budget Limit")
                self.budget_sheet.update_acell("B1", "")

        except Exception as e:
            self.expenses_sheet = None
            self.budget_sheet = None
            self.show_message(f"Failed to connect to Google Sheets. Check credentials.json and network.", is_error=True)
            self.page.update()

    def read_sheet_lines(self):
        if self.expenses_sheet is None:
            return []
        try:
            return self.expenses_sheet.get_all_records()
        except Exception:
            return []

    def get_budget(self):
        if self.budget_sheet is None:
            return None
        try:
            val = self.budget_sheet.acell("B1").value
            if val:
                return float(val)
        except Exception:
            pass
        return None

    def show_message(self, message, is_error=False):
        color = ft.Colors.RED_700 if is_error else ft.Colors.GREEN_700
        self.page.show_dialog(
            ft.SnackBar(content=ft.Text(str(message)), bgcolor=color)
        )
        self.page.update()

    # ==========================================
    # VIEW SWITCHING
    # ==========================================
    def hide_all_frames(self):
        self.add_frame.visible = False
        self.manage_frame.visible = False
        self.search_frame.visible = False
        self.summary_frame.visible = False
        self.analytics_frame.visible = False
        self.settlements_frame.visible = False
        self.budget_frame.visible = False

    def handle_nav_change(self, e):
        idx = e.control.selected_index
        if idx == 0: self.show_add_frame()
        elif idx == 1: self.show_manage_frame()
        elif idx == 2: self.show_search_frame()
        elif idx == 3: self.show_summary_frame()
        elif idx == 4: self.show_analytics_frame()
        elif idx == 5: self.show_settlements_frame()
        elif idx == 6: self.show_budget_frame()

    def show_add_frame(self):
        self.hide_all_frames()
        self.add_frame.visible = True
        self.page.update()

    def show_manage_frame(self):
        self.hide_all_frames()
        self.manage_frame.visible = True
        self.refresh_manage_list()
        self.page.update()

    def show_search_frame(self):
        self.hide_all_frames()
        self.search_frame.visible = True
        self.page.update()

    def show_summary_frame(self):
        self.hide_all_frames()
        self.summary_frame.visible = True
        self.update_month_list()
        self.page.update()

    def show_analytics_frame(self):
        self.hide_all_frames()
        self.analytics_frame.visible = True
        self.draw_chart()
        self.page.update()

    def show_settlements_frame(self):
        self.hide_all_frames()
        self.settlements_frame.visible = True
        self.generate_settlements()
        self.page.update()

    def show_budget_frame(self):
        self.hide_all_frames()
        self.budget_frame.visible = True
        self.refresh_budget_view()
        self.page.update()

    # ==========================================
    # 1. ADD EXPENSE
    # ==========================================
    def setup_add_frame(self):
        self.date_entry = ft.TextField(
            label="Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"),
            expand=True, border_radius=8
        )
        self.category_menu = ft.Dropdown(
            label="Category",
            options=[ft.dropdown.Option(c) for c in self.categories],
            value=self.categories[0],
            expand=True, border_radius=8
        )
        self.desc_entry = ft.TextField(
            label="Description (e.g. Walmart)", expand=True, border_radius=8
        )
        self.amount_entry = ft.TextField(
            label="Amount (e.g. 25.50)", expand=True, border_radius=8
        )
        self.payer_menu = ft.Dropdown(
            label="Payer",
            options=[ft.dropdown.Option("Bartek"), ft.dropdown.Option("Karolina")],
            value="Bartek",
            expand=True, border_radius=8
        )
        self.shared_switch = ft.Switch(label="Shared expense?", value=False)
        self.btn_save = ft.ElevatedButton(
            "Save expense",
            on_click=self.save_expense,
            expand=True,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
        )
        form_col = ft.Column(
            controls=[
                ft.Text("Add new expense", size=26, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                self.date_entry,
                ft.Container(height=FIELD_SPACING),
                self.category_menu,
                ft.Container(height=FIELD_SPACING),
                self.desc_entry,
                ft.Container(height=FIELD_SPACING),
                self.amount_entry,
                ft.Container(height=FIELD_SPACING),
                self.payer_menu,
                ft.Container(height=FIELD_SPACING),
                self.shared_switch,
                ft.Container(height=SECTION_SPACING),
                self.btn_save,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=CARD_MAX_WIDTH,
        )
        self.add_frame.content = _card(form_col)

    def save_expense(self, e):
        if self.expenses_sheet is None:
            self.show_message("Not connected to Google Sheets. Check credentials and try again.", is_error=True)
            self.page.update()
            return

        date = (self.date_entry.value or "").strip()
        category = (self.category_menu.value if self.category_menu.value is not None else "") or ""
        desc = (self.desc_entry.value or "").strip()
        amount_str = (self.amount_entry.value or "").replace(",", ".")
        payer = (self.payer_menu.value if self.payer_menu.value is not None else "") or "Bartek"
        is_shared = bool(self.shared_switch.value)

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.show_message("Invalid date format. Use YYYY-MM-DD.", is_error=True)
            self.page.update()
            return

        if not desc:
            self.show_message("Description cannot be empty.", is_error=True)
            self.page.update()
            return

        try:
            amount = float(amount_str)
        except ValueError:
            self.show_message("Amount must be a number.", is_error=True)
            self.page.update()
            return

        try:
            row = [str(date), str(category), str(desc), amount, str(payer), str(is_shared)]
            self.expenses_sheet.append_row(row)
            self.desc_entry.value = ""
            self.amount_entry.value = ""
            self.show_message("Expense saved successfully!")
        except Exception as ex:
            self.show_message(f"Error saving to cloud: {ex}", is_error=True)
        self.page.update()

    # ==========================================
    # 2. MANAGE (DELETE / EDIT)
    # ==========================================
    def setup_manage_frame(self):
        self.manage_list_col = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=8)
        header = ft.Row(
            controls=[ft.Text("Manage expenses", size=26, weight=ft.FontWeight.BOLD)],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        inner = ft.Column(
            controls=[header, ft.Container(height=16), self.manage_list_col],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=LIST_MAX_WIDTH,
        )
        self.manage_frame.content = _card(inner, width=LIST_MAX_WIDTH)

    def refresh_manage_list(self):
        self.manage_list_col.controls.clear()
        self.lines = self.read_sheet_lines()

        if not self.lines:
            self.manage_list_col.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No expenses yet. Add some in the Add tab.",
                        color=ft.Colors.GREY_500,
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=32,
                )
            )
            self.page.update()
            return

        for index, row in reversed(list(enumerate(self.lines))):
            is_shared = str(row.get("Shared")) == "True"
            
            badge = ft.Container(
                content=ft.Text("Shared" if is_shared else "Private", color=ft.Colors.WHITE, size=12),
                bgcolor=ft.Colors.GREEN_700 if is_shared else ft.Colors.AMBER_700,
                border_radius=5,
                padding=ft.padding.symmetric(horizontal=6, vertical=2)
            )

            row_text = f"{row['Date']} | {row['Category']} | {row['Amount']} PLN | {row['Payer']}"

            row_ui = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(row_text, weight=ft.FontWeight.W_500),
                        badge
                    ], expand=True),
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=lambda e, i=index: self.open_edit_window(i)),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=lambda e, i=index: self.delete_expense(i))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=8,
                margin=ft.margin.only(bottom=5)
            )
            self.manage_list_col.controls.append(row_ui)
        self.page.update()

    def delete_expense(self, index):
        self.lines.pop(index)
        self.save_all_lines()
        self.refresh_manage_list()
        self.show_message("Expense deleted.")

    def open_edit_window(self, index):
        if index < 0 or index >= len(self.lines):
            return
        expense = self.lines[index]
        edit_date = ft.TextField(
            label="Date (YYYY-MM-DD)",
            value=str(expense.get("Date", "")),
            width=280,
        )
        edit_amount = ft.TextField(
            label="Amount",
            value=str(expense.get("Amount", "")),
            width=280,
        )
        edit_desc = ft.TextField(
            label="Description",
            value=str(expense.get("Description", "")),
            width=280,
        )

        def save_edits(e):
            try:
                float((edit_amount.value or "").replace(",", "."))
            except ValueError:
                self.show_message("Amount must be a number.", is_error=True)
                self.page.update()
                return
            self.lines[index].update({
                "Date": (edit_date.value or "").strip(),
                "Amount": (edit_amount.value or "").replace(",", ".").strip(),
                "Description": (edit_desc.value or "").strip(),
            })
            self.save_all_lines()
            self.page.close_dialog()
            self.refresh_manage_list()
            self.show_message("Expense updated.")
            self.page.update()

        def cancel_edits(e):
            self.page.close_dialog()
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Edit expense"),
            content=ft.Column(
                [edit_date, edit_amount, edit_desc],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_edits),
                ft.TextButton("Save", on_click=save_edits),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)
        self.page.update()

    def save_all_lines(self):
        if self.expenses_sheet is None:
            return
        try:
            self.expenses_sheet.clear()
            headers = ["Date", "Category", "Description", "Amount", "Payer", "Shared"]
            data_to_upload = [headers]
            for row in self.lines:
                data_to_upload.append([
                    str(row.get("Date", "")),
                    str(row.get("Category", "")),
                    str(row.get("Description", "")),
                    str(row.get("Amount", "")),
                    str(row.get("Payer", "")),
                    str(row.get("Shared", "")),
                ])
            self.expenses_sheet.append_rows(data_to_upload)
        except Exception as e:
            self.show_message(f"Sync error: {e}", is_error=True)
            self.page.update()

    # ==========================================
    # 3. SEARCH
    # ==========================================
    def setup_search_frame(self):
        self.search_entry = ft.TextField(
            label="Search by keyword (description, category, amount)",
            width=400,
            border_radius=8,
            on_submit=lambda e: self.perform_search(e),
        )
        btn_search = ft.ElevatedButton(
            "Search",
            on_click=self.perform_search,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            height=48,
        )
        self.search_results_col = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=8,
        )
        self.search_results_col.controls.append(
            ft.Container(
                content=ft.Text(
                    "Enter a keyword above and click Search.",
                    color=ft.Colors.GREY_500,
                    size=15,
                ),
                padding=24,
                alignment=ft.Alignment.CENTER_LEFT,
            )
        )
        search_bar_row = ft.Row(
            controls=[
                self.search_entry,
                btn_search,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
            wrap=True,
        )
        search_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Search expenses", size=26, weight=ft.FontWeight.BOLD),
                    ft.Text("Find by description, category or amount.", size=14, color=ft.Colors.GREY_400),
                    ft.Container(height=12),
                    search_bar_row,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=0,
            ),
            padding=ft.padding.only(bottom=20),
        )
        inner = ft.Column(
            controls=[
                search_section,
                ft.Text("Results", size=16, weight=ft.FontWeight.W_500),
                ft.Container(height=8),
                self.search_results_col,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=LIST_MAX_WIDTH,
        )
        self.search_frame.content = _card(inner, width=LIST_MAX_WIDTH)

    def perform_search(self, e=None):
        self.search_results_col.controls.clear()
        keyword = (self.search_entry.value or "").strip().lower()
        if not keyword:
            self.search_results_col.controls.append(
                ft.Container(
                    content=ft.Text("Enter a keyword above and click Search.", color=ft.Colors.GREY_500, size=15),
                    padding=24,
                    alignment=ft.Alignment.CENTER_LEFT,
                )
            )
            self.page.update()
            return

        lines = self.read_sheet_lines()
        found = False

        for row in reversed(lines):
            if keyword in str(row.get("Description", "")).lower() or \
               keyword in str(row.get("Category", "")).lower() or \
               keyword in str(row.get("Amount", "")):
                
                found = True
                is_shared = str(row.get("Shared")) == "True"
                badge_color = ft.Colors.GREEN_700 if is_shared else ft.Colors.AMBER_700
                tag_text = "Shared" if is_shared else "Private"

                badge = ft.Container(
                    content=ft.Text(tag_text, color=ft.Colors.WHITE, size=12),
                    bgcolor=badge_color,
                    border_radius=5,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2)
                )

                row_text = f"{row['Date']} | {row['Category']} | {row['Amount']} PLN | {row['Description']}"
                
                ui_row = ft.Container(
                    content=ft.Row([ft.Text(row_text, expand=True), badge]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=8,
                    margin=ft.margin.only(bottom=5)
                )
                self.search_results_col.controls.append(ui_row)

        if not found:
            self.search_results_col.controls.append(
                ft.Container(
                    content=ft.Text("No results found.", color=ft.Colors.GREY_500, size=16),
                    alignment=ft.Alignment.CENTER,
                    padding=32,
                )
            )
        
        self.page.update()

    # ==========================================
    # 4. SUMMARY
    # ==========================================
    def setup_summary_frame(self):
        self.month_menu = ft.Dropdown(
            label="Month",
            options=[ft.dropdown.Option("All")],
            value="All",
            on_select=self.generate_summary,
            expand=True,
            border_radius=8,
        )
        self.summary_content_col = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
        inner = ft.Column(
            controls=[
                ft.Text("Monthly summary", size=26, weight=ft.FontWeight.BOLD),
                ft.Text("Breakdown by shared and personal expenses.", size=14, color=ft.Colors.GREY_400),
                ft.Container(height=16),
                self.month_menu,
                ft.Container(height=20),
                self.summary_content_col,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=CARD_MAX_WIDTH,
        )
        self.summary_frame.content = _card(inner)

    def update_month_list(self):
        lines = self.read_sheet_lines()
        months = set([str(row.get("Date", ""))[:7] for row in lines if row.get("Date")])
        sorted_months = ["All"] + sorted(list(months), reverse=True)
        
        self.month_menu.options = [ft.dropdown.Option(m) for m in sorted_months]
        if self.month_menu.value not in sorted_months:
            self.month_menu.value = sorted_months[0]
            
        self.generate_summary()

    def _section_card(self, title, color, items, subtotal):
        """One block: section title + category rows + subtotal."""
        rows = []
        for cat, val in sorted(items, key=lambda x: x[1], reverse=True):
            rows.append(
                ft.Row(
                    controls=[
                        ft.Text(cat, size=14, color=ft.Colors.ON_SURFACE),
                        ft.Text(f"{val:.2f} PLN", size=14, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
            rows.append(ft.Container(height=4))
        rows.append(ft.Divider(height=1))
        rows.append(ft.Container(height=8))
        rows.append(
            ft.Row(
                controls=[
                    ft.Text("Subtotal", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{subtotal:.2f} PLN", size=14, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=color),
                        padding=ft.padding.symmetric(vertical=0, horizontal=0),
                        margin=ft.margin.only(bottom=12),
                    ),
                    ft.Column(controls=rows, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=16,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        )

    def generate_summary(self, e=None):
        selected_month = self.month_menu.value or "All"
        lines = self.read_sheet_lines()
        self.summary_content_col.controls.clear()

        monthly_status = {"Shared": {}, "Bartek": {}, "Karolina": {}}
        month_total = 0.0

        for row in lines:
            month = str(row.get("Date", ""))[:7]
            if selected_month != "All" and month != selected_month:
                continue
            try:
                category = row.get("Category", "Other")
                amount = float(row.get("Amount", 0))
                section = "Shared" if str(row.get("Shared")) == "True" else row.get("Payer", "Unknown")
                if section not in monthly_status:
                    monthly_status[section] = {}
                monthly_status[section][category] = monthly_status[section].get(category, 0) + amount
                month_total += amount
            except Exception:
                continue

        section_colors = {
            "Shared": ft.Colors.GREEN_400,
            "Bartek": ft.Colors.BLUE_400,
            "Karolina": ft.Colors.PURPLE_400,
        }
        for section in ["Shared", "Bartek", "Karolina"]:
            if not monthly_status.get(section):
                continue
            section_total = sum(monthly_status[section].values())
            self.summary_content_col.controls.append(
                self._section_card(
                    section,
                    section_colors.get(section, ft.Colors.GREY_400),
                    list(monthly_status[section].items()),
                    section_total,
                )
            )

        total_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Total expenses", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{month_total:.2f} PLN", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=20,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        )
        self.summary_content_col.controls.append(total_card)

        budget_limit = self.get_budget()
        if budget_limit is not None and selected_month != "All":
            left = budget_limit - month_total
            if month_total <= budget_limit:
                status_text = f"You have {left:.2f} PLN left."
                status_color = ft.Colors.GREEN_400
            else:
                status_text = f"Over budget by {abs(left):.2f} PLN."
                status_color = ft.Colors.RED_400
            self.summary_content_col.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"Budget: {budget_limit:.2f} PLN", size=14),
                            ft.Text(status_text, size=14, weight=ft.FontWeight.W_500, color=status_color),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=12,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
                )
            )

        self.page.update()

    # ==========================================
    # 5. ANALYTICS (PIE CHART)
    # ==========================================
    def setup_analytics_frame(self):
        self.analysis_filter = ft.SegmentedButton(
            segments=[
                ft.Segment(value="All", label=ft.Text("All")),
                ft.Segment(value="Shared", label=ft.Text("Shared")),
                ft.Segment(value="Bartek", label=ft.Text("Bartek")),
                ft.Segment(value="Karolina", label=ft.Text("Karolina")),
            ],
            selected=["All"],
            on_change=self.draw_chart,
        )
        self.chart_container = ft.Container(expand=True, padding=16)

        inner = ft.Column(
            controls=[
                ft.Text("Analytics", size=26, weight=ft.FontWeight.BOLD),
                ft.Text("Expenses by category", size=14, color=ft.Colors.GREY_400),
                ft.Container(height=16),
                self.analysis_filter,
                ft.Container(height=20),
                self.chart_container,
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            width=LIST_MAX_WIDTH,
        )
        self.analytics_frame.content = _card(inner, width=LIST_MAX_WIDTH)

    def draw_chart(self, e=None):
        self.chart_container.content = None
        lines = self.read_sheet_lines()

        if not lines:
            self.chart_container.content = ft.Container(
                content=ft.Text("No expenses yet. Add some in the Add tab.", size=16, color=ft.Colors.GREY_500),
                alignment=ft.Alignment.CENTER,
                padding=32,
            )
            self.page.update()
            return

        # Get filter: All / Shared / Bartek / Karolina
        selected = getattr(self.analysis_filter, "selected", ["All"])
        filter_val = selected[0] if isinstance(selected, list) and selected else "All"

        # Filter rows
        filtered = []
        for row in lines:
            try:
                if filter_val == "All":
                    filtered.append(row)
                elif filter_val == "Shared":
                    if str(row.get("Shared")) == "True":
                        filtered.append(row)
                else:
                    if str(row.get("Payer")) == filter_val:
                        filtered.append(row)
            except Exception:
                continue

        if not filtered:
            self.chart_container.content = ft.Container(
                content=ft.Text(f"No expenses for '{filter_val}'. Try another filter.", size=16, color=ft.Colors.GREY_500),
                alignment=ft.Alignment.CENTER,
                padding=32,
            )
            self.page.update()
            return

        # Aggregate by category
        by_cat = {}
        total = 0.0
        for row in filtered:
            try:
                cat = str(row.get("Category", "Other"))
                amount = float(row.get("Amount", 0))
                by_cat[cat] = by_cat.get(cat, 0) + amount
                total += amount
            except Exception:
                continue

        if total <= 0:
            self.chart_container.content = ft.Container(
                content=ft.Text("No amounts to display.", size=16, color=ft.Colors.GREY_500),
                alignment=ft.Alignment.CENTER,
                padding=32,
            )
            self.page.update()
            return

        # Sort by amount descending
        sorted_cats = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
        max_bar_width = 280

        title_row = ft.Row(
            controls=[
                ft.Text("Category", size=14, weight=ft.FontWeight.W_600, width=120),
                ft.Text("Amount", size=14, weight=ft.FontWeight.W_600, width=90),
                ft.Text("Share", size=14, weight=ft.FontWeight.W_600, width=60),
            ],
            spacing=8,
        )
        rows_ui = [ft.Container(height=8), title_row, ft.Divider(height=1), ft.Container(height=8)]

        for i, (cat, amount) in enumerate(sorted_cats):
            pct = (amount / total) * 100
            bar_width = max(4, (amount / total) * max_bar_width)
            color = CHART_COLORS[i % len(CHART_COLORS)]
            bar = ft.Container(
                width=bar_width,
                height=22,
                border_radius=4,
                bgcolor=color,
            )
            rows_ui.append(
                ft.Row(
                    controls=[
                        ft.Text(cat, size=13, width=120, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{amount:.2f} PLN", size=13, width=90),
                        ft.Text(f"{pct:.1f}%", size=12, color=ft.Colors.GREY_400, width=44),
                        bar,
                    ],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
            rows_ui.append(ft.Container(height=4))

        total_row = ft.Column(
            controls=[
                ft.Divider(height=1),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Text("Total", size=14, weight=ft.FontWeight.BOLD, width=120),
                        ft.Text(f"{total:.2f} PLN", size=14, weight=ft.FontWeight.BOLD, width=90),
                        ft.Text("100%", size=12, weight=ft.FontWeight.W_500, width=60),
                    ],
                    spacing=8,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )
        rows_ui.append(total_row)

        self.chart_container.content = ft.Column(
            controls=rows_ui,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
        self.page.update()

    # ==========================================
    # 6. SETTLEMENTS & BUDGET
    # ==========================================
    def setup_settlements_frame(self):
        self.settlement_label = ft.Text("", size=18)
        self.result_label = ft.Text(
            "", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400
        )
        inner = ft.Column(
            controls=[
                ft.Text("Who owes whom?", size=26, weight=ft.FontWeight.BOLD),
                ft.Container(height=24),
                self.settlement_label,
                ft.Container(height=16),
                self.result_label,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=CARD_MAX_WIDTH,
        )
        self.settlements_frame.content = _card(inner)

    def generate_settlements(self):
        bartek_paid, karolina_paid = 0.0, 0.0
        for row in self.read_sheet_lines():
            if str(row.get("Shared")) == "True":
                try:
                    if row["Payer"] == "Bartek": bartek_paid += float(row["Amount"])
                    elif row["Payer"] == "Karolina": karolina_paid += float(row["Amount"])
                except Exception: continue

        self.settlement_label.value = f"Bartek paid for shared: {bartek_paid:.2f} PLN\nKarolina paid for shared: {karolina_paid:.2f} PLN"
        diff = abs(bartek_paid - karolina_paid) / 2
        
        if bartek_paid > karolina_paid: 
            self.result_label.value = f"=> Karolina owes Bartek: {diff:.2f} PLN"
        elif karolina_paid > bartek_paid: 
            self.result_label.value = f"=> Bartek owes Karolina: {diff:.2f} PLN"
        else: 
            self.result_label.value = "=> You are even! (0.00 PLN)"

    def setup_budget_frame(self):
        self.current_budget_lbl = ft.Text("", size=16)
        self.budget_entry = ft.TextField(
            label="New monthly limit (e.g. 3000)",
            expand=True,
            border_radius=8,
        )
        btn_save = ft.ElevatedButton(
            "Save budget",
            on_click=self.save_budget,
            expand=True,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            bgcolor=ft.Colors.CYAN_700,
            color=ft.Colors.WHITE,
        )
        inner = ft.Column(
            controls=[
                ft.Text("Budget settings", size=26, weight=ft.FontWeight.BOLD),
                ft.Container(height=24),
                self.current_budget_lbl,
                ft.Container(height=16),
                self.budget_entry,
                ft.Container(height=20),
                btn_save,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=CARD_MAX_WIDTH,
        )
        self.budget_frame.content = _card(inner)

    def refresh_budget_view(self):
        limit = self.get_budget()
        self.current_budget_lbl.value = f"Current monthly budget: {limit:.2f} PLN" if limit else "You haven't set a budget yet."

    def save_budget(self, e):
        if self.budget_sheet is None:
            self.show_message("Not connected to Google Sheets.", is_error=True)
            self.page.update()
            return
        try:
            limit = float((self.budget_entry.value or "").replace(",", "."))
            self.budget_sheet.update_acell("B1", limit)
            self.budget_entry.value = ""
            self.refresh_budget_view()
            self.show_message("Budget updated successfully!")
        except ValueError:
            self.show_message("Budget must be a number.", is_error=True)
        self.page.update()

def main_app(page: ft.Page):
    app = ExpenseManagerApp(page)

if __name__ == "__main__":
    ft.app(target=main_app, view=ft.AppView.WEB_BROWSER)