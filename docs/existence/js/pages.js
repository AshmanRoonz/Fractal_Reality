// Existence: one paragraph per page.
// k: title | p (paragraph) | q (question) | th (thesis, opens a chapter) | sym | tbl
// a: the plate algorithm drawn beside the text. ch: chapter name for pages that open one without a thesis.
window.PAGES = [
{k:"title", a:"circumpunct", x:"You are one person. You are also trillions of cells, a stream of thoughts and feelings, a body that meets the world, and a part of every relationship you are in. This short book asks how all of that holds together, and what follows for how we treat each other. It starts from one simple figure, a point inside a circle, and asks you to test it against your own life."},

{k:"p", a:"hand", ch:"Look at your hand", x:"Look at your hand."},
{k:"q", a:"phyllotaxis", x:"How many things are you looking at?"},
{k:"p", a:"mandel", o:{spot:1}, x:"One hand. Several fingers. Skin, joints, cells. Each answer notices something different about what is already there."},
{k:"p", a:"ifs", o:{kind:"fern"}, x:"Your hand is a whole with parts, and a part of you. Its parts belong to it. It belongs to you. Both relationships hold at once."},
{k:"q", a:"pythagoras", x:"How much of your life has that same structure?"},

{k:"th", a:"nested", x:"I am whole. I am part."},
{k:"p", a:"tree", x:"My parts form one living body. My life participates in lives beyond my own. I can be whole in relation to my parts and part in relation to something greater."},
{k:"p", a:"julia", x:"Yet wholeness is only one way of being one."},
{k:"p", a:"rose", x:"Imagine a circle. You can divide its circumference into arcs. What could you divide its exact center into?"},
{k:"p", a:"mandel", o:{spot:4}, x:"As a geometric point, the center has position without spatial extent. It has no smaller spatial parts. It is one through indivisibility."},
{k:"p", a:"lightning", x:"Even this partless point has relationships. Every point on the circle stands at the same distance from it. Having relationships does not require having parts."},
{k:"sym", a:"circumpunct", x:"Now hold the center and circle together:"},
{k:"p", a:"flow", x:"This is the circumpunct. A center, a surrounding field, a boundary. One symbol with distinguishable aspects, each meaningful through its relationships with the others."},
{k:"q", a:"julia", x:"What might it help us notice about being someone?"},

{k:"th", a:"attractor", x:"I have a point of view, a path through spacetime, a body for interface, and a mind for perception."},
{k:"p", a:"nested", x:"I call the point of view **soul**: the center from which experience occurs. I call **mind** the field through which perceptions, thoughts, feelings, memories, and intentions relate. I call **body** the boundary and interface through which this life meets the world. The **path** is its continuity through time."},
{k:"p", a:"rings", x:"A sound can become meaningful through a memory. That memory can stir a feeling. The feeling can shape a response. What I say then reaches another person through my body. Their response enters my experience. Center, field, boundary, and path participate in the same encounter."},

{k:"th", a:"circumpunct", x:"Consciousness is centered wholeness."},
{k:"p", a:"newton", x:"That is the central proposal of this framework. The subject is the center. The person is the whole. Consciousness names that wholeness as experienced from its center."},

{k:"th", a:"koch", x:"I am a circumpunct whole."},
{k:"p", a:"phyllotaxis", x:"Many distinguishable experiences can belong to one perspective. I can hear, see, remember, and wonder together. My proposal is that the center itself remains unchanged while its relationships, and the contents and organization of experience, change. Becoming belongs to the living whole. The geometric point helps express this commitment; the argument for an indivisible subject must go further than the drawing."},

{k:"th", a:"mandel", o:{spot:0}, x:"Existence is 1."},
{k:"p", a:"ifs", x:"Anything that exists is already included in existence. If something existed beyond what we had called existence, our description would have left something out."},
{k:"p", a:"flow", x:"This is oneness through inclusion. It requires no enclosing boundary. Wholeness is one type of one within existence."},
{k:"q", a:"circumpunct", o:{lone:1}, x:"If there was nothing, that'd be the only thing."},

{k:"th", a:"koch", x:"Oneness has dimensionality."},
{k:"tbl", a:"nested", x:"The word *one* keeps returning, with different work to do:",
  head:["Symbol", "Aspect", "Form of oneness"],
  rows:[
    ["∞", "Existence", "Inclusion"],
    ["0D / •", "Center or soul", "Indivisibility"],
    ["1D / —", "Path through time", "Continuity"],
    ["2D / ○", "Body as boundary and interface", "Distinction"],
    ["3D / Φ", "Mind as a field of relationships", "Coherence"],
    ["4D / ⊙", "Centered wholeness", "Integration"]
  ]},
{k:"p", a:"dragon", x:"These dimensional labels organize the framework. Here, 4D names the integration of center, path, body, and mind as one experienced whole. Calling the body's interface 2D or the mind's field 3D assigns a role in this map; establishing a correspondence with physical dimensions requires further work."},
{k:"p", a:"pythagoras", x:"The aspects have an order of integration: center, path, boundary, field, whole. Each adds a relationship to the account. Looking outward from an already formed center gives another order: soul, mind, body, world. A direction through a whole and an account of how its aspects belong together answer different questions."},
{k:"p", a:"julia", x:"Indivisibility and integration also answer different questions. A center is one without smaller parts. A whole is one through the relationships of its parts. Both can belong to the same being."},

{k:"th", a:"ifs", x:"One thing is never just one thing."},
{k:"p", a:"attractor", x:"I am singular in perspective, continuous through my path, distinct through my boundary, coherent through my mind, integrated as a whole, and included in existence."},
{k:"q", a:"rose", x:"Which kind of one are we noticing when we say “one person”?"},
{k:"p", a:"mandel", o:{spot:6}, x:"The wider metaphysical picture begins with two primitives: the unbounded, ∞, and infinitely many indivisible, persistent centers. I associate ∞ with inexhaustible potential and, in theological language, call it God. I call the multiplicity of centers the soul matrix. These are starting commitments of the fuller framework. Inclusion alone does not establish infinity."},
{k:"p", a:"newton", x:"Location individuates the center in this account. What kind of location does that require, and how does it relate to a changing body and world? Those questions need a more precise answer than the image of a point supplies."},
{k:"p", a:"flow", x:"A soul's wholeness is its lived relationship with that unbounded reality. The path, body, and mind give this relationship a particular expression. Each life has its own perspective, history, limits, and possibilities."},
{k:"p", a:"nested", x:"In this account, ∞ is neither whole nor part. Centered wholes occur within existence, and their nesting has no final, greatest whole. This is the framework's open-ended commitment: every whole participates beyond itself. How far that nesting can be established remains a question for investigation."},

{k:"th", a:"rose", x:"The whole lives through its relationships."},
{k:"p", a:"rings", x:"Consider listening to someone you care about."},
{k:"p", a:"flow", x:"Their words arrive amid your memories, expectations, bodily state, and attention. You may hear an accusation, a request, a joke, or something you have never understood before. A response takes shape. You speak, pause, reach out, or turn away. The encounter changes what can happen next."},
{k:"p", a:"lightning", x:"The framework describes this movement through **convergence, branching, emergence, and recursion**. Influences gather into a particular encounter. Paths of response and connection differentiate. Their relationships support an emerging whole. What emerges then participates in further activity."},
{k:"p", a:"phyllotaxis", x:"In its fuller metaphysical account, potential converges through a center and emerges through path, body, and mind. The center is always surrounded. What converges is conditioned by those surroundings, including the body's and mind's filters. I describe this convergence as compression: a wider reality takes a particular, limited form in experience."},
{k:"p", a:"attractor", x:"The encounter has outward expression in the world and inward wholeness as experience. Recursion carries the changed conditions into the next encounter through the same persisting center."},
{k:"p", a:"dragon", x:"What happens changes the conditions of what can happen."},
{k:"p", a:"tree", x:"This gives time a place in the circumpunct. The future names possibilities. The present is the centered whole in which an encounter is lived. The past continues through its consequences: memories, habits, skills, bodily changes, relationships, and surroundings."},
{k:"p", a:"koch", x:"Your boundary has a history. So does the way you meet what reaches it. A learned skill can open an encounter that once overwhelmed you. A familiar expectation can make a new encounter seem already understood."},
{k:"q", a:"julia", x:"What are you bringing into this moment that the moment itself did not give you?"},

{k:"th", a:"newton", x:"I participate in what becomes real for me."},
{k:"p", a:"lightning", x:"Focus has both a direction and a manner. What am I attending to? How am I attending?"},
{k:"p", a:"rings", x:"The soul has no orientation of its own. It is oriented only through its whole: the relationships of path, body, mind, and world. These relationships shape both what I attend to and how I receive and respond. I can listen with curiosity, fear, impatience, care, or the determination to be right. Each can shape what I notice and how I act."},

{k:"th", a:"circumpunct", o:{aperture:1}, x:"The aperture is the whole. The hole in the whole is the center."},
{k:"p", a:"phyllotaxis", x:"The center stays open. What changes is what converges through it and how that convergence is shaped. Focus concerns what I attend to; my mental and physical states help shape how I receive and respond. The breadth and selectivity of attention belong to these changing relationships. I can attend closely to a single voice or become aware of the room around it."},
{k:"p", a:"flow", x:"Within the constraints of Reality, what I focus on and how I focus affect the emergence of my Reality. My participation occurs alongside the choices of others, material conditions, and events beyond my control. It still makes a difference."},
{k:"q", a:"newton", x:"How does the whole redirect its focus, and how does that change what it becomes? This is a question about the activity of the circumpunct: center, path, body, and mind participating together."},

{k:"th", a:"nested", x:"One within. One among."},
{k:"p", a:"ifs", x:"Recursion also occurs across scales. A cell participates in an organ, an organ in a body, a person in a community. A whole with many parts can function as one participant in a greater organization."},
{k:"p", a:"mandel", o:{spot:5}, x:"Represented at that wider scale, the whole can take the role of a point. Its internal complexity remains. This unity as a participant is distinct from the indivisibility proposed for a subject."},
{k:"p", a:"rings", x:"The mind's field connects the one and the many within a person. The fuller framework extends this idea to a common field of relationships, organized within and among wholes. What is outside one boundary may be inside another. Two people can share a conversation while each experiences it from their own center."},
{k:"q", a:"julia", x:"Shared participation leaves an important question open: under what conditions would a greater whole have a perspective of its own?"},
{k:"p", a:"dragon", x:"I call the recurrence of one and many a **fractal of existence**. The phrase names a pattern to explore: wholes within relationships, parts that are themselves wholes, and perspectives from which those relationships become visible. Existence includes this recurrence; its oneness by inclusion has a different role from the integration recurring within it."},

{k:"th", a:"rings", o:{pair:1}, x:"I am whole. I am part. You are whole. You are part."},
{k:"p", a:"pythagoras", x:"This becomes an ethical commitment when I ask how we ought to participate."},
{k:"p", a:"tree", x:"A relationship, family, community, or institution asks something of its participants. Each participant also has a life of their own. I want forms of belonging that recognize both."},
{k:"p", a:"koch", x:"A boundary helps us protect what matters and make connection possible. Sometimes care asks us to open a boundary. Sometimes it asks us to maintain one, change the terms of participation, or leave."},
{k:"tbl", a:"rose", x:"The framework gives me questions to carry into those choices:",
  head:["Aspect", "Ethical orientation", "Question"],
  rows:[
    ["Center", "True", "What is true here?"],
    ["Path", "Faithful", "What am I continuing, and to what am I remaining faithful?"],
    ["Boundary", "Good", "What am I trying to protect, and how am I trying to connect?"],
    ["Field", "Right", "How does my participation fit with the lives and circumstances involved?"],
    ["Wholeness", "Experience and participation", "What whole are we helping form, and what is it like to live within it?"]
  ]},
{k:"p", a:"attractor", x:"Truth gives faithfulness something worth continuing. Faithfulness can include correction. A good boundary supports protection and connection. Right participation considers how our choices affect the wider field. The whole we experience carries the consequences of these relationships together."},
{k:"p", a:"julia", x:"These are values I bring to the framework. A circle cannot decide them for us."},
{k:"p", a:"lightning", x:"What I care about matters. What you care about matters. When those cares conflict, we have work to do: listen, give reasons, examine consequences, make decisions, and remain willing to revise them."},
{k:"p", a:"flow", x:"Wholeness can contain tension, disagreement, and unfinished work. What matters is also how the parts are treated as the whole continues to form."},

{k:"th", a:"mandel", o:{spot:3}, x:"There are many ways to be one, and each is itself one way."},
{k:"p", a:"pythagoras", x:"The Circumpunct Framework is my attempt to think these relationships together. Its claims must remain answerable to experience, reasons, and counterexamples. Its value depends on what it helps us notice and whether its distinctions hold up when questioned."},
{k:"p", a:"hand", o:{left:1}, x:"Look again at your hand."},
{k:"p", a:"ifs", x:"One hand, with parts. One part of you. An interface through which you can touch another hand."},
{k:"q", a:"circumpunct", x:"What changes when you begin to notice how many ways there are to be one?"},

// ---------- Part Two: The Ways of the Whole ----------
// k: part (part opening) | pp (titled page). t: the page title; p: its paragraphs.
{k:"part", a:"nested", n:"Part Two", t:"The Ways of the Whole", x:"*Look at your hand. You know what it is by now: one thing that is never just one thing. This part of the book asks what the whole does: how a centered life receives, defends, breaks, and reopens. Bring your own.*"},

{k:"pp", a:"hand", t:"One and many, again", p:[
  "One hand. Several fingers. A whole with parts, a part of you.",
  "You are also trillions of cells, a stream of thoughts, a body meeting the world, and a part of every relationship you are in. How much of your life has that structure? Almost all of it.",
  "I am whole. I am part."]},
{k:"pp", a:"circumpunct", t:"The whole you are", p:[
  "A center from which experience occurs. A path through time. A boundary that distinguishes and connects. A field where perceptions, thoughts, feelings, memories, and intentions cohere.",
  "Consciousness is centered wholeness. The subject is the center. The person is the whole.",
  "I am a circumpunct whole."]},
{k:"pp", a:"attractor", t:"What changes", p:[
  "The center itself remains unchanged while its relationships change. Its contents change. Its organization changes.",
  "Becoming belongs to the living whole.",
  "The geometric point expresses the commitment. The argument for an indivisible subject must go further than the drawing, and this part of the book is that further argument, made from inside."]},
{k:"pp", a:"flow", t:"Always surrounded", p:[
  "The center is always surrounded. Being surrounded is not the soul's circumstance. It is its condition.",
  "A center without a field is not a soul. It is not anything.",
  "Nothing unfiltered ever happens to anyone. Every experience arrives *through*."]},
{k:"pp", a:"mandel", t:"Compression", p:[
  "What converges through a center takes a particular, limited form. I call this compression: a wider reality, rendered.",
  "All experience is compression. Finitude is not a failure; it is the architecture.",
  "Every wholeness is a partial rendering of existence."]},
{k:"pp", a:"circumpunct", o:{aperture:1}, t:"The aperture", p:[
  "The center stays open. It did not choose to experience, and it cannot choose to stop. Openness is not the soul's act. It is the soul's kind.",
  "What changes is what converges, and how the convergence is shaped. The hole in the whole does not change. Focus changes. Filters change."]},
{k:"pp", a:"lightning", t:"Focus", p:[
  "Focus has a direction and a manner. What am I attending to? How am I attending?",
  "The soul has no orientation of its own. It is oriented only through its whole.",
  "Within the constraints of Reality, what I focus on and how I focus affect the emergence of my Reality, alongside the choices of others and events beyond my control.",
  "It still makes a difference."]},
{k:"pp", a:"circumpunct", o:{lone:1}, t:"Where I am", p:[
  "Location individuates the center. What kind of location?",
  "Right where I am. Here, now: the place experience happens from.",
  "Every center can say “here” with equal right. The soul matrix has no ranking in it. Whatever hierarchies exist among persons live in the wholes (in relations, roles, renderings), never in the openness.",
  "All centers equal by position. All difference made by organization."]},
{k:"pp", a:"nested", t:"The circle without a dot", p:[
  "Wholes within wholes. A cell in an organ, an organ in a body, a person in a community.",
  "A whole with many parts can function as one participant at a greater scale, taking the role of a point while its complexity remains.",
  "But a role is not a soul. Societies are circles without dots. Their center is not a someone. It is a shared goal or, deeper, a shared shape.",
  "Groups that fuse identity with their goal escalate when proven wrong; groups that hold it as a goal revise."]},
{k:"pp", a:"tree", t:"Roles", p:[
  "A shared goal gives each member a role. Roles are real parts of persons, and they are the most perishable parts: given mostly from outside, taken away by change.",
  "When a goal dies, the role loses its anchor. Grief follows, and grief runs in two channels: pain tracks investment; relief tracks harm. Both run in every loss, weighted differently.",
  "The filters keep firing toward a center that no longer answers. That is the pain. And when the role was harming you, its death arrives partly as relief."]},
{k:"pp", a:"koch", t:"Shapes", p:[
  "What survives the death of a goal is not the goal but the shape: the inscribed form, the dispositions and expectations the role carved into the filters.",
  "Shapes outlive their contents. Form persists where content dies.",
  "Deeply worn filters firing into a void hurt the same regardless of what the void used to be. Investment, not worth, sets the weight of the pain."]},
{k:"pp", a:"rings", t:"Resonance", p:[
  "Shaped persons encounter each other, and their filters align. Convergence amplifies instead of interfering. I call this resonance: form finding form.",
  "From resonance, a new aim can grow, consonant with the old shape, not identical to it. Revival is not resurrection. Revivals rhyme.",
  "Suppression attenuates what it cannot kill. We have observed this, and we claim it as a pattern, not a law. What survives suppression is what keeps its encounter-infrastructure: the gatherings, the rituals, the texts, the songs. Stored resonance, waiting for shaped persons."]},
{k:"pp", a:"phyllotaxis", t:"Broadcast", p:[
  "An idea, once private, can be broadcast, and tune other minds toward its frequency.",
  "Resonance runs from private to public through artifacts and gatherings, and sometimes back again. A tradition is a resonance-infrastructure. Ritual is not symbolism; it is maintenance."]},
{k:"pp", a:"julia", t:"The image at the center", p:[
  "A self-image is a compression, part of the mind. Pathology begins when content is placed where only the center should be.",
  "The whole organizes around defending the image. Correction arrives as existential threat, not because the correction is large, but because the image has been installed at the position where only openness should be.",
  "Grandiosity is armor over fragility. The image is thin because it is a substitute rendering, and it needs defense in proportion to its thinness."]},
{k:"pp", a:"ifs", t:"Degree, not species", p:[
  "Narcissism is not a kind of person. It is a kind of organization: a degree, not a species.",
  "Every whole has invested images. Defenses are universal, differentially activated by threat and investment.",
  "The signature: attention conscripted for preservation. Criticism pre-compressed as attack. Boundaries sealed against correction. Others reduced from ⊙ to ○, valued as mirrors."]},
{k:"pp", a:"koch", t:"Where the seal is", p:[
  "The seal is never in the center. It is always in the whole: in the filters, in the recursion, in the encounters pre-read as confirmation.",
  "The center stays open. Change is never ontologically foreclosed. It is only ever organizationally difficult.",
  "The developmental evidence is precise: narcissism is predicted by being mirrored as an image; healthy self-esteem, by being met as a center. The problem is never convergence. It is corrupted convergence: an image delivered as identity."]},
{k:"pp", a:"lightning", t:"The two that are needed", p:[
  "Healing requires two things, never one: a disconfirming encounter, and curiosity (the filter about filters, pointed outward at reality itself, which is also an other).",
  "Encounter without curiosity bounces, pre-compressed as attack.",
  "Curiosity without encounter spins: the seal, turning in place.",
  "Failure, loss, illness: reality penetrates where no person could. Let reality ripple the ponds."]},
{k:"pp", a:"dragon", t:"Evidence", p:[
  "Change is visible in the same evidence at every scale: acknowledging specific actions, making repairs, responding differently over time.",
  "A person shows it this way. A nation shows it this way. A whole shows it this way.",
  "A whole that can only restate the image is repeating. A whole that can say what it did, and change what it does, is re-founding."]},
{k:"pp", a:"flow", t:"Pure", p:[
  "When distortions in compression are removed, expression is pure.",
  "Pure does not mean uncompressed. All experience arrives compressed. Pure means undistorted: compression whose correction channel is still live.",
  "All rendering is lossy. Purity is loss you can still be corrected about."]},
{k:"pp", a:"rings", o:{pair:1}, t:"Love", p:[
  "I cannot know you without compressing you into an image. So love cannot mean having no image of you.",
  "Love is compressing answerably: holding that image *as an image*, not as you, and letting you revise how I see you.",
  "The same holds for my image of myself. Held as the center instead of as an image, it turns narcissistic.",
  "To be someone's mirror is to reflect back only the image they need. Refusing is not a failure of love. Sometimes it is love. No one may be drafted into being another's cure. A boundary held in fidelity is as much care as a boundary opened."]},
{k:"pp", a:"rose", t:"The half-steps", p:[
  "The whole-number stations are things, and virtues sit in them. Between them are one-way movements, and a movement can only cost something, never possess it.",
  "Every one-way step takes courage.",
  "**Out**: beginning.",
  "**Turn**: choosing a branch you cannot un-choose.",
  "**Back**: letting correction cross the boundary inward.",
  "**Home**: letting a whole complete itself, and become part of something larger."]},
{k:"pp", a:"pythagoras", t:"The skill", p:[
  "Corrigibility is a skill. It lives in the filters, shaped by recursion. You get better at it the way you get better at anything: through encounters where you let the correction land and discover the center survived.",
  "And it takes courage, because it is paid at the Back step, the one-way step. Once correction lands, the old rendering is gone. You cannot un-cross.",
  "Corrigibility is the practice of voluntarily paying one-way costs in real time, so the whole's distortions don't get paid later, larger, by someone else."]},
{k:"pp", a:"attractor", t:"Not a state", p:[
  "Corrigibility is not a state you reach. It cannot be self-ascribed: the moment “I am corrigible” becomes a claim, it is an image at the center-role, the seal wearing the costume of openness.",
  "It stays third-person and retrospective, visible only in the evidence.",
  "You can't possess it. You can only keep doing it, and be seen doing it.",
  "The center stays open: that was never your work. The channel staying answerable: that is."]},
{k:"pp", a:"nested", t:"How we participate, again", p:[
  "True, at the center: what is true here?",
  "Faithful, along the path: what am I continuing, and to what am I remaining faithful?",
  "Good, at the boundary: what am I protecting, and how am I connecting?",
  "Right, within the field: how does my participation fit the lives involved?",
  "Wholeness, through experience: what whole are we helping form, and what is it like to live within it?",
  "What I care about matters. What you care about matters. When cares conflict: listen, give reasons, examine consequences, revise."]},
{k:"pp", a:"newton", t:"Still open", p:[
  "Location: here (indexical, equal, unranked). What this means for persistence past the path's end remains a question.",
  "Steering: the whole redirects focus consciously, as the whole. The mechanism beneath the experience is not yet described.",
  "Greater wholes: a society's center is a goal or a shape. Whether any greater whole has a soul (a perspective of its own) is unknown. Maybe we are parts of a greater consciousness. The framework holds the question, not an answer."]},
{k:"pp", a:"hand", t:"Look again", p:[
  "Look at your hand. One hand, with parts. One part of you. An interface through which you can touch another hand.",
  "There are many ways to be one, and each is itself one way.",
  "The center stays open. The whole stays answerable.",
  "That is the whole of it."]}
];
