-- SkillBridge Local Milestone 3
-- Administrator verification and secure opportunity publishing.

do $$ begin
    create type public.opportunity_status as enum ('draft', 'pending_review', 'published', 'rejected', 'closed');
exception when duplicate_object then null; end $$;

do $$ begin
    create type public.work_arrangement as enum ('on_site', 'remote', 'hybrid');
exception when duplicate_object then null; end $$;

do $$ begin
    create type public.compensation_type as enum ('paid', 'stipend', 'unpaid');
exception when duplicate_object then null; end $$;

create table if not exists public.opportunities (
    id uuid primary key default gen_random_uuid(),
    business_id uuid not null references public.business_profiles(user_id) on delete cascade,
    title text not null check (char_length(trim(title)) >= 5),
    description text not null check (char_length(trim(description)) >= 30),
    skills_required text[] not null check (cardinality(skills_required) > 0),
    location text not null,
    work_arrangement public.work_arrangement not null,
    compensation_type public.compensation_type not null,
    compensation_amount numeric(12,2) check (compensation_amount is null or compensation_amount > 0),
    duration_weeks smallint not null check (duration_weeks between 1 and 52),
    application_deadline date not null,
    status public.opportunity_status not null default 'draft',
    review_note text,
    reviewed_at timestamptz,
    reviewed_by uuid references public.profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint compensation_amount_required check (
        (compensation_type = 'unpaid' and compensation_amount is null)
        or (compensation_type in ('paid', 'stipend') and compensation_amount > 0)
    )
);

drop trigger if exists opportunities_set_updated_at on public.opportunities;
create trigger opportunities_set_updated_at before update on public.opportunities
for each row execute function public.set_updated_at();

create or replace function public.is_admin()
returns boolean language sql stable security definer set search_path = ''
as $$ select exists (select 1 from public.profiles where id = auth.uid() and role = 'admin'); $$;

create or replace function public.protect_business_verification()
returns trigger language plpgsql set search_path = '' as $$
begin
    if tg_op = 'INSERT' then
        new.verification_status := 'pending';
        new.verification_note := null;
        new.verified_at := null;
        new.verified_by := null;
    elsif not public.is_admin() and (
        new.verification_status is distinct from old.verification_status
        or new.verification_note is distinct from old.verification_note
        or new.verified_at is distinct from old.verified_at
        or new.verified_by is distinct from old.verified_by
    ) then raise exception 'Verification fields can only be changed through an administrator workflow'; end if;
    return new;
end; $$;

create or replace function public.protect_opportunity_review()
returns trigger language plpgsql set search_path = '' as $$
begin
    if not public.is_admin() and (
        new.status in ('published', 'rejected')
        or new.review_note is distinct from old.review_note
        or new.reviewed_at is distinct from old.reviewed_at
        or new.reviewed_by is distinct from old.reviewed_by
    ) then raise exception 'Review fields can only be changed by an administrator'; end if;
    return new;
end; $$;

drop trigger if exists protect_opportunity_review on public.opportunities;
create trigger protect_opportunity_review before update on public.opportunities
for each row execute function public.protect_opportunity_review();

alter table public.opportunities enable row level security;

drop policy if exists "Anyone reads published opportunities" on public.opportunities;
create policy "Anyone reads published opportunities" on public.opportunities for select
using (status = 'published' and application_deadline >= current_date);

drop policy if exists "Businesses read own opportunities" on public.opportunities;
create policy "Businesses read own opportunities" on public.opportunities for select to authenticated
using (business_id = auth.uid());

drop policy if exists "Verified businesses create opportunities" on public.opportunities;
create policy "Verified businesses create opportunities" on public.opportunities for insert to authenticated
with check (
    business_id = auth.uid() and status in ('draft', 'pending_review') and exists (
        select 1 from public.business_profiles b where b.user_id = auth.uid() and b.verification_status = 'verified'
    )
);

drop policy if exists "Businesses update own drafts" on public.opportunities;
create policy "Businesses update own drafts" on public.opportunities for update to authenticated
using (business_id = auth.uid() and status in ('draft', 'rejected'))
with check (business_id = auth.uid() and status in ('draft', 'pending_review'));

drop policy if exists "Admins read all opportunities" on public.opportunities;
create policy "Admins read all opportunities" on public.opportunities for select to authenticated
using (public.is_admin());

drop policy if exists "Admins read all profiles" on public.profiles;
create policy "Admins read all profiles" on public.profiles for select to authenticated
using (public.is_admin());

drop policy if exists "Admins read all businesses" on public.business_profiles;
create policy "Admins read all businesses" on public.business_profiles for select to authenticated
using (public.is_admin());

create or replace function public.review_business(
    target_business_id uuid, decision text, p_review_note text default null
) returns void language plpgsql security definer set search_path = '' as $$
begin
    if not public.is_admin() then raise exception 'Administrator access required'; end if;
    if decision not in ('verified', 'rejected') then raise exception 'Invalid decision'; end if;
    update public.business_profiles set
        verification_status = decision::public.verification_status,
        verification_note = p_review_note,
        verified_at = case when decision = 'verified' then now() else null end,
        verified_by = auth.uid()
    where user_id = target_business_id;
end; $$;

create or replace function public.review_opportunity(
    target_opportunity_id uuid, decision text, p_review_note text default null
) returns void language plpgsql security definer set search_path = '' as $$
begin
    if not public.is_admin() then raise exception 'Administrator access required'; end if;
    if decision not in ('published', 'rejected') then raise exception 'Invalid decision'; end if;
    update public.opportunities set status = decision::public.opportunity_status,
        review_note = p_review_note, reviewed_at = now(), reviewed_by = auth.uid()
    where id = target_opportunity_id and status = 'pending_review';
end; $$;

revoke all on function public.review_business(uuid, text, text) from public;
grant execute on function public.review_business(uuid, text, text) to authenticated;
revoke all on function public.review_opportunity(uuid, text, text) from public;
grant execute on function public.review_opportunity(uuid, text, text) to authenticated;
