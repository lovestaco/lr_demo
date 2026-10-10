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
| 8 | 73.0s | S16 product: engineers (~27 s) | [confident] LiveReview helps your engineers focus on what matters. [focused] Every issue is prioritized by risk, based on what a change affects, how far its impact spreads, and the potential consequences — so critical issues never get buried. [matter-of-fact] Then they can understand every change: a slide deck for each one, explaining what moved and why. [light] A quick quiz to check the reviewer understood it. [casual] Conversations right on the MR. [warm] And Livi, your bot for reports and actions. |
| 9 | 100.0s | S17 product: agents (~19 s) | [confident] And it gives your agents what they need to enforce your standards at scale. [assertive] CI/CD gates apply precise, customized enforcement on every merge. [friendly] Integrations help you work with Livi everywhere — in Microsoft Teams and Slack. [matter-of-fact] And MCP lets any preferred AI agent operate Livi right from your own agent. |
| 10 | 116.0s | S18 the rebuild (~6 s) | [steady] Use agents for scale. Use your judgment for better product. [emphatic] Inspection holds it all up. |
| 11 | 123.0s | S19 call to action (~12 s) | [confident] LiveReview keeps you competitive: humans and AI, working together. [clear] The risk aware AI code reviewer for your critical systems. [inviting] Sign in to try it, or contact us to learn more. |
| 12 | 100.0s | S18.5 Meta: the idea (after he goes up) | [serious] Inspection is a big deal. [confident] Meta saw it too, and went risk-first. [matter-of-fact] Low-risk changes skip the line, so attention goes where risk is. |
| 13 | 110.0s | S18.5 Meta: the results | [excited] And the results? [emphatic] One fiftieth of the production incidents. One third of the deploy reverts. Thirty-three percent lower wait time. |
| 14 | 120.0s | S18.5 Meta: the bridge to LiveReview | [warm] You can get the same results in your org, with LiveReview. |
