# How your setup works

Use this page to explain the setup to the owner in plain words: before the system
map, and again whenever a part is new to them. Use the owner's own names for the
host and the agents.

## The parts

| Part | Think of it as | What it is for |
|---|---|---|
| Agent host | The power room | The always-on computer that runs the agents, their memory, files and tools. Keep it on, awake and online. |
| Slack | The boardroom | Daily work: the owner gives direction, raises ideas and gets results. |
| T3 Code | The IT department | The development team (CTO and Engineer) builds and tests projects and new workflows. Works from a laptop or phone. |
| Hermes Desktop | The door to the power room | The owner's way into the agent host from their daily computer: setup, settings and errors. |
| Parsec | The back door | The agent host's own screen, for hands-on fixes when Desktop cannot help. |
| Tailscale | The private hallway | The private network between the owner's devices and the agent host. |

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

## Setup milestones

The milestones group the baseline rows so the owner can see where setup stands.
Work follows the actual dependencies on the host, so a later milestone can start
before an earlier one is finished. A milestone is done only when all its rows are
verified.

| Milestone | Baseline rows |
|---|---|
| 1. The main assistant works | Hermes and model access, Main assistant, Responsibilities and roster |
| 2. Your devices connect | Tailscale/private transport, Hermes Desktop, Parsec remote debugging |
| 3. The development team works | T3 Code development team |
| 4. Slack works | Slack |
| 5. Files, memory and knowledge work | Canonical context and projects, OpenViking memory, Memory watchdog, Local file discovery, Scheduled index refresh, Curated knowledge and scoped currentness, Knowledge viewing and device workflow |
| 6. Each role has its tools | Capability allocation |
| 7. Safe to run every day | Maintenance and recovery data, Complete operating cycle |

A status board for the owner can look like this example:

```text
SETUP STATUS
1 Main assistant     done
2 Devices            done
3 Development team   doing
4 Slack              next
5 Files and memory   to do
6 Role tools         to do
7 Safe to run        to do
You: nothing right now
```
