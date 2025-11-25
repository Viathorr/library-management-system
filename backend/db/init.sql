CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TYPE role AS ENUM ('reader', 'librarian');

CREATE TYPE book_status AS ENUM ('available', 'borrowed', 'reserved');

CREATE TYPE order_status AS ENUM ('pending', 'completed', 'overdue');

CREATE TYPE order_type AS ENUM ('borrow', 'read_in_library');


CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role role NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    book_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    publication_year INT,
    description TEXT
);

CREATE TABLE book_copies (
    copy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    book_id UUID NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    status book_status NOT NULL DEFAULT 'available',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    copy_id UUID NOT NULL REFERENCES book_copies(copy_id) ON DELETE CASCADE,
    order_type order_type,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    return_date TIMESTAMP,
    status order_status NOT NULL DEFAULT 'pending'
);

