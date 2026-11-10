# Curated editorial data for Portfolio V2 (themes, connections, placeholders).
# Project records themselves live in the `items` array of Main.dc.html.

THEMES = [
    {
        "id": "t1", "n": "01", "hash": "thinking-understand",
        "short": "Understand people",
        "title": "Understand people. Continuously.",
        "q": "How do we know we’re still solving the right problem, for the right people?",
        "covers": "Continuous research, needs, mental models, evaluation, learning loops.",
        "paras": [
            "Research was part of how I worked long before “User Researcher” was my title: rebuilding a bootcamp from what each cohort told us, finding the moments where customers most need to understand, staying with designers for three months after the demo.",
            "The methods change. The loop doesn’t: listen, adapt, improve, and check again.",
        ],
        "order": ["rbk", "programme", "stress", "algo_journey", "algo_personas", "algo_academy", "mind", "clinic", "clear",
                  "system", "plm", "prio", "sat3d", "aiid", "vizcom", "cassandre"],
    },
    {
        "id": "t2", "n": "02", "hash": "thinking-knowledge",
        "short": "Make knowledge everyone’s business",
        "title": "Make knowledge everyone’s business.",
        "q": "What if expertise made people more independent, not more dependent?",
        "covers": "Knowledge transmission, learning systems, research democratisation, collective intelligence.",
        "paras": [
            "I don’t measure my value by how many people need me. I want the teams I work with to become more capable and autonomous.",
            "So I keep building the same kind of thing: systems, routines, tools and practices that let people learn, improve and decide without waiting for an expert.",
        ],
        "order": ["teach", "algo_academy", "system", "usab", "community", "superpowers", "agents", "cassandre"],
    },
    {
        "id": "t3", "n": "03", "hash": "thinking-automate",
        "short": "Automate the predictable",
        "title": "Automate the predictable. Make room for the unknown.",
        "q": "Why spend human intelligence on problems we already know how to identify?",
        "covers": "Automation, research tools, AI, methodological rigour, where human attention goes.",
        "paras": [
            "AI is the latest tool in this journey, not its starting point.",
            "The idea is older than the technology: automate what we already know how to check, and keep human attention for what we don’t understand yet.",
        ],
        # Cassandre is on this thread too, shown as its closing block rather than in the grid.
        "order": ["swiss", "agents", "aiid", "vizcom", "cassandre"],
    },
]

T3_STEPS = [
    "First, I developed methodologies and taught people to use them.",
    "Then, I built tools to make these methodologies accessible.",
    "When conversational AI became available, I started turning them into assistants.",
    "Now, with Cassandre, I am exploring how to make part of this methodology executable and automated.",
]

T2_TODO = [
    "Peer working and cross-functional mentoring",
    "Training PMs, designers and support teams in research principles",
    "Research decision trees",
    "Heuristic evaluation guidelines",
    "Training on cognitive biases",
    "Turning customer support tickets into reusable user knowledge",
    "Involving cross-functional colleagues in interviews and co-design",
]
T3_TODO = [
    "Research Plan Generator",
    "Interview guide and questionnaire review tools",
]

# Curated connections. Each pair shows on both projects (max 3 per project, in this order).
LINKS = [
    ("algo_academy", "system", "From helping people understand a product to helping teams understand their users."),
    ("system", "agents", "From documenting research methods to making them accessible through conversation."),
    ("agents", "cassandre", "From helping teams ask better questions to automatically checking what can already be verified."),
    ("rbk", "system", "Different environments. The same principle: listen, adapt, improve."),
    ("rbk", "programme", "One rough first cohort, then a habit: let each cohort teach the next."),
    ("stress", "rbk", "Same bootcamp, two ways of listening: one-to-one conversations and a stress measure."),
    ("stress", "tracking", "Measuring what people go through to adjust their conditions. Years later, I tried it on myself."),
    ("vizcom", "aiid", "The survey said what designers wanted from AI. The diary showed what they did with it over three months."),
    ("vizcom", "sat3d", "Two ways of staying with users over time: a three-month diary and a monthly pulse."),
    ("swiss", "agents", "A method first, then assistants that carry methods to people who never asked for one."),
    ("swiss", "cassandre", "AI runs the predictable part, a human decides what matters. Same split, one step further."),
    ("aiid", "agents", "Studying how others adopt AI, while building assistants for my own teams."),
    ("system", "community", "A shared repository for five teams, then a shared space for the researchers themselves."),
    ("community", "superpowers", "The same bet twice: the expertise is already in the building, people just can’t find each other."),
    ("algo_journey", "algo_personas", "Who is learning, and when they most need to understand: two halves of one question."),
    ("algo_journey", "clinic", "Finding the moments that matter in a journey: for customers implementing a product, for members seeking care."),
    ("mind", "clinic", "Two Alan products, one starting point: understand how people think about care before designing for it."),
    ("mind", "tracking", "Mental health, studied for a product, then tracked for myself."),
    ("prio", "plm", "Who decides which products get made, and how engineers keep them alive afterwards: two ends of the same pipeline."),
    ("prio", "system", "Atomic research, built as a repository in one project and used as the analysis method in the other."),
    ("usab", "sat3d", "Evaluative research made readable: a verdict in ten seconds, a pulse every month."),
    ("usab", "cassandre", "Making a usability verdict readable was one step. Checking the predictable issues before any participant is the next question."),
    ("teach", "algo_academy", "From classrooms to an academy: still working out where someone really is before deciding where to take them."),
    ("programme", "sat3d", "A cohort retrospective and a monthly survey are the same reflex: ask again, regularly."),
]

SUBSTANTIAL = ["aiid", "vizcom", "system", "prio", "plm", "sat3d", "usab", "swiss", "clinic", "mind", "clear",
               "algo_journey", "algo_personas", "stress", "rbk", "programme", "algo_academy", "agents", "community"]

ALL_CASES = ['aiid', 'vizcom', 'system', 'prio', 'plm', 'sat3d', 'usab', 'agents', 'swiss', 'community', 'superpowers',
             'clinic', 'mind', 'clear', 'algo_academy', 'algo_journey', 'algo_personas', 'rbk', 'stress', 'programme',
             'simplon', 'teach', 'embassy', 'workshops', 'sistech', 'bsf', 'vgwb', 'daradam', 'tracking', 'bastille',
             'palier', 'askip', 'oasis', 'papier']

EXTRA_TITLES = {"programme": "Better from cohort to cohort", "cassandre": "Cassandre"}


def links_for(pid, cap=3):
    out = []
    for a, b, why in LINKS:
        if a == pid:
            out.append((b, why))
        elif b == pid:
            out.append((a, why))
    return out[:cap]


def themes_for(pid):
    return [t for t in THEMES if pid in t["order"]]
