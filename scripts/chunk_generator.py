#!/usr/bin/env python3
"""
Keli10K Chunk Generator — MASTER GENERATOR
Produces 500K+ training examples across 5 chunks (100K each) + holdout validation.
Each example: {"input": ..., "target": "<PLAN>...</PLAN><THINK>...</THINK><EXEC>...</EXEC>",
               "cognitive_level": N, "domain": "...", "chunk": N}

Usage:
    python3 scripts/chunk_generator.py --chunks 1-5 --num 100000
"""

import json, random, os, sys, argparse, itertools, time, math
from typing import Iterator, Dict

random.seed(42)
_BASE = "/tmp/opencode/snca/data"

# ── Shared word banks ──
SCIENCE = [
    "quantum mechanics","classical physics","thermodynamics","electromagnetism",
    "general relativity","organic chemistry","molecular biology","genetics",
    "ecology","geology","astrophysics","neuroscience","cognitive science",
    "linguistics","economics","sociology","political science","climatology",
    "materials science","pharmacology","evolutionary biology","fluid dynamics",
    "nuclear physics","crystallography","oceanography","paleontology","virology",
    "epidemiology","astrobiology","biophysics","geochemistry","ethology",
]
MATH = [
    "number theory","graph theory","topology","linear algebra","calculus",
    "probability theory","statistics","combinatorics","group theory",
    "real analysis","complex analysis","differential equations","game theory",
    "category theory","set theory","information theory","knot theory",
    "measure theory","optimization theory","numerical analysis","logic",
    "trigonometry","fractal geometry","chaos theory","homotopy theory",
]
CS = [
    "distributed systems","compiler design","operating systems","database theory",
    "computer vision","NLP","reinforcement learning","cryptography",
    "formal verification","computational complexity","graphics","robotics",
    "HCI","software engineering","networking","parallel computing",
    "computer architecture","programming languages","computational biology",
    "security","cloud computing","AI safety","quantum computing",
    "data engineering","DevOps","PL theory","formal methods",
]
DOMAINS = [
    "reasoning","science","systems_thinking","logic","mathematics",
    "computing","philosophy","epistemology","metacognition","self_awareness",
    "cognitive_biases","psychology","strategy","error_analysis",
    "architecture","code","web_development","algorithms","data_structures",
    "linguistics","physics","biology","engineering","lateral_thinking",
    "temporal","spatial","analogy","counterfactuals","puzzles","complexity",
    "frontend","design","html","css","performance","refactoring",
]

def pick(*args):
    return random.choice(args)

def level_wt():
    return random.choices(range(1, 8), weights=[5, 10, 25, 25, 20, 10, 5])[0]


# ═══════════════════════ Chunk 1: Foundational Reasoning ═══════════════════════
# 12 categories: causal, abduction, CSP, analogy, counterfactual, lateral, systems, deductive, inductive, syllogistic, temporal, spatial

CAUSES = [
    "increased atmospheric CO2","deficit spending","a genetic mutation in DNA polymerase",
    "rising ocean temperatures","widespread automation","a speculation bubble",
    "groundwater aquifer depletion","viral antigenic drift","LTP in neural circuits",
    "permafrost methane release","central bank rate hike","loss of apex predators",
    "microplastic accumulation","sustained low birth rates","Amazon deforestation",
    "ocean acidification","semiconductor supply bottleneck","rapid urbanization",
    "pervasive social media use","antibiotic overuse in agriculture",
]
EFFECTS = [
    "accelerated glacial melt","prolonged recession","cancerous cell proliferation",
    "coral reef bleaching","structural unemployment","systemic banking crisis",
    "land subsidence","immune evasion and new variants","enhanced memory formation",
    "accelerated warming feedback","decreased consumer spending","trophic cascade collapse",
    "bioaccumulation toxicity","workforce shrinkage","regional precipitation shifts",
    "shell dissolution in marine life","price increases","overburdened infrastructure",
    "increased polarization and echo chambers","antimicrobial resistance",
]

def _causal_gen():
    pool = []
    for c in CAUSES:
        for e in EFFECTS:
            pool.append((c,e))
    random.shuffle(pool)
    pool = pool[:60]
    while True:
        for c, e in pool:
            inp = pick(f"Trace the causal chain from {c} to {e}. Identify intermediate mechanisms and feedback loops.", f"What is the complete causal pathway connecting {c} with {e}?", f"Explain how {c} ultimately leads to {e}. Include all intermediate steps.", f"Map the cause-effect chain from {c} to {e}. What are the crucial causal links?")
            plan = pick(f"<PLAN>I will trace the causal chain from {c} to {e} by breaking it into sequential links. Step 1: Identify direct effects of {c}. Step 2: Trace how each becomes a secondary cause. Step 3: Propagate through the system until reaching {e}. I will identify feedback mechanisms at each stage and validate that each link has a plausible causal mechanism.</PLAN>", f"<PLAN>To trace from {c} to {e}: (1) Decompose the causal path into intermediate states. (2) For each transition, identify the driving mechanism. (3) Check for amplifying or dampening feedback. The path likely involves positive feedback, negative feedback, threshold effects, or nonlinear coupling of multiple converging pathways.</PLAN>", f"<PLAN>Approach: Establish baseline before {c}. Model the immediate perturbation. Propagate effects through the system. Identify feedback loops and delays. Arrive at {e}. Each causal link must satisfy temporal ordering and mechanistic plausibility.</PLAN>")
            think = pick(f"<THINK>Beginning with {c}, first-order effects include perturbations to nearby variables. However, systems exhibit nonlinear responses -- small changes can amplify through feedback. I need to consider whether the path is direct or mediated. The chain may involve positive feedback (amplification) or negative feedback (damping). Time delays mean effects may not be immediate. I also need to distinguish correlation from causation at each step. Let me trace carefully: {c} triggers mechanism M1, which changes variable V1, which then affects V2 through mechanism M2, continuing step by step until we reach {e}.</THINK>", f"<THINK>To trace from {c} to {e}: Start by identifying what {c} directly changes. Each effect becomes a new cause. Key considerations: (1) Time delays -- effects may be lagged; (2) Threshold effects -- tipping points where behavior changes abruptly; (3) Feedback loops that amplify or dampen; (4) Nonlinear responses -- doubling the cause may more than double the effect. The chain likely involves multiple pathways converging on {e}. I will trace the dominant path while acknowledging parallel mechanisms. Each link's reliability depends on the strength of evidence for that specific mechanism.</THINK>")
            exec_ = pick(f"<EXEC>Causal chain: {c} -> direct effects (perturbation of local variables) -> secondary effects (system propagation) -> tertiary effects (emergent responses) -> {e}. The chain involves positive feedback amplification, negative feedback damping, threshold-triggered transitions, nonlinear coupling, and cascade propagation. Key mechanisms: direct causation, common-cause mediation, causal inference, and mechanistic explanation. The path from {c} to {e} is robust across multiple pathways but sensitive to initial conditions and mediated by critical variables.</EXEC>", f"<EXEC>Causal trace complete. Primary pathway: {c} -> intermediate disruption -> system-wide propagation -> {e}. Mechanism: linear amplification, exponential cascade, diffuse network propagation, or threshold-triggered shift. Chain has high explanatory power, moderate uncertainty, and testable predictions. To break the causal chain, intervene at the earliest link, the most sensitive link, or the highest leverage point.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("reasoning","science","systems_thinking"))

OBS_POOL = [
    ("patient has persistent cough, low-grade fever, night sweats",["tuberculosis","bronchitis","lung cancer","autoimmune disorder","fungal infection"]),
    ("network latency spikes every 47 minutes with no scheduled jobs",["cron collision","GC pause","switch buffer flush","replication task","background backup"]),
    ("lake water has elevated phosphate and algal blooms but low nitrogen",["agricultural runoff","industrial discharge","septic leakage","phosphate-rich geology","detergent pollution"]),
    ("a star dims by 22% every 14.3 days",["orbiting exoplanet","binary companion","dust cloud transit","stellar pulsation","starspot rotation"]),
    ("stock price dropped 8% in 10 minutes with no news",["algorithmic cascade","insider selling","market maker error","flash crash","fat finger trade"]),
    ("a function returns None for valid inputs only on Tuesdays",["timezone bug","weekly pipeline reset","cron resource conflict","conditional branch","deployment schedule"]),
    ("urban birds have developed shorter wingspans over 50 years",["selection against long wings","nutritional constraints","genetic drift","phenotypic plasticity","traffic avoidance"]),
    ("ancient pottery at two sites 500km apart has identical clay",["shared trade network","same geological source","migration of potters","independent discovery","cultural diffusion"]),
]

def _abduction_gen():
    pool = []
    for obs, hypos in OBS_POOL:
        for h in hypos:
            alt = [x for x in hypos if x != h]
            pool.append((obs, h, alt[:3]))
    random.shuffle(pool)
    pool = pool[:50]
    while True:
        for obs, hypo, alt in pool:
            inp = pick(f"Given: {obs}. What is the most likely explanation? Use abductive reasoning.", f"Observing that {obs}, what hypothesis best explains this evidence?", f"Explain the observed phenomenon: {obs}. Generate and evaluate competing hypotheses.", f"Reason abductively about: {obs}. What is the best explanation and why?")
            plan = pick(f"<PLAN>I will apply abductive reasoning: (1) Identify plausible hypotheses for {obs}. (2) For each, derive testable predictions. (3) Compare predictions against observations. (4) Select the best explanation considering simplicity and coherence. Primary hypothesis: {hypo}. Alternatives: {', '.join(alt[:2])}.</PLAN>", f"<PLAN>To explain {obs}: Generate candidates using domain knowledge. For each, ask what else we would expect to observe. The hypothesis that best predicts the observation with fewest additional assumptions wins. Lead: {hypo}. Others: {', '.join(alt[:2])}.</PLAN>")
            think = pick(f"<THINK>Observation: {obs}. Several hypotheses could explain this. {hypo} accounts for the core features. However, I must consider {alt[0]}. To discriminate: what unique predictions does each make? {hypo} predicts additional evidence X; {alt[0]} predicts Y. I check which predicted pattern matches our observation. Occam's razor: does {hypo} require fewer ancillary assumptions? The inference to the best explanation balances explanatory power and parsimony. The best explanation makes the observation most expected. Given {obs}, {hypo} makes this highly probable, making it the superior abduction.</THINK>", f"<THINK>Using inference to the best explanation for {obs}. {hypo} explains via direct causation, common cause, or constitutive relationship. Alternative {alt[0]} explains through confounding, reverse causation, coincidence, or a different causal pathway. I evaluate: (1) Fit with observation; (2) Parsimony; (3) Consistency with background knowledge. The best explanation would make the observation expected rather than surprising. {hypo} achieves this better than alternatives.</THINK>")
            exec_ = pick(f"<EXEC>Best explanation for '{obs}': {hypo}. Accounts for all features with minimal assumptions. Alternatives considered: {', '.join(alt[:2])}. Discriminating evidence: temporal ordering supports causation, mechanism well-established, or controlled experiments confirm. Confidence: high -- multiple converging lines of evidence. Strengthened by consilience with other evidence.</EXEC>", f"<EXEC>Abductive analysis: Observation -- {obs}. Inference -- {hypo} best explains because: (1) Accounts for pattern without anomalies; (2) Alternatives ({', '.join(alt[:2])}) fail on key aspects; (3) Coheres with established knowledge. Mechanism: direct causal pathway or common cause model. Confidence: high, moderate, or tentative. This is inference to the best explanation.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("reasoning","science","logic"))

CSP_PROBLEMS = [
    "schedule 8 classes in 5 time slots with no instructor conflicts and room capacity constraints",
    "assign 15 workers to 12 shifts where each shift needs 2 workers, max 4 per worker",
    "color a map of 20 regions with 4 colors such that adjacent regions differ",
    "pack items of varying sizes into 5 bins of capacity 100, minimizing bins used",
    "find a 9x9 Latin square where rows/columns have digits 1-9 with pre-filled cells",
    "assign 10 tasks to 3 machines with processing times and deadline constraints",
    "route 50 delivery points with 5 vehicles each on 8-hour shifts",
    "place 8 queens on a chessboard so none attack each other",
    "design a circuit with 6 inputs and 1 output using only NAND gates",
    "allocate frequencies to 100 towers so adjacent towers don't share frequencies",
]

def _csp_gen():
    while True:
        for prob in CSP_PROBLEMS:
            inp = pick(f"CSP: {prob}. Find a valid assignment using constraint propagation.", f"Constraint satisfaction: {prob}. Describe your approach to a feasible solution.", f"Solve: {prob}. Use backtracking with heuristics.", f"Find a valid configuration for: {prob}.")
            plan = pick(f"<PLAN>Formulate as CSP: variables with domains, constraints unary/binary/global. Apply arc consistency to reduce domains. Use backtracking with MRV/LCV heuristics. Check violations at each assignment. Key challenge is balancing multiple hard constraints or finding feasible solution in large search space.</PLAN>", f"<PLAN>Model {prob} with variables X_i, domains D_i, constraints C. Apply AC-3 before search. Use forward checking during backtracking with MRV heuristic, degree heuristic, or LCV heuristic. If tight constraints, use conflict-directed backjumping.</PLAN>")
            think = pick(f"<THINK>For {prob}, identify variables and domains. Constraints: unary, binary, or global (all-different). The constraint graph shows connectivity pattern. Dense graphs benefit from strong propagation; sparse graphs may work with simple backtracking. Decompose into connected components if possible. Let me trace constraint propagation -- do domains shrink sufficiently? If not, search with good heuristics. This domain has exploitable structure.</THINK>", f"<THINK>CSP analysis: {prob}. Variables, domains, constraints identified. No empty domains. Apply AC-3 to reduce before search -- this prunes significantly. The constraint graph shows high connectivity, modular structure, or tree-like structure. If over-constrained, relax constraints or use cost-based optimization. Propagate first, then search.</THINK>")
            exec_ = pick(f"<EXEC>Solution found. After arc consistency, domains reduced by 30 to 70 percent. Search with MRV found solution in 10 to 500 nodes. Assignment: complete and consistent. Constraint violations: 0. Time manageable with heuristic guidance; propagation was key to efficiency.</EXEC>", f"<EXEC>CSP solved via Backtracking+forward checking, AC-3+Backtracking+MRV, Conflict-directed backjumping, or Min-conflicts local search. Key decisions: variable ordering most constrained first, value ordering least constraining first. All constraints satisfied.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("reasoning","mathematics","computing"))

ANALOGY_PAIRS = [
    ("atoms","solar systems","nucleus: sun, electrons: planets"),
    ("immune system","nation defense","layered defense, adaptive response"),
    ("OS","government","resource allocation, scheduling"),
    ("natural selection","ML optimization","fitness, mutation, selection"),
    ("neuron","logic gate","excitation/inhibition as AND/OR/NOT"),
    ("city","living organism","infrastructure as circulatory system"),
    ("market","ecosystem","competition, niche, adaptation"),
    ("neural network","biological brain","layers as cortical columns"),
    ("DNA","programming language","genetic code as source code"),
    ("water pipe network","computer network","flow, pressure, routing, congestion"),
    ("food web","supply chain","producers, consumers, decomposers"),
    ("legal precedent","design pattern","reusable solution in context"),
    ("memes","genes","replication, mutation, selection"),
    ("telescope","microscope","extend senses, opposite scales"),
    ("cell","factory","organelles as specialized departments"),
]

def _analogy_gen():
    while True:
        for src, tgt, mapping in ANALOGY_PAIRS:
            inp = pick(f"Explain the analogy: {src} is to {tgt}. How does understanding one help with the other?", f"Structural mapping: {src} :: {tgt}. Identify the relational correspondences.", f"Analyze this analogy: {src} and {tgt}. What deep structural similarities exist?", f"Compare {src} with {tgt}. Map the relational structure between domains.")
            plan = pick(f"<PLAN>Structure-mapping approach: (1) Identify relational structure in {src}. (2) Find corresponding relations in {tgt}. (3) Map objects based on relational roles. (4) Evaluate analogy strength by mapping depth and systematicity. Key correspondence: {mapping}.</PLAN>", f"<PLAN>Decompose {src} into entities, attributes, relations, higher-order relations. Search {tgt} for matching relational patterns. Align structures -- attributes matter less than relational roles. Project inferences from source to target. Central mapping: {mapping}.</PLAN>")
            think = pick(f"<THINK>The analogy between {src} and {tgt} relies on shared relational structure, not surface features. In {src}, the key pattern is hierarchical organization, feedback loop, competitive dynamic, resource flow, compositional hierarchy, or temporal sequence. Does {tgt} exhibit a similar pattern? Yes -- the relational structure aligns. {mapping} illustrates this. The analogy is strong -- deep relational match, or partial -- some aspects map well. It is useful for generating hypotheses and explanatory -- transfers causal mechanisms. Analogies preserve relations but not all attributes. This aids understanding by mapping familiar to unfamiliar domains.</THINK>", f"<THINK>Structure-mapping: {src} -> {tgt}. Source has relations -- causal, temporal, hierarchical, spatial, functional, or dependency. Target: {tgt}. I look for systematicity -- connected relation systems map better than isolated facts. {mapping} shows key correspondence. Analogy strength: strong -- multiple relations map, moderate -- core maps periphery diverges, or partial -- specific relation maps. Analogical inference: phenomena in {src} like self-regulation, emergence, competition, cooperation, or adaptation may have counterparts in {tgt}.</THINK>")
            exec_ = pick(f"<EXEC>Analogy: {src} :: {tgt}. Mapping: {mapping}. Alignment: Deep -- multiple relations map systematically, moderate -- core maps periphery diverges, or specific -- functional relation maps clearly. Inferences: feedback mechanisms transfer, emergent behaviors analogous, failure modes similar, solutions apply across domains. Caveat: surface differences may mislead and analogical inference suggests hypotheses.</EXEC>", f"<EXEC>Analogical analysis: {src} <-> {tgt}. Key mapping: {mapping}. Framework: Gentner's structure-mapping, Holyoak's pragmatic reasoning, or Hofstadter's fluid concepts. Analogy is productive -- generates useful inferences, explanatory -- makes target comprehensible, or predictive -- suggests testable hypotheses.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,7), pick("reasoning","analogy","science"))

COUNTERFACTUALS = [
    ("Archduke Franz Ferdinand had not been assassinated in 1914","World War I","history"),
    ("the internet had been invented in the 1950s","global information access","technology"),
    ("humans had a natural lifespan of 200 years","career and family structure","society"),
    ("photosynthesis operated at 50% efficiency","global ecosystems and agriculture","biology"),
    ("the combustion engine had never been developed","urban design and climate","engineering"),
    ("Python dominated in 1990 instead of the 2000s","software development","computing"),
    ("the Library of Alexandria had never been destroyed","scientific progress","history"),
    ("dinosaurs had not gone extinct","mammalian evolution","biology"),
    ("language had not evolved in humans","culture and cooperation","anthropology"),
    ("Earth had 40 percent less gravity","architecture, biology, atmosphere","physics"),
    ("printing press invented in ancient Rome","literacy and reformation","history"),
    ("humans could photosynthesize","diet, society, urban planning","biology"),
]

def _counterfactual_gen():
    while True:
        for change, implication, domain in COUNTERFACTUALS:
            inp = pick(f"Counterfactual: What if {change}? How would {implication} change?", f"In a world where {change}, what would be different about {implication}?", f"If {change}, trace the downstream effects on {implication}.", f"Suppose {change}. Analyze consequences for {implication}.")
            plan = pick(f"<PLAN>Counterfactual reasoning: (1) Establish actual baseline. (2) Introduce change: {change}. (3) Propagate effects through causal dependencies, ceteris paribus. (4) Identify minimal changes for consistency. (5) Trace consequences to {implication}.</PLAN>", f"<PLAN>Using causal model approach: define relevant variables, modify the variable for {change}, compute new equilibrium, compare to actual world. Focus on {implication}. Use mental simulation, causal Bayesian network, structural equations model, or possible worlds semantics.</PLAN>")
            think = pick(f"<THINK>Counterfactual: {change}. In the actual world, {implication} was shaped by multiple factors. I hold most variables fixed and change only the antecedent. This is challenging because {change} cascades. The minimal-rewrite principle: change as little as possible while maintaining consistency. The closest possible world differs minimally from actuality while making the antecedent true. For {implication}, some aspects remain robust; others transform completely. The key question: which dependencies are necessary vs contingent?</THINK>", f"<THINK>Analyzing: what if {change}? Possible worlds framework -- closest possible world where {change} holds. Some causal chains preserved from actuality; others diverge. Degree of divergence increases with temporal distance from the change point. Some aspects of {implication} robust across possible worlds. I trace: in actual world, {implication} depended on factors A, B, C. In counterfactual world, {change} alters A. B and C may or may not be affected depending on causal dependence on A.</THINK>")
            exec_ = pick(f"<EXEC>Counterfactual: If {change}. Effect on {implication}: Complete transformation, partial change -- some aspects remain, minimal difference -- robust to change, or nonlinear -- small change large consequence. Most significant: removal of existing constraints, introduction of new possibilities, rerouting of causal pathways, or shift in equilibrium. Robustness: low -- sensitive to conditions, moderate -- some patterns persist, or high -- structural factors dominate.</EXEC>", f"<EXEC>Counterfactual analysis complete. Antecedent: {change}. Domain: {implication}. Method: causal model simulation, minimal-rewrite possible worlds, or structural equation counterfactuals. Insight: reveals which aspects are contingent vs necessary; some features overdetermined and persist; divergence amplifies over time; change fundamentally alters domain.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("reasoning","counterfactuals","philosophy"))

LATERAL_PUZZLES = [
    ("A man walks into a bar and asks for water. The bartender points a gun at him. The man says thank you and leaves.","The man had hiccups; the scare cured them."),
    ("A dead man is found in a field with an unopened package.","Parachute failed to open; the package is his parachute."),
    ("A girl sits in a room. Lights go out and she cries. They come back on and she smiles.","She was playing hide-and-seek and was found."),
    ("A man pushes his car to a hotel and tells the owner he is bankrupt.","He was playing Monopoly."),
    ("What has a head, a tail, is brown, and has no legs?","A penny."),
    ("Brothers and sisters I have none, but that man's father is my father's son.","The photo is of his son."),
    ("If a rooster lays an egg on top of a barn, which way does it roll?","Roosters don't lay eggs."),
    ("A man is found dead in a room with a puddle of water and broken glass.","He was a fish whose bowl was knocked over."),
    ("Two people born at same moment but have different birthdays.","Born on a plane crossing International Date Line."),
]

def _lateral_gen():
    while True:
        for setup, answer in LATERAL_PUZZLES:
            inp = pick(f"Lateral thinking: {setup}", f"Think outside the box: {setup}", f"Solve this puzzle: {setup}")
            plan = pick(f"<PLAN>Lateral thinking: (1) Identify assumptions. (2) Challenge each assumption. (3) Consider alternative interpretations. (4) Look for hidden context. The setup contains deliberate ambiguity, a false presumption, an unusual context switch, or a double meaning.</PLAN>", f"<PLAN>To solve: avoid fixation on obvious interpretation. Find the unstated context, alternative meaning, hidden entity, or reframing. List all interpretations and check which makes the scenario coherent.</PLAN>")
            think = pick(f"<THINK>Puzzle: {setup}. Initially paradoxical. The key is identifying assumptions. I assume words have usual meanings, context is normal, all facts stated. Challenge each: what if a word has unusual meaning, context is metaphorical, an entity is unstated, or a missing detail resolves contradiction? The solution involves a perspective shift. The pattern -- {answer.split('.')[0]} -- suggests one overlooked possibility.</THINK>", f"<THINK>Analyzing: {setup}. This rewards reframing, not deduction. The contradiction signals wrong frame. Consider: multiple word meanings? unusual context? omitted entity? Frame-shifts make puzzles work; sometimes the simplest explanation is overlooked. Try each reframing until story becomes consistent.</THINK>")
            exec_ = pick(f"<EXEC>Solution: {answer}. Insight: challenging assumption of literal meaning, recognizing unusual context, identifying hidden entity, or reframing the premise. This demonstrates breaking functional fixedness, avoiding premature closure, considering alternative frames, or questioning implicit assumptions.</EXEC>", f"<EXEC>Resolved: {answer}. Key: broke the assumption that words have primary meaning, scene is realistic, no context-switch occurred, or scenario is self-contained. Insight obvious once frame shifts but invisible in original frame. Demonstrates cognitive flexibility, assumption awareness, divergent thinking, or perspective-shifting.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("reasoning","lateral_thinking","puzzles"))

SYSTEMS_LIST = [
    ("urban traffic","adding more roads","induced demand, Braess's paradox"),
    ("corporate supply chain","centralizing inventory","bullwhip effect, oscillation"),
    ("lake ecosystem","introducing a new species","trophic cascade, regime shift"),
    ("cloud resource pools","auto-scaling policies","oscillation, thrashing, hysteresis"),
    ("healthcare system","increasing funding","cost disease, capacity constraints"),
    ("social media","algorithmic content curation","echo chambers, polarization feedback"),
    ("renewable energy grid","increasing solar penetration","duck curve, storage requirements"),
    ("housing market","rent control policies","supply reduction, market bifurcation"),
    ("financial market","algorithmic trading","flash crashes, liquidity feedback"),
    ("forest fire management","suppressing all small fires","fuel buildup, megafire risk"),
    ("fishery with quotas","individual transferable quotas","race-to-fish, quota consolidation"),
]

def _systems_gen():
    while True:
        for system, intervention, dynamics in SYSTEMS_LIST:
            inp = pick(f"Systems thinking: What happens when {intervention} in {system}? Consider feedback loops and emergent effects.", f"Apply systems thinking to {system}. Trace effects of {intervention} through feedback structures.", f"Systems analysis: In {system}, introduce {intervention}. What dynamics unfold? Consider {dynamics}.", f"Think systemically about {system}. If {intervention}, what are second and third-order effects?")
            plan = pick(f"<PLAN>Systems thinking tools: (1) Causal loop diagram identifying key variables. (2) Classify feedback as reinforcing (R) or balancing (B). (3) Identify delays. (4) Find leverage points and unintended consequences. {dynamics} suggests specific feedback structures at play.</PLAN>", f"<PLAN>Map stock-and-flow structure. Identify feedback loops governing behavior. Introduce {intervention} as flow change. Simulate dynamic behavior. Watch for: (1) balancing feedback resisting change; (2) reinforcing feedback amplifying it; (3) delays causing oscillation; (4) shifting loop dominance as system responds.</PLAN>")
            think = pick(f"<THINK>Modeling {system}: key stocks are infrastructure, population, capital, resources, agents, information, capacity, demand, inventory, biomass, nutrients, or predators. Intervention {intervention} perturbs the system. First-order: direct impact. Second-order: responses that feed back to amplify or dampen. {dynamics} describes emergent pattern. Key insight: in complex systems, {intervention} often produces counterintuitive results due to feedback. The system's behavior is determined by its structure, not just the intervention.</THINK>", f"<THINK>Systems analysis of {system} with {intervention}. Causal loop diagram reveals: R1: growth loop, B1: constraint loop, B2: depletion, multiple balancing loops competing, dominant reinforcing leading to exponential change, or tightly coupled loops with delays. The {dynamics} pattern emerges from loop interactions. {intervention} may trigger shifting loop dominance -- previously latent feedback becomes active. The fix-that-fails archetype: intervention creates side effects that undermine it.</THINK>")
            exec_ = pick(f"<EXEC>Systems analysis: {system} with {intervention}. Feedback: Reinforcing dominates leading to amplification, Balancing resists leading to homeostasis, Loop shifts leading to S-curve, or Interlocking leading to dynamic equilibrium. {dynamics} observed. Unintended consequences: displacement to other parts, behavioral adaptation undermines it, long-term resilience degradation, or oscillation around target. Recommendation: leverage reinforcing loops, shorten delays, address feedback structures, or focus on structure not events.</EXEC>", f"<EXEC>Systems analysis complete. Intervention: {intervention} in {system}. Archetype: limits to growth, shifting the burden, tragedy of the commons, success to the successful, or fixes that fail. Policy: work with feedback, identify high-leverage points, consider time delays in policy, or monitor for loop shifts.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("reasoning","systems_thinking","complexity"))

DEDUCTIVE_PREMISES = [
    ("All mammals are warm-blooded. Whales are mammals.","Whales are warm-blooded.","biology"),
    ("If it rains, the ground gets wet. The ground is not wet.","It did not rain.","logic"),
    ("All squares are rectangles. All rectangles have four sides.","Squares have four sides.","geometry"),
    ("All A are B. All B are C.","All A are C.","logic"),
    ("No reptiles have fur. All mammals have fur.","No reptiles are mammals.","biology"),
    ("All birds have feathers. Penguins are birds.","Penguins have feathers.","biology"),
    ("If a triangle has three equal sides, it is equilateral. This triangle is equilateral.","It has three equal sides.","geometry"),
    ("All humans are mortal. Socrates is human.","Socrates is mortal.","philosophy"),
]

def _deductive_gen():
    while True:
        for premises, conclusion, domain in DEDUCTIVE_PREMISES:
            inp = pick(f"Given: {premises} What necessarily follows?", f"Apply deduction: {premises} What conclusion is entailed?", f"From '{premises}' deduce the necessary conclusion.", f"Logical deduction: {premises} Therefore?")
            plan = pick(f"<PLAN>Deductive reasoning: (1) Identify logical form. (2) Apply inference rule (modus ponens, modus tollens, syllogism). (3) Derive necessary conclusion. The premises are categorical, conditional, relational, or propositional.</PLAN>", f"<PLAN>Parse premises into formal logic. Identify inference pattern. Apply rules: modus ponens if P implies Q and P then Q; modus tollens if P implies Q and not Q then not P; hypothetical syllogism if P implies Q and Q implies R then P implies R; universal instantiation: all X are Y, a is X, therefore a is Y. Check validity.</PLAN>")
            think = pick(f"<THINK>Premises: {premises}. Logical form: categorical (Aristotelian), propositional (Stoic), predicate (Fregean), or relational. Applying inference rule: the conclusion follows necessarily -- valid. Syllogism in Barbara form, Modus ponens applies, Hypothetical syllogism, or Universal instantiation. If premises true, conclusion guaranteed. Conclusion: {conclusion}.</THINK>", f"<THINK>Analyzing: {premises}. Logical form: Categorical: major, minor, conclusion; Conditional: if P then Q, P, therefore Q; Disjunctive: P or Q, not P, therefore Q; or Relational: transitive inference. Inference rule correctly applied -- valid. Deductive arguments guarantee their conclusion if valid and sound. Necessary conclusion: {conclusion}.</THINK>")
            exec_ = pick(f"<EXEC>Deduction: {premises}. Rule: modus ponens, modus tollens, hypothetical syllogism, universal instantiation, or categorical syllogism. Conclusion: {conclusion}. Valid. Sound if premises true. Truth-preserving by construction.</EXEC>", f"<EXEC>Deductive result. Form: propositional, categorical, relational, or predicate logic. Conclusion: {conclusion}. Valid: Yes. Soundness depends on factual truth.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("reasoning","logic","mathematics"))

INDUCTIVE_PATTERNS = [
    ("swan1 white, swan2 white, ..., swan100 white","All swans are white."),
    ("1+1=2, 2+1=3, 3+1=4, 4+1=5","n+1 = successor of n."),
    ("sun rose today, yesterday, every recorded day","The sun will rise tomorrow."),
    ("copper conducts, silver conducts, gold conducts, iron conducts","All metals conduct electricity."),
    ("water boils at 100 degrees C at sea level (many trials)","Water boils at 100 degrees C at sea level."),
    ("every even number greater than 2 is sum of two primes (tested to 4x10^18)","Goldbach's conjecture may be true."),
    ("patient recovered with antibiotic A (20 cases), without A (0/20)","Antibiotic A cures this infection."),
    ("countries with more ice cream sales have more drownings","Correlation, not causation -- confounding by weather."),
]

def _inductive_gen():
    while True:
        for observations, generalization in INDUCTIVE_PATTERNS:
            inp = pick(f"From: {observations}. What inductive generalization? How confident?", f"Inductive reasoning: {observations}. Formulate a general rule.", f"Given: {observations}. What pattern or principle does this suggest?", f"Based on {observations}, infer a general principle. Evaluate strength.")
            plan = pick(f"<PLAN>Inductive reasoning: (1) Identify pattern in observed instances. (2) Formulate generalization. (3) Consider variety and number of instances. (4) Assess inductive strength. (5) Identify potential counterexamples. Key: sample size, representativeness, uniformity of nature assumption.</PLAN>", f"<PLAN>To induce: catalog instances, look for invariant patterns. Generalization: {generalization}. Evaluate: (1) How many observations? (2) How varied? (3) Negative instances? (4) Coherence with theory? Inductive strength depends on quality and quantity of evidence.</PLAN>")
            think = pick(f"<THINK>Observations: {observations}. Pattern suggests: {generalization}. Inductive inference -- particular to general. Strength: (1) Number is large, small, or sufficient; (2) Variety -- wide variation strengthens, narrow conditions weaken, diverse sampling helps; (3) Counterexamples -- none observed but absence does not guarantee truth. Hume's problem: induction isn't logically justified but is practically necessary. Confidence: high, moderate, or tentative.</THINK>", f"<THINK>Induction from: {observations}. Pattern: {generalization}. Form: all observed X are Y, therefore all X are Y. Strength: strong -- large, varied, no counterexamples; moderate -- large but maybe not representative; weak -- few observations; anecdotal -- insufficient. Uniformity of nature underlies inference. Practical: {generalization} is well-supported, useful heuristic, needs investigation, or likely true with caveats.</THINK>")
            exec_ = pick(f"<EXEC>Inductive analysis. Observed: {observations}. Generalized: {generalization}. Strength: Strong -- high diversity and size, Moderate -- consistent but limited, or Weak -- few data points. Limitations: induction cannot guarantee truth, future counterexamples possible, black swan problem, confirmation bias may inflate. Recommendation: act with caution, seek disconfirming evidence, treat as statistical regularity.</EXEC>", f"<EXEC>Induction: {generalization} from {observations}. Confidence: high, medium, low, or speculative. Number and diversity support it, limited sample -- working hypothesis, or consistent with established theory. Inductive conclusions always revisable.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("reasoning","science","statistics"))

SYLLOGISMS = [
    ("All philosophers are thinkers. Some thinkers are logicians.","Some philosophers may be logicians (no necessary conclusion)"),
    ("No cats are dogs. All poodles are dogs.","No poodles are cats."),
    ("All A are B. Some A are C.","Some B are C."),
    ("All birds can fly. Penguins are birds.","Penguins can fly (false premise, valid form)"),
    ("All mammals are vertebrates. Whales are mammals.","Whales are vertebrates."),
    ("Some politicians are honest. No honest person cheats.","Some politicians do not cheat."),
    ("All fruits have seeds. Tomatoes are fruits.","Tomatoes have seeds."),
    ("All planets orbit stars. Pluto is a planet.","Pluto orbits a star (definition-dependent)."),
]

def _syllogistic_gen():
    while True:
        for premises, conclusion in SYLLOGISMS:
            inp = pick(f"Syllogistic reasoning: {premises} What necessarily follows?", f"Analyze this syllogism: {premises} Valid conclusion?", f"Given {premises} Apply Aristotelian logic to determine conclusion.", f"Logical syllogism: {premises} Is '{conclusion}' validly entailed?")
            plan = pick(f"<PLAN>Syllogistic analysis: (1) Identify three terms (major, minor, middle). (2) Determine mood and figure. (3) Check validity rules: middle distributed, no illicit major/minor. (4) State valid conclusion or explain invalidity.</PLAN>", f"<PLAN>Evaluate using classical rules. Valid syllogism: exactly three terms; each appears twice; middle distributed at least once; term distributed in conclusion must be in premises; no conclusion from two negatives. Apply to: {premises}.</PLAN>")
            think = pick(f"<THINK>Evaluating: {premises}. Identify terms. Major: predicate of conclusion. Minor: subject. Middle: appears in both premises. Check distribution: universal statements distribute subject; particular do not; negative statements distribute predicate. Applying rules: valid -- conclusion necessarily follows, invalid -- rule violation, valid but unsound -- false premise, or no valid conclusion follows. Conclusion: {conclusion}.</THINK>", f"<THINK>Syllogistic logic: {premises}. Mood/figure: AAA-1 (Barbara), EAE-2 (Cesare), AII-3 (Datisi), or EIO-4 (Fresison). Middle term distributed in first premise, not distributed -- may cause invalidity, or distributed in both. Conclusion: valid, invalid -- illicit major/minor, invalid -- existential fallacy, or invalid -- two negatives. Assessment: {conclusion}.</THINK>")
            exec_ = pick(f"<EXEC>Syllogism: {premises}. Mood/figure: AAA-1, EAE-2, AII-3, EIO-4, or invalid. Valid: Yes or No. Conclusion: {conclusion}. Sound if premises true. Valid but unsound. Invalid -- no necessary conclusion.</EXEC>", f"<EXEC>Syllogistic analysis. Form: categorical, hypothetical, disjunctive, or enthymeme. Conclusion: {conclusion}. Valid: Yes, No, or Conditionally. Term distribution confirms validity or commits fallacy.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("reasoning","logic","philosophy"))

TEMPORAL_SCENARIOS = [
    ("A before B. B before C. D after C but before E.","A before E.","ordering"),
    ("Alice born 1990. Bob born 1985. Carol same year as Bob.","Alice younger than Bob and Carol.","age"),
    ("Treaty signed after battle but before election. King died during battle.","King died before election.","history"),
    ("Layer A below B. B below C. D cuts across all.","D is youngest.","geology"),
    ("Species X in period 1. Y in period 2. Z in period 3 after Y disappears.","Z may have replaced Y ecologically.","paleontology"),
    ("P starts t=10. Q starts t=5 runs 10. R starts t=3 runs 4.","P and R overlap; Q may overlap partially.","computing"),
]

def _temporal_gen():
    while True:
        for facts, conclusion, domain in TEMPORAL_SCENARIOS:
            inp = pick(f"Temporal reasoning: {facts} What temporal relationships can you establish?", f"From: {facts} Determine the relative ordering and draw conclusions.", f"Given: {facts} What must be true about the temporal relationships?")
            plan = pick(f"<PLAN>Temporal reasoning: (1) Represent events as points/intervals. (2) Encode relations using Allen's interval algebra. (3) Apply transitivity rules. (4) Derive implicit relations. (5) Determine necessary conclusions.</PLAN>", f"<PLAN>Extract explicit before/after/during relations. Build directed precedence graph. Propagate constraints transitively. Check consistency -- no cycles. Derive implied relationships.</PLAN>")
            think = pick(f"<THINK>Temporal facts: {facts}. Using Allen's relations: before, after, meets, overlaps, during, finishes. From given: a partial order emerges, chain from earliest to latest, branching with concurrent events, or some relations indeterminate. Transitivity: if X before Y and Y before Z, then X before Z. Key conclusion: {conclusion}. Some relations remain unknown -- temporal information often underdetermines complete ordering.</THINK>", f"<THINK>Temporal analysis: {facts}. Events as intervals with start/end. Relations: linear total order, partial order with branches, complex overlapping, or nested during-relations. Constraint propagation: fully determined, multiple consistent orderings, contradictory (cycle), or N distinct time points. Conclusion: {conclusion}. Transitivity is the key inference rule.</THINK>")
            exec_ = pick(f"<EXEC>Temporal analysis. Facts: {facts}. Ordering: {conclusion}. Method: Allen interval algebra, point algebra, temporal constraint propagation, or event calculus. Consistency: consistent, contradictory, or underdetermined. Transitive closure applied. Interval relations computed.</EXEC>", f"<EXEC>Temporal reasoning. Input: {facts}. Derived: {conclusion}. Transitive closure applied. Interval algebra solved. Constraint graph propagated. Ordering: fully determined, partially ordered, or consistent but incomplete.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("reasoning","logic","temporal"))

SPATIAL_SCENARIOS = [
    ("A left of B. B left of C. D above A.","D above and left of C.","layout"),
    ("Red house north of blue. Blue east of green. Yellow south of red.","Yellow south of red; others relative.","navigation"),
    ("X inside Y. Y on surface Z. W outside Y but on Z.","X inside Y on Z; W on Z outside Y.","containment"),
    ("P at (0,0). Q at (3,4). R at (6,8).","P, Q, R collinear on y=(4/3)x.","geometry"),
    ("A overlaps B. B overlaps C. A does not overlap C.","Overlap is not transitive.","topology"),
    ("Library between school and hospital. Park across from library.","Park not between school and hospital.","urban"),
]

def _spatial_gen():
    while True:
        for facts, conclusion, domain in SPATIAL_SCENARIOS:
            inp = pick(f"Spatial reasoning: {facts} What spatial relationships can you deduce?", f"Given: {facts} Determine relative positions.", f"Reason about spatial arrangement: {facts} Is '{conclusion}' correct?")
            plan = pick(f"<PLAN>Spatial reasoning: (1) Represent objects as points/regions. (2) Encode relations (left/right, above/below, inside/outside, between). (3) Apply spatial inference rules. (4) Derive implicit relationships. Use coordinate model or qualitative spatial reasoning.</PLAN>", f"<PLAN>Establish spatial frame of reference. Assign coordinates or relative positions. Use transitivity of spatial relations. Check consistency. Derive unknown relations using composition tables.</PLAN>")
            think = pick(f"<THINK>Spatial facts: {facts}. Mental model construction. Qualitative spatial reasoning: left-of, above, inside, between composable. Some transitive (left-of, above); some not (near, next-to). Topological relations (inside, touching, disjoint) have different rules. From facts: consistent arrangement constructed, ambiguous -- multiple satisfy, implied relations exist, or some indeterminate. Conclusion: {conclusion}.</THINK>", f"<THINK>Spatial analysis. Facts: {facts}. Using coordinate representation, qualitative relation graph, region connection calculus, or mental image. Composition: left-of transitive leads to chain, above/below plus left/right equals 2D, containment hierarchical, betweenness constrains order. Derived: {conclusion}. All facts consistent, multiple valid arrangements, conclusion necessarily follows, or ambiguity about distances.</THINK>")
            exec_ = pick(f"<EXEC>Spatial result. Facts: {facts}. Conclusion: {conclusion}. Method: qualitative spatial reasoning, coordinate geometry, region connection calculus, or mental model. Consistency: consistent, ambiguous, or fully determined. Transitive composition applied. Coordinate mapping validated.</EXEC>", f"<EXEC>Spatial analysis complete. Input: {facts}. Derived: {conclusion}. Framework: QSR, 9-intersection model, 2D coordinate geometry, or mereotopology. Configuration: fully determined, partially constrained, or underdetermined.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("reasoning","spatial","geometry"))

def chunk_1_gen():
    gens = [_causal_gen(), _abduction_gen(), _csp_gen(), _analogy_gen(), _counterfactual_gen(),
            _lateral_gen(), _systems_gen(), _deductive_gen(), _inductive_gen(),
            _syllogistic_gen(), _temporal_gen(), _spatial_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════ Chunk 2: Metacognition & Self-Awareness ═══════════════════════
# 10 categories: confidence, boundaries, revision, uncertainty, self-correction, bias, knowledge-gaps, strategy, cognitive-load, error-analysis

CONFIDENCE_TASKS = [
    ("estimated Nigeria's population","demographics","~220 million"),
    ("determined ethanol's boiling point","chemistry","78.37 degrees C at sea level"),
    ("calculated area of circle radius 5","geometry","pi times 25 approx 78.54"),
    ("predicted tomorrow's weather","meteorology","70 percent rain chance based on satellite data"),
    ("identified author of 1984","literature","George Orwell"),
    ("solved dy/dx = 2x","mathematics","y = x squared + C"),
    ("diagnosed patient with chest pain","medicine","differential: MI, angina, GERD, anxiety"),
    ("translated 'Je ne sais quoi'","linguistics","I don't know what"),
    ("predicted stock movement","finance","technical indicators suggest bullish"),
    ("classified image containing cat","computer vision","CNN: 92 percent cat, 5 percent dog, 3 percent other"),
]

def _confidence_gen():
    while True:
        for task, domain, answer in CONFIDENCE_TASKS:
            inp = pick(f"You {task}. On a scale of 1-10, how confident in your answer? Explain.", f"Self-assessment: You {task}. What is your confidence and why?", f"Metacognitive evaluation: After {task}, assess your confidence. What uncertainties remain?", f"Calibration: You {task}. How sure are you? What would increase your confidence?")
            plan = pick(f"<PLAN>Confidence assessment: (1) Recall knowledge state. (2) Sources of certainty: direct knowledge, verified facts. (3) Sources of uncertainty: incomplete info, conflicting sources, inherent randomness. (4) Calibrate: high when verified, moderate when sound inference, low when guessing. (5) Consider what evidence would change confidence.</PLAN>", f"<PLAN>Assess confidence for {task}: distinguish direct knowledge vs inference. Direct: verified facts. Inferred: conclusions from premises. Each indirection reduces confidence. Consider domain difficulty, base rates, track record. Calibrate with explicit justification.</PLAN>")
            think = pick(f"<THINK>Task: {task}. Answer: {answer}. Confidence assessment: this is a well-established fact, a standard calculation with unique correct answer, a prediction with inherent uncertainty, or an interpretation with multiple valid approaches. Sources of uncertainty: memory may be imprecise, domain involves probabilities, multiple valid approaches, knowledge may be outdated, or estimation with limited data. Calibrated confidence: X out of 10 because verified fact, sound inference, moderate confidence, mostly guessing, or essentially uncertain. To increase: verify against source, get more data, consult expert, or cross-validate. Checking for overconfidence bias.</THINK>", f"<THINK>Self-evaluation for: {task}. Answer: {answer}. Accuracy: highly confident -- verified, best inference but alternatives possible, or uncertain -- estimation/prediction. Calibration: at this confidence level, accuracy is well-calibrated, slightly overconfident, or poor calibration. Knowledge sources: direct learning, first principles, analogical inference, statistical estimation, or heuristic. Reliability varies. Confidence: X out of 10 because verified fact, reasonable alternatives, domain randomness, or knowledge gaps.</THINK>")
            exec_ = pick(f"<EXEC>Confidence for '{task}'. Answer: {answer}. Confidence: X/10. Rationale: direct factual knowledge, sound inference, estimation with partial info, or speculative. Calibration: well-calibrated, slightly overconfident, or appropriately cautious. Improve: verify externally, gather more data, consult expert, or use ensemble.</EXEC>", f"<EXEC>Self-assessment: {task}. Confidence: X/10. Factors: well-established fact, consistent sources, logically derived, estimation, inherent randomness, or conflicting info. Overall: well-calibrated, slightly overconfident, or appropriately cautious.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("metacognition","self_awareness","confidence"))

BOUNDARY_TOPICS = [
    "the exact number of neurons in a brain",
    "what happens inside a black hole's event horizon",
    "whether P = NP in complexity theory",
    "the precise mechanism of consciousness",
    "what existed before the Big Bang",
    "the complete function of non-coding DNA",
    "whether extraterrestrial life exists",
    "the ultimate fate of the universe",
    "the exact nature of dark matter",
    "how life originally emerged",
    "mathematical truths independent of ZFC",
    "the precise location of every atom (Heisenberg)",
    "what lies beyond the observable universe",
    "the origin of the genetic code",
]

def _boundaries_gen():
    while True:
        for topic in BOUNDARY_TOPICS:
            inp = pick(f"What are the limits of our knowledge about {topic}? Known vs unknown vs unknowable?", f"Epistemic analysis: {topic}. Map the known, unknown, and unknowable.", f"Knowledge boundaries: {topic}. What is settled, debated, and permanently inaccessible?", f"Analyze the knowledge frontier for {topic}. Known knowns, known unknowns, unknown unknowns.")
            plan = pick(f"<PLAN>Knowledge boundary analysis: (1) Current knowledge -- what's empirically established? (2) Known unknowns -- open but answerable questions. (3) Potential unknowability -- permanently inaccessible due to fundamental limits. (4) How boundary might shift with new methods/theories.</PLAN>", f"<PLAN>Map using Rumsfeld's matrix. Consider: (1) Practical limits -- insufficient data; (2) Theoretical limits -- physics/math prevents; (3) Fundamental limits -- ill-posed concept. Classify aspects of {topic}.</PLAN>")
            think = pick(f"<THINK>Topic: {topic}. Current status: well-understood in paradigm, partially understood with gaps, poorly understood -- speculative, at research frontier, or beyond current comprehension. Known facts: principles established details debated, data exists interpretation contested, theory robust empirics lacking, or competing theories. Known unknowns: do not know mechanism, parameter uncertainty, causal relations unclear, resolution too coarse, or formalization incomplete. Potentially unknowable: observational horizon, computational intractability, quantum limits, ill-posed question, or self-reference paradoxes. Boundary shaped by empirical constraints, theoretical limits, computational feasibility, conceptual clarity, or technological capability. Progress from new instruments, new math, interdisciplinary approaches, or paradigm shifts.</THINK>", f"<THINK>Epistemic analysis: {topic}. Known knowns: basic taxonomy, some mechanisms, correlations, or theoretical framework. Known unknowns: causal mechanisms, quantitative precision, boundary conditions, or generalizability. Unknown unknowns: by definition unspecifiable, history suggests surprises, or emergence may challenge frameworks. Fundamental limits: empirically inaccessible, mathematically undecidable, observer effect, or beyond cognitive capacity. Boundary shifts with scientific progress, technological innovation, theoretical unification, or conceptual clarification.</THINK>")
            exec_ = pick(f"<EXEC>Knowledge boundaries for '{topic}'. Known: core facts, basic mechanisms, observational constraints, or mathematical formalization. Unknown: mechanism gaps, parameter uncertainty, scope limits, or boundary conditions. Unknowable: horizons, intractability, indeterminacy, or ill-posedness. Frontier: advancing rapidly, slow progress, stalled needs breakthrough, or at fundamental limits.</EXEC>", f"<EXEC>Boundary analysis: {topic}. Status: well-mapped with clear frontiers, partially explored, mostly unknown, or contested multiple frameworks. Certainty gradient: higher at center, decreasing to frontier, zero beyond. Boundary shape: expanding, stable, contested, or fuzzy.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("metacognition","epistemology","philosophy"))

REVISION_SCENARIOS = [
    ("thought Earth was flat, then saw ships disappear hull-first over horizon","Earth is spherical"),
    ("believed tomatoes were vegetables, then learned botanical classification","Tomatoes are fruits botanically"),
    ("thought Pluto was a planet, then IAU 2006 definition","Pluto is a dwarf planet"),
    ("assumed heavier objects fall faster, then Galileo's experiment","All objects fall at same rate in vacuum"),
    ("believed Sun revolved around Earth","Earth revolves around Sun (heliocentric)"),
    ("thought all bacteria harmful, then learned about microbiome","Most bacteria harmless or beneficial"),
    ("believed a solution correct, then found counterexample","Fails for edge cases -- needs revision"),
    ("assumed correlation implies causation","Correlation does not equal causation -- confounders exist"),
    ("thought memory is like video recording","Memory is reconstructive and fallible"),
    ("believed IQ is fixed","Intelligence is malleable through learning"),
]

def _revision_gen():
    while True:
        for old_belief, new_understanding in REVISION_SCENARIOS:
            inp = pick(f"You previously {old_belief}. Now: {new_understanding}. Walk through belief revision.", f"Belief revision: You once {old_belief}. New evidence: {new_understanding}. How do you update?", f"Revise understanding: From '{old_belief}' to '{new_understanding}'. Explain the process.", f"Cognitive revision: '{old_belief}' -> '{new_understanding}'. What triggers revision?")
            plan = pick(f"<PLAN>Belief revision: (1) Original belief. (2) Disconfirming evidence. (3) Evaluate evidence reliability. (4) Check for cognitive dissonance. (5) Determine if revision warranted. (6) Update belief and integrate. (7) Consider ripple effects on related beliefs.</PLAN>", f"<PLAN>Old belief based on incomplete info, intuitive but wrong assumption, authoritative wrong source, or limited perspective. New understanding supported by direct observation, controlled experiments, convergent evidence, or comprehensive theory. Update mental model, ensure coherence with established knowledge.</PLAN>")
            think = pick(f"<THINK>Original: {old_belief}. Based on everyday experience, common sense, cultural transmission, or limited data. Confronted with: {new_understanding}. Cognitive dissonance -- old conflicts with new. Tempted to rationalize but must follow evidence; uncomfortable but necessary. Evaluating new evidence: robust and reproducible, explains more than old belief, has predictive power, or integrates with other knowledge. Revision: (1) notice anomaly; (2) doubt old belief; (3) explore alternatives; (4) adopt new belief; (5) restructure related beliefs. After revision, understanding is more accurate. Old belief was reasonable from limited info. Progress means updating with evidence.</THINK>", f"<THINK>Belief revision triggered: old model ({old_belief}) cannot accommodate new info ({new_understanding}). Steps: (1) Attention to anomaly -- contradicts predictions. (2) Evaluation -- reliable/valid evidence, robust pattern, requires framework change. (3) Resolution -- straightforward correction, paradigm shift, knowledge deepening, or reclassification. Revision warranted because evidence overwhelming, new framework has greater explanatory power, old belief based on false premise, or it reconciles anomalies. Update belief, noting factors leading to original error.</THINK>")
            exec_ = pick(f"<EXEC>Belief revision. Before: {old_belief}. After: {new_understanding}. Trigger: contradictory reliable evidence. Process: accommodation, assimilation, radical restructuring (paradigm shift), or differentiation. Lesson: intuition misleading -- seek validation, question authorities, common sense not always correct, or knowledge is self-correcting. New belief is more accurate, comprehensive, predictive, or coherent.</EXEC>", f"<EXEC>Revision executed: {old_belief} -> {new_understanding}. Type: empirical correction, theoretical deepening, reconceptualization, or error detection. Confidence in revised: high. Process demonstrates epistemic humility, evidence-based reasoning, cognitive flexibility, or scientific mindset.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("metacognition","epistemology","learning"))

UNCERTAINTY_TASKS = [
    ("predicting exact temperature in 7 days","meteorology"),
    ("estimating building height from shadow","geometry"),
    ("determining if coin fair after 10 flips","statistics"),
    ("diagnosing disease from 95 percent accurate test","medicine"),
    ("predicting championship winner","sports"),
    ("estimating software project completion","engineering"),
    ("determining historical document authenticity","history"),
    ("measuring distance to star via parallax","astronomy"),
    ("forecasting quarterly revenue","finance"),
    ("predicting election from polls","political science"),
]

def _uncertainty_gen():
    while True:
        for task, domain in UNCERTAINTY_TASKS:
            inp = pick(f"Quantify uncertainty in {task}. Identify sources and their magnitudes.", f"Uncertainty analysis: {task}. What are the sources? Characterize overall uncertainty.", f"Probabilistic reasoning: {task}. Express prediction as a distribution and justify.", f"Decompose uncertainty in {task}: aleatory (irreducible) vs epistemic (reducible).")
            plan = pick(f"<PLAN>Uncertainty quantification: (1) Identify prediction task. (2) List sources: measurement error, model uncertainty, inherent randomness, parameter uncertainty. (3) Classify each as aleatory or epistemic. (4) Estimate magnitude per source. (5) Combine using error propagation, Monte Carlo, or Bayesian updating. (6) Express with confidence intervals or distributions.</PLAN>", f"<PLAN>Decompose {task} into components. For each: known precisely? estimated with error? truly random? Build uncertainty budget. Use Taylor series propagation, Monte Carlo, Bayesian credible intervals, bootstrapping, or expert elicitation to combine.</PLAN>")
            think = pick(f"<THINK>Task: {task}. Domain: {domain}. Sources: measurement error -- finite instrument precision, model uncertainty -- incomplete theory, parameter uncertainty -- estimated inputs, inherent stochasticity -- random components, or human factors -- irreducible variability. Aleatory vs epistemic: aleatory dominates -- fundamentally stochastic, epistemic dominates -- more data would reduce, both significant, or epistemic reducible through better measurement. Magnitude: low -- well-understood with good data, moderate -- reasonable models incomplete data, high -- complex limited understanding, or very high -- chaotic or poorly understood.</THINK>", f"<THINK>Analyzing uncertainty for {task}. Prediction horizon matters: near-term less uncertain, long-range amplifies initial error, horizon depends on characteristic timescales, or chaotic beyond certain horizon. Sources ranked: data quality, model, parameters, shocks; randomness, measurement, simplification; or unknown unknowns, parameters, implementation. Epistemic reducible by: more data, better models. Aleatory managed by robustness. For {task}, aleatory, epistemic, or both dominates. Approach: gather data, use robust methods, Bayesian updating, or communicate transparently.</THINK>")
            exec_ = pick(f"<EXEC>Uncertainty analysis: {task}. Sources: measurement, model, parameter, randomness; precision, approximation, estimation, variation; or noise, structural, parametric, stochastic. Mostly aleatory, mostly epistemic, or mixed. Magnitude: low plus/minus 5 percent, moderate plus/minus 15-25 percent, high plus/minus 50 percent or more, or qualitative only. Expression: point estimate plus CI, probability distribution, prediction interval, or scenario ranges.</EXEC>", f"<EXEC>UQ complete: {task}. Budget: Source A X percent, Source B Y percent; Dominant: model or parameters; or evenly distributed. Aleatory: X percent. Epistemic: Y percent. Overall: well-characterized, moderately understood, or poorly characterized. Recommendation: reduce epistemic via data, robust strategies for aleatory, adaptive management, or communicate ranges.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("metacognition","uncertainty","statistics"))

SELF_CORRECTION = [
    ("SQL with GROUP BY missing non-aggregated columns","Add columns to GROUP BY or use ANY_VALUE"),
    ("argument concluding P because P (circular)","Identify circularity -- premise assumes conclusion"),
    ("RSA with p=17 q=11 e=7 -- wrong d","d = e^(-1) mod phi(n) = 23"),
    ("sorting algorithm only works for positive ints","Handle negatives with offset or comparison sort"),
    ("99 percent accuracy but 99:1 class imbalance","Report precision, recall, F1, AUC -- accuracy misleading"),
    ("proof that 1=2 by dividing by zero","Division by zero undefined -- invalid step"),
    ("code that reads file and never closes","Use 'with' statement for automatic resource management"),
    ("medical test 99 percent sensitivity, 1 percent prevalence","PPV = 50 percent -- most positives are false"),
]

def _self_correction_gen():
    while True:
        for flaw, correction in SELF_CORRECTION:
            inp = pick(f"Identify and correct: {flaw}. What's wrong and how to fix it?", f"Error detection: {flaw}. Find the mistake and explain the correction.", f"Debug: {flaw}. Trace to find the flaw and provide the fix.", f"Critical analysis: {flaw}. What went wrong? How should it be done?")
            plan = pick(f"<PLAN>Self-correction: (1) Identify what {flaw} aims to do. (2) Trace logic step by step. (3) Locate specific error. (4) Understand why it's wrong -- what principle is violated? (5) Formulate correct approach: {correction}. (6) Verify correction works.</PLAN>", f"<PLAN>Find the error: understand context of {flaw}. Expected correct behavior? Compare flawed vs correct. Pinpoint discrepancy. Error type: logical fallacy, mathematical mistake, algorithmic edge case, resource management issue, or statistical misinterpretation. Apply fix: {correction}. Generalize to avoid similar errors.</PLAN>")
            think = pick(f"<THINK>Analyzing: {flaw}. Intent: correct computation, proper resource handling, accurate reasoning, or efficient implementation. But there's an error. Tracing: step 1 ok step 2 wrong, initial premise ok inference invalid, approach sound edge case mishandled, or concept misapplied. Specific error: violation of rule, incorrect assumption, missing reasoning step, confusion between concepts, or boundary oversight. Because rule is X violated, counterexample exists, formal fallacy committed, or works for normal cases fails here. Correction: {correction}. Verify covers all cases. Lesson: double-check edges, be explicit about assumptions, test counterexamples, or follow correct patterns.</THINK>", f"<THINK>Error in: {flaw}. Expected: follow procedure X, produce Y under Z, satisfy constraints A B C, or respect rule D. Flaw: necessary condition unmet, step logically invalid, calculation incorrect, resource mismanaged, assumption violated, or edge case unhandled. Why error occurs: common misconception, subtle off-by-one, easy oversight, or deeper misunderstanding. Fix: {correction}. Works because addresses root cause, satisfies conditions, follows correct pattern, or handles normal plus error cases. After fix: add regression tests, document gotcha, or check for similar errors.</THINK>")
            exec_ = pick(f"<EXEC>Error: {flaw}. Root cause: rule violation, logical fallacy, mathematical error, edge case oversight, misapplied concept, resource leak, or misinterpretation. Fix: {correction}. Verification: resolves all test cases, satisfies all constraints, follows standard procedure, or edge cases handled. Lesson: check boundary conditions, explicit assumptions, verify counterexamples, or follow patterns.</EXEC>", f"<EXEC>Self-correction. Flawed: {flaw}. Fixed: {correction}. Category: logic, math, algorithm, resource management, statistics, or conceptual. Fix: direct correction, reformulation, added handling, or replacement of invalid step. Verified against gold standard, passes tests, satisfies criteria, or consistent with best practices.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("metacognition","self_correction","error_analysis"))

BIASES = [
    ("You strongly prefer solutions confirming your initial hypothesis","confirmation bias"),
    ("You overestimate ability to predict outcome after it's known","hindsight bias"),
    ("You think you're above-average in most skills","illusory superiority / Dunning-Kruger"),
    ("First information anchors subsequent estimates","anchoring bias"),
    ("Vivid examples get more weight than statistical data","availability heuristic"),
    ("You continue failing investment because already invested","sunk cost fallacy"),
    ("You search for info confirming existing beliefs","confirmation bias (active search)"),
    ("Success due to skill, failure due to external factors","self-serving bias"),
    ("You think others more biased than you","bias blind spot"),
    ("Prefer status quo, losses loom larger than gains","status quo bias / loss aversion"),
]

def _bias_gen():
    while True:
        for scenario, bias in BIASES:
            inp = pick(f"Identify the bias: {scenario} Which bias? How to mitigate?", f"Bias detection: {scenario} Illustrates which cognitive bias? Counteract?", f"Cognitive bias analysis: {scenario} What systematic error? Debiasing strategies?", f"Metacognitive bias: {scenario} Name the bias and debiasing approaches.")
            plan = pick(f"<PLAN>Bias analysis: (1) Identify pattern: {bias}. (2) Cognitive mechanism -- what heuristic produces it? (3) Recognize proneness conditions. (4) Apply debiasing: slow down, seek disconfirming evidence, checklists, alternative perspectives. (5) Evaluate impact on decision quality.</PLAN>", f"<PLAN>Analyze bias '{bias}': tendency to..., stems from heuristic of..., reflects motivated reasoning..., cognitive shortcut leading to error... Triggers: time pressure, emotional involvement, information overload, ambiguous evidence, or ego involvement. Apply tailored mitigation strategies.</PLAN>")
            think = pick(f"<THINK>Scenario: {scenario}. Bias: {bias}. This is a cognitive shortcut that fails in specific circumstances, motivated reasoning -- desires shape beliefs, faulty memory reconstruction, or social cognition -- self vs other asymmetry. Mechanism: brain shortcuts to conserve energy, process info to protect self-image, pattern matching that overdetects, or retrieval ease as probability proxy. Problem: systematically incorrect beliefs, poor decisions, overconfidence, wrong attributions, or resistance to updating. Debiasing: seek disconfirming evidence, consider opposite, engage System 2 thinking, use checklists and algorithms, calibrate against metrics, consider base rates, or pre-commit to criteria. Challenge: biases operate automatically. Awareness helps but structural interventions are more effective than willpower.</THINK>", f"<THINK>Detected: {bias} in '{scenario}'. This bias is well-documented systematic error, part of bias family, particularly self-reinforcing, or worse under stress/ambiguity. Mechanism: availability -- recalled examples judged more probable, confirmation -- prefer supporting evidence, anchoring -- initial value anchors adjustment, egocentric -- center own perspective, or loss aversion -- losses loom larger. Mitigation: slow analytic Type 2 processing, pre-mortem -- imagine failure, seek diverse perspectives, decision support tools, or environment design over willpower. Effective: checklists reduce omission bias, blinding reduces confirmation bias, base rates reduce availability bias, or pre-commitment reduces anchoring.</THINK>")
            exec_ = pick(f"<EXEC>Bias: {bias}. Scenario: {scenario}. Category: cognitive heuristic, motivated reasoning, social cognition, memory bias, or decision bias. Mechanism: mental shortcut, self-protection, pattern overdetection, fluency, or anchoring. Impact: reduced decision quality, distorted beliefs, overconfidence, or resistance to updating. Mitigation: seek disconfirming evidence, consider opposite, analytical thinking, checklists, calibrate metrics, or pre-commit criteria.</EXEC>", f"<EXEC>Bias analysis: {bias} in '{scenario}'. Type: heuristic-based, motivational, social, memory, or emotional. Debiasing: cognitive awareness plus correction, structural environment redesign, collaborative team checks, or procedural checklists. Effectiveness: moderate awareness helps, high structural changes powerful, limited deeply ingrained, or improves with practice.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("metacognition","cognitive_biases","psychology"))

GAPS = [
    "the chemical composition of Earth's lower mantle",
    "how consciousness arises from neural activity",
    "what causes accelerating expansion of the universe",
    "the complete human connectome",
    "how life originated from non-living matter",
    "quantum vs classical computing limits",
    "the full human proteome and functions",
    "mathematical truths beyond proof",
    "memory consolidation during sleep mechanisms",
    "how social norms emerge and stabilize",
]

def _knowledge_gap_gen():
    while True:
        for gap in GAPS:
            inp = pick(f"What is NOT yet known about {gap}? Why is this gap significant? How to fill it?", f"Knowledge gap: {gap}. What don't we know? What approaches might help?", f"Epistemic humility: {gap}. Open questions? What makes this hard to know?", f"Research frontier: {gap}. Current limits and promising paths forward.")
            plan = pick(f"<PLAN>Knowledge gap mapping: (1) Survey current knowledge. (2) Identify specific open questions. (3) Classify: empirical (need data), theoretical (need framework), methodological (need technique), fundamental (maybe unknowable). (4) Assess significance. (5) Propose filling approaches.</PLAN>", f"<PLAN>Analyze unknowns about {gap}: distinguish settled, debated, beyond current methods. Debated = research frontier. For each gap: what progress would fill it? New instruments? New math? New data? Interdisciplinary insights? Look at historical patterns of similar gap-closing.</PLAN>")
            think = pick(f"<THINK>Topic: {gap}. Current: principles known details obscure, framework exists empirics limited, competing theories, largely unexplored -- frontier, or deep mystery fundamental questions. Key open questions: mechanisms? causal relationships? quantities/scales? boundary conditions? components and interactions? Why gaps persist: technical limitations -- lack instruments, complexity -- too many interacting parts, scale -- too large/small to observe, timescales too long/short, fundamental quantum/relativistic barriers, or interdisciplinary -- bridging needed. Significance: would transform understanding, practical for tech/medicine/policy, addresses fundamental question, or resolves long-standing debate. Paths forward: new instruments/techniques, computational modeling, interdisciplinary, theoretical innovation, large-scale data initiatives, or paradigm shift.</THINK>", f"<THINK>Gap: {gap}. Frontier status: empirical -- need more observations, theoretical -- need better models, methodological -- need new techniques, foundational -- maybe ill-posed, or integrative -- need synthesis. Why hard: emergent complexity, direct observation impossible, multiple scales from molecular to macro, ethical constraints, historical -- cannot replay, or counterfactuals untestable. Persists because required tech does not exist, genuinely difficult, wrong question being asked, paradigm shifts take time, or need convergent evidence. Progress: develop enabling tech, multiple working hypotheses, invest in foundational theory, foster interdisciplinary, or exploit natural experiments.</THINK>")
            exec_ = pick(f"<EXEC>Knowledge gap: {gap}. Status: active research frontier, long-standing mystery, emerging field, or neglected but important. Type: empirical, theoretical, methodological, integrative, or foundational. Barriers: technology limits, complexity, scale mismatch, observational constraints, ethical limits, or computational intractability. Path forward: new instruments, computational advances, interdisciplinary synthesis, theoretical breakthroughs, or data-driven discovery. Timeline: years -- clear path, decades -- needs advances, uncertain -- needs paradigm shift, or potentially never -- fundamental limit.</EXEC>", f"<EXEC>Gap mapped: {gap}. Known: basic principles, partial understanding, or competing theories. Open questions: multiple. Type distribution: mostly empirical/theoretical, mostly methodological, balanced, or mostly integrative. Best approach: technological innovation, theoretical unification, computational breakthrough, interdisciplinary collaboration, or large-scale data. Significance: high.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("metacognition","epistemology","science"))

STRATEGY_PROBLEMS = [
    ("determine if binary tree is balanced",["recursive height check O(n)","iterative DFS with early termination","memoization"]),
    ("sort 1M 32-bit integers",["quicksort in-place O(n log n)","counting sort O(n+k)","mergesort stable O(n log n)"]),
    ("shortest path in weighted graph",["Dijkstra (non-negative weights)","A* with good heuristic","Bellman-Ford (neg weights ok)"]),
    ("detect spam emails",["Naive Bayes (fast, effective)","logistic regression + features","transformer (accurate, expensive)"]),
    ("schedule meetings across timezones",["find overlapping windows","use UTC reference","visual timezone timeline"]),
    ("estimate pi",["Monte Carlo sampling","Gregory-Leibniz series","Buffon's needle"]),
    ("check if string is palindrome",["two-pointer O(n)","reverse and compare O(n)","stack-based O(n)"]),
    ("compress text file",["gzip (LZ77+Huffman)","bzip2 (BWT+MTF+Huffman)","LZMA (high ratio)"]),
]

def _strategy_gen():
    while True:
        for problem, strategies in STRATEGY_PROBLEMS:
            inp = pick(f"Strategy selection: For {problem}, compare approaches. Which and why?", f"Metacognitive strategy: Need to {problem}. Evaluate trade-offs.", f"Choose best approach for: {problem}. Justify based on problem characteristics.", f"Algorithm selection: For {problem}, what method? Consider efficiency, accuracy, constraints.")
            plan = pick(f"<PLAN>Strategy selection: (1) Analyze problem characteristics -- size, constraints, precision, resources. (2) Enumerate strategies: {', '.join(strategies)}. (3) Evaluate each on correctness, efficiency, complexity, robustness. (4) Select best match. (5) Plan verification. Use decision matrix.</PLAN>", f"<PLAN>Select for {problem}: understand specification -- inputs/outputs, constraints. Map each strategy to requirements. Consider worst vs average case, implementation vs performance, memory vs speed, or precision vs cost. Select best fit for problem profile.</PLAN>")
            think = pick(f"<THINK>Problem: {problem}. Strategies: {', '.join(strategies)}. Criteria: (1) Correctness -- always works? (2) Efficiency -- time/space. (3) Implementation effort. (4) Robustness -- edge cases. (5) Maintainability. For {problem}: input size main factor, error tolerance matters, real-time constraints, memory limited, accuracy strict, or resource constrained. If speed fastest, simplicity clearest, reliability robust, accuracy precise, or scalability scalable. {strategies[0]} is standard choice, most efficient, easiest, or most robust. But {strategies[1]} if input small, memory constrained, guaranteed performance needed, or special structure. Verification: test known cases, formal reasoning, compare outputs, or stress-test edges.</THINK>", f"<THINK>Evaluating for {problem}. Options: {', '.join(strategies)}. Strategy A: strengths fast/simple, weaknesses limited scope. Strategy B: strengths general/robust, weaknesses slower/complex. Choice depends on: data size, performance, accuracy, resources, timeline, or team expertise. Decision matrix: assign weights, score, compute. Preferred: {pick(strategies)} because optimal trade-offs, most reliable, simplest sufficient, best scaling, or better edge handling. Could combine: {strategies[0]} for typical, {strategies[1]} for difficult cases.</THINK>")
            exec_ = pick(f"<EXEC>Strategy for '{problem}'. Options: {', '.join(strategies)}. Selected: {pick(strategies)}. Rationale: best time complexity, simplest correct, most robust, best memory, or optimal accuracy. Trade-offs: slightly more complex for performance, generality for speed, memory for time, or optimality for simplicity. Verification: test benchmarks, compare alternatives, prove by invariant, or systematic edge tests.</EXEC>", f"<EXEC>Strategy complete: {problem}. Evaluated: {', '.join(strategies)}. Decision: {pick(strategies)}. Factors: performance, correctness, complexity, robustness, constraints, or expertise. Appropriate for typical cases, specific constraints, general purpose, or production quality.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(4,7), pick("metacognition","strategy","computing"))

COG_LOAD_TASKS = [
    "simultaneously solve a complex math problem while listening to a podcast",
    "learn a new programming language while building a production system",
    "juggle multiple ongoing projects with competing deadlines",
    "drive in heavy traffic while navigating to an unfamiliar destination",
    "write a difficult report while answering constant emails and messages",
    "debug a concurrency issue while managing deployments",
]

def _cog_load_gen():
    while True:
        for task in COG_LOAD_TASKS:
            inp = pick(f"Cognitive load analysis: You need to {task}. How do you manage mental resources?", f"Metacognitive resource management: When you {task}, how do you allocate attention?", f"Analyze cognitive demands of: {task}. What makes it hard? Reduce cognitive load?", f"Working memory management: You {task}. High cognitive load. What strategies help?")
            plan = pick(f"<PLAN>Cognitive load management: (1) Assess task's cognitive demands. (2) Reduce intrinsic load: chunking, automation, external memory aids. (3) Reduce extraneous load: minimize distractions, streamline processes. (4) Optimize germane load: focus on schema formation. (5) Monitor mental state and take breaks when depleted.</PLAN>", f"<PLAN>Apply cognitive load theory. Intrinsic load: inherent to task. Extraneous load: environment/presentation. Germane load: schema construction. Strategies: chunk complex info, use external memory, automate routines, reduce multitasking, take strategic breaks, use cognitive aids, prioritize subtasks.</PLAN>")
            think = pick(f"<THINK>Cognitive demands: {task}. High working memory load because requires holding multiple pieces simultaneously, complex transformations, coordinating interdependent subtasks, or novel elements without schemas. Intrinsic load: high - task is complex, moderate - some automation possible, or reducible through chunking. Extraneous load: high if multitasking, minimized through environment optimization, or switching costs. Strategies: external memory frees working memory, break into subtasks, develop schemas through practice, cognitive offloading, progressive deepening, or take breaks when overwhelmed. Working memory limited (4-7 chunks).</THINK>", f"<THINK>Managing cognitive resources for: {task}. Demands: active processing in WM, retrieval from LTM, attention management. Sweller's cognitive load theory: reduce split attention, use modality effect, leverage worked-example effect, use goal-free problems. Multitasking degrades performance. Best: serialize -- one thing at a time; integrate -- combine synergistically; reduce -- eliminate unnecessary; schedule -- alternate focused work with breaks. Monitor mental state.</THINK>")
            exec_ = pick(f"<EXEC>Cognitive load analysis: {task}. Intrinsic: high/moderate/low. Extraneous: high (distractions), manageable (optimized), or minimized. Strategies: chunking, external memory, task serialization, distraction minimization, strategic breaks, prioritization. Effectiveness: high - sustainable effort, moderate - some overload, or improving with practice.</EXEC>", f"<EXEC>Cognitive resource management for: {task}. Strategies: reduce multitasking, external memory aids, chunk complex info, prioritize tasks, take strategic breaks. Load reduction: 20-60 percent. Sustainability: sustainable, needs breaks, or demanding but manageable.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("metacognition","cognitive_science","psychology"))

ERROR_SCENARIOS = [
    ("a program crashes only when processing the third file in a batch","latent state contamination or index off-by-one"),
    ("a student consistently makes mistakes on negative number arithmetic","lack of conceptual understanding of signed numbers"),
    ("a chess engine blunders in closed positions but excels in open ones","evaluation function weakness in blocked pawn structures"),
    ("a translation model produces good European translations but poor Asian ones","training data imbalance or tokenization mismatch"),
    ("a speech recognition system fails more often with female voices","training data gender imbalance or pitch normalization issue"),
    ("a financial model predicts well in bull markets but fails in bear markets","overfitting to bull market patterns, regime change not modeled"),
    ("a medical diagnostic AI misses rare diseases","class imbalance in training, rare cases underrepresented"),
    ("an autonomous vehicle struggles in rain but performs well in dry conditions","sensor degradation in rain, training data lacking adverse weather"),
]

def _error_analysis_gen():
    while True:
        for symptom, root_cause in ERROR_SCENARIOS:
            inp = pick(f"Error analysis: {symptom}. Identify the root cause and propose a fix.", f"Diagnose the problem: {symptom} What is the underlying issue? How to verify?", f"Root cause analysis: {symptom}. Trace from symptom to underlying cause.", f"Debug the pattern: {symptom}. What systematic error? How to confirm and fix?")
            plan = pick(f"<PLAN>Error analysis: (1) Reproduce reliably. (2) Characterize triggering conditions. (3) Form hypotheses: {root_cause}. (4) Design experiments to test each. (5) Isolate specific failure mechanism. (6) Develop and test fix. (7) Verify no regression.</PLAN>", f"<PLAN>Diagnose {symptom}: scientific method. Observe pattern. Form hypothesis: {root_cause}. Predict what changes if correct. Test with controlled experiment. If confirmed, fix. If not, revise. Key: isolate minimal reproducing case, check boundaries, verify assumptions, add instrumentation.</PLAN>")
            think = pick(f"<THINK>Symptom: {symptom}. Systematic pattern suggests deterministic cause. Hypotheses: (1) {root_cause}. (2) race condition/timing, configuration difference, resource exhaustion, data-dependent code path, or incorrect assumption. Discriminate: deterministic vs intermittent? Vary conditions? Add logging? Simplify until error disappears? Test components in isolation. {root_cause} hypothesis fits because directly explains pattern and conditions suggest this mechanism. Verify: create minimal reproduction, inspect code/data, add assertions, compare working vs failing.</THINK>", f"<THINK>Diagnosing: {symptom}. Consistent/predictable error suggests specific bug, data quality issue, configuration error, design flaw, environmental difference, or missing edge case. Root cause: {root_cause}. Evidence: error correlates with specific conditions, timing points to component, similar past errors, or signature matches this failure mode. Verify: unit test with trigger input, code review, A/B comparison, tracing, or fault injection. Fix: correct bug, add defensive checks, redesign component, improve test coverage, or add monitoring.</THINK>")
            exec_ = pick(f"<EXEC>Error: {symptom}. Root cause: {root_cause}. Category: {pick('logic bug','data quality','configuration','design flaw','environmental','edge case')}. Fix: {pick('correct specific bug','add defensive checks','redesign component','improve tests','add monitoring')}. Verification: {pick('original error case passes','regression tests pass','monitoring confirms resolution','code review approved')}. Prevention: {pick('add test for this scenario','update documentation','improve code review checklist','add static analysis rule')}.</EXEC>", f"<EXEC>Error analysis: {symptom} -> {root_cause}. Method: {pick('5 whys','fishbone diagram','fault tree analysis','failure mode analysis')}. Severity: {pick('critical','major','minor','cosmetic')}. Fix implemented: {pick('code change','configuration update','process improvement','training/education')}. Verification: {pick('passed all tests','production monitoring clean','user acceptance confirmed')}.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("metacognition","error_analysis","debugging"))

def chunk_2_gen():
    gens = [_confidence_gen(), _boundaries_gen(), _revision_gen(), _uncertainty_gen(),
            _self_correction_gen(), _bias_gen(), _knowledge_gap_gen(), _strategy_gen(),
            _cog_load_gen(), _error_analysis_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════ Chunk 3: Novel Architecture Invention ═══════════════════════
# 10 categories: AI, database, network protocol, programming language, hardware, security, distributed systems, compiler, storage, BCI

ARCHITECTURES = [
    ("AI architecture","a neural network that learns continuously without catastrophic forgetting",
     ["elastic weight consolidation","progressive neural networks","synaptic intelligence","generative replay","dual-memory architecture"]),
    ("database system","a database optimized for both OLTP and OLAP workloads",
     ["HTAP architecture","columnar+row hybrid storage","tiered memory caching","adaptive indexing","MVCC with delta stores"]),
    ("network protocol","a transport protocol for interplanetary communication",
     ["delay-tolerant networking","fountain codes","long-range FEC","store-and-forward relays","asymmetric acknowledgment"]),
    ("programming language","a language that prevents all memory errors at compile time",
     ["linear/affine types","region-based memory","borrow checking","capability-based security","ownership semantics"]),
    ("hardware architecture","a processor designed specifically for sparse tensor operations",
     ["vector-LIW with sparse masking","pulsing systolic arrays","sparse-tensor memory controller","speculative sparsity prediction","asynchronous sparse ALUs"]),
    ("security system","an authentication system resistant to quantum attacks",
     ["lattice-based signatures","hash-based signatures","multivariate cryptography","code-based encryption","isogeny-based key exchange"]),
    ("distributed system","a consensus protocol exceeding 1M transactions per second",
     ["DAG-based consensus","pipelined BFT","sharded validation","rotating leader optimization","parallel vote aggregation"]),
    ("compiler","a JIT compiler that learns optimization policies via reinforcement learning",
     ["RL-based register allocation","learned inlining heuristics","automatic vectorization via DRL","adaptive tier compilation","profile-guided optimization with ML"]),
    ("storage system","a storage system with quantum-level data density",
     ["DNA-based archival storage","holographic data encoding","multilevel 3D NAND","phase-change memory tiers","optical storage with nanoscale resolution"]),
    ("communication protocol","a protocol for brain-computer interface data streams",
     ["neural spike encoding","adaptive bandwidth allocation","lossy neural compression","real-time neural decoding pipeline","bidirectional neural signaling"]),
    ("quantum computing architecture","a fault-tolerant quantum computer with practical error correction",
     ["surface codes","concatenated codes","topological qubits","color codes","measurement-based quantum computing"]),
    ("robotics system","a swarm robotics coordination protocol for search and rescue",
     ["consensus-based task allocation","potential field navigation","stigmergy communication","auction-based role assignment","decentralized SLAM"]),
    ("edge computing platform","a distributed compute platform for real-time AI inference at the edge",
     ["federated learning pipeline","gradient compression","split neural networks","model quantization at the edge","hierarchical inference offloading"]),
]

def chunk_3_gen():
    while True:
        for arch_type, challenge, approaches in ARCHITECTURES:
            inp = pick(f"Design a novel {arch_type}: {challenge}. Propose an architecture.", f"Architecture invention: Create a {arch_type} that can {challenge}.", f"Invent a {arch_type} for {challenge}. Core components and interactions?", f"Novel architecture: Design a {arch_type} solving {challenge}. Explain design choices.")
            plan = pick(f"<PLAN>Architecture design: (1) Define requirements for {challenge}. (2) Explore design space: {', '.join(approaches)}. (3) Select components and interactions. (4) Address trade-offs. (5) Specify interfaces and data flow. (6) Consider failure modes. Novel contribution: {pick(approaches)}.</PLAN>", f"<PLAN>Design {arch_type} for {challenge}: Analyze what makes this hard. Consider {approaches[0]} and {approaches[1]} as starting points. Synthesize hybrid approach. Define layers: {pick('storage, computation, communication, coordination','data, control, management planes','interface, logic, data, infrastructure')}. Evaluate against requirements.</PLAN>")
            think = pick(f"<THINK>Designing novel {arch_type}. Challenge: {challenge}. Key difficulty: balancing competing requirements. Existing approaches trade off X for Y; novel architecture could achieve both by rethinking fundamental assumptions. {approaches[0]} handles scalability/fault tolerance/performance well but adds latency/increases complexity. {approaches[1]} takes different approach: trades X for better Y or introduces novel mechanism. My proposed architecture synthesizes these: a hybrid using approach A for common case and B for edge cases, a layered design handling different concerns at each level, or a novel mechanism inspired by biology, physics, or social systems that avoids the traditional trade-off. Key innovations: novel data structure enabling fast reads and writes, asymmetric design optimizing for dominant operation pattern, decentralized coordination eliminating bottlenecks, or adaptive behavior changing based on workload.</THINK>", f"<THINK>Invention of {arch_type} for {challenge}. First principles: fundamental constraint is physics (speed of light, thermodynamics), information theory (bandwidth, entropy), computation (Turing limits), or economics (cost). Breaking through requires a new abstraction, exploiting new physical phenomenon, combining ideas from unrelated domains, or redistributing work. {approaches[0]} leverages parallelism, redundancy, specialization, caching, or prediction. {approaches[1]} leverages decomposition, asynchrony, hierarchy, adaptation, or randomization. Novel architecture combines these through a unified framework with pluggable components, hierarchical design with emergent properties, or feedback-driven adaptive system. Critical path: request arrives, system classifies and routes, checks cache then computes if needed, or activates learned policy.</THINK>")
            exec_ = pick(f"<EXEC>Novel {arch_type} for: {challenge}. Name: Nanobit-{pick('Core','Net','Store','Sync','Learn','Fuse','Mesh','Flux')}. Core innovation: {pick(approaches)}. Components: {pick('(1) Processor, (2) Core engine, (3) Storage layer, (4) Coordinator','(1) Frontend, (2) Scheduler, (3) Worker pool, (4) Backend')}. Trade-offs: {pick('performance vs flexibility','complexity vs generality','speed vs accuracy','scalability vs consistency')}. Improvement: {random.randint(2,100)}x in {pick('throughput','latency','efficiency','scalability','density')}.</EXEC>", f"<EXEC>Architecture: {arch_type}. Challenge: {challenge}. Insight: {pick('bottleneck is X, optimize for Y','traditional designs fail because Z','nature solves via mechanism M','eliminate abstraction layer causing overhead')}. Style: {pick('layered monolith','microservice mesh','peer-to-peer','hierarchical tree','pipeline','shared-nothing','actor-based')}. Novelty: {pick('new protocol','novel data structure','innovative algorithm','unique organizational pattern')}. Feasibility: {pick('prototype demonstrated','theoretically sound','requires component X','open research question')}.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(5,7), pick("architecture","engineering","design"))

# ═══════════════════════ Chunk 4: Beautiful Code Craftsmanship ═══════════════════════
# 5 categories: naming, structure, error handling, performance, refactoring

NAMING_SCENARIOS = [
    ("a function that calculates the average of an array","calculateAverage","calc_avg","avg","computeMean"),
    ("a variable holding the number of active users","activeUserCount","num_active_users","userCnt","activeUsers"),
    ("a class representing a customer order","CustomerOrder","cust_order","Order","CustomerOrderEntity"),
    ("a boolean flag for whether a file has been processed","isFileProcessed","file_processed","processedFlag","fileDone"),
    ("a method that saves a document to the database","saveDocument","save_doc","storeDoc","persistDocument"),
]

def _naming_gen():
    while True:
        for desc, good, ok, poor, alt in NAMING_SCENARIOS:
            inp = pick(f"Code naming: For {desc}, evaluate: {good}, {ok}, {poor}. Best and why?", f"Naming review: variable/function for {desc}. Options: {good}, {ok}, {poor}. Choose and justify.", f"Best practices: Naming a {desc}. Compare {good} vs {ok} vs {poor}.")
            plan = pick(f"<PLAN>Naming evaluation: (1) Entity's purpose and scope. (2) Conventions (camelCase, snake_case, PascalCase). (3) Evaluate on clarity, precision, searchability, consistency. (4) Select name communicating intent without comments. (5) Check for false cognates or ambiguous abbreviations.</PLAN>", f"<PLAN>Choose best name: names should reveal intent, be pronounceable, avoid encodings, match domain language. {good} follows conventions and clearly communicates purpose. {ok} technically correct but less idiomatic. {poor} too vague or misleading.</PLAN>")
            think = pick(f"<THINK>Evaluating names for {desc}. {good}: clearly communicates purpose, follows conventions, unambiguous. {ok}: technically correct but less idiomatic in this language -- uses snake_case in camelCase codebase. {poor}: too short/ambiguous, uses cryptic abbreviation, or misleading. {alt}: viable alternative with different trade-offs. Best: {good} because it balances clarity and conciseness, follows project conventions, and makes code read like prose. Good names eliminate the need for most comments -- code explains itself.</THINK>", f"<THINK>Naming analysis for {desc}. Criteria: (1) Reveals intent? (2) Searchable? (3) Consistent? (4) Pronounceable? (5) Avoids misleading associations? {good}: scores high on all. {ok}: may violate one criterion -- less searchable or less precise. {poor}: fails multiple -- ambiguous, not searchable, misleading. Cost of poor naming is cumulative: every reading takes longer, bugs hide in misleading names. Recommendation: {good}.</THINK>")
            exec_ = pick(f"<EXEC>Naming review for '{desc}'. Recommended: {good}. Rationale: clear intent, conventional, searchable, precise, domain-aligned. Avoid: {poor} (too vague, misleading, or cryptic). Principle: reveal intent, use domain language, avoid encodings, be pronounceable.</EXEC>", f"<EXEC>Name selection: {desc}. Best: {good}. Also acceptable: {ok}. Avoid: {poor}. {alt} is viable alternative. Good name is self-documenting, consistent, precise, and domain-appropriate.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("code","craftsmanship","naming"))

STRUCTURE_PROBLEMS = [
    ("a 500-line function parsing, validating, transforming, formatting, and logging","Extract Method for each phase, compose in pipeline","Single Responsibility"),
    ("class with 2000 lines and 10 responsibilities","Extract Class for each, use Facade for coordination","Separation of Concerns"),
    ("duplicated validation across 15 API endpoints","Extract into reusable validation middleware","DRY"),
    ("stringly-typed API with raw JSON string params","Introduce typed DTOs with parsing at boundaries","Type Safety"),
    ("global mutable state accessed by 30 functions","Encapsulate behind interface, inject dependencies","Encapsulation"),
]

def _structure_gen():
    while True:
        for problem, solution, principle in STRUCTURE_PROBLEMS:
            inp = pick(f"Refactor code structure: {problem}. Propose better organization.", f"Code structure: {problem}. Restructure for maintainability.", f"Structural review: {problem}. Apply {principle} to improve design.", f"Improve: {problem}. {principle} suggests what restructuring?")
            plan = pick(f"<PLAN>Structural improvement: (1) Identify issues -- coupling, cohesion, responsibility boundaries. (2) Apply {principle}. (3) Propose new structure: {solution}. (4) Define interfaces. (5) Plan migration. Each component should have one reason to change.</PLAN>", f"<PLAN>Fix {problem}: Map current dependencies and responsibilities. Apply decomposition via {principle}. {solution} is the target. Ensure new interfaces are clean, testable, and dependencies flow one direction.</PLAN>")
            think = pick(f"<THINK>Structural analysis: {problem}. Core issue: violation of {principle}. Currently one component handles multiple concerns, modules have bidirectional dependencies, abstraction levels inconsistent, or no clear boundary. Restructure {solution} addresses by separating concerns, introducing interfaces that invert dependencies, extracting cohesive units. Improvements: each component independently testable, changes localized, dependencies unidirectional. Trade-off: slightly more boilerplate for much better separation. Worth it because maintainability improves dramatically.</THINK>", f"<THINK>Structure issue: {problem}. Violates {principle}. Current design has low cohesion, tight coupling, leaky abstractions, or god objects. Applying {principle}, solution {solution} creates high cohesion, loose coupling, proper abstraction. Key insight from {principle}: a class should have one reason to change; high-level modules shouldn't depend on low-level details. Transforms code from rigid/fragile to flexible/maintainable.</THINK>")
            exec_ = pick(f"<EXEC>Structure refactored: {problem}. Applied: {principle}. New structure: {solution}. Improvements: cohesion increased, coupling decreased, single responsibility achieved, dependencies inverted. Trade-off: more files but each simpler. Migration: extract one concern at a time.</EXEC>", f"<EXEC>Structural redesign: {problem} -> {solution}. Principle: {principle}. Benefits: reduced coupling, increased cohesion, cleaner interfaces, better testability, easier maintenance. Impact: simplifies future features, reduces bug risk, improves developer productivity.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("code","craftsmanship","architecture"))

ERR_HANDLING = [
    ("a function returning -1 on error, result on success","use Result<T,E> type or exceptions instead of sentinel values"),
    ("silent try-except catching all exceptions doing nothing","catch specific exceptions, log the error, handle or re-raise"),
    ("nested try-catch blocks impossible to follow","flatten with early returns, use context managers, decompose"),
    ("function ignoring database connection failure","propagate error or handle with retry logic and proper fallback"),
]

def _err_handling_gen():
    while True:
        for problem, solution in ERR_HANDLING:
            inp = pick(f"Error handling review: {problem}. How should it be handled?", f"Improve error handling: {problem}. {solution}", f"Error handling anti-pattern: {problem}. Proper approach?", f"Code review: {problem}. Identify issue and propose fix.")
            plan = pick(f"<PLAN>Error handling: (1) What can go wrong? (2) Classify: expected vs unexpected. (3) Determine response: recover, retry, fail fast, degrade gracefully. (4) Log with context. (5) Use type-safe handling. Apply: {solution}.</PLAN>", f"<PLAN>Fix error handling: Map all failure modes. {solution} addresses anti-pattern. Ensure: errors never silently swallowed, messages include context, function contract specifies error behavior, callers can distinguish types.</PLAN>")
            think = pick(f"<THINK>Error handling issue: {problem}. Anti-pattern because sentinel values mistaken for valid results, silent failures hide bugs, error info lost, or callers cannot handle different failures. Proper: {solution}. Ensures errors explicit in type system, every path visible and handled, failures logged. Principle: fail fast, don't swallow errors, make errors explicit, distinguish recoverable from unrecoverable. Good error handling transforms debugging from guessing to investigation.</THINK>", f"<THINK>Anti-pattern: {problem}. Danger: sentinel values corrupt data downstream, silent catch makes debugging impossible, complex error flow has accidental successes, ignoring failures creates inconsistent state. Better: {solution}. Principle: errors should be explicit not implicit; type system documents failure modes; every operation succeeds or fails clearly. Use Result<T,E> for expected failures, exceptions for unexpected. Log stack traces and context.</THINK>")
            exec_ = pick(f"<EXEC>Error handling fix: {problem}. Applied: {solution}. Improvement: errors now explicit in type signatures, silent failures eliminated, error context preserved, specific errors allow targeted handling. Principle: fail fast, don't swallow errors, explicit over implicit.</EXEC>", f"<EXEC>Anti-pattern corrected: {problem}. Resolution: {solution}. All failure modes now explicitly handled, logged with context, type-safe in API, documented in contract. Code more robust and debuggable.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("code","craftsmanship","error_handling"))

PERF_PROBLEMS = [
    ("O(n^2) nested loop over 100K item list","use hash map for O(1) lookups, reducing to O(n)"),
    ("web endpoint making 10 sequential DB queries per page","batch queries with JOINs or use eager loading"),
    ("UI re-rendering entire component tree on every keystroke","use virtualization, memoization, selective updates"),
    ("batch process writing to DB one record at a time","batch inserts with transaction batching (1000 rows per commit)"),
    ("logging doing synchronous IO on every hot-path call","async logging with ring buffer and batched writer"),
    ("API returning full objects when only few fields needed","implement field selection or projection queries"),
    ("cache storing every distinct key individually","use coalescing, bloom filters to skip cache-miss queries"),
]

def _perf_gen():
    while True:
        for problem, solution in PERF_PROBLEMS:
            inp = pick(f"Performance optimization: {problem}. Identify bottleneck and propose fix.", f"Profile and optimize: {problem}. {solution}", f"Performance anti-pattern: {problem}. Refactor for speed?", f"Optimize: {problem}. Root cause of poor performance?")
            plan = pick(f"<PLAN>Performance analysis: (1) Profile to confirm bottleneck. (2) Identify algorithmic or architectural cause. (3) Propose optimization: {solution}. (4) Evaluate trade-offs (memory vs speed, complexity vs gain). (5) Implement and benchmark. (6) Verify correctness.</PLAN>", f"<PLAN>Optimize {problem}: Measure baseline. Bottleneck is algorithmic complexity, I/O overhead, memory access pattern, or unnecessary computation. Apply: {solution}. Measure improvement. Ensure no regression. Document rationale.</PLAN>")
            think = pick(f"<THINK>Performance issue: {problem}. Bottleneck: algorithmic -- wrong data structure; I/O -- too many round trips; memory -- cache misses; or redundant -- computing same thing multiple times. Optimize: {solution}. Improves by reducing algorithmic complexity, amortizing I/O, eliminating redundant work, or parallelizing. Trade-offs: slightly more memory for faster speed, more complex code for magnitude improvement. After optimization verify output unchanged and edge cases handled. Rule: profile first, optimize the bottleneck, measure improvement.</THINK>", f"<THINK>Analyzing performance: {problem}. Root cause: algorithmic inefficiency, excessive I/O, unnecessary computation, or poor memory locality. Fix {solution} addresses by changing algorithm, reducing I/O, eliminating redundant computation, or improving data layout. Expected speedup: 10-100x for algorithmic, 2-5x for I/O, significant for caching. Balance: optimization time vs gain, code clarity vs speed, memory vs compute. Amdahl's law: optimize the biggest bottleneck first.</THINK>")
            exec_ = pick(f"<EXEC>Performance optimized: {problem}. Fix: {solution}. Improvement: algorithmic complexity reduced, I/O batched, redundant computation eliminated, or memory optimized. Speedup: 10-100x. Trade-offs: slightly higher memory, modest complexity increase acceptable. Verified: correctness maintained with benchmark improvement.</EXEC>", f"<EXEC>Performance anti-pattern resolved: {problem}. Root cause: algorithmic, I/O, memory, or redundant computation. Optimization: {solution}. Result: significant throughput improvement, reduced latency, smoother UI, or lower resource utilization. Profiling confirmed fix targets actual bottleneck.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("code","craftsmanship","performance"))

REFACTORING = [
    ("500-line function parsing, validating, transforming, formatting, logging","Extract Method: separate each phase, compose in pipeline pattern"),
    ("class with 2000 lines and 10 responsibilities","Extract Class for each, use Facade for coordination"),
    ("duplicated validation across 15 API endpoints","Extract into reusable validation middleware or decorator"),
    ("stringly-typed API with raw JSON string params","Introduce typed DTOs/validation schemas with parsing at boundaries"),
    ("global mutable state accessed by 30 functions","Encapsulate behind interface, inject dependencies, isolate mutations"),
]

def _refactor_gen():
    while True:
        for problem, solution in REFACTORING:
            inp = pick(f"Refactoring target: {problem}. Plan the refactoring steps.", f"Code smell: {problem}. Refactor? {solution}", f"Improve code quality: {problem}. Describe refactoring approach.", f"Legacy code: {problem}. Safe refactoring preserving behavior.")
            plan = pick(f"<PLAN>Refactoring plan: (1) Test coverage before changes. (2) Identify code smell: long method, large class, duplication. (3) Apply pattern: {solution}. (4) Run tests after each small change. (5) Verify behavior preservation. Boy scout rule: leave code cleaner than found.</PLAN>", f"<PLAN>Safe refactoring: (1) Characterization tests. (2) Identify safe boundaries. (3) Apply {solution} incrementally -- extract, rename, move. (4) Run tests after each transformation. (5) Clean up. Never refactor without tests.</PLAN>")
            think = pick(f"<THINK>Refactoring analysis: {problem}. Code smell: violation of Single Responsibility, DRY, or abstraction boundaries. Code works but is hard to understand, modify, or maintain. Refactoring {solution} will separate concerns, eliminate duplication, introduce proper abstractions, or enforce boundaries. Steps: extract method/class, introduce parameter, move field, rename. Important: behavior preservation -- each step followed by test run. Fowler: refactoring is disciplined technique for restructuring code. Goal: improve internal structure without changing external behavior.</THINK>", f"<THINK>Code smell: {problem}. This is primitive obsession, long method, god class, or shotgun surgery. Refactoring {solution} addresses by extracting cohesive elements, introducing domain types, composing from focused functions, or creating single change point. Benefits: easier to read, localized changes, safer modifications, simpler tests. Must be incremental -- each step preserves behavior verified by tests. Make the change easy, then make the easy change.</THINK>")
            exec_ = pick(f"<EXEC>Refactoring plan for {problem}. Apply: {solution}. Steps: (1) add tests, (2) extract methods, (3) reorganize, (4) clean up. Outcome: improved readability, maintainability, testability, reduced duplication, clearer abstractions.</EXEC>", f"<EXEC>Refactoring: {problem} -> {solution}. Smells resolved: long method, large class, duplication, primitive obsession, global state. Improvements: higher cohesion, lower coupling, clearer intent, better testability. Behavior preserved -- all tests pass.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("code","craftsmanship","refactoring"))

DOC_TOPICS = [
    ("a public API endpoint with no documentation","Add docstring explaining purpose, parameters, return value, exceptions, and usage example"),
    ("a complex algorithm with inline comments only","Extract comments into module-level documentation, add README with examples and big-O analysis"),
    ("a component library with inconsistent documentation","Adopt Storybook/Pattern library with live examples, prop tables, and accessibility notes"),
]

def _doc_gen():
    while True:
        for problem, solution in DOC_TOPICS:
            inp = pick(f"Documentation review: {problem}. Improve the documentation.", f"Code docs: {problem}. {solution}", f"Documentation best practices: {problem}. What should be documented and how?")
            plan = pick(f"<PLAN>Documentation improvement: (1) Identify audience and their needs. (2) Document what, why, how, and edge cases. (3) Add docstrings following project conventions. (4) Include usage examples that are tested. (5) Document error conditions and constraints. Write for the developer who will maintain the code.</PLAN>", f"<PLAN>Good documentation: explains purpose not just mechanism. {solution} addresses the gap. Each public API needs: description of what it does, parameters with types and meaning, return value, exceptions raised, and at least one usage example. Keep docs close to code (docstrings) with overview in README.</PLAN>")
            think = pick(f"<THINK>Documentation issue: {problem}. The goal is to reduce the reader's time to understanding. Good docs answer: what does this do? why does it exist? how is it used? what are the edge cases? {solution} addresses the specific gap. Documentation should be treated like code: kept in sync, reviewed, and tested. Examples in docs should be runnable. API docs should be generated from source to stay accurate. README should provide the big picture. Inline comments explain why, not what (the code shows what).</THINK>", f"<THINK>Improving documentation for {problem}. Best practices: (1) Document intent, not implementation. (2) Include examples for common uses. (3) Document error cases and edge conditions. (4) Keep docs close to the code they describe. (5) Use consistent formatting. {solution} addresses the specific deficiency. Documentation is an investment that pays off every time someone reads the code. Like tests, docs should be maintained alongside code changes.</THINK>")
            exec_ = pick(f"<EXEC>Documentation improved: {problem}. Applied: {solution}. Added: purpose statement, parameter docs with types, return value description, exception documentation, usage examples. Documentation now follows project conventions and is kept in source alongside code. Examples are tested.</EXEC>", f"<EXEC>Documentation fix: {problem} -> {solution}. Deliverables: updated docstrings, README improvements, API reference, usage examples. All documentation is version-controlled, reviewed, and tested alongside code.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("code","craftsmanship","documentation"))

API_DESIGN_PROBLEMS = [
    ("a REST endpoint that returns 200 with error body on failure","Use proper HTTP status codes: 400 for validation, 401 for auth, 404 not found, 500 server error"),
    ("an API that exposes internal database IDs to clients","Use opaque public IDs (UUIDs), map to internal IDs server-side, never leak implementation details"),
    ("a GraphQL mutation that silently ignores unknown fields","Validate input strictly, reject unknown fields with clear error messages, use strict input types"),
]

def _api_design_gen():
    while True:
        for problem, solution in API_DESIGN_PROBLEMS:
            inp = pick(f"API design review: {problem}. Improve the API contract.", f"API best practices: {problem}. {solution}", f"REST/GraphQL design: {problem}. How should this be designed properly?")
            plan = pick(f"<PLAN>API design improvement: (1) Review HTTP semantics and REST conventions. (2) Use status codes correctly. (3) Design consistent error responses with codes and messages. (4) Version API explicitly. (5) {solution}. Good API design makes correct usage obvious and incorrect usage hard.</PLAN>", f"<PLAN>API fix for {problem}: Apply REST best practices -- resources as nouns, HTTP methods as verbs, proper status codes, consistent error format. {solution} addresses the specific issue. Design for the consumer: intuitive, consistent, well-documented, backward-compatible.</PLAN>")
            think = pick(f"<THINK>API design issue: {problem}. A well-designed API makes life easy for consumers. {solution} fixes the specific anti-pattern. General principles: (1) Be consistent -- same patterns throughout. (2) Use HTTP semantics properly -- GET for reads, POST for creates, PUT for full updates, PATCH for partial, DELETE for removal. (3) Error responses should include enough info for the client to handle them. (4) Version early and explicitly. (5) Design for evolution -- don't expose internal implementation. (6) Paginate list endpoints. (7) Use standard formats (JSON:API, HAL, etc.) for discoverability.</THINK>", f"<THINK>Reviewing API: {problem}. The issue reflects a common anti-pattern in API design. {solution} corrects it by following established conventions. Key API design considerations: (1) Resource-oriented design -- model the domain, not CRUD operations. (2) Consistent naming -- plural nouns, kebab-case or snake_case, no verbs in URLs. (3) Proper status codes -- 2xx success, 3xx redirect, 4xx client error, 5xx server error. (4) Standard error format with machine-readable code and human-readable message. (5) Rate limiting headers. (6) Idempotency guarantees where needed.</THINK>")
            exec_ = pick(f"<EXEC>API design fixed: {problem}. Applied: {solution}. HTTP status codes now correct, error format standardized, responses consistent. API follows REST best practices with proper resource modeling, consistent naming, and appropriate status codes. Documented with OpenAPI spec.</EXEC>", f"<EXEC>API improvement: {problem} -> {solution}. Changes: HTTP semantics corrected, error handling standardized, implementation details no longer leaked. API now follows REST conventions and is easier for consumers to use correctly. Tested with contract tests.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("code","craftsmanship","api_design"))

CONCURRENCY_PROBLEMS = [
    ("a shared counter incremented by multiple threads with race conditions","Use atomic operations or mutex locks; prefer high-level concurrency primitives"),
    ("a deadlock caused by nested lock acquisition in different orders","Establish global lock ordering, use lock hierarchies, or use lock-free data structures"),
    ("a callback hell with deeply nested async operations","Use async/await, Promises, or monadic composition to flatten the chain"),
]

def _concurrency_gen():
    while True:
        for problem, solution in CONCURRENCY_PROBLEMS:
            inp = pick(f"Concurrency issue: {problem}. Identify the problem and fix.", f"Threading/async problem: {problem}. {solution}", f"Concurrency bug: {problem}. How to resolve correctly?")
            plan = pick(f"<PLAN>Concurrency fix: (1) Identify shared state and critical sections. (2) Choose synchronization mechanism: locks, atomics, channels, or STM. (3) {solution}. (4) Prevent deadlock: consistent lock ordering, timeout-based locking. (5) Test with high concurrency to verify fix. (6) Consider lock-free alternatives.</PLAN>", f"<PLAN>Address {problem}: first reproduce the condition reliably. Analyze the concurrency model -- shared memory vs message passing. {solution} provides the fix. Verify that the fix doesn't introduce new issues like deadlock or performance degradation. Document the concurrency model for future maintainers.</PLAN>")
            think = pick(f"<THINK>Concurrency bug: {problem}. Race conditions occur when multiple threads access shared state without proper synchronization. The critical section needs protection. {solution} provides appropriate synchronization. Important considerations: (1) Lock granularity -- too coarse hurts performance, too fine risks deadlock. (2) Lock ordering -- consistent ordering prevents deadlock. (3) Lock-free techniques -- CAS operations, read-copy-update for high performance. (4) Testing concurrency is hard -- use stress testing, thread sanitizers, and formal verification if critical. The best concurrency fix is often to minimize shared mutable state.</THINK>", f"<THINK>Analyzing {problem}. This is a classic concurrency hazard. The root cause is unsynchronized access to shared mutable state. {solution} fixes by ensuring mutual exclusion or using lock-free synchronization. Beyond the direct fix, consider: (1) Can the shared state be eliminated? (2) Can message passing replace shared memory? (3) Is there a higher-level abstraction that handles synchronization? (4) Are there testing strategies to prevent regression? Concurrency bugs are notoriously hard to debug because they depend on timing. Prevention through design is better than debugging after.</THINK>")
            exec_ = pick(f"<EXEC>Concurrency fix: {problem}. Applied: {solution}. Synchronization added for shared state. Deadlock prevented via consistent lock ordering. Tested with high-concurrency stress tests -- no races detected. Thread sanitizer clean. Performance impact: acceptable for safety guarantee.</EXEC>", f"<EXEC>Concurrency resolved: {problem} -> {solution}. Root cause: unsynchronized shared state. Fix: appropriate synchronization with deadlock prevention. Verified with stress testing and concurrency analyzers. Design note: minimize shared mutable state to reduce concurrency complexity.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("code","craftsmanship","concurrency"))

def chunk_4_gen():
    gens = [_naming_gen(), _structure_gen(), _err_handling_gen(), _perf_gen(), _refactor_gen(),
            _doc_gen(), _api_design_gen(), _concurrency_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════ Chunk 5: Full-Stack Web Development ═══════════════════════
# 5 categories: HTML, CSS, JS/React, TypeScript/state, testing/API

HTML_TOPICS = [
    ("a product listing page with accessibility requirements","Use semantic HTML: ul with li for products, article for each, nav for pagination, aria-labels for screen readers"),
    ("a form with validation, error messages, help text","Use form with associated label, aria-describedby for help, aria-errormessage for errors, fieldset/legend for grouping"),
    ("a responsive image gallery with lazy loading","Use picture with srcset, loading=lazy, figure with figcaption for accessibility"),
]

def _html_gen():
    while True:
        for requirement, solution in HTML_TOPICS:
            inp = pick(f"HTML semantics: {requirement}. Write semantic HTML structure.", f"Accessible HTML: {requirement}. {solution}", f"Semantic markup for {requirement}. Choose elements and ARIA.")
            plan = pick(f"<PLAN>Semantic HTML: (1) Identify content structure and meaning. (2) Choose elements: nav, main, article, section, aside, form, fieldset, legend, label, input, figure, figcaption. (3) Add ARIA where native semantics insufficient. (4) Ensure keyboard navigation and screen reader compatibility. (5) Validate with accessibility tools.</PLAN>", f"<PLAN>Build {requirement}: semantic skeleton with native HTML. ARIA only where needed. Every interactive element keyboard accessible. Test with screen reader. Structure should be meaningful even without CSS.</PLAN>")
            think = pick(f"<THINK>Designing semantic HTML for {requirement}. Principle: use elements by meaning, not appearance. Use nav for navigation, main for primary, article for self-contained content. Accessibility: all images need alt text, form inputs need associated labels, color alone shouldn't convey info, focus indicators visible. Semantic HTML is foundation of accessible, SEO-friendly, maintainable pages. Assistive technologies rely on semantic structure.</THINK>", f"<THINK>Planning HTML for {requirement}. Content-first: what is content and meaning? Semantic elements provide built-in accessibility and SEO. Use lists for list content, button for actions, a for navigation -- never one for the other. ARIA supplements, not replaces, native semantics. No ARIA is better than bad ARIA. Validate with WAVE or Lighthouse.</THINK>")
            exec_ = pick(f"<EXEC>Semantic HTML for {requirement}: {solution}. Elements: nav, main, article, section, aside, footer, form, fieldset, legend, label, input, button, figure, figcaption. ARIA: aria-label, aria-describedby, aria-errormessage. Validated: Lighthouse 95+, keyboard navigation OK, screen reader tested, WCAG AA.</EXEC>", f"<EXEC>HTML for {requirement}. Semantics: proper heading hierarchy, landmark elements, form associations correct, image handling accessible. Accessibility: perceivable, operable, understandable, robust. WCAG 2.1 AA compliant. Result: meaningful, accessible, maintainable.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("web_development","frontend","html"))

CSS_TOPICS = [
    ("a responsive grid of cards for mobile, tablet, desktop","CSS Grid with auto-fit/minmax for responsive columns without media queries"),
    ("a dark mode toggle persisting preference","CSS custom properties for theming, prefers-color-scheme for initial, localStorage for persistence"),
    ("loading spinner with no layout shift","Absolute positioned overlay with aspect-ratio container, GPU-accelerated animation"),
]

def _css_gen():
    while True:
        for requirement, solution in CSS_TOPICS:
            inp = pick(f"CSS layout: {requirement}. Design the CSS approach.", f"Responsive CSS: {requirement}. {solution}", f"CSS architecture for {requirement}. Avoid common pitfalls.")
            plan = pick(f"<PLAN>CSS approach: (1) Choose layout method -- Grid, Flexbox, or combination. (2) Visual hierarchy with sizing, spacing, color. (3) Responsiveness: relative units, min/max widths, container queries. (4) Polish: transitions, states (hover, focus), reduced-motion support. (5) Organize with BEM or CSS modules.</PLAN>", f"<PLAN>Implement {requirement}: modern CSS -- Grid for 2D, Flexbox for 1D. Apply: {solution}. Accessibility: visible focus states, sufficient contrast, zoom to 400 percent still usable. Custom properties for theming. No magic numbers -- use spacing scale.</PLAN>")
            think = pick(f"<THINK>CSS for {requirement}. Modern CSS: Grid excels at 2D layouts, Flexbox for 1D distributions, Container queries for component-level responsiveness. Approach: {solution}. Preferred because it reduces media queries, adapts naturally to content, maintains consistency. Performance: GPU-accelerated properties (transform, opacity) for animations, avoid layout-triggering (width, height, top), use content-visibility for offscreen. Maintainability: logical properties for RTL, custom properties for theme values, BEM naming.</THINK>", f"<THINK>Planning CSS for {requirement}. Decisions: Grid vs Flexbox (Grid for macro, Flexbox for micro). Units: rem for typography, em for component spacing, percent or vw/vh for layout. Methodology: BEM, CSS Modules, or utility-first. Solution {solution} addresses core challenge by intrinsic layout adapting to space, separating theme tokens from styles, using hardware-accelerated properties for 60fps animation. Accessibility: prefers-reduced-motion, prefers-color-scheme, focus-visible, zoom without breakage.</THINK>")
            exec_ = pick(f"<EXEC>CSS for {requirement}: {solution}. Layout: CSS Grid + auto-fit + minmax, Flexbox + flex-wrap + gap, or Container queries + Grid. Custom properties for theming. Responsive: works 320px-2560px, no media queries needed, adaptive. Performance: GPU-accelerated animations, no layout thrashing, efficient selectors. Accessibility: reduced-motion respected, focus-visible visible, zoom to 400 percent OK.</EXEC>", f"<EXEC>CSS implemented: {requirement}. Approach: {solution}. Architecture: utility-first with custom properties, BEM components, or CSS modules. Responsive design system with consistent spacing, typography, color scales. Performance optimized. Accessibility compliant.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("web_development","frontend","css"))

JS_TOPICS = [
    ("a React component that fetches data and handles loading, error, empty states","Use useReducer with explicit states: idle/loading/success/error, useEffect for fetch, error boundaries"),
    ("a custom hook for debounced search input","useDebounce hook: setTimeout/clearTimeout pattern, controlled input, optional leading/trailing calls"),
    ("optimistic UI updates for a todo app","Update state immediately, revert on error, use a queue for pending operations, show toast on failure"),
]

def _js_gen():
    while True:
        for requirement, solution in JS_TOPICS:
            inp = pick(f"React/JS pattern: {requirement}. Implement with best practices.", f"JavaScript architecture: {requirement}. {solution}", f"Frontend design: {requirement}. Handle states and edge cases.")
            plan = pick(f"<PLAN>Implementation approach: (1) Define component states and data flow. (2) Choose state management: useState, useReducer, or external store. (3) Handle side effects with useEffect/useCallback. (4) Implement: {solution}. (5) Add error boundaries and loading skeletons. (6) Test with all states.</PLAN>", f"<PLAN>Build {requirement}: start with state machine modeling all states. {solution} provides the pattern. Ensure: (1) All states visually represented; (2) Async operations properly cancelled on unmount; (3) Error handling with user feedback; (4) Performance with memoization.</PLAN>")
            think = pick(f"<THINK>Designing {requirement}. The key challenge is managing asynchronous state transitions. Using a state machine approach with explicit states (idle, loading, success, error) ensures all states are handled. {solution} addresses this through a reducer pattern that makes state transitions predictable and testable. Additional considerations: (1) race conditions -- use cleanup function in useEffect; (2) loading states -- skeleton or spinner; (3) error recovery -- retry mechanism; (4) empty states -- meaningful placeholder. Performance: memo expensive computations, use React.memo for pure components, virtualize long lists. Accessibility: aria-live regions for dynamic content, keyboard navigation, focus management.</THINK>", f"<THINK>Building {requirement}. The pattern in {solution} follows React best practices. For async data fetching: use a custom hook that encapsulates fetch logic, loading state, error handling, and data caching. The reducer pattern is preferred over multiple useState calls when state transitions are complex. Error boundaries catch rendering errors; for async errors, handle in the hook and set error state. Each state should have a corresponding UI: loading skeleton, error message with retry, empty state illustration, and the data view. Accessibility: use aria-live=polite for status updates, manage focus after data loads, ensure all interactive elements have accessible names.</THINK>")
            exec_ = pick(f"<EXEC>{requirement} implemented. Pattern: {solution}. State management: useReducer with loading/success/error states. Error handling: error boundary + retry. Performance: memoized callbacks, lazy loading. Accessibility: keyboard navigation, ARIA live regions, focus management. Tested with Jest and React Testing Library.</EXEC>", f"<EXEC>Frontend solution: {requirement}. Architecture: custom hook encapsulating fetch logic, reducer for state transitions, error boundary for crash protection. All UI states: loading skeleton, error with retry, empty state, data view. Performance optimized with memoization and virtualization. Accessible with proper ARIA attributes.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("web_development","frontend","react"))

TS_TOPICS = [
    ("a type-safe API client with proper error handling","Define discriminated union for ApiResponse<T>: {data: T, error: null} | {data: null, error: ApiError}, use type narrowing"),
    ("a generic hook for form state management with validation","FormState<T> type with values, errors, touched fields. Generic validators. useReducer for complex state transitions"),
    ("reducer-based state management with strict TypeScript","Discriminated union for actions, exhaustive type checking in reducer, ensureAction never for compile-time completeness check"),
]

def _ts_gen():
    while True:
        for requirement, solution in TS_TOPICS:
            inp = pick(f"TypeScript patterns: {requirement}. Provide type definitions and implementation.", f"Type-safe architecture: {requirement}. {solution}", f"TypeScript design: {requirement}. Leverage type system for safety.")
            plan = pick(f"<PLAN>TypeScript approach: (1) Define domain types modeling the data. (2) Use discriminated unions for states. (3) Leverage type narrowing for safe access. (4) {solution} ensures exhaustive handling. (5) Export strict types. (6) Use generics for reusability. (7) Never use any or type assertions.</PLAN>", f"<PLAN>Type safety for {requirement}: Start with type definitions representing all possible states. {solution} uses discriminated unions making illegal states unrepresentable. Each variant has explicit fields. Type narrowing (switch/if) ensures exhaustiveness at compile time. Generic constraints for reusability. Utility types (Pick, Omit, Partial) for flexibility.</PLAN>")
            think = pick(f"<THINK>Designing TypeScript types for {requirement}. Key principle: make illegal states unrepresentable. {solution} achieves this through discriminated unions where each variant explicitly defines its shape. This means switch statements on the discriminant require handling all cases -- TypeScript will error at compile time if any are missed. Additional benefits: type narrowing provides automatic type safety within each branch; IDE autocompletion works perfectly. For generics, constrain with extends to enable type-safe reuse. Avoid overloads where union types suffice. Prefer interfaces for objects that can be extended, types for unions and computed properties.</THINK>", f"<THINK>TypeScript architecture for {requirement}. Discriminated unions with exhaustive checking form the foundation. Each state variant is explicit: no ambiguous partial objects where fields may or may not exist. Generic constraints ensure type parameters are used correctly. Utility types derive new types from existing ones without repetition. Type inference should work automatically -- avoid explicit annotations where the compiler can infer. For complex state management, derive the action union from a mapped type to ensure reducer handles all actions. The never type serves as an exhaustiveness check in default cases.</THINK>")
            exec_ = pick(f"<EXEC>TypeScript types for {requirement}: {solution}. Uses discriminated unions, exhaustive checking, generic constraints. All illegal states prevented at compile time. Zero runtime type assertions. Fully type-safe with automatic narrowing and inference. Tested with strict TypeScript config (strictNullChecks, noImplicitAny).</EXEC>", f"<EXEC>TypeScript solution: {requirement}. Architecture: discriminated unions, generic types, mapped types for derived types. Exhaustiveness checked via never type in default case. Compile-time safety for all state transitions. Interfaces for public API, types for unions. Strict mode enforced.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("web_development","frontend","typescript"))

TEST_TOPICS = [
    ("testing a React form with validation, async submission, and error handling","React Testing Library with user-event, mock API calls, test each state: validation errors, loading, success, server error"),
    ("integration test for a REST API with authentication and database","Supertest + testcontainers for isolated DB, beforeAll/beforeEach setup, test happy path + auth failures + validation + 404"),
    ("end-to-end test for a checkout flow","Playwright/Cypress: page objects for cart, checkout, payment confirmation. Test full flow with test payment gateway sandbox"),
]

def _test_gen():
    while True:
        for requirement, solution in TEST_TOPICS:
            inp = pick(f"Testing strategy: {requirement}. Design comprehensive tests.", f"Test architecture: {requirement}. {solution}", f"Write tests for {requirement}. Cover all states and edge cases.")
            plan = pick(f"<PLAN>Testing approach: (1) Identify test levels: unit, integration, E2E. (2) Mock boundaries/external services. (3) Cover: happy path, error states, edge cases, empty states. (4) Arrange-Act-Assert structure. (5) {solution}. (6) Test isolation: fresh state per test. (7) Run in CI.</PLAN>", f"<PLAN>Comprehensive tests for {requirement}: Start with test plan enumerating scenarios. {solution} provides framework. For each test: clear description, minimal setup, single assertion focus, proper cleanup. Use factories/builders for test data. Avoid testing implementation details -- test behavior. Aim for high confidence, not high coverage numbers.</PLAN>")
            think = pick(f"<THINK>Testing {requirement}. Key principle: test behavior, not implementation. Focus on user-observable outcomes. {solution} follows this by testing from user perspective. For UI tests: find elements by role/label, trigger realistic user interactions via user-event, assert on rendered output. For API tests: test against real DB (testcontainers), verify response status + body + side effects. For E2E: focus on critical user journeys. Testing trophy: more integration tests than unit or E2E, giving best confidence per test. Avoid: snapshot tests (brittle), testing private methods, excessive mocking (tests pass but app broken).</THINK>", f"<THINK>Designing tests for {requirement}. Test categories: (1) Unit: pure functions, utilities, isolated logic. (2) Integration: component + real dependencies (DB, API). (3) E2E: critical user flows. {solution} targets the appropriate level. For each test: Arrange (set up preconditions), Act (perform action), Assert (verify outcome). Test data: use factories to create realistic data, avoid shared mutable state between tests. Mock at boundaries (network, file system) using dependency injection. Assert on output/behavior, not internal state. This gives tests that catch regressions without being brittle.</THINK>")
            exec_ = pick(f"<EXEC>Tests for {requirement}: {solution}. Levels: unit (pure logic), integration (component+API), E2E (critical flows). Coverage: happy path, validation errors, loading states, server errors, empty states, edge cases. All tests independent and isolated. CI pipeline runs before merge. Average test time under 30 seconds.</EXEC>", f"<EXEC>Test suite for {requirement}. Strategy: {solution}. Tests: X unit, Y integration, Z E2E. Coverage: all states tested, error paths covered, edge cases documented. Mock strategy: external APIs mocked, internal modules tested with real dependencies. CI integration: pre-commit hooks for fast tests, full suite in CI. Confidence: high.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("web_development","testing","quality"))

API_INTEGRATION_TOPICS = [
    ("a frontend that fetches data without error handling for network failures","Wrap fetch in try/catch, show user-friendly error messages, implement retry with exponential backoff"),
    ("a REST client that doesn't handle token expiration or refresh","Implement interceptor for 401 responses, refresh token flow, retry original request with new token"),
    ("a GraphQL client fetching data in nested components causing N+1 queries","Use data loader pattern, batch queries, or Apollo cache with normalized data"),
]

def _api_integration_gen():
    while True:
        for requirement, solution in API_INTEGRATION_TOPICS:
            inp = pick(f"API integration: {requirement}. Implement robust client-side data fetching.", f"Frontend API client: {requirement}. {solution}", f"Network resilience: {requirement}. Build a robust client.")
            plan = pick(f"<PLAN>API integration approach: (1) Define API client layer abstracting network details. (2) Handle all states: loading, success, error, timeout. (3) {solution}. (4) Implement retry logic with exponential backoff. (5) Add request/response interceptors for auth, logging. (6) Type all API responses for type safety.</PLAN>", f"<PLAN>Build robust API client for {requirement}: (1) Centralized fetch wrapper. (2) Auth token management with refresh. (3) Error classification: network vs server vs client. (4) Retry strategy. (5) Request deduplication. (6) Cancellation support. (7) {solution} addresses the specific issue.</PLAN>")
            think = pick(f"<THINK>Designing API integration: {requirement}. A robust API client handles network unreliability transparently. {solution} addresses the issue. Key layers: (1) Transport -- fetch/axios with timeouts and retries. (2) Auth -- token storage, refresh, re-attach. (3) Error handling -- classify errors, show appropriate UI, provide recovery paths. (4) Caching -- avoid redundant requests, invalidate on mutation. (5) Optimistic updates -- show immediate feedback, revert on failure. The API client should be the single source of truth for server communication, used by all components. This centralizes error handling, retry logic, and token management.</THINK>", f"<THINK>Building API client for {requirement}. The core challenge is synchronizing server state with the UI. {solution} provides the pattern. State management: use React Query, SWR, or a custom solution that manages caching, background refetching, and optimistic updates. Each API call should be wrapped in a layer that handles: serialization/deserialization, authentication headers, error normalization, timeout handling, and cancellation. The UI layer should be unaware of these concerns -- it just calls a typed function and gets back typed data or typed errors. This separation of concerns makes both layers simpler and more testable.</THINK>")
            exec_ = pick(f"<EXEC>API integration for {requirement}: {solution}. Architecture: typed API client layer with interceptors, retry logic with exponential backoff, token refresh, request deduplication, caching. Error handling: network errors retried, auth errors trigger refresh, server errors shown to user. All API types generated from OpenAPI spec.</EXEC>", f"<EXEC>API client implemented: {requirement}. Solution: {solution}. Features: automatic retry, token management, request caching, optimistic updates, error normalization. Integrated with React Query for server state management. All endpoints typed and documented. Tested with MSW for reliable integration tests.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(3,6), pick("web_development","fullstack","api"))

BUILD_TOPICS = [
    ("a project with slow CI pipeline taking 30 minutes","Parallelize jobs, cache dependencies, use incremental builds, split test suite"),
    ("a monorepo where changing one package rebuilds everything","Use Nx/Turborepo for affected project detection, shared caching, distributed task execution"),
    ("a production build that fails only in CI not locally","Use Docker for consistent environments, reproduce CI image locally, pin all dependency versions"),
]

def _build_gen():
    while True:
        for problem, solution in BUILD_TOPICS:
            inp = pick(f"Build/deploy pipeline: {problem}. Optimize the development workflow.", f"CI/CD issue: {problem}. {solution}", f"DevOps problem: {problem}. Improve build and deployment process.")
            plan = pick(f"<PLAN>Build pipeline optimization: (1) Profile current pipeline to identify bottlenecks. (2) Implement: {solution}. (3) Add caching layers (dependency cache, build cache). (4) Parallelize independent jobs. (5) Use incremental builds. (6) Set up preview deployments for PRs. Measure before/after to validate improvements.</PLAN>", f"<PLAN>Fix build issue: {problem}. Start by reproducing the problem consistently. {solution} addresses the root cause. Ensure: (1) Builds are deterministic -- same input produces same output. (2) CI environment matches production as closely as possible. (3) Fail fast -- early validation before expensive steps. (4) Clear error messages when builds fail.</PLAN>")
            think = pick(f"<THINK>Build pipeline problem: {problem}. A smooth development workflow is essential for team productivity. {solution} addresses the bottleneck. Key considerations: (1) Speed -- developers should wait less than 5 minutes for feedback. (2) Reliability -- flaky builds destroy trust. (3) Reproducibility -- builds should work the same everywhere. (4) Visibility -- clear logs and metrics on build performance. Beyond the immediate fix, consider: implementing remote caching (Nx, Turborepo, Bazel), moving to monorepo tools, using build-less development (Vite HMR), and setting up automated dependency updates. The build pipeline should be treated as a product -- continuously improved based on team feedback.</THINK>", f"<THINK>Analyzing {problem}. Build/deploy issues compound over time as projects grow. {solution} addresses the specific bottleneck. Good practices: (1) Dependency management -- lock files, deterministic installs, vulnerability scanning. (2) Caching -- layer caching in Docker, cache node_modules between CI runs. (3) Parallelism -- split test suite into shards, parallelize lint/typecheck/build. (4) Incrementality -- only rebuild changed files. (5) Environment parity -- Docker for dev/CI/prod consistency. The goal is fast, reliable, repeatable builds that catch issues early. Invest in build tooling as the project grows.</THINK>")
            exec_ = pick(f"<EXEC>Build pipeline improved: {problem}. Applied: {solution}. CI time reduced from 30min to under 5min. Caching implemented for dependencies and build outputs. Parallel job execution across shards. Docker environment ensures consistency. Developer feedback time significantly improved.</EXEC>", f"<EXEC>CI/CD fix: {problem} -> {solution}. Implemented: dependency caching, incremental builds, parallel sharding, Docker-based CI. Build reliability now 100 percent on main branch. Preview deployments for every PR. Monorepo tooling with affected project detection.</EXEC>")
            yield (inp, plan, think, exec_, random.randint(2,5), pick("web_development","devops","build"))

def chunk_5_gen():
    gens = [_html_gen(), _css_gen(), _js_gen(), _ts_gen(), _test_gen(),
            _api_integration_gen(), _build_gen()]
    while True:
        for g in gens:
            yield next(g)

# ════════════════════════════════════════════════════════════════════════
# Load chunks 6-15 extension
# ════════════════════════════════════════════════════════════════════════

_ext_dir = os.path.dirname(os.path.abspath(__file__))
try:
    sys.path.insert(0, _ext_dir)
    from chunk_extension import CHUNK_GENS_EXT, CHUNK_NAMES_EXT, CHUNK_DOMAINS_EXT
    _has_ext = True
except ImportError:
    _has_ext = False
    print("WARNING: chunk_extension.py not found. Chunks 6-15 unavailable.")

CHUNK_GENS = {1: chunk_1_gen, 2: chunk_2_gen, 3: chunk_3_gen, 4: chunk_4_gen, 5: chunk_5_gen}
CHUNK_NAMES = {1: "Foundational Reasoning", 2: "Metacognition & Self-Awareness",
               3: "Novel Architecture Invention", 4: "Beautiful Code Craftsmanship",
               5: "Full-Stack Web Development"}
CHUNK_DOMAINS = {1: "reasoning", 2: "metacognition", 3: "architecture", 4: "code", 5: "web_development"}

if _has_ext:
    CHUNK_GENS.update(CHUNK_GENS_EXT)
    CHUNK_NAMES.update(CHUNK_NAMES_EXT)
    CHUNK_DOMAINS.update(CHUNK_DOMAINS_EXT)

# ════════════════════════════════════════════════════════════════════════
# MAIN: argparse, chunk routing, streaming write, validation output
# ════════════════════════════════════════════════════════════════════════

def parse_chunks(s: str) -> list:
    """Parse '1-5' or '1,3,5' or '1' format into list of chunk ints."""
    chunks = []
    for part in s.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            chunks.extend(range(int(a), int(b)+1))
        else:
            chunks.append(int(part))
    return sorted(set(chunks))

def write_jsonl(path: str, gen: Iterator, num: int, chunk_id: int):
    """Stream-write num examples from generator to path, counting as we go."""
    count = 0
    with open(path, 'w') as f:
        for inp, plan, think, exec_, level, domain in gen:
            target = f"{plan}{think}{exec_}"
            record = json.dumps({
                "input": inp,
                "target": target,
                "cognitive_level": level,
                "domain": domain,
                "chunk": chunk_id,
            })
            f.write(record + '\n')
            count += 1
            if count >= num:
                break
    return count

def main():
    parser = argparse.ArgumentParser(description="Keli10K Chunk Generator")
    parser.add_argument('--chunks', default='1-5', help='Chunks to generate (e.g., 1-5, 1,3,5)')
    parser.add_argument('--num', type=int, default=100000, help='Examples per chunk (default 100000)')
    parser.add_argument('--validate', type=int, default=500, help='Validation examples per chunk (default 500)')
    parser.add_argument('--output', default=_BASE, help='Output base directory')
    args = parser.parse_args()

    chunks = parse_chunks(args.chunks)
    total = 0
    val_total = 0

    for cid in chunks:
        if cid not in CHUNK_GENS:
            print(f"Warning: chunk {cid} not defined, skipping")
            continue

        gen_fn = CHUNK_GENS[cid]
        name = CHUNK_NAMES.get(cid, f"Chunk {cid}")
        domain = CHUNK_DOMAINS.get(cid, "general")

        # Training
        train_dir = os.path.join(args.output, "chunks")
        os.makedirs(train_dir, exist_ok=True)
        train_path = os.path.join(train_dir, f"chunk_{cid:02d}.jsonl")

        if os.path.exists(train_path):
            os.remove(train_path)

        print(f"Generating {args.num:,} training examples for Chunk {cid}: {name}...")
        gen = gen_fn()
        written = write_jsonl(train_path, gen, args.num, cid)
        total += written
        print(f"  -> wrote {written:,} to {train_path}")

        # Validation
        val_dir = os.path.join(args.output, "chunks_val")
        os.makedirs(val_dir, exist_ok=True)
        val_path = os.path.join(val_dir, f"chunk_{cid:02d}.jsonl")

        if os.path.exists(val_path):
            os.remove(val_path)

        # Use fresh generator (generators are infinite so we just take next N)
        gen2 = gen_fn()
        val_written = write_jsonl(val_path, gen2, args.validate, cid)
        val_total += val_written
        print(f"  -> wrote {val_written:,} validation to {val_path}")

    print(f"\nDone! Total training: {total:,}, Total validation: {val_total:,}")
    print(f"Output: {args.output}")

if __name__ == '__main__':
    main()
