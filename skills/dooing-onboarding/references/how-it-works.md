# How your setup works

Use this page to explain the setup to the owner in plain words: before the system
map, and again whenever a part is new to them. Use the owner's own names for the
host and the agents.

## The parts

Each part is a place in one building. On a board, show each place with the words
before the colon as its short line.

| Part | Think of it as | What it is for |
|---|---|---|
| Agent host | The power room | Runs everything: the always-on computer with the agents, their memory, files and tools. Keep it on, awake and online. |
| Slack | The boardroom | Direction, research and reports: the owner gives direction, raises ideas and gets results. |
| T3 Code | The workshop | Builds projects and workflows: the development team (CTO and Engineer) builds and tests them in project folders. Works from a laptop or phone. |
| Hermes Desktop | The breaker room | Initial setup, settings and errors: the owner's way into the agent host from their daily computer. Setup connects it first. |
| Parsec | The emergency hatch | Remote screen, last resort: the agent host's own screen, for hands-on fixes when Desktop cannot help. |
| Tailscale | The private hallway | Private connection: the private network between the owner's devices and the agent host. |

The EA, the owner's main assistant, coordinates. It works in Slack and Hermes
Desktop and hands development work to the team in T3 Code. Each role is one
Hermes profile. The Engineer is one profile that runs two conversations at once,
so T3 Code and Hermes Desktop show one Engineer, not two.

## How work flows after setup

1. An idea or a recurring chore comes up in Slack.
2. The EA writes it up as a project: the goal, the first useful result, the data
   and tools it may use, and who approves. The owner approves it.
3. The development team builds it in T3 Code, in the project's folder on the
   agent host. The CTO plans and reviews. The Engineer builds and tests.
4. When it works, the team packages the repeatable part as a skill, and as a
   schedule when it should run by itself. The owner approves each.
5. The owner uses it from Slack by asking the agent in that job's channel.
   Results come back to the same channel.
6. A change or a new idea starts again at step 2.

## Start a project in T3 Code

A T3 Code project is a folder on the agent host. To start one:

1. On the host, create a folder for the project, for example inside the
   workspace folder the setup uses.
2. Copy the folder's path. On a Mac, select the folder in Finder and press
   Option-Command-C.
3. In T3 Code, add a project and paste that path.

Start exploratory work in a project folder too, because it may grow. T3 Code
0.1.1 cannot move an existing thread into another project. To carry a thread's
work into a new project, start a new thread there and paste a short summary of
the old one.

## Setup milestones

The milestones group the baseline rows so the owner can see where setup stands.
Work follows the actual dependencies on the host, so a later milestone can start
before an earlier one is finished. A milestone is done only when all its rows are
verified.

| Milestone | Baseline rows |
|---|---|
| 1. Your daily computer connects | Tailscale/private transport, Hermes Desktop |
| 2. The main assistant works | Hermes and model access, Main assistant, Responsibilities and roster |
| 3. The development team works | T3 Code development team |
| 4. Slack works | Slack |
| 5. Files, memory and knowledge work | Canonical context and projects, OpenViking memory, Memory watchdog, Local file discovery, Scheduled index refresh, Curated knowledge and scoped currentness, Knowledge viewing and device workflow |
| 6. Each role has its tools | Capability allocation |
| 7. Safe to run every day | Maintenance and recovery data, Parsec remote debugging, Complete operating cycle |

A status board for the owner can look like this example:

```text
SETUP STATUS
1 Daily computer     done
2 Main assistant     done
3 Development team   doing
4 Slack              next
5 Files and memory   to do
6 Role tools         to do
7 Safe to run        to do
You: nothing right now
```
