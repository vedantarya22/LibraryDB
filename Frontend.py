import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Login")
        self.root.geometry("400x300")
        self.root.configure(bg="#ede2d3")
        self.root.resizable(False, False)
       
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#ede2d3')
        self.style.configure('TLabel', background='#ede2d3', foreground='#504033', font=('Arial', 10))
        self.style.configure('TButton', background='#504033', foreground='#ede2d3', font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', fieldbackground='#ede2d3', foreground='#504033')
       
        # Create login frame
        login_frame = ttk.Frame(root, padding=20)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
       
        # App title
        ttk.Label(login_frame, 
                 text="Library Management System", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
       
        # Username field
        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(login_frame, textvariable=self.username_var, width=25)
        username_entry.grid(row=1, column=1, pady=5)
       
        # Password field
        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, width=25, show="*")
        password_entry.grid(row=2, column=1, pady=5)
       
        # Login button
        login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)
       
        # Database connection
        self.conn = None
        self.cursor = None
        self.connect_to_db()
       
    def connect_to_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Vasu765@",
                database="LibraryDB"
            )
            self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
           
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
       
        if not username or not password:
            messagebox.showwarning("Login Error", "Please enter both username and password")
            return
           
        try:
            # Check user credentials
            self.cursor.execute("""
                SELECT user_id, role FROM user
                WHERE username = %s AND password = %s
            """, (username, password))
           
            user = self.cursor.fetchone()
           
            if user:
                user_id, role = user
               
                # Close login window
                self.root.withdraw()
               
                # Open appropriate window based on role
                if role == 'Admin':
                    admin_window = tk.Toplevel(self.root)
                    AdminApp(admin_window, user_id, role, self.root)
                else:
                    # Get student_id for this user
                    self.cursor.execute("""
                        SELECT student_id, name FROM students
                        WHERE user_id = %s
                    """, (user_id,))
                   
                    student_data = self.cursor.fetchone()
                   
                    if student_data:
                        student_id, student_name = student_data
                        student_window = tk.Toplevel(self.root)
                        StudentApp(student_window, user_id, student_id, student_name, self.root)
                    else:
                        messagebox.showerror("Error", "Student record not found")
                        self.root.deiconify()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during login: {err}")

    def __del__(self):
        if self.conn:
            self.conn.close()


class AdminApp:
    def __init__(self, root, user_id, role, login_window):
        self.root = root
        self.user_id = user_id
        self.role = role
        self.login_window = login_window
       
        self.root.title("Library Management System - Admin Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg="#ede2d3")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
       
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#ede2d3')
        self.style.configure('TLabel', background='#ede2d3', foreground='#504033')
        self.style.configure('TNotebook', background='#ede2d3')
        self.style.configure('TNotebook.Tab', background='#ede2d3', foreground='#504033', padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', '#ede2d3')], foreground=[('selected', '#504033')])
        self.style.configure('Treeview', background='#ede2d3', fieldbackground='#ede2d3', foreground='#504033')
        self.style.configure('Treeview.Heading', background='#504033', foreground='#ede2d3')
        self.style.configure('TButton', background='#504033', foreground='#ede2d3', font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', fieldbackground='#ede2d3', foreground='#504033')
        self.style.configure('TCombobox', fieldbackground='#ede2d3', foreground='#504033')
       
        # Top frame for user info and logout
        top_frame = ttk.Frame(root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
       
        ttk.Label(top_frame, text=f"Logged in as: Admin", font=("Arial", 10, "italic")).pack(side=tk.LEFT)
        logout_btn = ttk.Button(top_frame, text="Logout", command=self.logout)
        logout_btn.pack(side=tk.RIGHT)
       
        # Database connection
        self.conn = None
        self.cursor = None
        self.connect_to_db()
       
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        # Create tabs
        self.create_books_tab()
        self.create_students_tab()
        self.create_borrowing_tab()
        self.create_returns_tab()
       
    def connect_to_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Vasu765@",
                database="LibraryDB"
            )
            self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
           
    def create_books_tab(self):
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books Management")
       
        # Left frame for book list
        left_frame = ttk.Frame(books_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Create treeview for books
        columns = ("ID", "Title", "Author", "ISBN", "Available")
        self.books_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
       
        # Configure columns
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
       
        # Pack treeview and scrollbar
        self.books_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       
        # Right frame for adding books
        right_frame = ttk.Frame(books_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
       
        # Form for adding new books
        ttk.Label(right_frame, text="Add New Book", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
       
        ttk.Label(right_frame, text="Title:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.title_var, width=25).grid(row=1, column=1, pady=5)
       
        ttk.Label(right_frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.author_var, width=25).grid(row=2, column=1, pady=5)
       
        ttk.Label(right_frame, text="ISBN:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.isbn_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.isbn_var, width=25).grid(row=3, column=1, pady=5)
       
        ttk.Label(right_frame, text="Copies:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.copies_var = tk.IntVar(value=1)
        ttk.Entry(right_frame, textvariable=self.copies_var, width=25).grid(row=4, column=1, pady=5)
       
        # Add book button
        add_book_btn = ttk.Button(right_frame, text="Add Book", command=self.add_book)
        add_book_btn.grid(row=5, column=0, columnspan=2, pady=10)
       
        # Delete book button
        delete_book_btn = ttk.Button(right_frame, text="Delete Selected Book", command=self.delete_book)
        delete_book_btn.grid(row=6, column=0, columnspan=2, pady=5)
       
        # Refresh and search buttons
        refresh_btn = ttk.Button(right_frame, text="Refresh List", command=self.load_books)
        refresh_btn.grid(row=7, column=0, columnspan=2, pady=5)
       
        ttk.Label(right_frame, text="Search by Title/Author:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.search_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.search_var, width=25).grid(row=8, column=1, pady=5)
        search_btn = ttk.Button(right_frame, text="Search", command=self.search_books)
        search_btn.grid(row=9, column=0, columnspan=2, pady=5)
       
        # Load books data
        self.load_books()

    def add_book(self):
        """Add a new book to the library"""
        title = self.title_var.get()
        author = self.author_var.get()
        isbn = self.isbn_var.get()
        copies = self.copies_var.get()

        if not title or not isbn or not copies:
            messagebox.showwarning("Input Error", "Please fill in all required fields")
            return

        try:
            # Insert new book
            self.cursor.execute("""
                INSERT INTO books (title, author, isbn, copies_available)
                VALUES (%s, %s, %s, %s)
            """, (title, author, isbn, copies))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Book added successfully")
            
            # Clear form
            self.title_var.set("")
            self.author_var.set("")
            self.isbn_var.set("")
            self.copies_var.set(1)
            
            # Refresh book list
            self.load_books()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding book: {err}")

    def delete_book(self):
        """Delete the selected book from the library"""
        selected_item = self.books_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book to delete")
            return
            
        try:
            # Get book ID
            item = self.books_tree.item(selected_item[0])
            book_id = item['values'][0]
            
            # Check if book is currently borrowed
            self.cursor.execute("""
                SELECT COUNT(*) FROM borrowedbooks 
                WHERE book_id = %s AND return_date IS NULL
            """, (book_id,))
            
            borrowed_count = self.cursor.fetchone()[0]
            
            if borrowed_count > 0:
                messagebox.showwarning("Delete Error", "Cannot delete book that is currently borrowed")
                return
                
            # Delete the book
            self.cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Book deleted successfully")
            self.load_books()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error deleting book: {err}")

    def load_books(self):
        """Load books data into the treeview"""
        try:
            # Clear current data
            for item in self.books_tree.get_children():
                self.books_tree.delete(item)
                
            # Execute query
            self.cursor.execute("""
                SELECT book_id, title, author, isbn, copies_available
                FROM books
                ORDER BY book_id
            """)
            
            # Insert data into treeview
            for book in self.cursor.fetchall():
                self.books_tree.insert("", tk.END, values=book)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading books: {err}")

    def search_books(self):
        """Search books by title"""
        search_term = self.search_var.get()
        
        if not search_term:
            self.load_books()
            return
            
        try:
            # Clear current data
            for item in self.books_tree.get_children():
                self.books_tree.delete(item)
                
            # Execute search query
            self.cursor.execute("""
                SELECT book_id, title, author, isbn, copies_available
                FROM books
                WHERE title LIKE %s OR author LIKE %s
                ORDER BY book_id
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            # Insert data into treeview
            for book in self.cursor.fetchall():
                self.books_tree.insert("", tk.END, values=book)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching books: {err}")

    def create_students_tab(self):
        students_frame = ttk.Frame(self.notebook)
        self.notebook.add(students_frame, text="Students Management")
       
        # Left frame for student list
        left_frame = ttk.Frame(students_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        # Create treeview for students
        columns = ("ID", "Name", "Email", "Phone")
        self.students_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
       
        # Configure columns
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=100)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscroll=scrollbar.set)
       
        # Pack treeview and scrollbar
        self.students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       
        # Right frame for adding students
        right_frame = ttk.Frame(students_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
       
        # Form for adding new students
        ttk.Label(right_frame, text="Add New Student", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
       
        ttk.Label(right_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.student_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.student_name_var, width=25).grid(row=1, column=1, pady=5)
       
        ttk.Label(right_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.student_email_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.student_email_var, width=25).grid(row=2, column=1, pady=5)
       
        ttk.Label(right_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.student_phone_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.student_phone_var, width=25).grid(row=3, column=1, pady=5)
       
        ttk.Label(right_frame, text="Username:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.student_username_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.student_username_var, width=25).grid(row=4, column=1, pady=5)
       
        ttk.Label(right_frame, text="Password:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.student_password_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.student_password_var, width=25, show="*").grid(row=5, column=1, pady=5)
       
        # Add student button
        add_student_btn = ttk.Button(right_frame, text="Add Student", command=self.add_student)
        add_student_btn.grid(row=6, column=0, columnspan=2, pady=10)
       
        # Delete student button
        delete_student_btn = ttk.Button(right_frame, text="Delete Selected Student", command=self.delete_student)
        delete_student_btn.grid(row=7, column=0, columnspan=2, pady=5)
       
        # Refresh and search buttons
        refresh_btn = ttk.Button(right_frame, text="Refresh List", command=self.load_students)
        refresh_btn.grid(row=8, column=0, columnspan=2, pady=5)
       
        ttk.Label(right_frame, text="Search by Name:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.student_search_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.student_search_var, width=25).grid(row=9, column=1, pady=5)
        search_btn = ttk.Button(right_frame, text="Search", command=self.search_students)
        search_btn.grid(row=10, column=0, columnspan=2, pady=5)
       
        # Load students data
        self.load_students()

    def add_student(self):
        """Add a new student to the system"""
        name = self.student_name_var.get()
        email = self.student_email_var.get()
        phone = self.student_phone_var.get()
        username = self.student_username_var.get()
        password = self.student_password_var.get()

        if not all([name, email, username, password]):
            messagebox.showwarning("Input Error", "Please fill in all required fields")
            return

        try:
            # First add user
            self.cursor.execute("""
                INSERT INTO user (username, password, role)
                VALUES (%s, %s, 'Normal')
            """, (username, password))
            
            user_id = self.cursor.lastrowid
            
            # Then add student
            self.cursor.execute("""
                INSERT INTO students (name, email, phone, user_id)
                VALUES (%s, %s, %s, %s)
            """, (name, email, phone, user_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Student added successfully")
            
            # Clear form
            self.student_name_var.set("")
            self.student_email_var.set("")
            self.student_phone_var.set("")
            self.student_username_var.set("")
            self.student_password_var.set("")
            
            # Refresh student list
            self.load_students()
            
        except mysql.connector.Error as err:
            self.conn.rollback()
            if "Duplicate entry" in str(err):
                messagebox.showerror("Input Error", "Username already exists")
            else:
                messagebox.showerror("Database Error", f"Error adding student: {err}")

    def delete_student(self):
        """Delete the selected student from the system"""
        selected_item = self.students_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a student to delete")
            return
            
        try:
            # Get student ID
            item = self.students_tree.item(selected_item[0])
            student_id = item['values'][0]
            
            # Check if student has borrowed books
            self.cursor.execute("""
                SELECT COUNT(*) FROM borrowedbooks 
                WHERE student_id = %s AND return_date IS NULL
            """, (student_id,))
            
            borrowed_count = self.cursor.fetchone()[0]
            
            if borrowed_count > 0:
                messagebox.showwarning("Delete Error", "Cannot delete student with borrowed books")
                return
                
            # Get user_id for this student
            self.cursor.execute("SELECT user_id FROM students WHERE student_id = %s", (student_id,))
            user_id = self.cursor.fetchone()[0]
            
            # Delete the student and user
            self.cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            self.cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Student deleted successfully")
            self.load_students()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error deleting student: {err}")

    def load_students(self):
        """Load students data into the treeview"""
        try:
            # Clear current data
            for item in self.students_tree.get_children():
                self.students_tree.delete(item)
                
            # Execute query
            self.cursor.execute("""
                SELECT student_id, name, email, phone
                FROM students
                ORDER BY student_id
            """)
            
            # Insert data into treeview
            for student in self.cursor.fetchall():
                self.students_tree.insert("", tk.END, values=student)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading students: {err}")

    def search_students(self):
        """Search students by name"""
        search_term = self.student_search_var.get()
        
        if not search_term:
            self.load_students()
            return
            
        try:
            # Clear current data
            for item in self.students_tree.get_children():
                self.students_tree.delete(item)
                
            # Execute search query
            self.cursor.execute("""
                SELECT student_id, name, email, phone
                FROM students
                WHERE name LIKE %s
                ORDER BY student_id
            """, (f"%{search_term}%",))
            
            # Insert data into treeview
            for student in self.cursor.fetchall():
                self.students_tree.insert("", tk.END, values=student)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching students: {err}")

    def create_borrowing_tab(self):
        borrowing_frame = ttk.Frame(self.notebook)
        self.notebook.add(borrowing_frame, text="Book Borrowing")
       
        # Create form for borrowing
        ttk.Label(borrowing_frame, text="Borrow a Book", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20)
       
        # Student dropdown
        ttk.Label(borrowing_frame, text="Select Student:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=20)
        self.borrow_student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(borrowing_frame, textvariable=self.borrow_student_var, width=30)
        self.student_combo.grid(row=1, column=1, pady=5, padx=20)
       
        # Book dropdown
        ttk.Label(borrowing_frame, text="Select Book:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=20)
        self.borrow_book_var = tk.StringVar()
        self.book_combo = ttk.Combobox(borrowing_frame, textvariable=self.borrow_book_var, width=30)
        self.book_combo.grid(row=2, column=1, pady=5, padx=20)
       
        # Borrow button
        borrow_btn = ttk.Button(borrowing_frame, text="Borrow Book", command=self.borrow_book)
        borrow_btn.grid(row=3, column=0, columnspan=2, pady=10)
       
        # Create treeview for borrowed books
        columns = ("Borrow ID", "Student Name", "Book Title", "Borrow Date", "Return Date")
        self.borrowed_tree = ttk.Treeview(borrowing_frame, columns=columns, show="headings")
       
        # Configure columns
        for col in columns:
            self.borrowed_tree.heading(col, text=col)
            self.borrowed_tree.column(col, width=120)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(borrowing_frame, orient=tk.VERTICAL, command=self.borrowed_tree.yview)
        self.borrowed_tree.configure(yscroll=scrollbar.set)
       
        # Pack treeview and scrollbar
        self.borrowed_tree.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky=(tk.W, tk.E))
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
       
        # Refresh button
        refresh_btn = ttk.Button(borrowing_frame, text="Refresh Borrowed Books", command=self.load_borrowed_books)
        refresh_btn.grid(row=5, column=0, columnspan=2, pady=10)
       
        # Load data
        self.load_students_for_combo()
        self.load_books_for_combo()
        self.load_borrowed_books()
       
    def create_returns_tab(self):
        returns_frame = ttk.Frame(self.notebook)
        self.notebook.add(returns_frame, text="Book Returns")
       
        # Create form for returning books
        ttk.Label(returns_frame, text="Return a Book", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10, padx=20)
       
        # Borrow ID entry
        ttk.Label(returns_frame, text="Enter Borrow ID:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=20)
        self.return_borrow_id_var = tk.StringVar()
        ttk.Entry(returns_frame, textvariable=self.return_borrow_id_var, width=25).grid(row=1, column=1, pady=5, padx=20)
       
        # Return button
        return_btn = ttk.Button(returns_frame, text="Return Book", command=self.return_book)
        return_btn.grid(row=2, column=0, columnspan=2, pady=10)
       
        # Create treeview for borrowed books (to see which ones need to be returned)
        columns = ("Borrow ID", "Student Name", "Book Title", "Borrow Date", "Status")
        self.returns_tree = ttk.Treeview(returns_frame, columns=columns, show="headings")
       
        # Configure columns
        for col in columns:
            self.returns_tree.heading(col, text=col)
            self.returns_tree.column(col, width=120)
       
        # Add scrollbar
        scrollbar = ttk.Scrollbar(returns_frame, orient=tk.VERTICAL, command=self.returns_tree.yview)
        self.returns_tree.configure(yscroll=scrollbar.set)
       
        # Pack treeview and scrollbar
        self.returns_tree.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky=(tk.W, tk.E))
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
       
        # Refresh button
        refresh_btn = ttk.Button(returns_frame, text="Refresh Borrowed Books", command=self.load_returns_data)
        refresh_btn.grid(row=4, column=0, columnspan=2, pady=10)
       
        # Load data
        self.load_returns_data()
   
    def load_students_for_combo(self):
        """Load students for the combobox in borrow tab"""
        try:
            self.cursor.execute("""
                SELECT student_id, name FROM students ORDER BY student_id
            """)
            students = [f"{row[0]}: {row[1]}" for row in self.cursor.fetchall()]
            self.student_combo['values'] = students
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading students: {err}")

    def load_books_for_combo(self):
        """Load available books for the combobox in borrow tab"""
        try:
            self.cursor.execute("""
                SELECT book_id, title FROM books WHERE copies_available > 0 ORDER BY book_id
            """)
            books = [f"{row[0]}: {row[1]}" for row in self.cursor.fetchall()]
            self.book_combo['values'] = books
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading books: {err}")
           
    def load_borrowed_books(self):
        try:
            # Clear current data
            for item in self.borrowed_tree.get_children():
                self.borrowed_tree.delete(item)
               
            # Execute query
            self.cursor.execute("""
                SELECT bb.borrow_id, s.name, b.title, bb.borrow_date, bb.return_date
                FROM borrowedbooks bb
                JOIN students s ON bb.student_id = s.student_id
                JOIN books b ON bb.book_id = b.book_id
                ORDER BY bb.borrow_id
            """)
           
            # Insert data into treeview
            for borrowed in self.cursor.fetchall():
                self.borrowed_tree.insert("", tk.END, values=borrowed)
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading borrowed books: {err}")
           
    def load_returns_data(self):
        try:
            # Clear current data
            for item in self.returns_tree.get_children():
                self.returns_tree.delete(item)
               
            # Execute query to show borrowed books with status
            self.cursor.execute("""
                SELECT bb.borrow_id, s.name, b.title, bb.borrow_date,
                       CASE
                           WHEN bb.return_date IS NULL THEN 'Borrowed'
                           ELSE 'Returned'
                       END AS status
                FROM borrowedbooks bb
                JOIN students s ON bb.student_id = s.student_id
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.return_date IS NULL
                ORDER BY bb.borrow_id
            """)
           
            # Insert data into treeview
            for borrowed in self.cursor.fetchall():
                self.returns_tree.insert("", tk.END, values=borrowed)
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading returns data: {err}")
           
    def borrow_book(self):
        try:
            student_selection = self.borrow_student_var.get()
            book_selection = self.borrow_book_var.get()
           
            if not student_selection or not book_selection:
                messagebox.showwarning("Input Error", "Please select both student and book")
                return
               
            # Extract IDs
            student_id = int(student_selection.split(":")[0])
            book_id = int(book_selection.split(":")[0])
           
            # Call the stored procedure
            self.cursor.callproc("borrowbook", (student_id, book_id))
            self.conn.commit()
           
            messagebox.showinfo("Success", "Book borrowed successfully")
           
            # Clear selections
            self.borrow_student_var.set("")
            self.borrow_book_var.set("")
           
            # Refresh all relevant tabs
            self.load_books()
            self.load_borrowed_books()
            self.load_returns_data()
            self.load_books_for_combo()
           
        except mysql.connector.Error as err:
            if "No copies available" in str(err):
                messagebox.showwarning("Borrow Error", "No copies of this book are currently available")
            else:
                messagebox.showerror("Database Error", f"Error borrowing book: {err}")
           
    def return_book(self):
        try:
            borrow_id = self.return_borrow_id_var.get()
           
            if not borrow_id.isdigit():
                messagebox.showwarning("Input Error", "Please enter a valid Borrow ID")
                return
               
            borrow_id = int(borrow_id)
            
            # Call the stored procedure
            self.cursor.callproc("returnbook", (borrow_id,))
            self.conn.commit()
           
            messagebox.showinfo("Success", "Book returned successfully")
           
            # Clear selection
            self.return_borrow_id_var.set("")
           
            # Refresh all relevant tabs
            self.load_books()
            self.load_borrowed_books()
            self.load_returns_data()
            self.load_books_for_combo()
           
        except mysql.connector.Error as err:
            if "Book is already returned" in str(err):
                messagebox.showwarning("Return Error", "This book is already returned")
            else:
                messagebox.showerror("Database Error", f"Error returning book: {str(err)}")
           
    def logout(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()
        self.login_window.deiconify()
       
    def on_close(self):
        self.logout()
       
    def __del__(self):
        if self.conn:
            self.conn.close()


class StudentApp:
    def __init__(self, root, user_id, student_id, student_name, login_window):
        self.root = root
        self.user_id = user_id
        self.student_id = student_id
        self.student_name = student_name
        self.login_window = login_window
       
        self.root.title(f"Library Management System - {student_name}")
        self.root.geometry("900x650")
        self.root.configure(bg="#ede2d3")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
       
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#ede2d3')
        self.style.configure('TLabel', background='#ede2d3', foreground='#504033')
        self.style.configure('TNotebook', background='#ede2d3')
        self.style.configure('TNotebook.Tab', background='#ede2d3', foreground='#504033', padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', '#ede2d3')], foreground=[('selected', '#504033')])
        self.style.configure('Treeview', background='#ede2d3', fieldbackground='#ede2d3', foreground='#504033')
        self.style.configure('Treeview.Heading', background='#504033', foreground='#ede2d3')
        self.style.configure('TButton', background='#504033', foreground='#ede2d3', font=('Arial', 10, 'bold'))
        self.style.configure('TEntry', fieldbackground='#ede2d3', foreground='#504033')
        self.style.configure('TCombobox', fieldbackground='#ede2d3', foreground='#504033')
       
        # Top frame for user info and logout
        top_frame = ttk.Frame(root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
       
        ttk.Label(top_frame, text=f"Logged in as: {student_name}", font=("Arial", 10, "italic")).pack(side=tk.LEFT)
        logout_btn = ttk.Button(top_frame, text="Logout", command=self.logout)
        logout_btn.pack(side=tk.RIGHT)
       
        # Database connection
        self.conn = None
        self.cursor = None
        self.connect_to_db()
       
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        # Create tabs for student interface
        self.create_dashboard_tab()
        self.create_browse_tab()
        self.create_current_borrowings_tab()
        self.create_borrowing_history_tab()
       
    def connect_to_db(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Vasu765@",
                database="LibraryDB"
            )
            self.cursor = self.conn.cursor(buffered=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
           
    def create_dashboard_tab(self):
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Personal Dashboard")
       
        # Welcome message
        ttk.Label(dashboard_frame,
                 text=f"Welcome, {self.student_name}!",
                 font=("Arial", 14, "bold")).pack(pady=20)
       
        # Student information section
        info_frame = ttk.LabelFrame(dashboard_frame, text="Your Information")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
       
        try:
            # Get student details
            self.cursor.execute("""
                SELECT name, email, phone FROM students
                WHERE student_id = %s
            """, (self.student_id,))
           
            student_data = self.cursor.fetchone()
           
            if student_data:
                name, email, phone = student_data
               
                ttk.Label(info_frame, text=f"Name: {name}").pack(anchor=tk.W, padx=10, pady=5)
                ttk.Label(info_frame, text=f"Email: {email}").pack(anchor=tk.W, padx=10, pady=5)
                ttk.Label(info_frame, text=f"Phone: {phone}").pack(anchor=tk.W, padx=10, pady=5)
           
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading student info: {err}")
       
        # Current borrowings summary
        borrow_frame = ttk.LabelFrame(dashboard_frame, text="Current Borrowings")
        borrow_frame.pack(fill=tk.X, padx=20, pady=10)
       
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM borrowedbooks
                WHERE student_id = %s AND return_date IS NULL
            """, (self.student_id,))
           
            count = self.cursor.fetchone()[0]
            ttk.Label(borrow_frame, text=f"You currently have {count} books borrowed").pack(anchor=tk.W, padx=10, pady=5)
           
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading borrow count: {err}")
       
        # Overdue books warning
        overdue_frame = ttk.LabelFrame(dashboard_frame, text="Overdue Books")
        overdue_frame.pack(fill=tk.X, padx=20, pady=10)
       
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM borrowedbooks
                WHERE student_id = %s AND return_date IS NULL
                AND DATEDIFF(CURDATE(), borrow_date) > 14
            """, (self.student_id,))
           
            overdue_count = self.cursor.fetchone()[0]
           
            if overdue_count > 0:
                ttk.Label(overdue_frame,
                         text=f"You have {overdue_count} overdue books to return!",
                         foreground="red").pack(anchor=tk.W, padx=10, pady=5)
            else:
                ttk.Label(overdue_frame,
                         text="You have no overdue books.",
                         foreground="green").pack(anchor=tk.W, padx=10, pady=5)
           
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error checking overdue books: {err}")
       
    def create_browse_tab(self):
        browse_frame = ttk.Frame(self.notebook)
        self.notebook.add(browse_frame, text="Book Browsing")
       
        # Search frame
        search_frame = ttk.Frame(browse_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
       
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
       
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
       
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_books)
        search_btn.pack(side=tk.LEFT, padx=5)
       
        refresh_btn = ttk.Button(search_frame, text="Refresh", command=self.load_available_books)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
       
        # Books treeview
        tree_frame = ttk.Frame(browse_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
       
        columns = ("ID", "Title", "Author", "ISBN", "Available")
        self.books_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
       
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=120)
       
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
       
        self.books_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       
        # Borrow button
        button_frame = ttk.Frame(browse_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
       
        borrow_btn = ttk.Button(button_frame, text="Borrow Selected Book", command=self.borrow_book)
        borrow_btn.pack()
       
        # Load initial book data
        self.load_available_books()
       
    def create_current_borrowings_tab(self):
        current_frame = ttk.Frame(self.notebook)
        self.notebook.add(current_frame, text="Current Borrowings")
       
        # Treeview for current borrowings
        tree_frame = ttk.Frame(current_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        columns = ("Borrow ID", "Book Title", "Borrow Date", "Due Date")
        self.current_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
       
        for col in columns:
            self.current_tree.heading(col, text=col)
            self.current_tree.column(col, width=120)
       
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.current_tree.yview)
        self.current_tree.configure(yscroll=scrollbar.set)
       
        self.current_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       
        # Button frame
        button_frame = ttk.Frame(current_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
       
        # Request renewal button
        renew_btn = ttk.Button(button_frame, text="Request Renewal", command=self.request_renewal)
        renew_btn.pack(side=tk.LEFT, padx=5)
       
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.load_current_borrowings)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
       
        # Load initial data
        self.load_current_borrowings()
       
    def create_borrowing_history_tab(self):
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="Borrowing History")
       
        # Treeview for borrowing history
        tree_frame = ttk.Frame(history_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        columns = ("Book Title", "Borrow Date", "Return Date", "Status")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
       
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
       
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
       
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
       
        # Refresh button
        refresh_btn = ttk.Button(history_frame, text="Refresh", command=self.load_borrowing_history)
        refresh_btn.pack(pady=10)
       
        # Load initial data
        self.load_borrowing_history()
       
    def load_available_books(self):
        try:
            # Clear current data
            for item in self.books_tree.get_children():
                self.books_tree.delete(item)
               
            # Execute query
            self.cursor.execute("""
                SELECT b.book_id, b.title, b.author, b.isbn, b.copies_available
                FROM books b
                WHERE b.copies_available > 0
                ORDER BY b.book_id
            """)
           
            # Insert data into treeview
            for book in self.cursor.fetchall():
                self.books_tree.insert("", tk.END, values=book)
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading books: {err}")
           
    def search_books(self):
        try:
            search_term = self.search_var.get()
           
            if not search_term:
                self.load_available_books()
                return
               
            # Clear current data
            for item in self.books_tree.get_children():
                self.books_tree.delete(item)
               
            # Execute search query
            self.cursor.execute("""
                SELECT b.book_id, b.title, b.author, b.isbn, b.copies_available
                FROM books b
                WHERE (b.title LIKE %s OR b.author LIKE %s) AND b.copies_available > 0
                ORDER BY b.book_id
            """, (f"%{search_term}%", f"%{search_term}%"))
           
            # Insert data into treeview
            for book in self.cursor.fetchall():
                self.books_tree.insert("", tk.END, values=book)
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching books: {err}")
           
    def borrow_book(self):
        try:
            selected_item = self.books_tree.selection()
           
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a book to borrow")
                return
               
            # Get book details
            item = self.books_tree.item(selected_item[0])
            book_id = item['values'][0]
            book_title = item['values'][1]
           
            # Check if student has already borrowed this book
            self.cursor.execute("""
                SELECT COUNT(*) FROM borrowedbooks
                WHERE student_id = %s AND book_id = %s AND return_date IS NULL
            """, (self.student_id, book_id))
           
            if self.cursor.fetchone()[0] > 0:
                messagebox.showwarning("Borrow Error", "You have already borrowed this book")
                return
               
            # Borrow the book using the stored procedure
            self.cursor.callproc("borrowbook", (self.student_id, book_id))
            self.conn.commit()
           
            messagebox.showinfo("Success", f"You have successfully borrowed '{book_title}'")
           
            # Refresh all relevant tabs
            self.load_available_books()
            self.load_current_borrowings()
            self.load_borrowing_history()
           
        except mysql.connector.Error as err:
            if "No copies available" in str(err):
                messagebox.showwarning("Borrow Error", "No copies of this book are currently available")
            else:
                messagebox.showerror("Database Error", f"Error borrowing book: {err}")
           
    def request_renewal(self):
        try:
            selected_item = self.current_tree.selection()
           
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select a book to renew")
                return
               
            # Get borrow details
            item = self.current_tree.item(selected_item[0])
            borrow_id = item['values'][0]
            book_title = item['values'][1]
           
            # Check if book is already overdue
            self.cursor.execute("""
                SELECT DATEDIFF(CURDATE(), borrow_date) 
                FROM borrowedbooks 
                WHERE borrow_id = %s
            """, (borrow_id,))
           
            days_borrowed = self.cursor.fetchone()[0]
            
            if days_borrowed > 14:
                messagebox.showwarning("Renewal Error", "Cannot renew overdue books. Please return them first.")
                return
                
            # Check if renewal is possible (only one renewal allowed)
            self.cursor.execute("""
                SELECT renewal_requested 
                FROM borrowedbooks 
                WHERE borrow_id = %s
            """, (borrow_id,))
            
            already_renewed = self.cursor.fetchone()[0]
            
            if already_renewed:
                messagebox.showwarning("Renewal Error", "You have already requested renewal for this book")
                return
                
            # Request renewal
            self.cursor.execute("""
                UPDATE borrowedbooks 
                SET renewal_requested = TRUE 
                WHERE borrow_id = %s
            """, (borrow_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Renewal requested for '{book_title}'. Please wait for approval.")
            self.load_current_borrowings()
           
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error requesting renewal: {err}")
           
    def load_current_borrowings(self):
        try:
            # Clear current data
            for item in self.current_tree.get_children():
                self.current_tree.delete(item)
               
            # Execute query with due date (14 days from borrow date)
            self.cursor.execute("""
                SELECT bb.borrow_id, b.title, bb.borrow_date, 
                       DATE_ADD(bb.borrow_date, INTERVAL 14 DAY) as due_date
                FROM borrowedbooks bb
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.student_id = %s AND bb.return_date IS NULL
                ORDER BY bb.borrow_date
            """, (self.student_id,))
           
            # Insert data into treeview
            for borrow in self.cursor.fetchall():
                borrow_id, title, borrow_date, due_date = borrow
                
                # Check if book is overdue
                if date.today() > due_date:
                    self.current_tree.insert("", tk.END, values=(borrow_id, title, borrow_date, due_date), tags=('overdue',))
                else:
                    self.current_tree.insert("", tk.END, values=(borrow_id, title, borrow_date, due_date))
            
            # Configure tag for overdue books
            self.current_tree.tag_configure('overdue', foreground='red')
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading current borrowings: {err}")
           
    def load_borrowing_history(self):
        try:
            # Clear current data
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
               
            # Execute query
            self.cursor.execute("""
                SELECT b.title, bb.borrow_date, bb.return_date,
                       CASE
                           WHEN bb.return_date IS NULL THEN 'Borrowed'
                           ELSE 'Returned'
                       END AS status
                FROM borrowedbooks bb
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.student_id = %s
                ORDER BY bb.borrow_date DESC
            """, (self.student_id,))
           
            # Insert data into treeview
            for history in self.cursor.fetchall():
                self.history_tree.insert("", tk.END, values=history)
               
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading borrowing history: {err}")
           
    def logout(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()
        self.login_window.deiconify()
       
    def on_close(self):
        self.logout()
       
    def __del__(self):
        if self.conn:
            self.conn.close()


# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()