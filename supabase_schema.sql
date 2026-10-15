-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql)

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Users table
create table if not exists users (
    id serial primary key,
    username text unique not null,
    password text not null,
    role text default 'citizen',
    name text,
    email text,
    avatar text
);

-- Posts table
create table if not exists posts (
    id serial primary key,
    user_id integer references users(id),
    title text,
    content text,
    category text default 'general',
    image text,
    status text default 'draft',
    created_at text,
    published_at text,
    author text
);

-- Events table
create table if not exists events (
    id serial primary key,
    user_id integer references users(id),
    title text,
    content text,
    date text,
    location text,
    image text,
    status text default 'draft',
    created_at text
);

alter table events add column if not exists image text;

-- Albums table
create table if not exists albums (
    id serial primary key,
    user_id integer references users(id),
    title text,
    posts jsonb default '[]'::jsonb
);

-- Contact form submissions are private and written only by the Flask service.
create table if not exists contact_messages (
    id bigserial primary key,
    name text not null,
    email text not null,
    message text not null,
    created_at timestamptz not null default now()
);

-- The Flask backend uses SUPABASE_SERVICE_ROLE_KEY and is the only database client.
-- Never expose that key to browsers or other untrusted clients.
alter table users enable row level security;
alter table posts enable row level security;
alter table events enable row level security;
alter table albums enable row level security;
alter table contact_messages enable row level security;

-- Remove legacy policies that exposed user hashes and allowed unrestricted writes.
drop policy if exists "Allow public read" on users;
drop policy if exists "Allow public read" on posts;
drop policy if exists "Allow public read" on events;
drop policy if exists "Allow public read" on albums;
drop policy if exists "Allow all operations" on users;
drop policy if exists "Allow all operations" on posts;
drop policy if exists "Allow all operations" on events;
drop policy if exists "Allow all operations" on albums;

grant usage on schema public to service_role;
grant select, insert, update, delete on public.users, public.posts, public.events, public.albums to service_role;
grant select, insert on public.contact_messages to service_role;
grant usage, select on all sequences in schema public to service_role;
