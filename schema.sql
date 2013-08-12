CREATE TABLE authors (
        id INTEGER NOT NULL,
        name VARCHAR(50),
        PRIMARY KEY (id),
        UNIQUE (name)
);
CREATE TABLE books (
        id INTEGER NOT NULL,
        name VARCHAR(50),
        PRIMARY KEY (id)
);
CREATE TABLE persons (
        id INTEGER NOT NULL,
        name VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        password VARCHAR(50) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (name),
        UNIQUE (email)
);
CREATE TABLE shelfs (
        id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(author_id) REFERENCES authors (id),
        FOREIGN KEY(book_id) REFERENCES books (id)
);