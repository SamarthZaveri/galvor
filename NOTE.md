# Note: key choices and what I'd build next

**1. Start from what sells, then find creators who can make it.** The brand runs creator-style videos as paid ads, so the question is really "who can make the video that converts?" I first found what converts in the 100 ads, then scored creators on whether that kind of video is native to their feed. Reach is secondary: 30% of the score.

**2. Don't let one ad decide.** LJ-004 is 30% of revenue. Every pattern is judged on median ROAS and re-tested without the group's top ad. A pattern is "Strong" only if it also survives a regression that holds the other patterns and launch month fixed. That check changed one conclusion: skits look bad in raw numbers, but the model shows no skit effect. Skits are mostly the weak regional-language ads.

**3. Treat labels as hypotheses.** I read transcripts before relying on a label. Three label errors would have changed the answer: spoken language (captions vs speech), product (Proteinmix tagged as milk mix, including the top ad), and one presenter age. Each fix is listed in the code and the report.

**4. Find the data that lies.** LJ-089 (1,544 carts, 0 purchases) is a tracking break, not a creative result, so it's excluded. The same video run twice produced ROAS 1.42 and 2.30, which shows how noisy single-ad numbers are.

**5. Hard gates beat a lower score.** A creator who promoted Gritzo, Complan, Troovy or Good Monk in the last 90 days is blocked, not marked down. This includes the best fit of all, @sia_3vedi. A manager needs to know why someone isn't on the list, so blocked creators are shown with the reason and what would unblock them.

**6. The briefs can't invent claims.** A test fails the build if any claim in a brief isn't already in a Little Joys ad. Another test checks every number written into the prose against the data.

**7. Show how sure we are.** A slider re-ranks the creators live. Picks 1 to 3 never change; slots 4 and 5 are near-ties, and the report says so.

**What I'd build next with a week**

* **Close the loop.** Ingest results from each creator test (cost per purchase vs the ₹535 median) and update the pattern weights. A Bayesian hierarchical model would replace the hand-set fit weights.
* **Look at the videos, not only the labels.** Run the 100 MP4s through a vision model to verify labels such as `child_in_first_3s`, and fill gaps like LJ-035, a top ad with no labels.
* **Find more creators.** The scoring already works on any feed. Point it at a larger creator pool to find child-presenter, English/Hinglish creators without competitor conflicts.
* **Pull audience data** for the 17 creators without it. Gender and geography gates currently apply to only 3.
* **Draft brief scripts** with an LLM constrained to the approved claim list and the creator's own transcripts, with a human edit before anything ships.
