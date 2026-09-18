import tkinter as tk
from tkinter import messagebox, ttk

import database
from config import APP_NAME, APP_SUBTITLE, CATEGORIES, LOCATIONS, MIN_HEIGHT, MIN_WIDTH, PRIORITIES, STATUSES, WINDOW_SIZE


class CampusFixApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - {APP_SUBTITLE}")
        self.geometry(WINDOW_SIZE)
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.configure(bg="#eef2f7")
        self.current_user = None
        self._configure_styles()
        database.initialize_database()
        self.show_login()

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#eef2f7")
        style.configure("Card.TFrame", background="white")
        style.configure("Title.TLabel", background="#eef2f7", foreground="#162033", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#eef2f7", foreground="#5d687a", font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background="white", foreground="#1b2434", font=("Segoe UI", 13, "bold"))
        style.configure("CardText.TLabel", background="white", foreground="#5f6b7b", font=("Segoe UI", 10))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.configure("TButton", font=("Segoe UI", 9), padding=(10, 7))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=29)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def clear_root(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.current_user = None
        self.clear_root()
        LoginFrame(self, self.on_login).pack(fill="both", expand=True)

    def on_login(self, user):
        self.current_user = user
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_root()
        if self.current_user["role"] == "Admin":
            AdminDashboard(self, self.current_user, self.show_login).pack(fill="both", expand=True)
        else:
            UserDashboard(self, self.current_user, self.show_login).pack(fill="both", expand=True)


class LoginFrame(ttk.Frame):
    def __init__(self, master, login_callback):
        super().__init__(master, padding=30)
        self.login_callback = login_callback
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        wrap = ttk.Frame(self, style="Card.TFrame", padding=32)
        wrap.grid(row=0, column=0)
        wrap.columnconfigure(0, weight=1)

        ttk.Label(wrap, text=APP_NAME, style="CardTitle.TLabel", font=("Segoe UI", 24, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(wrap, text=APP_SUBTITLE, style="CardText.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 22))

        ttk.Label(wrap, text="Email", style="CardText.TLabel").grid(row=2, column=0, sticky="w")
        self.email = ttk.Entry(wrap, width=38, font=("Segoe UI", 10))
        self.email.grid(row=3, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(wrap, text="Password", style="CardText.TLabel").grid(row=4, column=0, sticky="w")
        self.password = ttk.Entry(wrap, width=38, show="*", font=("Segoe UI", 10))
        self.password.grid(row=5, column=0, sticky="ew", pady=(4, 16))
        self.password.bind("<Return>", lambda _e: self.login())

        ttk.Button(wrap, text="Sign In", style="Primary.TButton", command=self.login).grid(row=6, column=0, sticky="ew")
        ttk.Button(wrap, text="Create Student/Staff Account", command=self.open_register).grid(row=7, column=0, sticky="ew", pady=(8, 0))

        hint = "Demo: admin@campusfix.local / admin123   |   student@campusfix.local / student123"
        ttk.Label(wrap, text=hint, style="CardText.TLabel", wraplength=360, justify="left").grid(row=8, column=0, sticky="w", pady=(18, 0))

    def login(self):
        user = database.authenticate(self.email.get(), self.password.get())
        if not user:
            messagebox.showerror("Login Failed", "Incorrect email or password.")
            return
        self.login_callback(user)

    def open_register(self):
        win = tk.Toplevel(self)
        win.title("Create Account")
        win.resizable(False, False)
        frm = ttk.Frame(win, style="Card.TFrame", padding=22)
        frm.pack(fill="both", expand=True)

        fields = {}
        for r, label in enumerate(["Full Name", "Email", "Password", "Confirm Password"]):
            ttk.Label(frm, text=label, style="CardText.TLabel").grid(row=r*2, column=0, sticky="w")
            entry = ttk.Entry(frm, width=38, show="*" if "Password" in label else "")
            entry.grid(row=r*2+1, column=0, pady=(3, 10))
            fields[label] = entry

        def save():
            name = fields["Full Name"].get().strip()
            email = fields["Email"].get().strip()
            p1 = fields["Password"].get()
            p2 = fields["Confirm Password"].get()
            if len(name) < 3 or "@" not in email or len(p1) < 6:
                messagebox.showwarning("Check Details", "Enter a valid name, email, and password of at least 6 characters.")
                return
            if p1 != p2:
                messagebox.showwarning("Check Password", "Passwords do not match.")
                return
            ok, msg = database.register_user(name, email, p1)
            if ok:
                messagebox.showinfo("Account Created", msg)
                win.destroy()
            else:
                messagebox.showerror("Could Not Register", msg)

        ttk.Button(frm, text="Create Account", style="Primary.TButton", command=save).grid(row=8, column=0, sticky="ew", pady=(4, 0))


class Header(ttk.Frame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master, padding=(24, 18))
        self.columnconfigure(0, weight=1)
        text = f"{APP_NAME}  •  {APP_SUBTITLE}"
        ttk.Label(self, text=text, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self, text=f"Signed in as {user['full_name']} ({user['role']})", style="Sub.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(self, text="Logout", command=logout_callback).grid(row=0, column=1, rowspan=2, padx=(20, 0))


class StatCard(ttk.Frame):
    def __init__(self, master, title, value):
        super().__init__(master, style="Card.TFrame", padding=16)
        ttk.Label(self, text=title, style="CardText.TLabel").pack(anchor="w")
        ttk.Label(self, text=str(value), style="CardTitle.TLabel", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(5, 0))


class UserDashboard(ttk.Frame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        Header(self, user, logout_callback).pack(fill="x")

        self.body = ttk.Frame(self, padding=(24, 4, 24, 24))
        self.body.pack(fill="both", expand=True)
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(2, weight=1)

        self.cards = ttk.Frame(self.body)
        self.cards.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for i in range(4):
            self.cards.columnconfigure(i, weight=1)

        actions = ttk.Frame(self.body)
        actions.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        ttk.Button(actions, text="+ New Complaint", style="Primary.TButton", command=self.new_complaint).pack(side="left")
        ttk.Button(actions, text="Refresh", command=self.refresh).pack(side="left", padx=8)

        table_card = ttk.Frame(self.body, style="Card.TFrame", padding=14)
        table_card.grid(row=2, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)
        ttk.Label(table_card, text="My Complaints", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        columns = ("id", "title", "category", "priority", "status", "assigned", "created")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        headings = {"id":"ID", "title":"Title", "category":"Category", "priority":"Priority", "status":"Status", "assigned":"Assigned To", "created":"Created"}
        widths = {"id":55, "title":250, "category":130, "priority":85, "status":105, "assigned":140, "created":145}
        for c in columns:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew")
        sb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", self.view_selected)

        self.refresh()

    def refresh(self):
        for w in self.cards.winfo_children():
            w.destroy()
        stats = database.get_dashboard_stats(self.user["id"])
        labels = [("Total Requests", stats["total"]), ("Open", stats["open"]), ("Resolved", stats["resolved"]), ("Urgent Open", stats["urgent"])]
        for i, (title, value) in enumerate(labels):
            card = StatCard(self.cards, title, value)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0 if i == 3 else 6))

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in database.get_user_complaints(self.user["id"]):
            self.tree.insert("", "end", values=(row["id"], row["title"], row["category"], row["priority"], row["status"], row["assigned_to"] or "-", row["created_at"]))

    def new_complaint(self):
        ComplaintForm(self, self.user, self.refresh)

    def view_selected(self, _event=None):
        item = self.tree.focus()
        if not item:
            return
        complaint_id = int(self.tree.item(item, "values")[0])
        show_complaint_detail(self, complaint_id, editable=False)


class ComplaintForm(tk.Toplevel):
    def __init__(self, master, user, refresh_callback):
        super().__init__(master)
        self.user = user
        self.refresh_callback = refresh_callback
        self.title("Submit New Complaint")
        self.geometry("560x600")
        self.resizable(False, False)

        frm = ttk.Frame(self, style="Card.TFrame", padding=20)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(0, weight=1)
        ttk.Label(frm, text="New Maintenance Request", style="CardTitle.TLabel", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 14))

        ttk.Label(frm, text="Short Title", style="CardText.TLabel").grid(row=1, column=0, sticky="w")
        self.title_entry = ttk.Entry(frm)
        self.title_entry.grid(row=2, column=0, sticky="ew", pady=(3, 10))

        ttk.Label(frm, text="Category", style="CardText.TLabel").grid(row=3, column=0, sticky="w")
        self.category = ttk.Combobox(frm, values=CATEGORIES, state="readonly")
        self.category.current(0)
        self.category.grid(row=4, column=0, sticky="ew", pady=(3, 10))

        ttk.Label(frm, text="Location", style="CardText.TLabel").grid(row=5, column=0, sticky="w")
        self.location = ttk.Combobox(frm, values=LOCATIONS, state="readonly")
        self.location.current(0)
        self.location.grid(row=6, column=0, sticky="ew", pady=(3, 10))

        ttk.Label(frm, text="Priority", style="CardText.TLabel").grid(row=7, column=0, sticky="w")
        self.priority = ttk.Combobox(frm, values=PRIORITIES, state="readonly")
        self.priority.current(1)
        self.priority.grid(row=8, column=0, sticky="ew", pady=(3, 10))

        ttk.Label(frm, text="Description", style="CardText.TLabel").grid(row=9, column=0, sticky="w")
        self.description = tk.Text(frm, height=11, wrap="word", font=("Segoe UI", 10), relief="solid", borderwidth=1)
        self.description.grid(row=10, column=0, sticky="nsew", pady=(3, 14))

        ttk.Button(frm, text="Submit Complaint", style="Primary.TButton", command=self.save).grid(row=11, column=0, sticky="ew")

    def save(self):
        title = self.title_entry.get().strip()
        desc = self.description.get("1.0", "end").strip()
        if len(title) < 4 or len(desc) < 10:
            messagebox.showwarning("Missing Information", "Please provide a clear title and a short description.")
            return
        cid = database.add_complaint(self.user["id"], title, self.category.get(), self.location.get(), self.priority.get(), desc)
        messagebox.showinfo("Submitted", f"Complaint #{cid} has been submitted.")
        self.refresh_callback()
        self.destroy()


class AdminDashboard(ttk.Frame):
    def __init__(self, master, user, logout_callback):
        super().__init__(master)
        self.user = user
        Header(self, user, logout_callback).pack(fill="x")

        self.body = ttk.Frame(self, padding=(24, 4, 24, 24))
        self.body.pack(fill="both", expand=True)
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(2, weight=1)

        self.cards = ttk.Frame(self.body)
        self.cards.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for i in range(4): self.cards.columnconfigure(i, weight=1)

        filters = ttk.Frame(self.body)
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(filters, text="Status:", style="Sub.TLabel").pack(side="left")
        self.status_filter = ttk.Combobox(filters, values=["All"] + STATUSES, state="readonly", width=16)
        self.status_filter.current(0)
        self.status_filter.pack(side="left", padx=(5, 12))
        self.status_filter.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        ttk.Label(filters, text="Search:", style="Sub.TLabel").pack(side="left")
        self.search_var = tk.StringVar()
        search = ttk.Entry(filters, textvariable=self.search_var, width=28)
        search.pack(side="left", padx=(5, 8))
        search.bind("<Return>", lambda _e: self.refresh())
        ttk.Button(filters, text="Apply", command=self.refresh).pack(side="left")
        ttk.Button(filters, text="Clear", command=self.clear_filters).pack(side="left", padx=6)

        table_card = ttk.Frame(self.body, style="Card.TFrame", padding=14)
        table_card.grid(row=2, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)
        ttk.Label(table_card, text="Complaint Queue", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        cols = ("id", "title", "reporter", "category", "priority", "status", "assigned", "created")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")
        headings = {"id":"ID", "title":"Title", "reporter":"Reporter", "category":"Category", "priority":"Priority", "status":"Status", "assigned":"Assigned To", "created":"Created"}
        widths = {"id":50, "title":215, "reporter":150, "category":120, "priority":80, "status":100, "assigned":130, "created":135}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew")
        sb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", self.edit_selected)

        btns = ttk.Frame(table_card, style="Card.TFrame")
        btns.grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Button(btns, text="Open / Update Selected", style="Primary.TButton", command=self.edit_selected).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side="left", padx=8)

        self.refresh()

    def clear_filters(self):
        self.status_filter.current(0)
        self.search_var.set("")
        self.refresh()

    def refresh(self):
        for w in self.cards.winfo_children(): w.destroy()
        stats = database.get_dashboard_stats()
        labels = [("All Requests", stats["total"]), ("Open", stats["open"]), ("Resolved", stats["resolved"]), ("Urgent Open", stats["urgent"])]
        for i, (title, value) in enumerate(labels):
            card = StatCard(self.cards, title, value)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0 if i == 3 else 6))

        for item in self.tree.get_children(): self.tree.delete(item)
        for r in database.get_all_complaints(self.status_filter.get(), self.search_var.get()):
            self.tree.insert("", "end", values=(r["id"], r["title"], r["reporter"], r["category"], r["priority"], r["status"], r["assigned_to"] or "-", r["created_at"]))

    def edit_selected(self, _event=None):
        item = self.tree.focus()
        if not item:
            messagebox.showinfo("Select Complaint", "Select a complaint from the table first.")
            return
        cid = int(self.tree.item(item, "values")[0])
        show_complaint_detail(self, cid, editable=True, refresh_callback=self.refresh)


def show_complaint_detail(master, complaint_id, editable=False, refresh_callback=None):
    data = database.get_complaint(complaint_id)
    if not data:
        messagebox.showerror("Not Found", "Complaint could not be found.")
        return

    win = tk.Toplevel(master)
    win.title(f"Complaint #{complaint_id}")
    win.geometry("650x650")
    frm = ttk.Frame(win, style="Card.TFrame", padding=20)
    frm.pack(fill="both", expand=True)
    frm.columnconfigure(1, weight=1)

    ttk.Label(frm, text=f"Complaint #{data['id']}: {data['title']}", style="CardTitle.TLabel", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

    details = [
        ("Reporter", f"{data['reporter']} ({data['reporter_email']})"),
        ("Category", data['category']),
        ("Location", data['location']),
        ("Priority", data['priority']),
        ("Created", data['created_at']),
        ("Updated", data['updated_at']),
    ]
    row = 1
    for label, value in details:
        ttk.Label(frm, text=label + ":", style="CardText.TLabel").grid(row=row, column=0, sticky="nw", padx=(0, 10), pady=3)
        ttk.Label(frm, text=value, style="CardText.TLabel", wraplength=440).grid(row=row, column=1, sticky="w", pady=3)
        row += 1

    ttk.Label(frm, text="Description:", style="CardText.TLabel").grid(row=row, column=0, sticky="nw", pady=(8, 3))
    desc = tk.Text(frm, height=7, wrap="word", font=("Segoe UI", 10), relief="solid", borderwidth=1)
    desc.insert("1.0", data['description'])
    desc.config(state="disabled")
    desc.grid(row=row, column=1, sticky="ew", pady=(8, 8)); row += 1

    ttk.Label(frm, text="Status:", style="CardText.TLabel").grid(row=row, column=0, sticky="w", pady=4)
    status = ttk.Combobox(frm, values=STATUSES, state="readonly" if editable else "disabled")
    status.set(data['status'])
    status.grid(row=row, column=1, sticky="ew", pady=4); row += 1

    ttk.Label(frm, text="Assigned To:", style="CardText.TLabel").grid(row=row, column=0, sticky="w", pady=4)
    assigned = ttk.Entry(frm)
    assigned.insert(0, data['assigned_to'])
    if not editable: assigned.config(state="disabled")
    assigned.grid(row=row, column=1, sticky="ew", pady=4); row += 1

    ttk.Label(frm, text="Admin Note:", style="CardText.TLabel").grid(row=row, column=0, sticky="nw", pady=4)
    note = tk.Text(frm, height=5, wrap="word", font=("Segoe UI", 10), relief="solid", borderwidth=1)
    note.insert("1.0", data['admin_note'])
    if not editable: note.config(state="disabled")
    note.grid(row=row, column=1, sticky="ew", pady=4); row += 1

    if editable:
        def save():
            database.update_complaint(complaint_id, status.get(), assigned.get(), note.get("1.0", "end").strip())
            messagebox.showinfo("Updated", "Complaint status has been updated.")
            if refresh_callback: refresh_callback()
            win.destroy()
        ttk.Button(frm, text="Save Update", style="Primary.TButton", command=save).grid(row=row, column=1, sticky="ew", pady=(10, 0))


def run_app():
    app = CampusFixApp()
    app.mainloop()
