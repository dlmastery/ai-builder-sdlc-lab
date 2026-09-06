import { api } from "@/lib/api";
import { relTime } from "@/lib/format";
import type { ModelVersionOut, Paginated } from "@/lib/types";

export const metadata = { title: "Models & runs" };

export default async function ModelsPage() {
  const models = await api<Paginated<ModelVersionOut>>("/models");
  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="micro">Models &amp; runs</p>
        <h1 className="mt-2 text-step-2 font-medium tracking-tight">Model versions</h1>
        <p className="mt-2 max-w-[64ch] text-step-0 text-ink-2">
          One pinned version per kind serves production. Pinning is an audited row flip; datasets,
          jobs and evaluation reports attach here in Slice B.
        </p>
      </div>
      <ul className="rule-y border-t border-rule">
        {models.items.map((m) => (
          <li
            key={m.id}
            data-testid="model-row"
            className="grid items-center gap-4 py-4 md:grid-cols-[140px_1fr_140px_140px]"
          >
            <span className="micro">{m.kind}</span>
            <span className="text-step-0 text-ink">
              {m.name}
              {m.pinned ? <span className="ml-3 text-step--1 text-signal">● pinned</span> : null}
            </span>
            <span className="font-mono text-step--1 text-ink-3">{m.id.slice(0, 8)}</span>
            <span className="text-step--1 text-ink-3">{relTime(m.created_at)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
