# Intent: vendor-f1-drop · Northwind Traders

*Written by the maintain job, 2026-09-06T08:29:32+00:00. Not yet triaged.*

## Problem

Required-field accuracy on Northwind Traders's reviewed documents fell to 75% (1 of 4 required fields corrected; floor 99%). Corrected by field: total ×1.

## Proposed outcome

An extractor version that reads Northwind Traders's documents at or above the floor, trained on the corrections that produced this signal.

## Affected users and systems

- AP clerks reviewing this vendor's documents; the finance lead's automation rate.
- The pinned extractor, calibrator and threshold versions named in the evidence.

## Evidence

- vendor: Northwind Traders
- reviewed required fields: 4
- corrected: 1
- accuracy: 0.75
- floor: 0.99
- corrected by field: total ×1
- extractor versions: ['f7f01bd4-ce71-41df-968b-314dc576fb14']

## Constraints

- Same laptop budget and split discipline as the original intent; corrections from this
  vendor are the new training signal (dataset source `corrections`).

## Open questions

- Is this a layout change on the vendor's side, a scan-quality change, or a model regression?

## Definition of done

- A new extractor version whose evaluation on this vendor's corrected documents is at or
  above the floor, pinned through the audited path; the signal closed with a reference to it.
