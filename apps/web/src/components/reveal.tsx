"use client";

import { useEffect, useRef, useState } from "react";

// One entrance per section as it scrolls into view (bar.md mechanism 7): the plate first,
// then the scaffold; under 400 ms; nothing loops; reduced motion honoured by the CSS.
export function Reveal({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && setOn(true)),
      { threshold: 0.25 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div ref={ref} className={`${className} ${on ? "reveal-on" : "reveal-off"}`}>
      {children}
    </div>
  );
}
