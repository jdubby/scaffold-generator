### nextjs (frontend)

Next.js owns the web-facing layer: routes, server components, and client state.
Default to server components; mark components `"use client"` only when they need
interactivity, and keep that boundary explicit. Data fetching and mutations live
in server actions or route handlers — client components receive data as props,
so rendering stays testable without a browser.
