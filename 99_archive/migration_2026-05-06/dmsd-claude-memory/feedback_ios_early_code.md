---
name: Early iOS/SwiftUI code is throwaway
description: Existing Swift/SwiftUI code in the repo is scrap work from before project start — do not treat as basis for v1.0 iOS development
type: feedback
originSessionId: 271ab726-df78-45f3-bfc0-048b8a268bb4
---
The existing Swift/SwiftUI iOS code in the DMSD repo was written as casual experimentation before the project formally started. It should NOT be used as the foundation for v1.0.

**Why:** itsuki confirmed on 2026-04-10 that the current iOS UI was "随便试了一下" (just a casual test) and explicitly said "不要用" (don't use it). Treating it as a starting point would anchor design decisions on throwaway code.

**How to apply:**
- When planning iOS work, assume a clean slate — do not reference or extend existing Swift files
- Any project overview documents (like DMSD_project_overview_for_AC.md) that describe "iOS UI skeleton already exists" need correction
- iOS development path: learn SwiftUI basics first → then build fresh from v1.0 specs in 01_specs/
- Before writing any iOS code, verify which files (if any) are worth keeping vs deleting
