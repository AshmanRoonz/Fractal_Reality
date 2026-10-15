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
{k:"q", a:"circumpunct", x:"What changes when you begin to notice how many ways there are to be one?"}
];
