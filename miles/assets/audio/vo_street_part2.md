# Street part 2 — voice-over script (~2:20): why inspection wins, human + agent, how LiveReview does it

Voice: the same as part 1 (ElevenLabs "Mark – Natural Conversations", one website take, then
`python3 scripts/07b_split_take.py TAKE.mp3 --script assets/audio/vo_street_part2.md --out assets/audio/vo_street_part2`).
Until that take exists, `scripts/07c_estimate_vo.py` writes estimated line lengths + word times to
`assets/audio/vo_street_part2/lines.json` (marked "estimated") so the scene can be built and timed; the real take
re-times everything on the next build.

| # | Starts | Scene / visual | Line |
|---|---|---|---|
| 1 | 3.0s | S10 why inspect: two shops | Now picture this. You ship without inspection. Your competitor inspects every change. Who does the customer pick? |
| 2 | 12.0s | S10.1 the answer | Easy. Customers pick the better product when price and new updates are the same. If you don't inspect what you ship, your competitor will ship with higher standards. |
| 3 | 23.0s | S11 site A: human only | Option one: you review everything. Features are shipped carefully, but you can't keep up with the pace. |
| 4 | 31.0s | S12 site B: agent only | Option two: let agents do it all. Fast, but no one's sweating the details, and the subtle things break. Customers notice, because the most refined product wins. |
| 5 | 42.0s | S13 site C: human + agent | Or combine them. Agents for speed and scale, humans for judgment. That team beats human-only, and it beats agent-only. |
| 6 | 51.0s | S14 close-up: three things | Every team wants three things: the same headcount, more results, and a better product. Only a human plus agent gets all three. That's how you stay competitive. |
| 7 | 61.0s | S15 close-up: common sense | Why keep humans in the loop? Cuz common sense! AI lets everyone ship more, but it doesn't make more great products. Human judgment and care do that, and they're not in any model's training data. |
| 8 | 73.0s | S16 product: engineers | LiveReview gives your engineers attention and understanding: issues ranked by importance, a slide deck for every change, a quick quiz, conversations on the MR, and Livi, the bot that turns your data into analysis reports and actionable items. |
| 9 | 87.0s | S17 product: agents | And it gives your agents what they need to enforce your standards at scale: your rules on every pre-commit, your integrations, and MCP. |
| 10 | 95.0s | S18 the rebuild | Use agents for scale. Use your judgment, always. Inspection holds it all up. |
| 11 | 105.0s | S19 call to action | LiveReview keeps you competitive: the most efficient way for humans and AI to work together. The blast-radius aware AI code reviewer for your critical systems. Sign in to try it, or contact us to learn more. |
