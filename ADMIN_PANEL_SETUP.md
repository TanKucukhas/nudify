# Admin Panel Setup Guide

## 🎉 What's Been Built

### Backend API (Sprint 1 - COMPLETED ✅)

**New Endpoints Added:**
```
GET  /api/models                              - List all models
GET  /api/experiments                         - List all experiments
GET  /api/experiments/{id}                    - Get experiment details
GET  /api/experiments/{id}/images/{filename}  - Serve images
DELETE /api/experiments/{id}                  - Delete experiment
POST /api/batch                               - Create batch generation
GET  /api/batch/{batch_id}                    - Get batch status
GET  /api/batch                               - List all batch jobs
```

**Features:**
- ✅ Model management API
- ✅ Experiment listing and details
- ✅ Image serving endpoint
- ✅ Batch job manager (background processing)
- ✅ CORS enabled for Next.js
- ✅ Full integration with existing model manager

### Next.js Admin Panel (COMPLETED ✅)

**All Pages Built:**
- ✅ Dashboard - Health monitoring, stats, recent experiments
- ✅ Generate (`/generate`) - Single image generation with live preview
- ✅ Batch Creator (`/batch`) - Multi-prompt generation with JSON paste support
- ✅ Image Gallery (`/gallery`) - Browse, filter, compare, and manage images
- ✅ Model Manager (`/models`) - View models, test generation, configuration info

**Core Features:**
- ✅ Next.js 14 app with TypeScript
- ✅ React Query for API state management
- ✅ TypeScript types matching backend
- ✅ API client with all endpoints
- ✅ Real-time polling for batch job progress
- ✅ Image comparison mode
- ✅ Model testing functionality
- ✅ Responsive UI with Tailwind CSS

**Current Status:**
- Running on: `http://localhost:4000`
- Backend API: `http://localhost:8001`
- ComfyUI: `http://localhost:8000`

---

## 🚀 Quick Start

### 1. Start Backend (Already Running)
```bash
cd ~/workspace/nudify
source venv/bin/activate
python -m backend.server

# Should see:
# Starting server on 0.0.0.0:8001
# ComfyUI URL: http://localhost:8000
```

### 2. Start Next.js Admin Panel
```bash
cd ~/workspace/nudify/admin
PORT=4000 npm run dev

# Or use the start script:
npm run dev
```

### 3. Access Admin Panel
Open browser: `http://localhost:4000`

You should see:
- Dashboard with backend health status
- Model count
- Experiment count
- Quick action buttons
- Recent experiments list

---

## 📁 Project Structure

```
nudify/
├── backend/
│   ├── server.py           ← Updated with new endpoints
│   ├── models.py           ← Added BatchRequest model
│   ├── job_manager.py      ← NEW: Batch job processing
│   ├── model_manager.py    ← Existing (used by new endpoints)
│   └── comfyui_client.py   ← Existing
│
├── configs/
│   └── models.json         ← Central model configuration
│
└── admin/                  ← NEW: Next.js Admin Panel
    ├── app/
    │   ├── layout.tsx      ← Root layout with nav
    │   ├── page.tsx        ← Dashboard
    │   ├── providers.tsx   ← React Query provider
    │   ├── generate/       ← TODO: Prompt Builder
    │   ├── batch/          ← TODO: Batch Creator
    │   ├── gallery/        ← TODO: Image Gallery
    │   └── models/         ← TODO: Model Manager
    │
    ├── lib/
    │   ├── api-client.ts   ← Backend API wrapper
    │   └── types.ts        ← TypeScript types
    │
    ├── .env.local          ← Environment config
    └── package.json
```

---

## 🛠️ Development Workflow

### Testing Backend Endpoints

```bash
# Health check
curl http://localhost:8001/health | jq

# List models
curl http://localhost:8001/api/models | jq

# List experiments
curl http://localhost:8001/api/experiments | jq

# Get experiment details
curl http://localhost:8001/api/experiments/exp_sdxl_base_test | jq

# View an image
curl http://localhost:8001/api/experiments/exp_sdxl_base_test/images/test_1763299287_456.png --output test.png
```

### Making API Changes

1. Edit `backend/server.py` or `backend/models.py`
2. Backend auto-reloads (uvicorn --reload)
3. Update `admin/lib/types.ts` if response changed
4. Next.js auto-refreshes

### Adding a New Page

```bash
cd admin/app
mkdir generate
touch generate/page.tsx
```

Example structure:
```typescript
'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');

  const generate = useMutation({
    mutationFn: (req: GenerateRequest) => apiClient.generate(req),
  });

  // ... rest of component
}
```

---

## 📋 Features Overview

### Dashboard (`/`)
- Real-time backend and ComfyUI health monitoring
- Statistics cards (experiments count, models count)
- Recent experiments list
- Quick action buttons to all pages
- Auto-refresh every 5 seconds

### Generate Page (`/generate`)
- Single image generation with full parameter control
- Model selector with auto-loaded recommended settings
- Prompt and negative prompt inputs
- Parameter sliders (steps, CFG scale)
- Dimension selectors (width/height)
- Seed control (random or fixed)
- Advanced settings (denoise, scheduler)
- Live image preview
- Download generated images
- Copy seed from successful generations

### Batch Creator (`/batch`)
- **Simple Mode**: Paste multiple prompts (one per line)
- **JSON Mode**: Import full experiment configurations
- Shared parameters across all prompts
- Real-time batch progress tracking
- Individual job status monitoring
- Success/failure statistics
- Direct link to gallery for completed batches
- Progress polling (updates every 2 seconds)

### Image Gallery (`/gallery`)
- Grid view of all generated images
- Filter by experiment, stage
- Search by filename or experiment ID
- Click to enlarge with full metadata
- Download individual images
- Delete entire experiments
- **Compare Mode**: Select up to 4 images for side-by-side comparison
- Image details (file size, creation date, path)
- Responsive grid layout

### Model Manager (`/models`)
- View all enabled and disabled models
- Model statistics and default settings
- Detailed model information (checkpoint, type, description)
- Recommended settings display
- Quick test generation for any model
- Configuration guidance
- Links to model documentation

---

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check if port 8001 is in use
lsof -i :8001

# Check backend logs
cd ~/workspace/nudify
python -m backend.server
```

### Next.js not starting
```bash
# Check if port 4000 is in use
lsof -i :4000

# Clear Next.js cache
cd admin
rm -rf .next
npm run dev
```

### API calls failing (CORS)
Check backend/server.py has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Images not loading
1. Check backend logs for 404s
2. Verify image path: `results_dev/{experiment_id}/{filename}`
3. Test direct URL: `http://localhost:8001/api/experiments/{id}/images/{file}.png`

---

## 📚 API Documentation

Full API docs available at: `http://localhost:8001/docs` (FastAPI Swagger UI)

---

## 🎯 Current Progress

- [x] Backend API endpoints
- [x] Batch job manager
- [x] Next.js app initialized
- [x] Dashboard page
- [x] API client
- [x] Navigation layout
- [x] Prompt Builder page (`/generate`)
- [x] Batch Creator page (`/batch`)
- [x] Image Gallery page (`/gallery`)
- [x] Model Manager page (`/models`)
- [ ] Real-time progress (SSE) - Optional enhancement

**Status**: Core admin panel complete and functional! 🎉

**Optional Future Enhancements:**
- Server-Sent Events (SSE) for real-time generation progress
- Backend endpoints for editing models.json via UI
- Advanced image filters and search
- Experiment comparison tools
- Export/import experiment configurations

---

## 💡 Tips

1. **Use React Query DevTools**: Add to `app/providers.tsx`:
   ```typescript
   import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

   <QueryClientProvider client={queryClient}>
     {children}
     <ReactQueryDevtools />
   </QueryClientProvider>
   ```

2. **Test API endpoints directly** before building UI:
   ```bash
   curl http://localhost:8001/api/models | jq
   ```

3. **Use TypeScript types** from `lib/types.ts` - they match backend exactly

4. **Hot reload works** - just save files and browser refreshes

5. **Check browser console** for API errors

---

## 🔗 Useful Links

- Next.js Docs: https://nextjs.org/docs
- React Query Docs: https://tanstack.com/query/latest/docs/framework/react/overview
- Tailwind CSS: https://tailwindcss.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com

---

**Questions?** Check `MODEL_SETUP.md` for model management or `CLAUDE.md` for project overview.
