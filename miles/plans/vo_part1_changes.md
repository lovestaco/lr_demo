# Part 1: full voice-over and on-screen text (2026-10-11)

Source of the new opening: the review discussion (problem and solution first: low-risk changes are approved and merged
automatically, humans review only what is risky, developers get the review time back, faster and safer).

Markers: 
**NEW** = new take to record. 
**CHANGED** = existing line with new wording (the old one is shown under it).
**REMOVED** = existing line no longer used in the film (its scene goes too).
**No marker = existing line, unchanged** (already recorded, nothing to do).

---

# 1. Voice-over, in the order it plays

1. **NEW** (recorded: `assets/audio/vo_street/takes/take_14.mp3`, 36.7 s)
   ```
[serious] AI writes your code faster than your team can review it. 
[concerned] Every M R is twice as big as last year. 
[concerned] And every dev ships one and a half times more of them. 
[concerned] So reviewers run out of attention, and may skip the changes that are actually risky. 
[confident] Meta fixed the attention problem by giving every M R a risk score. 
[excited] Low-risk M R are approved automatically, and humans only review high risk changes. 
[emphatic] The result? Production incidents down 98%, rollback rates down 30%, and wait time down 33%. 
[confident] Engineers ship faster and safer, while also reviewing less. 
[casual] Here's why inspection matters. 
```

   Same take with its structure labelled, without the tags (for reading only; the labels are NOT spoken, don't paste this):
   ```
   Reality:     AI writes your code faster than your team can review it.
   Prob:        Every M R is twice as big as last year.
   Prob:        And every dev ships one and a half times more of them.
   Prob:        So reviewers run out of attention, and may skip the changes that are actually risky.
   Sol:         Meta fixed the attention problem by giving every M R a risk score.
   Sol:         Low-risk M R are approved automatically, and humans only review high risk changes.
   Res:         The result? Production incidents down 98%, rollback rates down 30%, and wait time down 33%.
   Consequence: Engineers ship faster and safer, while also reviewing less.
   Bridge:      Here's why inspection matters.
   ```
2. (line 1) `[confident] You already ship a lot of AI-generated code.`
3. (line 2) `[playful] But do you do enough code inspection?`
4. ~~(line 3) `[excited] Code now ships faster than ever.`~~ **REMOVED**
5. (line 4) `[concerned] More code means bigger systems... [gasps] and more bugs.`
6. ~~(line 5) `[frustrated] And human review just can't keep up.`~~ **REMOVED**
7. (line 6) `[worried] So customers walk away... over downtime, security holes, slow apps, and bad UI.`
8. (line 7) `[thoughtful] How do you stay competitive?`
9. (line 8) `[confident] You need a better inspection layer.`
10. (line 9) `[building up] Inspection gives engineers confidence.`
11. (line 10) `Engineers' confidence gives customers confidence.`
12. (line 11) `And customer confidence keeps you competitive, 
[excited] and the money coming in.`
13. (line 12) `[dramatic] Without inspection, everything above it collapses.`
14. (line 13) `It starts with inspection.`  


---

# 2. On-screen text, scene by scene


| Scene | Plays on | Text on screen |
|---|---|---|
| **NEW** opening (take_14) | not designed yet | **Nothing is defined yet.** It needs a visual. Proposal, one short line per beat: "Too much code, too little review" / "At Meta: a risk score on every change" / "Low-risk: approved and merged automatically" |
| S0, aerial | he zips down the avenue | no text |
| S1, wall mural | line 1 | You already ship a lot of **AI-generated code.** |
| S2, billboard | line 2 | But do you do enough **code inspection?** |
| S3, LED ticker | line 3 | Code now ships **faster than ever.** |
| S4, bus-stop ad | line 4 | More code means **bigger systems** (then) **Bigger systems,** more **bugs.** (with a network graphic and bugs) |
| S5, subway lightbox | line 5 | Human review **can't keep up.** Two counters: **Incoming PRs** (climbs from 12 to 482) and **Reviewed** (creeps from 3 to 12), with a progress bar |
| S6, big screen | line 6 | Customers **walk away** over: four tiles: **Downtime**, **Security**, **Slow apps**, **Bad UI** (then) ...and customers **walk away.** |
| S7, rooftop screen | lines 7-8 | How do you stay **competitive?** (then) You need a better **inspection layer.** |
| S8, the tower (each floor lights on its word) | lines 9-11 | **INSPECTION** (a web with this word woven in) / **ENGINEERS' CONFIDENCE** / **CUSTOMER CONFIDENCE** / **COMPETITIVE PRODUCT $$$** (cash on top) |
| S9, the collapse | lines 12-13 | no new text (the tower falls) |

Not on screen: the city's own signs (a pharmacy, a bank and so on) are scenery.

If you want different wording on any of these signs (for example S5's "can't keep up", or S6's four risks), tell me which and I'll change the sign text.
