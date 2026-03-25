-- SJDAS v2.0: Enterprise RLS Migration Script
-- Objective: Absolute Tenant Isolation for B2B Textile Factories

-- ==========================================
-- 1. ENABLE RLS ON ALL TABLES
-- ==========================================
ALTER TABLE factories ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE loom_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE thread_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE designs ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 2. THE MULTI-TENANT HELPER FUNCTION
-- ==========================================
CREATE OR REPLACE FUNCTION public.get_auth_factory_id()
RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  SELECT factory_id FROM public.users WHERE id = auth.uid();
$$;

-- ==========================================
-- 3. CORE TABLE POLICIES (ISOLATION)
-- ==========================================

-- FACTORIES: A user can only see their own factory's top-level details.
CREATE POLICY "Tenant Isolation: View Own Factory" 
ON factories FOR SELECT 
USING (id = public.get_auth_factory_id());

-- USERS: A user can read their own profile. (Prevents infinite recursion loops).
CREATE POLICY "Users: Read Own Profile" 
ON users FOR SELECT 
USING (id = auth.uid());

-- LOOM PROFILES: Only members of the factory can see/edit their machine setups.
CREATE POLICY "Tenant Isolation: Loom Profiles" 
ON loom_profiles FOR ALL 
USING (factory_id = public.get_auth_factory_id());

-- THREAD INVENTORY: Total lockdown on physical stock visibility.
CREATE POLICY "Tenant Isolation: Thread Inventory" 
ON thread_inventory FOR ALL 
USING (factory_id = public.get_auth_factory_id());

-- DESIGNS: The IP Vault. Absolute isolation for all design assets and metadata.
CREATE POLICY "Tenant Isolation: Designs" 
ON designs FOR ALL 
USING (factory_id = public.get_auth_factory_id());

-- ==========================================
-- 4. SUPABASE STORAGE BUCKET POLICIES
-- ==========================================
-- RAW UPLOADS BUCKET (Private)
CREATE POLICY "Strict Factory Access: Raw Uploads"
ON storage.objects FOR ALL
USING (
  bucket_id = 'raw_uploads' AND 
  (storage.foldername(name))[1] = public.get_auth_factory_id()::text
);

-- PRODUCTION FILES BUCKET (Private)
CREATE POLICY "Strict Factory Access: Production BMPs"
ON storage.objects FOR ALL
USING (
  bucket_id = 'production_files' AND 
  (storage.foldername(name))[1] = public.get_auth_factory_id()::text
);
