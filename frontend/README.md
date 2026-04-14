# Frontend - React + Tailwind CSS

## Setup

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env
# Configure API URL

# Start development server
npm run dev
```

## Commands

```bash
npm run dev      # Start dev server (port 5173)
npm run build    # Production build
npm run lint     # Run ESLint
npm test         # Run tests
npm test -- --watchAll=false  # Run tests once
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Route pages
├── hooks/          # Custom React hooks
├── services/       # API calls
├── types/          # TypeScript types
├── App.tsx         # Main app component
└── main.tsx        # Entry point
```

## Environment Variables

```
VITE_API_URL=http://localhost:8000/api
```

## Tech Stack

- React 18 with TypeScript
- Tailwind CSS for styling
- React Router for navigation
- TanStack Query for data fetching

See `docs/AGENTS.md` for code style guidelines.
