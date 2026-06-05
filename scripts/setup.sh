#!/usr/bin/env bash
# Wathiq — Setup script. Run this after cloning.
set -e
echo "=== Wathiq Setup ==="
if [ ! -f backend/.env ]; then
    echo "Creating backend/.env..."
    cat > backend/.env << 'ENVEOF'
SUPABASE_URL=https://yywowhdgwcxulgnglcck.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5d293aGRnd2N4dWxnbmdsY2NrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk0MTYzMDEsImV4cCI6MjA5NDk5MjMwMX0.dmMi7gxOL3qztqX2k7bElN7siGr2Eg7I_MsXoyzo7uk
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5d293aGRnd2N4dWxnbmdsY2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTQxNjMwMSwiZXhwIjoyMDk0OTkyMzAxfQ.7VFEg15ow1pSGJuKAtincXsuV17yeS_3ClISDm0If2M
GEMINI_API_KEY=***
ENVEOF
    echo "✅ .env created"
fi

# Apply Supabase migrations
echo "Applying Supabase migrations..."
cd supabase
# You'll need to run the SQL from supabase/migrations/ manually in the Supabase dashboard
echo "🔧 Go to https://supabase.com/dashboard/project/yywowhdgwcxulgnglcck/sql/new"
echo "   and paste the contents of:"
echo "   - supabase/migrations/001_initial_schema.sql"
echo "   - supabase/migrations/002_seed_data.sql"
echo "   - supabase/seed/compliance_rules_seed.sql"

echo ""
echo "=== Setup Complete ==="
echo "To start the backend locally:"
echo "  cd backend && pip install -r requirements.txt && PYTHONPATH=. uvicorn app.main:app --reload --port 8000"
echo ""
echo "To deploy to Render:"
echo "  1. Push to GitHub"
echo "  2. Connect repo to Render (dashboard.render.com)"
echo "  3. Use render.yaml as blueprint"
echo "  4. Add secrets: SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY"