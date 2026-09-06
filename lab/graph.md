# Graph: Ledgerlens SDLC as a directed graph

*Generated from the accepted `spec.md`. Four node kinds only: **Play** (agent session), **Artifact** (committed file or DB row), **Gate** (human accept/reject), **Signal** (machine event). Edges are triggers.*

## Rules this graph obeys

- No node exists to satisfy ceremony. No `tasks.md`.
- Exactly four gates plus one optional taste review. More is micromanagement.
- Every implement path is restartable: a crashed train re-enters the Train play with the same plan; it never demands a new spec.
- The **modeling subgraph** and the **product subgraph** share two things: the database and the `ModelVersion` row. That join is the point of the lab.

## The graph

```mermaid
flowchart TB
  classDef play fill:#1f2937,stroke:#111827,color:#f9fafb
  classDef artifact fill:#fef3c7,stroke:#b45309,color:#111827
  classDef gate fill:#fee2e2,stroke:#b91c1c,color:#111827,stroke-width:2px
  classDef signal fill:#dcfce7,stroke:#15803d,color:#111827,stroke-dasharray: 4 3
  classDef store fill:#e0e7ff,stroke:#3730a3,color:#111827,stroke-width:3px

  subgraph SDLC["Artifact chain"]
    P0([Discover]):::play --> A1[/intent.md/]:::artifact --> G1{Gate 1<br/>intent}:::gate
    G1 -->|accept| P1([Design]):::play --> A2[/spec.md/]:::artifact --> G2{Gate 2<br/>spec}:::gate
    G2 -->|accept| P2([Loop + graph]):::play --> A3[/loop.md<br/>graph.md/]:::artifact --> G3{Gate 3<br/>loop + graph}:::gate
    G3 -->|accept| P3([Plan mode]):::play --> A4[/plan.md<br/>+ hero direction/]:::artifact --> G4{Gate 4<br/>plan}:::gate
    G1 -->|edit-in-spirit| P0
    G2 -->|edit-in-spirit| P1
    G3 -->|edit-in-spirit| P2
    G4 -->|edit-in-spirit| P3
  end

  subgraph PRODUCT["Product subgraph"]
    G4 -->|accept| PA([Implement<br/>Slice A: skeleton]):::play
    PA --> AA[/migrations · auth · API · empty UI<br/>model_versions table · stub predictor/]:::artifact
    AA --> ST{{tests}}:::signal
    ST -->|red| PA
    ST -->|green| GT{Taste review<br/>running shell}:::gate
    GT -->|change direction| PA
    GT -->|keep| PC([Implement<br/>Slice C: inference + transparency view]):::play
    PC --> AC[/serve path · transparency view<br/>review queue · Production view/]:::artifact
    AC --> ST2{{tests}}:::signal
    ST2 -->|red| PC
    ST2 -->|green| SERVE([Serve]):::play
    SERVE --> ROWS[/Extraction · Field · Verdict<br/>Correction · Approval rows/]:::artifact
  end

  subgraph MODEL["Modeling subgraph"]
    GT -->|keep| PB([Implement<br/>Slice B: ingest · split · train · eval]):::play
    PB --> AB[/ingest + train + eval jobs/]:::artifact
    AB --> TRAIN([Train job<br/>2B QLoRA]):::play
    TRAIN --> OOM{{job failed / OOM}}:::signal
    OOM -->|same plan| TRAIN
    TRAIN --> EVAL([Eval + calibrate<br/>+ fit threshold]):::play
    EVAL --> REP[/model card · EvalReport<br/>EvalScore · calibrator · threshold/]:::artifact
    REP --> BEAT{{beats baseline<br/>ECE within budget}}:::signal
    BEAT -->|no| NOIMP[/lab/intent/no-improvement.md/]:::artifact
    BEAT -->|yes| PIN[/ModelVersion.pinned = true/]:::artifact
  end

  DB[(Postgres + object store)]:::store
  MV[(ModelVersion row)]:::store
  PIN --> MV
  MV -->|pinned version read per request| SERVE
  ROWS --> DB
  REP --> DB
  AB --> DB
  AA --> DB
  MV --- DB

  subgraph MAINTAIN["Maintain"]
    ROWS --> OBS([Observe<br/>after each batch]):::play
    OBS --> S1{{vendor F1 drop}}:::signal
    OBS --> S2{{calibration drift}}:::signal
    OBS --> S3{{grounding collapse · job failures<br/>new vendor template}}:::signal
    S1 --> I1[/lab/intent/vendor-f1-drop-*.md/]:::artifact
    S2 --> I2[/lab/intent/calibration-drift.md/]:::artifact
    S3 -.documented.-> I3[/lab/intent/*.md/]:::artifact
    I1 --> G1
    I2 --> G1
    NOIMP --> G1
  end

  ROWS -->|corrections cross threshold| TRAIN
```

## Reading the graph

- **The chain at the top** is the only part that looks like "SDD". Four artifacts, four gates, each gate loops back to its own play on edit-in-spirit — never further back.
- **Slice A ships a database and a web app before a weight file exists.** The taste review on the running shell is the one optional human node inside build.
- **Slices B and C run in parallel** after the taste review; they meet at the `ModelVersion` row. B writes it; C reads it per request. Neither knows the other's internals.
- **The Train play is a cycle with its own failure signal.** OOM or crash goes back into Train with the same plan. Nothing upstream is touched.
- **Pinning is an artifact, not a play.** It is a row flip, audited, and it is the single edge that lets a trained model reach a user.
- **Maintain has no human in it.** Observe runs after each batch; signals write intents; the intent lands at Gate 1, where a human triages it. Corrections crossing a threshold can also re-enter Train directly — that is the learning loop without a human.
- **Count the human nodes:** Gate 1, 2, 3, 4 and the taste review. Five. If a sixth appears in a later revision, delete it.
