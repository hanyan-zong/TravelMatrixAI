# 数据库 SQL 草案

## 1. 说明

这是一份 PostgreSQL 建表草案，开发时可以根据 ORM 框架调整。

## 2. 枚举

```sql
create type platform_type as enum (
  'xiaohongshu',
  'douyin',
  'wechat_channels',
  'toutiao',
  'weibo',
  'douban'
);

create type risk_level as enum ('low', 'medium', 'high');
create type publish_method as enum ('api', 'enterprise_api', 'manual_assist');
create type post_status as enum (
  'draft',
  'pending_review',
  'approved',
  'rejected',
  'scheduled',
  'published',
  'failed'
);
```

## 3. 核心表

```sql
create table workspaces (
  id uuid primary key,
  name text not null,
  created_at timestamptz not null default now()
);

create table users (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  name text not null,
  email text unique,
  phone text,
  password_hash text not null,
  role text not null,
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table brands (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  name text not null,
  logo_url text,
  brand_voice text,
  blocked_words text[],
  default_cta text,
  created_at timestamptz not null default now()
);
```

## 4. 旅游产品

```sql
create table travel_products (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  brand_id uuid references brands(id),
  name text not null,
  destination text not null,
  days integer,
  departure_city text,
  target_audience text,
  selling_points text[],
  reference_price text,
  inclusions text,
  exclusions text,
  notes text,
  status text not null default 'active',
  owner_id uuid references users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table day_itineraries (
  id uuid primary key,
  product_id uuid not null references travel_products(id) on delete cascade,
  day_number integer not null,
  title text,
  attractions text[],
  meals text,
  hotel text,
  transport text,
  description text
);
```

## 5. 素材

```sql
create table media_assets (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  type text not null,
  file_url text not null,
  thumbnail_url text,
  title text,
  tags text[],
  destination text,
  scene text,
  license_status text not null default 'pending',
  uploaded_by uuid references users(id),
  use_count integer not null default 0,
  created_at timestamptz not null default now()
);

create table person_assets (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  display_name text not null,
  asset_url text not null,
  authorization_type text not null,
  allowed_usages text[],
  expires_at timestamptz,
  forbidden_usages text[],
  notes text,
  created_at timestamptz not null default now()
);
```

## 6. 账号与内容

```sql
create table social_accounts (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  platform platform_type not null,
  account_name text not null,
  positioning text,
  allowed_content text,
  forbidden_content text,
  publish_frequency text,
  login_status text not null default 'unknown',
  health_score integer not null default 100,
  owner_id uuid references users(id),
  created_at timestamptz not null default now()
);

create table post_drafts (
  id uuid primary key,
  workspace_id uuid not null references workspaces(id),
  product_id uuid references travel_products(id),
  title text,
  body text,
  status post_status not null default 'draft',
  risk_level risk_level,
  created_by uuid references users(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table post_variants (
  id uuid primary key,
  draft_id uuid not null references post_drafts(id) on delete cascade,
  platform platform_type not null,
  account_id uuid references social_accounts(id),
  title text,
  body text,
  hashtags text[],
  cover_text text,
  video_script text,
  status post_status not null default 'draft',
  created_at timestamptz not null default now()
);
```

## 7. 审核、发布、数据

```sql
create table compliance_checks (
  id uuid primary key,
  target_type text not null,
  target_id uuid not null,
  risk_level risk_level not null,
  issues jsonb not null default '[]',
  suggestions jsonb not null default '[]',
  allow_publish boolean not null default false,
  created_at timestamptz not null default now()
);

create table publish_tasks (
  id uuid primary key,
  variant_id uuid not null references post_variants(id),
  platform platform_type not null,
  account_id uuid references social_accounts(id),
  scheduled_at timestamptz not null,
  publish_method publish_method not null default 'manual_assist',
  status post_status not null default 'scheduled',
  owner_id uuid references users(id),
  published_url text,
  created_at timestamptz not null default now()
);

create table publish_logs (
  id uuid primary key,
  task_id uuid not null references publish_tasks(id) on delete cascade,
  operator_id uuid references users(id),
  action text not null,
  result text not null,
  message text,
  created_at timestamptz not null default now()
);

create table platform_metrics (
  id uuid primary key,
  task_id uuid not null references publish_tasks(id) on delete cascade,
  impressions integer,
  views integer,
  completion_rate numeric,
  likes integer,
  saves integer,
  comments integer,
  shares integer,
  private_messages integer,
  leads integer,
  conversions integer,
  recorded_at timestamptz not null default now()
);
```

