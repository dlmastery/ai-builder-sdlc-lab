import specimen from "@/specimen/northwind.json";

/** The ledger of the exported specimen as the sentences the transparency view shows — shared by
 *  the home specimen and the pricing page's "what every document comes with" artefact. Nothing
 *  typed: every line is a verifier row. */
export function ledgerLines(): Array<[string, boolean]> {
  const rows = specimen.ledger as Array<{ rule: string; passed: boolean; field: string | null; detail: Record<string, unknown> | null }>;
  const out: Array<[string, boolean]> = [];
  for (const r of rows) {
    const d = (r.detail ?? {}) as Record<string, string>;
    if (r.rule === "arithmetic.line_items") out.push([`The line items add up to ${d.sum_of_line_items} · the subtotal reads ${d.subtotal}`, r.passed]);
    else if (r.rule === "arithmetic.total") out.push([`Subtotal ${d.subtotal} plus tax ${d.tax ?? "0"} makes ${d.expected_total} · the total reads ${d.total}`, r.passed]);
    else if (r.rule === "grounding" && !r.passed) out.push([`${(r.field ?? "field").replaceAll("_", " ")}: read, but the page could not confirm it`, false]);
  }
  out.push([`${rows.filter((r) => r.rule === "grounding" && r.passed).length} values found on the page where the model said they were`, true]);
  return out;
}
