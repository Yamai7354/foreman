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
    spec: "Scans my own project portfolio for reusable proof, scores product and market opportunities against what I’ve actually built, and turns job leads and market signals into a prioritized action queue.",
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
    spec: "An event-sourced, bi-temporal knowledge graph kernel for AI agent memory — immutable assertions with full retraction lineage, epistemic reasoning, hybrid retrieval, and multi-hop pathfinding.",
    status: "private",
  },
  {
    title: "Pipeline Tracker",
    tags: ["Python", "FastAPI", "SQLite"],
    spec: "A local-first CRM for freelance pipelines — a Kanban board over SQLite with suggest-and-confirm automations: stale-lead alerts, LLM-drafted follow-ups, and stage-change suggestions. Nothing moves without a human confirming it.",
    status: "public",
    repoUrl: "https://github.com/Yamai7354/pipeline-tracker",
  },
  {
    title: "Foreman",
    tags: ["Python", "CLI", "SQLite"],
    spec: "A developer workflow CLI — work-session tracking, auto-generated docs and architecture diagrams, and GitHub repo scaffolding, backed by SQLite instead of loose files.",
    status: "private",
  },
];

const STATUS_LABEL: Record<Project["status"], string> = {
  live: "Live demo",
  public: "Public repo",
  private: "Private system",
};

function StatusBadge({ status }: { status: Project["status"] }) {
  return (
    <span className={`status-badge status-${status}`}>
      <span className="status-dot" aria-hidden="true" />
      {STATUS_LABEL[status]}
    </span>
  );
}

function ArrowLink({ href, children }: { href: string; children: React.ReactNode }) {
  const isExternal = href.startsWith("http");
  return (
    <a href={href} target={isExternal ? "_blank" : undefined} rel={isExternal ? "noopener noreferrer" : undefined} className="arrow-link">
      <span>{children}</span>
      <span aria-hidden="true">↗</span>
    </a>
  );
}

function SystemTrace() {
  return (
    <aside className="trace-board" aria-label="An inspectable AI system flow">
      <div className="trace-head">
        <span>Production pattern</span>
        <span className="trace-ready"><i aria-hidden="true" /> ready</span>
      </div>
      <div className="trace-stage trace-stage-input">
        <span className="trace-index">01</span>
        <div><strong>Ground the input</strong><small>Documents · workflows · source data</small></div>
      </div>
      <div className="trace-connector" aria-hidden="true"><span /></div>
      <div className="trace-stage trace-stage-reason">
        <span className="trace-index">02</span>
        <div><strong>Make the decision visible</strong><small>Retrieval · routing · tool choice</small></div>
      </div>
      <div className="trace-connector" aria-hidden="true"><span /></div>
      <div className="trace-stage trace-stage-control">
        <span className="trace-index">03</span>
        <div><strong>Keep a human in control</strong><small>Validation · policy · safe execution</small></div>
      </div>
      <div className="trace-foot">
        <span>Input</span><span>Decision</span><span>Action</span><span>Evidence retained</span>
      </div>
    </aside>
  );
}

function FeaturedProject({ project }: { project: Project }) {
  return (
    <article className="featured-project">
      <div className="feature-copy">
        <div className="feature-meta"><span>Featured build</span><StatusBadge status={project.status} /></div>
        <h3>{project.title}</h3>
        <p>{project.spec}</p>
        <div className="tag-row">{project.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
        <div className="link-row">
          {project.repoUrl && <ArrowLink href={project.repoUrl}>View repository</ArrowLink>}
          {project.demoUrl && <ArrowLink href={project.demoUrl}>Open live demo</ArrowLink>}
        </div>
      </div>
      <div className="feature-visual" aria-label="Document Analysis Engine flow">
        <div className="visual-toolbar"><span /><span /><span /><small>document-analysis / run</small></div>
        <div className="visual-canvas">
          <div className="visual-node node-source"><small>source</small><strong>Uploaded docs</strong></div>
          <div className="visual-line line-one" aria-hidden="true"><i /></div>
          <div className="visual-node node-retrieve"><small>retrieve</small><strong>RAG search</strong></div>
          <div className="visual-line line-two" aria-hidden="true"><i /></div>
          <div className="visual-node node-agent"><small>reason</small><strong>Tool agent</strong></div>
          <div className="visual-line line-three" aria-hidden="true"><i /></div>
          <div className="visual-node node-output"><small>output</small><strong>Answers + charts</strong></div>
        </div>
        <div className="visual-log">
          <span>01</span><code>knowledge_base.search</code><b>complete</b>
          <span>02</span><code>chart.generate</code><b>validated</b>
        </div>
      </div>
    </article>
  );
}

export default function Home() {
  const [featured, ...projectIndex] = projects;
  return (
    <main id="top">
      <header className="site-header">
        <a href="#top" className="wordmark" aria-label="Randy Johnson, back to top"><span>RJ</span><strong>Randy Johnson</strong></a>
        <nav aria-label="Primary navigation"><a href="#work">Work</a><a href="#approach">Approach</a><a href="#contact">Contact</a></nav>
        <a className="availability" href="#contact"><i aria-hidden="true" /> Available</a>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Independent AI systems builder · Omaha, Nebraska</p>
          <h1>AI demos are easy.<span>I build the part that has to keep working.</span></h1>
          <p className="hero-deck">I turn documents, workflows, and operational knowledge into inspectable AI systems — with guardrails, provenance, and a human in control.</p>
          <div className="hero-actions">
            <a className="button button-primary" href="#work">Explore the work <span aria-hidden="true">↓</span></a>
            <a className="button button-secondary" href="mailto:randy.johnson@yamaiportfolio.com">Start a conversation <span aria-hidden="true">↗</span></a>
          </div>
        </div>
        <SystemTrace />
      </section>

      <section className="proof-strip" aria-label="Portfolio facts">
        <div><strong>08</strong><span>built systems</span></div>
        <div><strong>03</strong><span>public repositories</span></div>
        <div><strong>01</strong><span>live product demo</span></div>
        <p>Working systems,<br />not slideware.</p>
      </section>

      <section id="work" className="work-section">
        <div className="section-heading">
          <p className="eyebrow">Selected work</p>
          <h2>Proof, not promises.</h2>
          <p>Each project solves a real systems problem: retrieval, orchestration, safety, memory, or the operating layer around them.</p>
        </div>
        <FeaturedProject project={featured} />
        <div className="project-index">
          <div className="index-head"><span>Project</span><span>What it does</span><span>Stack / access</span></div>
          {projectIndex.map((project, index) => (
            <article className="project-row" key={project.title}>
              <div className="project-title">
                <span className="project-number">{String(index + 2).padStart(2, "0")}</span>
                <div><h3>{project.title}</h3><StatusBadge status={project.status} /></div>
              </div>
              <p className="project-spec">{project.spec}</p>
              <div className="project-access">
                <div className="tag-row">{project.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
                {project.repoUrl ? <ArrowLink href={project.repoUrl}>Repository</ArrowLink> : <span className="request-label">Available on request</span>}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="approach" className="approach-section">
        <div className="section-heading approach-heading"><p className="eyebrow">How I build</p><h2>The prototype is only the opening move.</h2></div>
        <div className="principles">
          <article><span>Inputs</span><h3>Start with the source.</h3><p>Ground the system in the documents, workflows, and facts the business already trusts.</p></article>
          <article><span>Decisions</span><h3>Expose the machinery.</h3><p>Make retrieval, routing, tool use, and failure states visible enough to inspect and improve.</p></article>
          <article><span>Actions</span><h3>Keep control explicit.</h3><p>Put validation and approval boundaries between a confident model and a consequential action.</p></article>
        </div>
      </section>

      <footer id="contact" className="contact-section">
        <div className="contact-kicker"><i aria-hidden="true" /> Available for new projects</div>
        <h2>Have a workflow that should work better?</h2>
        <p>Tell me where the friction is. I’ll tell you honestly whether AI belongs in the solution.</p>
        <a href="mailto:randy.johnson@yamaiportfolio.com" className="contact-email">randy.johnson@yamaiportfolio.com <span aria-hidden="true">↗</span></a>
        <div className="footer-line"><span>© 2026 Randy Johnson</span><span>AI agents · automation · document intelligence</span><a href="#top">Back to top ↑</a></div>
      </footer>
    </main>
  );
}
