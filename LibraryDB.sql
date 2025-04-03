DROP DATABASE IF EXISTS LibraryDB;
CREATE DATABASE LibraryDB;
USE LibraryDB;

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin','Normal') NOT NULL
);	

/*Students Table */  
CREATE TABLE students(	
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) UNIQUE,
    user_id INT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*Books Table */  
CREATE TABLE books(
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(30) NOT NULL,
    copies_available INT NOT NULL CHECK(copies_available>=0)
);

/*Borrowed books Table */  
CREATE TABLE borrowedbooks(
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE ON UPDATE CASCADE
);

/*Transactions Table */ 
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    borrow_id INT NOT NULL,
    student_id INT NOT NULL,
    book_id INT NOT NULL,
    transaction_type ENUM('Borrow','Return') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (borrow_id) REFERENCES borrowedbooks(borrow_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE authors (
    a_id INT AUTO_INCREMENT PRIMARY KEY,
    a_name VARCHAR(255) NOT NULL
);

CREATE TABLE publishers (
    p_id INT AUTO_INCREMENT PRIMARY KEY,
    p_name VARCHAR(255) NOT NULL,
    contact VARCHAR(50)
);

ALTER TABLE books 
ADD COLUMN a_id INT,
ADD COLUMN p_id INT,
ADD FOREIGN KEY (a_id) REFERENCES authors(a_id) ON DELETE SET NULL ON UPDATE CASCADE,
ADD FOREIGN KEY (p_id) REFERENCES publishers(p_id) ON DELETE SET NULL ON UPDATE CASCADE;

INSERT INTO authors (a_name) VALUES 
('J.D. Salinger'),
('Harper Lee'),
('George Orwell'),
('Valsarajan Nambiar'),
('Herman Melville'),
('Jane Austen');

INSERT INTO publishers (p_name, contact) VALUES 
('Penguin Books', '123-456-7890'),
('HarperCollins', '987-654-3210'),
('Random House', '555-123-4567'),
('Palava Publishers','956-845-517'),
('Oxford University Press', '222-333-4444'),
('Macmillan Publishers', '111-222-3333');

INSERT INTO books (title, author, isbn, copies_available, a_id, p_id) VALUES 
('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 5, 1, 1),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 3, 2, 2),
('1984', 'George Orwell', '9780451524935', 4, 3, 3),
('Harshita Nambiar','Valsarajan Nambiar','978045651354',1,4,4),
('Moby-Dick', 'Herman Melville', '9781503280786', 2, 5, 5),
('Pride and Prejudice', 'Jane Austen', '9781503290563', 6, 6, 6);

DELIMITER $$
CREATE TRIGGER after_borrow_book
AFTER INSERT ON borrowedbooks
FOR EACH ROW
BEGIN
    DECLARE book_count INT;
    SELECT copies_available INTO book_count FROM books WHERE book_id = NEW.book_id FOR UPDATE;
    
    IF book_count > 0 THEN
        UPDATE books SET copies_available = copies_available - 1 WHERE book_id = NEW.book_id;
    ELSE
        -- This shouldn't happen if using the borrowbook procedure
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No copies available';
    END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE borrowbook(IN studentId INT, IN bookId INT)
BEGIN
    DECLARE copies INT;
    DECLARE borrowId INT;
    
    SELECT copies_available INTO copies FROM books WHERE book_id = bookId FOR UPDATE;
     
    IF copies > 0 THEN
        INSERT INTO borrowedbooks(student_id, book_id, borrow_date) 
        VALUES(studentId, bookId, CURDATE());
        
        -- Get the last inserted borrow_id
        SET borrowId = LAST_INSERT_ID();
        
        -- Log the borrow transaction
        INSERT INTO transactions (borrow_id, student_id, book_id, transaction_type, transaction_date) 
        VALUES (borrowId, studentId, bookId, 'Borrow', NOW());
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No copies available';
    END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE returnbook(IN borrowId INT)
BEGIN
    DECLARE bookId INT;
    DECLARE returnstatus DATE;

    -- Get book_id and check if the book is already returned
    SELECT book_id, return_date INTO bookId, returnstatus 
    FROM borrowedbooks 
    WHERE borrow_id = borrowId FOR UPDATE;
    
    -- If return_date is already set, prevent duplicate return
    IF returnstatus IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book is already returned';
    ELSE
        -- Update return_date
        UPDATE borrowedbooks 
        SET return_date = CURDATE() 
        WHERE borrow_id = borrowId;
        
        -- Log the return transaction
        INSERT INTO transactions (borrow_id, student_id, book_id, transaction_type, transaction_date) 
        SELECT borrow_id, student_id, book_id, 'Return', NOW()
        FROM borrowedbooks
        WHERE borrow_id = borrowId;
    END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER after_book_return
AFTER UPDATE ON borrowedbooks
FOR EACH ROW
BEGIN
    IF NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        UPDATE books
        SET copies_available = copies_available + 1
        WHERE book_id = NEW.book_id;
    END IF;
END $$
DELIMITER ;

-- Not implemented right now, just adding it to try it later
DELIMITER $$
CREATE TRIGGER before_insert_user
BEFORE INSERT ON user
FOR EACH ROW
BEGIN
    IF NEW.role = 'Admin' AND NEW.password IS NULL THEN
        SET NEW.password = '1234a';
    ELSEIF NEW.role = 'Normal' AND NEW.password IS NULL THEN
        SET NEW.password = '1234n';
    END IF;
END $$
DELIMITER ;

DROP USER IF EXISTS 'admin_user'@'localhost';
CREATE USER 'admin_user'@'localhost' IDENTIFIED BY 'adminpassword';
DROP USER IF EXISTS 'normal_user'@'localhost';
CREATE USER 'normal_user'@'localhost' IDENTIFIED BY 'normalpassword';

GRANT ALL PRIVILEGES ON LibraryDB.* TO 'admin_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON LibraryDB.borrowedbooks TO 'normal_user'@'localhost';

INSERT INTO user (username, password, role) VALUES
('admin1', '1234a', 'Admin'),
('RB101', '1234n', 'Normal'),
('JF101', '1234n', 'Normal'),
('admin2', '1234a', 'Admin'),
('CB101', '1234n', 'Normal'),
('DW101', '1234n', 'Normal'),
('SM101', '1234n', 'Normal');

INSERT INTO students(name, email, phone, user_id) VALUES
('Robert Junior', 'Robjr@gmail.com', '9876543210', 2),
('Jimmy Fallon', 'JimFal@gmail.com', '9876543211', 3),
('Charlotte Brown', 'charlotte@gmail.com', '9876501234', 5),
('Daniel Wilson', 'daniel@gmail.com', '9876505678', 6),
('Sophia Martin', 'sophia@gmail.com', '9876512345', 7);

-- Use the borrowbook procedure instead of direct inserts
CALL borrowbook(1, 1);
CALL borrowbook(2, 2);
CALL borrowbook(1, 3);
CALL borrowbook((SELECT student_id FROM students WHERE name='Charlotte Brown'), 
                (SELECT book_id FROM books WHERE title='1984'));
CALL borrowbook((SELECT student_id FROM students WHERE name='Daniel Wilson'), 
                (SELECT book_id FROM books WHERE title='Moby-Dick'));
CALL borrowbook((SELECT student_id FROM students WHERE name='Sophia Martin'), 
                (SELECT book_id FROM books WHERE title='Moby-Dick'));

/* backup tables and triggers */
CREATE TABLE user_backup (
    user_id INT,
    username VARCHAR(255),
    password VARCHAR(255),
    role ENUM('Admin', 'Normal'),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_user
BEFORE DELETE ON user
FOR EACH ROW
BEGIN
    INSERT INTO user_backup (user_id, username, password, role, deleted_at)
    VALUES (OLD.user_id, OLD.username, OLD.password, OLD.role, NOW());
END $$
DELIMITER ;

CREATE TABLE students_backup (
    student_id INT,
    name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    user_id INT,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_students
BEFORE DELETE ON students
FOR EACH ROW
BEGIN
    INSERT INTO students_backup (student_id, name, email, phone, user_id, deleted_at)
    VALUES (OLD.student_id, OLD.name, OLD.email, OLD.phone, OLD.user_id, NOW());
END $$
DELIMITER ;

CREATE TABLE books_backup (
    book_id INT,
    title VARCHAR(255),
    author VARCHAR(255),
    isbn VARCHAR(30),
    copies_available INT,
    a_id INT,
    p_id INT,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_books
BEFORE DELETE ON books
FOR EACH ROW
BEGIN
    INSERT INTO books_backup (book_id, title, author, isbn, copies_available, a_id, p_id, deleted_at)
    VALUES (OLD.book_id, OLD.title, OLD.author, OLD.isbn, OLD.copies_available, OLD.a_id, OLD.p_id, NOW());
END $$
DELIMITER ;

CREATE TABLE borrowedbooks_backup (
    borrow_id INT,
    student_id INT,
    book_id INT,
    borrow_date DATE,
    return_date DATE,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_borrowedbooks
BEFORE DELETE ON borrowedbooks
FOR EACH ROW
BEGIN
    INSERT INTO borrowedbooks_backup (borrow_id, student_id, book_id, borrow_date, return_date, deleted_at)
    VALUES (OLD.borrow_id, OLD.student_id, OLD.book_id, OLD.borrow_date, OLD.return_date, NOW());
END $$
DELIMITER ;

CREATE TABLE transactions_backup (
    transaction_id INT,
    borrow_id INT,
    student_id INT,
    book_id INT,
    transaction_type ENUM('Borrow', 'Return'),
    transaction_date TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_transactions
BEFORE DELETE ON transactions
FOR EACH ROW
BEGIN
    INSERT INTO transactions_backup (transaction_id, borrow_id, student_id, book_id, transaction_type, transaction_date, deleted_at)
    VALUES (OLD.transaction_id, OLD.borrow_id, OLD.student_id, OLD.book_id, OLD.transaction_type, OLD.transaction_date, NOW());
END $$
DELIMITER ;

CREATE TABLE authors_backup (
    a_id INT,
    a_name VARCHAR(255),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_authors
BEFORE DELETE ON authors
FOR EACH ROW
BEGIN
    INSERT INTO authors_backup (a_id, a_name, deleted_at)
    VALUES (OLD.a_id, OLD.a_name, NOW());
END $$
DELIMITER ;

CREATE TABLE publishers_backup (
    p_id INT,
    p_name VARCHAR(255),
    contact VARCHAR(50),
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER before_delete_publishers
BEFORE DELETE ON publishers
FOR EACH ROW
BEGIN
    INSERT INTO publishers_backup (p_id, p_name, contact, deleted_at)
    VALUES (OLD.p_id, OLD.p_name, OLD.contact, NOW());
END $$
DELIMITER ;