export function pct(x: number | null | undefined, digits = 0): string {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return `${(x * 100).toFixed(digits)}%`;
}

export function moneyFromCents(cents: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(cents / 100);
}

export function fieldLabel(name: string): string {
  return name.replaceAll("_", " ");
}

export function statusLabel(status: string): string {
  return status.replaceAll("_", " ");
}

// Verdict reasons in the clerk's language, never the pipeline's (design loop P3, round 5).
// `why` is the verifier's rule name: missing | ungrounded | below_threshold | arithmetic.<rule>.
export function reasonText(field: string, why: string, confidence?: number): string {
  const label = fieldLabel(field);
  const cap = label.charAt(0).toUpperCase() + label.slice(1);
  switch (why) {
    case "missing":
      return `${cap}: the model did not read one`;
    case "ungrounded":
      return `${cap}: could not be found on the page`;
    case "below_threshold":
      return `${cap}: not sure enough${typeof confidence === "number" ? ` (${pct(confidence)})` : ""}`;
    case "arithmetic.total":
      return "Subtotal plus tax does not match the total";
    case "arithmetic.line_items":
      return "Line items do not add up to the subtotal";
    default:
      return `${cap}: ${why.replaceAll("_", " ").replaceAll(".", " · ")}`;
  }
}

// The same reasons, short enough for a chip.
export function reasonChip(field: string, why: string): string {
  const label = fieldLabel(field);
  switch (why) {
    case "missing":
      return `${label} · not read`;
    case "ungrounded":
      return `${label} · not on the page`;
    case "below_threshold":
      return `${label} · not sure enough`;
    default:
      return `${label} · ${why.replaceAll("_", " ").replaceAll("arithmetic.", "")}`;
  }
}

export function relTime(iso: string): string {
  const then = new Date(iso).getTime();
  const diff = Math.max(0, Date.now() - then);
  const m = Math.round(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} h ago`;
  return new Date(iso).toLocaleDateString();
}
