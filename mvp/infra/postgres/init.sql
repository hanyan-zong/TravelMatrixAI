create extension if not exists "uuid-ossp";

create table if not exists health_check (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  created_at timestamptz not null default now()
);

insert into health_check (name)
values ('travelmatrix-init')
on conflict do nothing;
