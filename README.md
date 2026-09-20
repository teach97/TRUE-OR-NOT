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
