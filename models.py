# Supabase Table Schemas (run these SQL queries in Supabase dashboard)

SCHEMA = """
-- Users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY,  -- telegram user id
    username TEXT,
    full_name TEXT,
    role TEXT CHECK (role IN ('employer', 'freelancer')),
    skills TEXT[],  -- only for freelancers
    bio TEXT,
    rating FLOAT DEFAULT 0,
    rating_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id BIGINT REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    budget_min BIGINT NOT NULL,  -- in Tomans
    budget_max BIGINT NOT NULL,
    deadline_days INT NOT NULL,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'completed', 'cancelled')),
    selected_freelancer_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Proposals table
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    freelancer_id BIGINT REFERENCES users(id),
    price BIGINT NOT NULL,
    delivery_days INT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    sender_id BIGINT REFERENCES users(id),
    receiver_id BIGINT REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Escrow table
CREATE TABLE escrow (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) UNIQUE,
    amount BIGINT NOT NULL,
    status TEXT DEFAULT 'held' CHECK (status IN ('held', 'released', 'refunded')),
    payment_ref TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Ratings table
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    rater_id BIGINT REFERENCES users(id),
    rated_id BIGINT REFERENCES users(id),
    score INT CHECK (score BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
