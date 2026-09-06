"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

// One entrance per section as it scrolls into view (bar.md mechanism 7): the plate first,
// then the scaffold; under 400 ms; nothing loops; reduced motion honoured by the CSS.
//
// Degrades to visible (customer test, finding 4): the server-rendered HTML hides nothing; a
// section is hidden only once the page has hydrated, and never for more than two seconds — a
// capture or a reader that never scrolls to it still gets the content.
export function Reveal({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const hydrated = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && setOn(true)),
      { threshold: 0.25 },
    );
    io.observe(el);
    const fallback = window.setTimeout(() => setOn(true), 2000);
    return () => {
      io.disconnect();
      window.clearTimeout(fallback);
    };
  }, []);
  const cls = !hydrated ? "" : on ? "reveal-on" : "reveal-off";
  return (
    <div ref={ref} className={`${className} ${cls}`}>
      {children}
    </div>
  );
}
