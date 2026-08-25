import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service — Randy Johnson",
  description:
    "Terms governing use of Randy Johnson's portfolio website, including affiliate disclosures and third-party links.",
};

const EFFECTIVE_DATE = "August 25, 2026";

export default function TermsPage() {
  return (
    <main className="legal-page">
      <header className="legal-header">
        <Link className="wordmark" href="/" aria-label="Randy Johnson, return to portfolio">
          <span>RJ</span><strong>Randy Johnson</strong>
        </Link>
        <Link className="legal-home" href="/">← Portfolio</Link>
      </header>

      <article className="legal-document">
        <div className="legal-intro">
          <p className="eyebrow">Website terms</p>
          <h1>Terms of<br />Service</h1>
          <dl className="legal-meta">
            <div><dt>Operator</dt><dd>Randy Johnson</dd></div>
            <div><dt>Effective</dt><dd>{EFFECTIVE_DATE}</dd></div>
            <div><dt>Applies to</dt><dd>This portfolio website</dd></div>
          </dl>
        </div>

        <div className="legal-body">
          <section>
            <span>01</span>
            <div>
              <h2>Scope</h2>
              <p>
                These terms describe the conditions for using this portfolio website operated by
                Randy Johnson. By continuing to use the site, you accept these terms. If you do not
                accept them, please do not use the site.
              </p>
              <p>
                The site presents project information, technical demonstrations, service descriptions,
                and ways to make contact. These terms govern the website only. Any freelance or consulting
                engagement is governed by its own written agreement.
              </p>
            </div>
          </section>

          <section>
            <span>02</span>
            <div>
              <h2>Permitted use</h2>
              <p>
                You may browse the site and share links to its public pages for lawful purposes. You may
                not interfere with the site, attempt unauthorized access, use it to distribute malicious
                code, misrepresent your affiliation with Randy Johnson, or reuse site content in a way
                that violates applicable law or another party&apos;s rights.
              </p>
            </div>
          </section>

          <section>
            <span>03</span>
            <div>
              <h2>Content and intellectual property</h2>
              <p>
                Unless otherwise stated, the site&apos;s original copy, design, and presentation belong to
                Randy Johnson. Public repositories and third-party materials linked from the portfolio
                remain subject to their own licenses and terms. A link to a repository does not change
                its license or grant rights beyond that license.
              </p>
            </div>
          </section>

          <section>
            <span>04</span>
            <div>
              <h2>Affiliate, referral, and sponsored content</h2>
              <p>
                The site may include affiliate or referral links. Randy Johnson may receive a commission
                or other benefit when someone purchases or signs up through one of those links, at no
                additional cost to that person. Sponsored content or other material relationships will
                be identified clearly near the relevant recommendation or link.
              </p>
              <p>
                Recommendations reflect honest opinions and available experience at the time of
                publication. This section is a general policy; it does not replace the specific disclosure
                presented with affiliate or sponsored content.
              </p>
            </div>
          </section>

          <section>
            <span>05</span>
            <div>
              <h2>Third-party services and links</h2>
              <p>
                The portfolio links to external repositories, demonstrations, platforms, and services.
                Randy Johnson does not control those third parties and is not responsible for their
                availability, security, content, privacy practices, or terms. Review the applicable
                third-party terms before using those services.
              </p>
            </div>
          </section>

          <section>
            <span>06</span>
            <div>
              <h2>Informational content</h2>
              <p>
                Portfolio and technical content is provided for general informational purposes. It is
                not legal, financial, tax, security, or other regulated professional advice. You remain
                responsible for evaluating whether any idea, product, or technical approach is suitable
                for your circumstances.
              </p>
            </div>
          </section>

          <section>
            <span>07</span>
            <div>
              <h2>Availability and warranties</h2>
              <p>
                The site is provided on an &quot;as is&quot; and &quot;as available&quot; basis. To the extent permitted by
                applicable law, no guarantee is made that the site will always be available, error-free,
                secure, or current. Project features and external demonstrations may change over time.
              </p>
            </div>
          </section>

          <section>
            <span>08</span>
            <div>
              <h2>Limitation of liability</h2>
              <p>
                To the extent permitted by applicable law, Randy Johnson will not be liable for indirect,
                incidental, special, consequential, or punitive damages arising from use of, or inability
                to use, this website or a linked third-party service. Nothing in these terms excludes a
                right or liability that applicable law does not permit to be excluded.
              </p>
            </div>
          </section>

          <section>
            <span>09</span>
            <div>
              <h2>Changes</h2>
              <p>
                These terms may be updated as the website or its partnerships change. The effective date
                at the top of this page identifies the latest published version. Continued use after an
                update means the revised terms apply to that later use.
              </p>
            </div>
          </section>

          <section>
            <span>10</span>
            <div>
              <h2>Contact</h2>
              <p>Questions about these terms can be sent to:</p>
              <a className="legal-email" href="mailto:randy.johnson@yamaiportfolio.com">
                randy.johnson@yamaiportfolio.com ↗
              </a>
            </div>
          </section>
        </div>
      </article>
    </main>
  );
}
