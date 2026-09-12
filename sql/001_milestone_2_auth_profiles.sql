-- SkillBridge Local Milestone 2
-- Authentication profile tables, integrity controls, and Row Level Security.

do $$
begin
    create type public.user_role as enum ('student', 'business', 'admin');
exception
    when duplicate_object then null;
end $$;

do $$
begin
    create type public.verification_status as enum ('pending', 'verified', 'rejected', 'suspended');
exception
    when duplicate_object then null;
end $$;

create table if not exists public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    role public.user_role not null,
    full_name text not null,
    email text not null,
    phone text,
    location text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.student_profiles (
    user_id uuid primary key references public.profiles(id) on delete cascade,
    education text,
    skills text[] not null default '{}',
    tools text[] not null default '{}',
    experience_level text,
    bio text,
    portfolio_url text,
    linkedin_url text,
    availability text,
    guardian_consent_confirmed boolean not null default false
);

create table if not exists public.business_profiles (
    user_id uuid primary key references public.profiles(id) on delete cascade,
    business_name text not null default '',
    industry text,
    description text,
    address text,
    verification_status public.verification_status not null default 'pending',
    verification_note text,
    verified_at timestamptz,
    verified_by uuid references public.profiles(id)
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
    requested_role public.user_role;
    requested_name text;
begin
    requested_role := case
        when new.raw_user_meta_data ->> 'role' = 'business' then 'business'::public.user_role
        else 'student'::public.user_role
    end;
    requested_name := coalesce(nullif(trim(new.raw_user_meta_data ->> 'full_name'), ''), 'New user');

    insert into public.profiles (id, role, full_name, email)
    values (new.id, requested_role, requested_name, coalesce(new.email, ''));

    if requested_role = 'student' then
        insert into public.student_profiles (user_id) values (new.id);
    else
        insert into public.business_profiles (user_id) values (new.id);
    end if;

    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

create or replace function public.protect_profile_role()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    if new.role is distinct from old.role then
        raise exception 'Account role cannot be changed directly';
    end if;
    return new;
end;
$$;

drop trigger if exists protect_profile_role on public.profiles;
create trigger protect_profile_role
before update on public.profiles
for each row execute function public.protect_profile_role();

create or replace function public.protect_business_verification()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
    if tg_op = 'INSERT' then
        new.verification_status := 'pending';
        new.verification_note := null;
        new.verified_at := null;
        new.verified_by := null;
    elsif new.verification_status is distinct from old.verification_status
       or new.verification_note is distinct from old.verification_note
       or new.verified_at is distinct from old.verified_at
       or new.verified_by is distinct from old.verified_by then
        raise exception 'Verification fields can only be changed through an administrator workflow';
    end if;
    return new;
end;
$$;

drop trigger if exists protect_business_verification on public.business_profiles;
create trigger protect_business_verification
before insert or update on public.business_profiles
for each row execute function public.protect_business_verification();

alter table public.profiles enable row level security;
alter table public.student_profiles enable row level security;
alter table public.business_profiles enable row level security;

drop policy if exists "Users read own profile" on public.profiles;
create policy "Users read own profile"
on public.profiles for select
to authenticated
using ((select auth.uid()) = id);

drop policy if exists "Users update own profile" on public.profiles;
create policy "Users update own profile"
on public.profiles for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

drop policy if exists "Students read own details" on public.student_profiles;
create policy "Students read own details"
on public.student_profiles for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "Students insert own details" on public.student_profiles;
create policy "Students insert own details"
on public.student_profiles for insert
to authenticated
with check (
    (select auth.uid()) = user_id
    and exists (
        select 1 from public.profiles p
        where p.id = (select auth.uid()) and p.role = 'student'
    )
);

drop policy if exists "Students update own details" on public.student_profiles;
create policy "Students update own details"
on public.student_profiles for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "Businesses read own details" on public.business_profiles;
create policy "Businesses read own details"
on public.business_profiles for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "Businesses insert own details" on public.business_profiles;
create policy "Businesses insert own details"
on public.business_profiles for insert
to authenticated
with check (
    (select auth.uid()) = user_id
    and exists (
        select 1 from public.profiles p
        where p.id = (select auth.uid()) and p.role = 'business'
    )
);

drop policy if exists "Businesses update own details" on public.business_profiles;
create policy "Businesses update own details"
on public.business_profiles for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

