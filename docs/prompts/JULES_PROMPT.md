<instruction>You are an expert software engineer. You are working on a WIP branch. Please run `git status` and `git diff` to understand the changes and the current state of the code. Analyze the workspace context and complete the mission brief.</instruction>
<workspace_context>
<artifacts>
--- CURRENT TASK CHECKLIST ---
# SJ-DAS Dual Platform Upgrade (Desktop & Web)

The goal is to establish SJ-DAS as a professional two-platform suite, similar to Adobe Creative Cloud, with a native Desktop app (PyQt) and a fully featured Web app (Next.js), sharing a common Python AI backend.

- [ ] **Phase 1: Architecture Definition**
  - [/] Define "Dual Platform" strategy in Implementation Plan <!-- id: 0 -->
  - [ ] Consolidate shared Python core (`sj_das.core`) for reuse by both frontends <!-- id: 1 -->

- [ ] **Phase 2: Web Edition (Next.js + Aceternity Upgrade)**
  - [x] Restore Next.js Project (`web/`) <!-- id: 14 -->
  - [x] Implement `Spotlight.js` (Hover Effects) <!-- id: 15 -->
  - [x] Implement `BentoGrid.js` (Dashboard Layout) <!-- id: 16 -->
  - [x] Update `web/app/studio/page.js` with new components <!-- id: 17 -->

- [ ] **Phase 3: Unified Launcher**
  - [ ] Update `tools/start_full_stack.py` to allow selective launching <!-- id: 5 -->

- [ ] **Phase 4: Cleanup & Handoff**
  - [x] Delete `futuristic_demo.html` <!-- id: 12 -->
  - [ ] Final verification of "Aceternity" performance <!-- id: 21 -->

--- IMPLEMENTATION PLAN ---
# Web Framework & Jules Integration Plan

## Goal Description
Create a modern web application framework using Next.js with the following integrations:
- **Hosting**: Replit-compatible structure
- **Database & Auth**: Supabase
- **Payments**: Stripe
- **Visuals**: Three.js animations
- **Maintenance**: "Jules" automated maintenance workflow

## Proposed Changes

### Web Application (`/web`)
I am initializing a Next.js application in the `web` directory.
#### [NEW] `web/package.json`
- Dependencies: `next`, `react`, `three`, `@react-three/fiber`, `@supabase/supabase-js`, `stripe`

#### [NEW] `web/lib/supabaseClient.js`
- Supabase client initialization.

#### [NEW] `web/lib/stripe.js`
- Stripe client initialization.

#### [NEW] `web/components/ThreeScene.js`
- A React-Three-Fiber component displaying a 3D animation (e.g., a rotating futuristic cube).

#### [MODIFY] `web/app/page.js`
- The main landing page incorporating the 3D scene and payment/auth buttons.

### Web Application Expansion (`/web`)
Transforming the single-page app into a full "Adobe Creative Cloud" style suite.

#### [NEW] `web/app/dashboard/page.js`
- Central hub listing all available apps (Studio, Assembler, Simulator, Vision).

#### [NEW] `web/components/AppSidebar.js`
- Unified navigation bar for switching between apps easily.

#### [NEW] `web/app/assembler/page.js`
- **Utility**: Drag-and-drop textile assembly (Border + Body + Pallu).
- **Integration**: Connects to `sj_das/core/assembler.py`.

#### [NEW] `web/app/simulator/page.js`
- **Utility**: 3D Fabric Drape Simulation.
- **Integration**: Connects to `sj_das/core/fabric_sim.py` (via Three.js visualization).

#### [NEW] `web/app/vision/page.js`
### Phase 2: Dual Platform Ecosystem (Desktop & Web)
Establishing SJ-DAS as a professional suite with two native access points, sharing a unified `sj_das.core` backend.

#### 1. Desktop Edition (PyQt6)
- **Entry Point**: `launcher.py`
- **Focus**: High-performance, offline-capable, local hardware access.
- **Theme**: Original Adobe Dark.

#### 2. Web Edition (Pure HTML5/CSS3)
- **Entry Point**: `tools/html_launcher.py` (serving `html_suite/`)
#### 2. Web Edition (Next.js + Aceternity UI)
- **Entry Point**: `tools/start_full_stack.py`
- **Focus**: "Futuristic Minimalist" aesthetic (Linear/Raycast standard).
- **Tech**: Next.js 14, Framer Motion, Tailwind CSS.

#### Unified Backend (`/backend`)
Allows both frontends to call the same AI logic.

### Phase 3: Fine Detail & Fluidity (Aceternity Standard)
Implementing "Copy-Paste" high-end UI patterns.

#### [NEW] `web/components/ui/Spotlight.js`
- **Effect**: Dynamic light cone that follows cursor on hover.
- **Usage**: Dashboard cards and Studio panels.

#### [NEW] `web/components/ui/BentoGrid.js`
- **Layout**: Asymmetric, responsive grid for feature showcasing.
- **Style**: Glassmorphism with glowing borders.

#### [MODIFY] `web/app/page.js`
- **Hero**: "Sparkles" or "Aurora" background effect.
- **Content**: Bento Grid displaying modules (Studio, Assembler, Jules).

#### [MODIFY] `web/app/studio/page.js`
- **Upgrade**: Apply "Spotlight" effects to the sidebar tool groups.
- **Physics**: Ensure all interactions use the Spring config.

### Phase 4: Project Cleanup
Removing prototypes and standardizing the codebase.
- [DELETE] `futuristic_demo.html` (Done)
- [DELETE] `web/public/next.svg`, `vercel.svg`
- [MODIFY] `tools/start_full_stack.py` to allow mode selection.

### Maintenance Integration ("Jules")
#### [NEW] `.github/workflows/jules_maintenance.yml`
- A GitHub Actions workflow that runs maintenance checks weekly or on push.

#### [NEW] `tools/jules_maintenance.py`
- A script that scans the codebase for TODOs and FIXMEs, acting as the "Jules" agent.

## Verification Plan
1.  **Web App**: Run `npm run dev` in `web` directory and verify the page loads with the 3D element.
2.  **Jules**: Run `python tools/jules_maintenance.py` to verify it scans correctly.
</artifacts>
</workspace_context>
<mission_brief>[Describe your task here...]</mission_brief>