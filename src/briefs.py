"""What each recommended creator should say.

Written by hand (with AI help) from three inputs, all in the data:
  - the patterns that win in Little Joys' ads (analysis.PATTERNS)
  - real winning ads to copy the shape of (reference_ads)
  - the creator's own feed: what feels native / foreign (creators.csv) and their posts

Guardrail: every product claim below must already appear in the `claims_made` column of at least
one Little Joys ad. tests/test_pipeline.py fails the build if a brief invents a claim.
"""

BRIEFS = {
    "storiesbyvihaa": dict(
        role="Lead bet",
        product="Proteinmix (mixed into dosa batter / roti)",
        why="The closest match to the account's best-selling ad type: a child who talks straight to camera. "
            "14 of her 20 recent posts are Viha presenting, and her paid posts keep 91% of normal reach.",
        format="Viha piece-to-camera, at the table with her own plate. Her usual phone-shot, home look; no studio.",
        hook="Viha, holding up her dosa: \"Ee roju naa plate lo emundo chudandi!\" (Look what's on my plate today!)",
        beats=[
            "0-3s: Viha shows her plate and says 'Little Joys' early (brand named in first 3s).",
            "Viha: 'Amma put one scoop of Little Joys Proteinmix in my dosa.' On-screen text: '1 scoop (15g) = 12g plant protein'.",
            "Viha takes a bite: 'Taste same-ey!' (the taste stays the same). Let the reaction be real.",
            "Parent's voice or text: made from pea, brown rice and soy; mixes into dosa batter, roti or chilla.",
            "End card + caption: clear 'Buy now' with link.",
        ],
        claims=["1 scoop (15g) contains 12g plant protein", "Made from pea, brown rice, and soy",
                "Easily mixes into flour, dosa batter, or chilla without altering taste"],
        language="Make two cuts of the same shoot: (A) English with her Telugu flavour, (B) Telugu. "
                 "The account has no Telugu ads at all, and the South Indian ones it has (Tamil, Kannada, "
                 "Malayalam) did poorly, so Telugu is a test, not a sure thing.",
        avoid="Viha reading out product specs like an adult (her feed's 'foreign' list). Numbers go on screen, not in her mouth.",
        reference_ads=["LJ-004", "LJ-097", "LJ-009"],
        watch=["Her Instagram audience is 70% men (as of 29 Oct 2026). Run the video as a paid partnership ad aimed at parents rather than relying on her own followers.",
               "She already did a Little Joys collab in the past year. Ask the team for those results before signing; they are not in this data."],
    ),
    "hello_ps8": dict(
        role="Strong fit",
        product="Proteinmix pancakes (check the age guidance for a 3-year-old; if it doesn't fit, use Nutrimix 2+ chocolate milk in the same format)",
        why="Her paid posts get more plays than her normal ones (1.3x), she speaks English/Hinglish, "
            "and her son Vayu (just turned 3) is in most of her videos.",
        format="Warm, bright home video with Vayu, the way she already films him. A taste test, not a pitch.",
        hook="\"One of these pancakes has 12g of extra protein. Let's see if Vayu can tell.\"",
        beats=[
            "0-3s: two plates side by side, the line above, 'Little Joys' on screen.",
            "Vayu tries both. His real reaction is the ad; don't script it.",
            "Pratibha: 'The difference? One scoop of Little Joys Proteinmix: 100% plant protein, and it doesn't change the taste.'",
            "Tie it to her own routine: she counts protein for her workouts, and this is how she does it for Vayu.",
            "Close: 'Link in bio, buy now.'",
        ],
        claims=["12g of extra protein per scoop", "100% plant protein", "Does not change the taste of the food"],
        language="English or Hinglish, as in her feed.",
        avoid="A stiff studio ad, or a product pitch that has nothing to do with her family (her feed's 'foreign' list).",
        reference_ads=["LJ-036", "LJ-056", "LJ-062"],
        watch=["Vayu is under 6. In the ads, under-6 kids did worse than 6 to 12 year olds (median ROAS 0.98 vs 1.34), so her mom-voice carries more of this ad.",
               "Food and meals are a small part of her feed (about 1 in 10 posts)."],
    ),
    "the_mum_wife_playbook": dict(
        role="Low-cost creative test",
        product="Nutrimix 2+ (chocolate milk)",
        why="Her daughter Seerat already talks straight to camera in her videos, and she speaks Hinglish. "
            "Small account (median ~20-90k plays), but her paid posts do better than her normal ones.",
        format="Seerat-led playful moment, the kind of mother-daughter bit she already posts.",
        hook="Seerat, holding her cup: \"Mumma, yeh wala doodh phir se!\" (Mumma, this milk again!)",
        beats=[
            "0-3s: Seerat asks for 'Little Joys wala doodh' by name.",
            "Mumma to camera: 'Isme ragi, bajra, almonds aur walnuts hain, aur meetha sirf jaggery aur dates se.'",
            "Seerat drinks and reacts. Her taste reaction is the proof.",
            "Close: buy-now ask plus link.",
        ],
        claims=["Made with Ragi, Bajra, Almonds, Walnuts", "Completely sweetened with jaggery and dates"],
        language="Hinglish (her feed is mostly Hindi with English).",
        avoid="Shooting without Seerat in frame, or TV-ad lighting and polish (both on her feed's 'foreign' list).",
        reference_ads=["LJ-035", "LJ-042", "LJ-009"],
        watch=["Seerat is about 3, and under-6 kids were weaker in the ads.",
               "Low reach: think of this as buying a creative for paid ads, not buying her audience."],
    ),
    "ohmother.in": dict(
        role="Creative test (format fit, small reach)",
        product="Proteinmix (in the school-morning breakfast)",
        why="Her signature format is the school-morning routine voiceover with two school-age kids. "
            "That is the 'routine' story the account uses most, and it is spoken in English.",
        format="Her timestamped school-morning montage, with Proteinmix going into the breakfast. Let the older child do the talking.",
        hook="Older child to camera, plate in hand: \"Guess what's hiding in my paratha?\"",
        beats=[
            "0-3s: the child's line above, 'Little Joys' on screen.",
            "Navya voiceover over the morning rush: one scoop into the dough, no extra recipe.",
            "Child eats: 'It tastes the same!'",
            "On screen: '1 scoop (15g) = 12g plant protein'.",
            "Close: buy-now ask; she already uses discount codes in captions.",
        ],
        claims=["1 scoop (15g) contains 12g plant protein", "Does not alter taste of rotis or batters"],
        language="English.",
        avoid="A mom-only voiceover. A similar rushed-breakfast mom ad (LJ-018) did poorly at ROAS 0.75. What separates the winners is a child doing the talking.",
        reference_ads=["LJ-004", "LJ-098", "LJ-100"],
        watch=["Small reach: her recent paid posts get about 23k plays.",
               "Her bio tags an adult protein brand (one.science.nutrition.in) she promoted on 5 Oct 2026. Check there is no category clash."],
    ),
    "foodies_by_neha": dict(
        role="Proteinmix recipe specialist",
        product="Proteinmix (in tiffin parathas / cheela)",
        why="1M followers, and she already runs a 'Kid's School Tiffin Box' series in Hinglish, with a "
            "'high protein' tiffin recipe posted on 27 Oct 2026. 'Mix it into everyday food' is the Proteinmix story.",
        format="Her own 'Tiffin Box Recipe Episode' format: text hook, top-down cooking shots, her voiceover.",
        hook="On screen: \"Tiffin Episode: 12g extra protein, bacche ko pata bhi nahi chalega\" (and the kids won't even notice)",
        beats=[
            "0-3s: episode text hook with 'Little Joys Proteinmix' on screen.",
            "One scoop into the atta; she says the number: '1 scoop mein 12g plant protein.'",
            "Cook and pack, in her usual style.",
            "Taste proof: her son's tiffin comes back empty, or his voice saying the taste is the same.",
            "Close: buy-now ask.",
        ],
        claims=["1 scoop (15g) contains 12g plant protein",
                "Can be added directly to everyday meals like roti, dosa, cheela, and pancakes without altering familiar tastes"],
        language="Hinglish (her transcripts are Hindi with English; the post label says 'English', which is wrong).",
        avoid="An ad that never shows the product being used in real cooking (her feed's 'foreign' list).",
        reference_ads=["LJ-004", "LJ-021", "LJ-098"],
        watch=["No children appear in her feed, and a child presenting is the account's strongest pattern. A child taste moment is worth asking for, but it is new for her.",
               "Recipe ads on their own are only about average once LJ-004 is taken out (ROAS 1.21)."],
    ),
}

# Strong fits we are NOT recommending right now, and what would change that.
ON_HOLD = {
    "sia_3vedi": "Best fit of all 20: a child presenter with 5.4M median plays. But she posted a paid Gritzo kids'-milk video on "
                 "28 Sep 2026. If there is no exclusivity, swap her in for #5 and pitch Proteinmix-in-roti "
                 "(an LJ-004 style plate video), not milk, so it doesn't look like she switched milk brands.",
    "raja_choudhary04": "Child-voiced daily vlogs, the winning format. But he did two paid Gritzo posts (Jul and Aug 2026) "
                        "and a paid Troovy post on 7 Oct 2026. Revisit once those deals end.",
    "mumma_and_ridhu": "Near-tie for the 5th slot (score within 0.3 of #5). Hinglish, with kids aged 3-12 on camera. Use her if "
                       "any of the five falls through.",
}
