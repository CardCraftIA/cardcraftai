-- Follow-up tuning for CardCraft Community.
-- Adds FK indexes and keeps auth.uid() out of per-row RLS evaluation.

create index if not exists community_comments_user_idx
  on public.community_comments(user_id);
create index if not exists community_posts_collection_item_idx
  on public.community_posts(collection_item_id)
  where collection_item_id is not null;
create index if not exists community_reactions_user_idx
  on public.community_reactions(user_id);
create index if not exists community_reports_post_idx
  on public.community_reports(post_id)
  where post_id is not null;
create index if not exists community_reports_comment_idx
  on public.community_reports(comment_id)
  where comment_id is not null;

drop policy if exists community_profiles_read on public.community_profiles;
create policy community_profiles_read on public.community_profiles
for select to authenticated using ((select auth.uid()) is not null);

drop policy if exists community_profiles_insert_own on public.community_profiles;
create policy community_profiles_insert_own on public.community_profiles
for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_profiles_update_own on public.community_profiles;
create policy community_profiles_update_own on public.community_profiles
for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_posts_insert_own on public.community_posts;
create policy community_posts_insert_own on public.community_posts
for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id and status = 'active');

drop policy if exists community_posts_update_own on public.community_posts;
create policy community_posts_update_own on public.community_posts
for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_posts_delete_own on public.community_posts;
create policy community_posts_delete_own on public.community_posts
for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_reactions_read on public.community_reactions;
create policy community_reactions_read on public.community_reactions
for select to authenticated using ((select auth.uid()) is not null);

drop policy if exists community_reactions_insert_own on public.community_reactions;
create policy community_reactions_insert_own on public.community_reactions
for insert to authenticated
with check (
  (select auth.uid()) is not null
  and (select auth.uid()) = user_id
  and exists (
    select 1 from public.community_posts p
    where p.id = post_id and p.status = 'active'
  )
);

drop policy if exists community_reactions_delete_own on public.community_reactions;
create policy community_reactions_delete_own on public.community_reactions
for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_comments_insert_own on public.community_comments;
create policy community_comments_insert_own on public.community_comments
for insert to authenticated
with check (
  (select auth.uid()) is not null
  and (select auth.uid()) = user_id
  and status = 'active'
  and exists (
    select 1 from public.community_posts p
    where p.id = post_id
      and p.status = 'active'
      and p.comments_enabled = true
  )
);

drop policy if exists community_comments_update_own on public.community_comments;
create policy community_comments_update_own on public.community_comments
for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_comments_delete_own on public.community_comments;
create policy community_comments_delete_own on public.community_comments
for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists community_follows_read on public.community_follows;
create policy community_follows_read on public.community_follows
for select to authenticated using ((select auth.uid()) is not null);

drop policy if exists community_follows_insert_own on public.community_follows;
create policy community_follows_insert_own on public.community_follows
for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = follower_id);

drop policy if exists community_follows_delete_own on public.community_follows;
create policy community_follows_delete_own on public.community_follows
for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = follower_id);

drop policy if exists community_reports_insert_own on public.community_reports;
create policy community_reports_insert_own on public.community_reports
for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = reporter_id and status = 'open');

drop policy if exists community_reports_read_own on public.community_reports;
create policy community_reports_read_own on public.community_reports
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = reporter_id);
