# Part 3: full voice-over and on-screen text (2026-10-11)

Source: the review discussion. The idea: low-risk changes are approved and merged automatically, high-risk ones go to a
human; that gives the review time, cost and attention back to developers; and it makes things faster AND safer (Meta's proof:
98% fewer production incidents, 30% fewer rollbacks, 33% lower wait time).

Markers: 
**NEW** = new take to record. 
**CHANGED** = existing line with new wording (the old one is shown under it).
**No marker = existing line, unchanged** (already recorded, nothing to do).

---

# 1. Voice-over, in the order it plays

### take 8, S16 engineers: **CHANGED** (the flagship comes first: low-risk changes are approved and merged automatically)

New:
```
[confident] LiveReview helps your engineers go safer and faster by skipping low-risk changes.
[focused] Every issue is prioritized by risk, based on what a change affects, how far its impact spreads, and the potential consequences, so critical issues never get buried.
[matter-of-fact] Then they can understand every change: a slide deck for each one, explaining what moved and why.
[light] A quick quiz to check the reviewer understood it.
[casual] Conversations right on the M R.
[warm] And Livi, your bot for reports and actions.
```
Was:
```
[confident] LiveReview helps your engineers focus on what matters.
[focused] Every issue is prioritized by risk, based on what a change affects, how far its impact spreads, and the potential consequences — so critical issues never get buried.
[matter-of-fact] Then they can understand every change: a slide deck for each one, explaining what moved and why.
[light] A quick quiz to check the reviewer understood it.
[casual] Conversations right on the M R.
[warm] And Livi, your bot for reports and actions.
```
(The words "issue", "slide", "quick", "conversations" and "Livi" stay in, so the board pops stay on the same words. The first board item now pops on "automatically".)

### take 9, S17 agents: unchanged
```
[confident] And it gives your agents what they need to enforce your standards at scale.
[assertive] C I C D gates apply precise, customized enforcement on every merge.
[friendly] Integrations help you work with Livi everywhere — in Microsoft Teams and Slack.
[matter-of-fact] And MCP lets any preferred AI agent operate Livi right from your own agent.
```

### take 10, S18 the rebuild: unchanged
```
[steady] Use agents for scale. Use your judgment for better product.
[emphatic] Inspection holds it all up.
```

### take 12, Meta CALLBACK: **CHANGED** (part 0 already told the Meta story, so this is a short reminder)
New:
```
[serious] Remember Meta?
[confident] Every M R scored by risk, and the low-risk ones approved automatically.
[emphatic] Production incidents down 98%.
```
Was:
```
[serious] Inspection is a big deal.
[confident] Meta saw it too, and went risk-first.
[matter-of-fact] Low-risk changes are approved and merged automatically. Humans review only the risky ones, so attention goes where risk is.
```

### take 13, Meta the results: **REMOVED** (part 0 has the results; the three result boards go)
Was:
```
[excited] And the results?
[confident] Skipping low-risk changes made them safer, and faster.
[emphatic] Ninety-eight percent fewer production incidents. Thirty percent fewer rollbacks. Thirty-three percent lower wait time.
```

### take 14, Meta the bridge to LiveReview: **CHANGED**
New:
```
[warm] LiveReview brings Meta's approach to your team.
[confident] Risk-scored MRs and the low-risk ones approved automatically. So engineers ship faster and safer, while also reviewing less!
```
Was:
```
[warm] You can get the same results in your org, with LiveReview.
```

### take 11, S19 call to action: unchanged
```
[confident] LiveReview keeps you competitive: humans and AI, working together.
[clear] The risk aware AI code reviewer for your critical systems.
[inviting] Sign in to try it, or contact us to learn more.
```

**Play order:** 8, 9, 10, 12, 14, 11. (Take 13 is gone. Take 11 plays after the Meta section, as it does now.)

---

# 2. On-screen text, scene by scene

Every scene also shows the **subtitles** (yellow strip at the bottom, the spoken words, the spoken word in bold). Those are
the voice-over above and aren't listed again. `**bold**` = bold words on the board. Product footage (the clips shown full
screen) has its own text inside it, which can't be edited.

## S16, product board for engineers (2D, take 8)
Left card, top: **LiveReview** and `hexmos.com/livereview` (blue header).
Card title: **ATTENTION** goes where **RISK** is

Numbered items, each lighting up on its spoken word, with a product clip full screen when it is longer than 2 s:

| # | Item text | Clip shown | |
|---|---|---|---|
| 1 | Low-risk changes **approved and merged automatically** | a plain dark text card, no clip | **NEW** (first, it is the flagship) |
| 2 | Issues ranked by **risk** | risk-ranking zoom clip (12 s) | **CHANGED** (was "ranked by importance") |
| 3 | A slide deck for every change | slide deck animation (5 s) | |
| 4 | A quick quiz to check understanding | quiz animation (3 s) | |
| 5 | Conversations right on the MR | a screenshot of the MR conversation (2 s) | |
| 6 | Livi: bot that turns your data into analysis reports and actionable items | Livi chat clip, seconds 2-5 | |

## S17, product board for agents (2D, take 9)
Same card. Title: For your agents: **enforcement + scale**

| # | Item text | Clip shown |
|---|---|---|
| 1 | CI/CD Gates: Precise, Customized Merge Enforcement | CI/CD gates demo (4 s) |
| 2 | Integrations: Microsoft Teams, Slack | Teams screenshot (1 s) then Slack screenshot (2 s) |
| 3 | MCP | a dark card with the line below (5 s) |

MCP card text: MCP can be used to connect to any preferred AI Agent to operate Livi right from your agent.

## S18, the rebuild (3D, take 10)
Signs on the wrecked and rebuilt tower, one per floor, lighting up in turn:
- first four floors: **INSPECTION** (blue, the ground floor), **ENGINEERS' CONFIDENCE**, **CUSTOMER CONFIDENCE**, **COMPETITIVE PRODUCT**
- the four rebuilt floors, on top: **AGENTS: SCALE**, **HUMANS: JUDGMENT**, **RISK** (red), **ATTENTION** (amber)

## Meta callback (3D, takes 12 and 14)
He waits on the roof, off screen. The camera flies down the avenue to the Meta billboard, as it does now.

- **Meta billboard:** the Meta logo, big, on a white board (no text). It stays.
- **take 12 ("Production incidents down 98%"):** ONE white result board on the west tower: **98%** fewer production incidents (fifty squares, one red).
- **take 14:** the camera returns to the Meta billboard and zooms in while LiveReview's risk-score demo plays on it (product footage, with its own text).

**REMOVED from part 3 (part 0 shows them):** the change cards (files, or the planned pull requests), and the 30% rollbacks and 33% wait-time boards.

## S19, call to action (3D, take 11)
No text while he talks. At the end the billboard shows: **LiveReview** and `hexmos.com/livereview`.

---

# 3. What this means for the build (not done yet)
- Take 8 is longer (+5 s) and the Meta section is shorter (about 21 s becomes about 12 s), so part 3's length stays close to what it is now.
- Everything after S16 shifts a little: the 2D boards (S16/S17) and all the 3D frames must be re-rendered.
- S18: a tighter camera so he reads (see the discussion notes).
- Meta: the demo footage on the billboard needs to be readable (see the discussion notes).
