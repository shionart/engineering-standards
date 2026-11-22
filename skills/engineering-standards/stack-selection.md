# Stack selection

Goal: the best match between the problem and the technology. What is already installed on the machine is not a criterion. A toolchain can be installed in minutes; a bad fit costs for the life of the code.

## Questions, in order

1. **Is the stack forced?** The platform decides: Joget plugin (Java), NetSuite SuiteScript (JavaScript), Boomi processes (Boomi, Groovy scripts), Ansible playbooks (YAML plus Python modules), a mobile app (Kotlin/Swift or a cross-platform framework). If forced, use it and stop here.
2. **What is the workload?**
   - Glue between systems, OCR, documents, data wrangling, quick automation, ML: ecosystem-driven.
   - Many concurrent connections, network services, CLIs and ops tools, a single deployable binary: concurrency- and deployment-driven.
   - Tight CPU or memory limits, parsers, crypto, long-running daemons that must not leak or crash, WASM, embedded: performance- and safety-driven.
   - Browser UI, JSON APIs next to a front end, browser automation: web-driven.
3. **What does the ecosystem already give?** A mature library for the hard part (OCR, PDF, Google APIs, browser automation, protocol client) can decide the stack on its own.
4. **How is it deployed and run?** A static binary on a server, a scheduled task, a container, a user's laptop, an always-on service. No runtime on the target favors Go or Rust.
5. **Who maintains it?** One person, or more later. Readability, tooling and hiring pool matter. A rare language needs a clear win.
6. **Time to first working version vs lifetime cost.** A throwaway or exploratory script favors the fastest language. Something that runs for years unattended favors the strictest one.

## Rough guide (a starting point, not a verdict)

| Fit | Usually best | Notes |
|---|---|---|
| Glue, OCR, document and PDF work, Google/Telegram bots, data and ML, test tooling | Python | Biggest library set. Keep it typed and structured. |
| Network services, API gateways, CLIs, schedulers, concurrent workers, single-binary ops tools | Go | Simple, fast to build, easy to ship and run. |
| Parsers, crypto, high-throughput or memory-critical daemons, WASM, anything where a crash or leak is costly | Rust | Higher build cost; use when the guarantees matter. |
| Web front ends, Node-native tooling, browser automation next to a web app, full-stack JSON apps | TypeScript | Share types front to back. |
| Joget plugins, JVM enterprise integrations | Java (Kotlin where the platform allows) | Forced by the platform. |
| Queries, reporting, set-based data work | SQL | Do it in the database when the data lives there. |
| Windows or Linux admin and one-shot ops | PowerShell or Bash | Keep them short; move logic to a real language past about 50 lines. |

## Decision record

Write `docs/adr/NNN-<topic>.md` in the project:

```
# NNN. <topic>
Date:
Problem: <what has to be solved, with the numbers that matter: volume, latency, run time, who runs it>
Options: <2 or 3, each with one line for and one against>
Choice: <one> because <the deciding reason>
Costs accepted: <toolchains to install, learning, anything non-standard>
Revisit when: <the condition that would change this>
```

Two lines each is enough for a small script. A rewrite of working code needs an ADR that says what the rewrite buys.

## Installing a toolchain

Installing the best-fit toolchain is expected. Prefer the standard route (winget, rustup, official installers, `go install`), keep it per user where possible, record what was installed and the version in the ADR, and tell the user. Ask first only for system-wide changes that touch services, firewall, PATH for all users, or paid software.
