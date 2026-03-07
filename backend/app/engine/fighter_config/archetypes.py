TECH_LEVELS = [
    "Fantasy Medieval",
    "Ancient / Mythological",
    "1800s Industrial",
    "Contemporary / Modern",
    "Near-Future",
    "Sci-Fi / Far Future",
]


ARCHETYPE_DESCRIPTIONS = {
    "The Siren": "weaponized beauty, seduction, charm",
    "The Witch": "mysticism, dark arts, supernatural",
    "The Viper": "poison, subterfuge, dirty tricks",
    "The Prodigy": "young technical genius, speed and precision",
    "The Doll": "deceptive innocence, psychological warfare",
    "The Huntress": "predatory, relentless, speed-based",
    "The Empress": "dominance through authority and manipulation",
    "The Experiment": "cybernetics, body modification, science",
    "The Demon": "infernal power, dark seduction, hellfire",
    "The Assassin": "lethal precision, stealth, silent killing",
    "The Nymph": "nature magic, fae trickery, ethereal allure",
    "The Brute": "raw physical power, intimidation",
    "The Veteran": "battle-scarred, tactical, experienced",
    "The Monster": "inhuman size and strength, terrifying",
    "The Technician": "precise, methodical, strategic",
    "The Wildcard": "unpredictable, chaotic",
    "The Mystic": "supernatural warrior, ancient traditions",
}


ARCHETYPES_FEMALE = [
    "The Siren",
    "The Witch",
    "The Viper",
    "The Prodigy",
    "The Doll",
    "The Huntress",
    "The Empress",
    "The Experiment",
    "The Demon",
    "The Assassin",
    "The Nymph",
]

ARCHETYPES_MALE = [
    "The Brute",
    "The Veteran",
    "The Monster",
    "The Technician",
    "The Wildcard",
    "The Mystic",
    "The Prodigy",
    "The Experiment",
]

ARCHETYPE_SUBTYPES = {
    "The Siren": [
        {
            "name": "Chanteuse",
            "description": "Hypnotic voice, musical seduction",
            "body_profile_bias": {"Slim": +25, "Curvy": -20, "Athletic": -5},
        },
        {
            "name": "Femme Fatale",
            "description": "Deadly beauty, lethal allure",
            "body_profile_bias": {"Curvy": +20, "Athletic": +10, "Petite": -30},
        },
        {
            "name": "Temptress",
            "description": "Overt seduction, irresistible magnetism",
            "body_profile_bias": {"Curvy": +25, "Slim": -15, "Petite": -10},
        },
        {
            "name": "Enchantress",
            "description": "Mystical charm, spellbinding presence",
            "body_profile_bias": {"Slim": +20, "Athletic": -10, "Curvy": -10},
        },
        {
            "name": "Muse",
            "description": "Inspires obsession, ethereal beauty",
            "body_profile_bias": {"Petite": +25, "Slim": +15, "Curvy": -35},
        },
    ],
    "The Witch": [
        {
            "name": "Hexcaster",
            "description": "Curse specialist, hex-focused combat",
            "body_profile_bias": {"Slim": +20, "Athletic": -10, "Curvy": -10},
        },
        {
            "name": "Oracle",
            "description": "Sees the future, fights with foreknowledge",
            "body_profile_bias": {"Petite": +20, "Slim": +10, "Curvy": -25},
        },
        {
            "name": "Necromancer",
            "description": "Death magic, drains life force",
            "body_profile_bias": {"Slim": +25, "Petite": +10, "Curvy": -30},
        },
        {
            "name": "Alchemist",
            "description": "Potions, transmutation, chemical warfare",
            "body_profile_bias": {"Athletic": +20, "Petite": -15, "Slim": -5},
        },
        {
            "name": "Coven Mother",
            "description": "Ritual power, commands dark authority",
            "body_profile_bias": {"Curvy": +25, "Slim": -15, "Petite": -10},
        },
    ],
    "The Viper": [
        {
            "name": "Poisoner",
            "description": "Toxic specialist, venomous attacks",
            "body_profile_bias": {"Slim": +20, "Curvy": -15, "Athletic": -5},
        },
        {
            "name": "Schemer",
            "description": "Manipulative mastermind, always three steps ahead",
            "body_profile_bias": {"Athletic": +15, "Curvy": +10, "Petite": -25},
        },
        {
            "name": "Blackmailer",
            "description": "Leverages secrets, psychological torment",
            "body_profile_bias": {"Curvy": +25, "Athletic": -15, "Petite": -10},
        },
        {
            "name": "Saboteur",
            "description": "Disables opponents before the fight begins",
            "body_profile_bias": {"Athletic": +25, "Curvy": -20, "Slim": -5},
        },
        {
            "name": "Infiltrator",
            "description": "Master of disguise, strikes from within",
            "body_profile_bias": {
                "Slim": +15,
                "Petite": +10,
                "Curvy": -15,
                "Athletic": -10,
            },
        },
    ],
    "The Prodigy": [
        {
            "name": "Wunderkind",
            "description": "Impossibly talented youth",
            "body_profile_bias": {
                "Petite": +25,
                "Slim": +10,
                "Curvy": -20,
                "Athletic": -15,
            },
        },
        {
            "name": "Savant",
            "description": "One transcendent skill, narrow brilliance",
            "body_profile_bias": {"Slim": +25, "Athletic": -15, "Curvy": -10},
        },
        {
            "name": "Phenom",
            "description": "Natural athlete, explosive raw talent",
            "body_profile_bias": {"Athletic": +30, "Petite": -20, "Slim": -10},
        },
        {
            "name": "Virtuoso",
            "description": "Technical perfection, flawless execution",
            "body_profile_bias": {
                "Slim": +20,
                "Athletic": +10,
                "Curvy": -20,
                "Petite": -10,
            },
        },
        {
            "name": "Ingenue",
            "description": "Deceptively innocent, underestimated",
            "body_profile_bias": {
                "Petite": +30,
                "Curvy": +5,
                "Athletic": -25,
                "Slim": -10,
            },
        },
    ],
    "The Doll": [
        {
            "name": "Porcelain",
            "description": "Fragile appearance, eerie perfection",
            "body_profile_bias": {
                "Petite": +25,
                "Slim": +10,
                "Athletic": -25,
                "Curvy": -10,
            },
        },
        {
            "name": "Marionette",
            "description": "Moves like she's controlled by strings",
            "body_profile_bias": {"Slim": +25, "Petite": +5, "Curvy": -25},
        },
        {
            "name": "Ragdoll",
            "description": "Limp and loose until she strikes",
            "body_profile_bias": {"Slim": +15, "Curvy": +10, "Athletic": -20},
        },
        {
            "name": "China Doll",
            "description": "Delicate beauty hiding sharp edges",
            "body_profile_bias": {
                "Petite": +20,
                "Slim": +15,
                "Curvy": -25,
                "Athletic": -10,
            },
        },
        {
            "name": "Wind-Up",
            "description": "Mechanical precision, clockwork violence",
            "body_profile_bias": {"Athletic": +25, "Curvy": -15, "Petite": -10},
        },
    ],
    "The Huntress": [
        {
            "name": "Stalker",
            "description": "Patient tracker, wears opponents down",
            "body_profile_bias": {"Athletic": +15, "Slim": +10, "Curvy": -20},
        },
        {
            "name": "Apex",
            "description": "Top predator, dominant aggression",
            "body_profile_bias": {"Athletic": +25, "Curvy": +5, "Petite": -25},
        },
        {
            "name": "Trapper",
            "description": "Sets up opponents, controls the cage",
            "body_profile_bias": {"Slim": +20, "Petite": +10, "Athletic": -20},
        },
        {
            "name": "Bloodhound",
            "description": "Relentless pursuit, never loses the scent",
            "body_profile_bias": {"Athletic": +20, "Curvy": -10, "Slim": -10},
        },
        {
            "name": "Falconer",
            "description": "Precision strikes from distance",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
    ],
    "The Empress": [
        {
            "name": "Sovereign",
            "description": "Born to rule, unquestioned authority",
            "body_profile_bias": {"Curvy": +15, "Athletic": +10, "Petite": -20},
        },
        {
            "name": "Warlord",
            "description": "Conquers through force of will",
            "body_profile_bias": {"Athletic": +30, "Slim": -15, "Petite": -15},
        },
        {
            "name": "Matriarch",
            "description": "Protective fury, motherly wrath",
            "body_profile_bias": {"Curvy": +25, "Petite": -20, "Slim": -5},
        },
        {
            "name": "Tyrant",
            "description": "Rules through fear and dominance",
            "body_profile_bias": {"Athletic": +20, "Curvy": +5, "Petite": -20},
        },
        {
            "name": "Regent",
            "description": "Graceful authority, silk over steel",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Athletic": -15,
                "Curvy": -15,
            },
        },
    ],
    "The Experiment": [
        {
            "name": "Cyborg",
            "description": "Mechanical augmentation, part machine",
            "body_profile_bias": {"Athletic": +30, "Curvy": -20, "Slim": -10},
        },
        {
            "name": "Chimera",
            "description": "Gene-spliced hybrid, unstable biology",
            "body_profile_bias": {
                "Curvy": +20,
                "Athletic": +5,
                "Slim": -15,
                "Petite": -10,
            },
        },
        {
            "name": "Prototype",
            "description": "First of her kind, untested potential",
            "body_profile_bias": {"Athletic": +20, "Slim": +10, "Petite": -20},
        },
        {
            "name": "Splice",
            "description": "DNA rewritten, evolved beyond human",
            "body_profile_bias": {"Slim": +25, "Petite": +5, "Curvy": -25},
        },
        {
            "name": "Ghost in the Machine",
            "description": "Digital consciousness in synthetic body",
            "body_profile_bias": {"Slim": +20, "Petite": +15, "Curvy": -30},
        },
    ],
    "The Demon": [
        {
            "name": "Succubus",
            "description": "Feeds on desire, drains through seduction",
            "body_profile_bias": {"Curvy": +30, "Petite": -20, "Slim": -10},
        },
        {
            "name": "Hellion",
            "description": "Chaotic hellfire, wild destruction",
            "body_profile_bias": {"Athletic": +25, "Slim": -15, "Curvy": -10},
        },
        {
            "name": "Infernal",
            "description": "Ancient evil, smoldering menace",
            "body_profile_bias": {"Curvy": +15, "Athletic": +10, "Petite": -20},
        },
        {
            "name": "Corrupted",
            "description": "Once pure, now twisted by dark power",
            "body_profile_bias": {"Slim": +20, "Petite": +10, "Curvy": -25},
        },
        {
            "name": "Abyssal",
            "description": "Deep darkness, void-touched horror",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
    ],
    "The Assassin": [
        {
            "name": "Shadow",
            "description": "Invisible until the killing blow",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
        {
            "name": "Blade",
            "description": "Edged weapon master, surgical precision",
            "body_profile_bias": {
                "Athletic": +25,
                "Slim": +5,
                "Petite": -20,
                "Curvy": -10,
            },
        },
        {
            "name": "Phantom",
            "description": "Ghost-like movement, untouchable",
            "body_profile_bias": {
                "Petite": +25,
                "Slim": +10,
                "Curvy": -20,
                "Athletic": -15,
            },
        },
        {
            "name": "Silencer",
            "description": "Ends fights before they start",
            "body_profile_bias": {
                "Slim": +20,
                "Athletic": +15,
                "Curvy": -25,
                "Petite": -10,
            },
        },
        {
            "name": "Venom",
            "description": "Poisoned weapons, toxic specialist",
            "body_profile_bias": {
                "Slim": +15,
                "Athletic": +10,
                "Petite": -15,
                "Curvy": -10,
            },
        },
    ],
    "The Nymph": [
        {
            "name": "Dryad",
            "description": "Forest spirit, nature's living weapon",
            "body_profile_bias": {
                "Slim": +20,
                "Petite": +10,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
        {
            "name": "Naiad",
            "description": "Water spirit, fluid and unpredictable",
            "body_profile_bias": {
                "Curvy": +20,
                "Slim": +10,
                "Petite": -20,
                "Athletic": -10,
            },
        },
        {
            "name": "Pixie",
            "description": "Tiny chaos agent, mischievous trickster",
            "body_profile_bias": {
                "Petite": +30,
                "Slim": +5,
                "Curvy": -25,
                "Athletic": -10,
            },
        },
        {
            "name": "Sylph",
            "description": "Air spirit, impossibly graceful",
            "body_profile_bias": {
                "Slim": +25,
                "Athletic": +5,
                "Curvy": -20,
                "Petite": -10,
            },
        },
        {
            "name": "Fae Queen",
            "description": "Otherworldly royalty, beautiful and cruel",
            "body_profile_bias": {
                "Curvy": +25,
                "Athletic": +5,
                "Petite": -20,
                "Slim": -10,
            },
        },
    ],
}


ARCHETYPE_SUBTYPES_MALE = {
    "The Brute": [
        {
            "name": "Berserker",
            "description": "Uncontrollable rage, fights like a cornered animal",
            "body_profile_bias": {"Massive": +15, "Lean": -15},
        },
        {
            "name": "Enforcer",
            "description": "Calculated brutality, breaks bones on purpose",
            "body_profile_bias": {"Muscular": +15, "Lean": -10},
        },
        {
            "name": "Juggernaut",
            "description": "Unstoppable forward pressure, walks through damage",
            "body_profile_bias": {"Massive": +20, "Athletic": -15},
        },
        {
            "name": "Brawler",
            "description": "Street-fighting savagery, no technique just violence",
            "body_profile_bias": {"Athletic": +10, "Muscular": +10, "Lean": -15},
        },
        {
            "name": "Mauler",
            "description": "Ground-and-pound specialist, smothering aggression",
            "body_profile_bias": {"Muscular": +10, "Massive": +10, "Lean": -15},
        },
    ],
    "The Veteran": [
        {
            "name": "Grizzled",
            "description": "Decades of scars, fights on muscle memory alone",
            "body_profile_bias": {"Athletic": +10, "Muscular": +10, "Lean": -15},
        },
        {
            "name": "Tactician",
            "description": "Reads opponents like books, always three moves ahead",
            "body_profile_bias": {"Athletic": +15, "Massive": -10},
        },
        {
            "name": "Warhorse",
            "description": "Refuses to stay down, legendary toughness",
            "body_profile_bias": {"Muscular": +15, "Lean": -10},
        },
        {
            "name": "Mentor",
            "description": "Old guard, still dangerous, teaches through pain",
            "body_profile_bias": {"Athletic": +10, "Lean": +5, "Massive": -10},
        },
        {
            "name": "Survivor",
            "description": "Should have died a dozen times, too stubborn to quit",
            "body_profile_bias": {"Lean": +15, "Massive": -15},
        },
    ],
    "The Monster": [
        {
            "name": "Titan",
            "description": "Godlike size, moves mountains",
            "body_profile_bias": {"Massive": +20, "Lean": -20},
        },
        {
            "name": "Behemoth",
            "description": "Living siege engine, destroys everything in his path",
            "body_profile_bias": {"Massive": +15, "Athletic": -10},
        },
        {
            "name": "Aberration",
            "description": "Something wrong with his proportions, uncanny and terrifying",
            "body_profile_bias": {"Muscular": +15, "Athletic": -10},
        },
        {
            "name": "Goliath",
            "description": "Towering giant, makes other big men look small",
            "body_profile_bias": {"Massive": +20, "Lean": -15},
        },
        {
            "name": "Nightmare",
            "description": "The thing you see in the dark, primal fear made flesh",
            "body_profile_bias": {"Muscular": +10, "Massive": +10, "Lean": -15},
        },
    ],
    "The Technician": [
        {
            "name": "Surgeon",
            "description": "Dissects opponents with clinical precision",
            "body_profile_bias": {"Lean": +15, "Massive": -15},
        },
        {
            "name": "Analyst",
            "description": "Studies film obsessively, knows every weakness",
            "body_profile_bias": {"Athletic": +15, "Massive": -10},
        },
        {
            "name": "Counter-Puncher",
            "description": "Waits for mistakes then punishes them brutally",
            "body_profile_bias": {"Athletic": +10, "Lean": +10, "Massive": -15},
        },
        {
            "name": "Chessmaster",
            "description": "Every move is a setup for the next three",
            "body_profile_bias": {"Lean": +10, "Athletic": +10, "Massive": -15},
        },
        {
            "name": "Pressure Fighter",
            "description": "Relentless technical volume, drowns opponents in output",
            "body_profile_bias": {"Athletic": +15, "Lean": -5},
        },
    ],
    "The Wildcard": [
        {
            "name": "Lunatic",
            "description": "Genuinely unhinged, nobody knows what he'll do next",
            "body_profile_bias": {"Lean": +15, "Massive": -10},
        },
        {
            "name": "Gambler",
            "description": "Throws everything on one big moment",
            "body_profile_bias": {"Athletic": +10, "Lean": +5, "Massive": -10},
        },
        {
            "name": "Trickster",
            "description": "Dirty tricks, misdirection, fights with his brain",
            "body_profile_bias": {"Lean": +15, "Athletic": +5, "Massive": -15},
        },
        {
            "name": "Anarchist",
            "description": "Fights the rules, the ref, and the opponent simultaneously",
            "body_profile_bias": {"Athletic": +10, "Muscular": +5, "Lean": -10},
        },
        {
            "name": "Showman",
            "description": "Every fight is a performance, lives for the crowd",
            "body_profile_bias": {"Athletic": +15, "Lean": -5, "Massive": -5},
        },
    ],
    "The Mystic": [
        {
            "name": "Monk",
            "description": "Disciplined spiritual warrior, fights with inner peace",
            "body_profile_bias": {"Lean": +15, "Athletic": +5, "Massive": -15},
        },
        {
            "name": "Shaman",
            "description": "Channels ancestral spirits, fights with otherworldly guidance",
            "body_profile_bias": {"Athletic": +10, "Lean": +5, "Massive": -10},
        },
        {
            "name": "Sage",
            "description": "Ancient knowledge, sees the flow of combat",
            "body_profile_bias": {"Lean": +15, "Massive": -15},
        },
        {
            "name": "Prophet",
            "description": "Fights with divine conviction, terrifying certainty",
            "body_profile_bias": {"Athletic": +10, "Muscular": +5, "Lean": -10},
        },
        {
            "name": "Ascetic",
            "description": "Denied himself everything, forged in deprivation",
            "body_profile_bias": {"Lean": +20, "Massive": -15},
        },
    ],
    "The Prodigy": [
        {
            "name": "Phenom",
            "description": "Natural athlete, explosive raw talent beyond his years",
            "body_profile_bias": {"Athletic": +15, "Lean": +5, "Massive": -15},
        },
        {
            "name": "Wunderkind",
            "description": "Impossibly talented youth, makes veterans look slow",
            "body_profile_bias": {"Lean": +10, "Athletic": +10, "Massive": -15},
        },
        {
            "name": "Natural",
            "description": "Born to fight, instinct over training",
            "body_profile_bias": {"Athletic": +20, "Massive": -15},
        },
        {
            "name": "Heir Apparent",
            "description": "Next in a legendary bloodline, born with expectations",
            "body_profile_bias": {"Athletic": +10, "Muscular": +5, "Lean": -10},
        },
        {
            "name": "Prodigy Son",
            "description": "Father was a legend, son might be better",
            "body_profile_bias": {"Athletic": +15, "Massive": -10},
        },
    ],
    "The Experiment": [
        {
            "name": "Cyborg",
            "description": "Mechanical augmentation, part machine",
            "body_profile_bias": {"Muscular": +15, "Lean": -10},
        },
        {
            "name": "Subject Zero",
            "description": "First successful test subject, unstable but powerful",
            "body_profile_bias": {"Massive": +15, "Lean": -15},
        },
        {
            "name": "Weapon X",
            "description": "Military black project, built to kill",
            "body_profile_bias": {"Muscular": +10, "Athletic": +5, "Lean": -10},
        },
        {
            "name": "Lab Rat",
            "description": "Escaped experimental facility, body permanently altered",
            "body_profile_bias": {"Massive": +10, "Muscular": +10, "Athletic": -15},
        },
        {
            "name": "Evolved",
            "description": "Next stage of human development, something beyond",
            "body_profile_bias": {"Athletic": +10, "Muscular": +10, "Lean": -15},
        },
    ],
}
