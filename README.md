# my-app

This project is a Next.js App Router application with TypeScript, Tailwind CSS, and interactive visual-effect dependencies.

## Getting Started

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The application is available at `http://localhost:3000` by default.

## Scripts

```bash
npm run dev       # Start the Next.js development server
npm run build     # Create a production build
npm run start     # Serve the production build
npm run typecheck # Run TypeScript without emitting files
```

## Project Structure

- `app/layout.tsx` — Root layout and metadata
- `app/page.tsx` — Home page
- `app/globals.css` — Global styles and Tailwind entry point
- `next.config.ts` — Next.js configuration
- `postcss.config.mjs` — Tailwind CSS PostCSS configuration

The project keeps the former React Router files (`app/root.tsx`, `app/routes/`, `vite.config.ts`, and `react-router.config.ts`) as an excluded rollback reference. They are not used by the Next.js scripts.

## Visual Dependencies

The project includes React Three Fiber, Shader Gradient, Paper Design shaders, Anime.js, Motion, html2canvas, and Liquid Glass React for future interactive UI work.

## Production

Build and run the production server with:

```bash
npm run build
npm run start
```

Next.js generates production output in `.next/`, which is excluded from version control.

## Optional Google organic search

The FactLens backend can use SerpApi to discover Google organic results before reading source pages. Copy `backend/.env.example` to the backend-local `.env` and set `SERPAPI_API_KEY` there; never put the key in a browser or Next.js public variable. Restart the backend after changing the file. The existing LLM provider key is still required for claim extraction, verification, and answer synthesis.

This path is free-plan-only: before any search, the backend checks SerpApi's no-charge Account API for a `Free`/`Free Plan` account, zero monthly price, no extra credits, and enough remaining searches for the distinct claim queries. If the check fails, it makes no SerpApi search request and falls back to the existing LLM web search, with a warning in the result. It does not create an account, upgrade a plan, or enable automatic billing. LLM provider API usage remains separate.

The search uses the extracted keywords with Korean language/country settings (`hl=ko`, `gl=kr`). The displayed organic position is for that exact query and setting; personalized Google pages may differ. Search snippets are only discovery data, never verified quotations. To spend at most one free-plan search on a live connectivity check, run `python backend/smoke_google_serp.py` with the backend's Python environment; the script prints only ranks, publishers, and titles.
