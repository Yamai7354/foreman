type Project = {
  title: string;
  tags: string[];
  spec: string;
  status: "live" | "public" | "private";
  repoUrl?: string;
  demoUrl?: string;
};

const projects: Project[] = [
  {
    title: "Document Analysis Engine",
    tags: ["FastAPI", "Streamlit", "RAG", "Agents"],
    spec: "A RAG chatbot with a genuine tool-calling agent on top — it searches uploaded documents, reports knowledge-base stats, and generates charts, all decided by the model itself. Swappable LLM provider (OpenAI, Anthropic, or OpenRouter).",
    status: "live",
    repoUrl: "https://github.com/Yamai7354/document-analysis-engine",
    demoUrl: "https://document-analysis-engine-sfnomhnlrsnbnmrukcffr7.streamlit.app",
  },
  {
    title: "Memory Graph Library",
    tags: ["Python", "FastAPI", "Neo4j", "Agents"],
    spec: "A graph-native memory layer for AI agents — hybrid vector, fulltext, and graph retrieval, with a full memory lifecycle (ingest, reflect, promote, archive) instead of stuffing everything into a prompt.",
    status: "public",
    repoUrl: "https://github.com/Yamai7354/memory-graph-library",
  },
  {
    title: "Network Observatory",
    tags: ["Python", "OpenWrt", "Security"],
    spec: "AI-assisted network monitoring and remediation for OpenWrt — log analysis, settings audits, threat detection, and safe command-execution gates before anything touches production.",
    status: "private",
  },
  {
    title: "Market Scout",
    tags: ["Python", "FastAPI", "Automation"],
    spec: "Scans my own project portfolio for reusable proof, scores product and market opportunities against what I've actually built, and turns job leads and market signals into a prioritized action queue.",
    status: "public",
    repoUrl: "https://github.com/Yamai7354/market-scout",
  },
  {
    title: "Agent Runtime",
    tags: ["Python", "Orchestration", "FastAPI"],
    spec: "A modular, project-agnostic runtime for AI agents — model routing, tool execution, policy enforcement, and child-agent delegation, so an application only has to own its domain logic, not execution mechanics.",
    status: "private",
  },
  {
    title: "Knowledge Graph Kernel",
    tags: ["Python", "Knowledge Graph", "Infrastructure"],
    spec: "An event-sourced, bi-temporal knowledge graph kernel for AI agent memory — immutable assertions with full retraction lineage, epistemic reasoning (facts vs. beliefs vs. rumors), and hybrid lexical/vector retrieval with multi-hop pathfinding. Plugs into Agent Runtime as its memory backend.",
    status: "private",
  },
  {
    title: "Foreman",
    tags: ["Python", "CLI", "SQLite"],
    spec: "A developer workflow CLI — work-session tracking, auto-generated docs and architecture diagrams, and GitHub repo scaffolding, backed by SQLite instead of loose files.",
    status: "private",
  },
];

const STATUS_LABEL: Record<Project["status"], string> = {
  live: "Live",
  public: "Public repo",
  private: "Private repo",
};

function StatusBadge({ status }: { status: Project["status"] }) {
  return (
    <span className="inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-widest text-text-dim">
      <span className={`pulse-dot ${status === "live" ? "" : "idle"}`} />
      {STATUS_LABEL[status]}
    </span>
  );
}

export default function Home() {
  return (
    <div className="flex-1">
      {/* Nav */}
      <header className="border-b border-hairline">
        <div className="mx-auto max-w-5xl px-6 py-5 flex items-center justify-between">
          <a href="#top" className="flex items-center gap-2.5 font-display font-semibold text-lg">
            <span className="pulse-dot" />
            Randy Johnson
          </a>
          <nav className="hidden sm:flex items-center gap-8 font-mono text-xs uppercase tracking-widest text-text-dim">
            <a href="#work" className="hover:text-text transition-colors">Work</a>
            <a href="#about" className="hover:text-text transition-colors">About</a>
            <a href="#contact" className="hover:text-text transition-colors">Contact</a>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section id="top" className="border-b border-hairline">
        <div className="mx-auto max-w-5xl px-6 py-24 md:py-32">
          <div className="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-widest text-signal mb-8 border border-hairline rounded-full px-3 py-1.5">
            <span className="pulse-dot" />
            Available for new projects
          </div>

          <h1 className="font-display font-semibold leading-[1.05] text-5xl sm:text-6xl md:text-7xl tracking-tight">
            AI systems that
            <br />
            <span className="text-signal">actually ship.</span>
          </h1>

          <p className="mt-8 max-w-xl text-lg text-text-dim leading-relaxed">
            I design and build AI agents, automations, and document
            intelligence for small and mid-size businesses — production
            systems your team actually uses, not proof-of-concepts.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <a
              href="#work"
              className="bg-signal text-ink font-mono text-sm font-semibold uppercase tracking-wide px-6 py-3 rounded-lg hover:bg-signal-dim transition-colors"
            >
              See the work
            </a>
            <a
              href="#contact"
              className="border border-hairline font-mono text-sm font-semibold uppercase tracking-wide px-6 py-3 rounded-lg hover:border-signal/50 transition-colors"
            >
              Get in touch
            </a>
          </div>
        </div>
      </section>

      {/* Projects */}
      <section id="work" className="mx-auto max-w-5xl px-6 py-20 md:py-24">
        <div className="font-mono text-xs uppercase tracking-widest text-text-dim mb-3">
          Selected work
        </div>
        <h2 className="font-display font-semibold text-3xl md:text-4xl tracking-tight mb-12">
          Systems I&apos;ve built
        </h2>

        <div className="grid md:grid-cols-3 gap-4">
          {projects.map((p) => (
            <article
              key={p.title}
              className="card-panel rounded-xl p-6 flex flex-col"
            >
              <div className="flex items-center justify-between mb-4">
                <StatusBadge status={p.status} />
              </div>

              <h3 className="font-display font-semibold text-xl mb-3">
                {p.title}
              </h3>

              <div className="flex flex-wrap gap-1.5 mb-4">
                {p.tags.map((tag) => (
                  <span
                    key={tag}
                    className="font-mono text-[10px] uppercase tracking-wide rounded-full border border-hairline px-2.5 py-1 text-text-dim"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <p className="text-sm text-text-dim leading-relaxed flex-1">
                {p.spec}
              </p>

              <div className="mt-6 flex flex-wrap gap-4 font-mono text-xs uppercase tracking-widest">
                {p.repoUrl && (
                  <a
                    href={p.repoUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-signal hover:underline underline-offset-4"
                  >
                    Repo →
                  </a>
                )}
                {p.demoUrl && (
                  <a
                    href={p.demoUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-signal hover:underline underline-offset-4"
                  >
                    Live demo →
                  </a>
                )}
                {!p.repoUrl && !p.demoUrl && (
                  <span className="text-text-dim">Available on request</span>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* About / capabilities */}
      <section id="about" className="border-t border-hairline">
        <div className="mx-auto max-w-5xl px-6 py-20 md:py-24 grid md:grid-cols-[1fr_auto] gap-12">
          <div>
            <div className="font-mono text-xs uppercase tracking-widest text-signal mb-3">
              Capabilities
            </div>
            <h2 className="font-display font-semibold text-3xl md:text-4xl tracking-tight mb-6">
              What I actually do
            </h2>
            <p className="max-w-2xl text-text-dim leading-relaxed">
              I design and build AI systems for small and mid-size
              businesses — automations that connect your existing tools,
              chatbots and assistants trained on your business, and the
              unglamorous infrastructure (monitoring, tooling, ops) that
              keeps it all running. If it needs to work in production, not
              just in a demo, that&apos;s the job.
            </p>
          </div>
          <dl className="font-mono text-xs uppercase tracking-widest space-y-5 self-start md:border-l md:border-hairline md:pl-8">
            <div>
              <dt className="text-text-dim">Stack</dt>
              <dd className="text-text mt-1.5 normal-case">Python, FastAPI, Next.js, SQLite/Postgres, LangChain</dd>
            </div>
            <div>
              <dt className="text-text-dim">Focus</dt>
              <dd className="text-text mt-1.5 normal-case">AI agents · automation · document intelligence</dd>
            </div>
            <div>
              <dt className="text-text-dim">Based in</dt>
              <dd className="text-text mt-1.5 normal-case">Omaha, Nebraska</dd>
            </div>
          </dl>
        </div>
      </section>

      {/* Contact / footer */}
      <footer id="contact" className="border-t border-hairline">
        <div className="mx-auto max-w-5xl px-6 py-16 md:py-20">
          <div className="font-mono text-xs uppercase tracking-widest text-signal mb-3">
            Get in touch
          </div>
          <h2 className="font-display font-semibold text-3xl md:text-4xl tracking-tight mb-6">
            Let&apos;s build something
          </h2>
          <a
            href="mailto:randy.johnson@yamaiportfolio.com"
            className="font-mono text-lg text-text hover:text-signal transition-colors underline underline-offset-4"
          >
            randy.johnson@yamaiportfolio.com
          </a>
          <div className="mt-16 pt-6 border-t border-hairline flex flex-wrap items-center justify-between gap-4 font-mono text-[11px] uppercase tracking-widest text-text-dim">
            <span>© 2026 Randy Johnson</span>
            <span className="inline-flex items-center gap-2">
              <span className="pulse-dot" />
              All systems operational
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
