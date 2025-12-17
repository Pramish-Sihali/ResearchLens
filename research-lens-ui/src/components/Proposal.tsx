import { Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { ProposalData } from "@/App";

interface ProposalProps {
  proposal: ProposalData;
  references: Array<{ number: number; reference: string }>;
  topic: string;
}

export function Proposal({ proposal, references, topic }: ProposalProps) {
  const currentDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  // Generate keywords from topic
  const keywords = topic
    .split(" ")
    .filter((w) => w.length > 3)
    .slice(0, 5)
    .join(", ");

  // Generate abstract from introduction
  const abstractText =
    proposal.introduction.split(" ").slice(0, 150).join(" ") +
    (proposal.introduction.split(" ").length > 150 ? "..." : "");

  // Timeline data
  const timelineData = [
    { phase: "Phase 1", activities: "Literature Review & Research Design", duration: "Months 1-2" },
    { phase: "Phase 2", activities: "Data Collection & Instrument Development", duration: "Months 3-5" },
    { phase: "Phase 3", activities: "Data Analysis & Interpretation", duration: "Months 6-8" },
    { phase: "Phase 4", activities: "Writing & Revision", duration: "Months 9-10" },
    { phase: "Phase 5", activities: "Final Review & Submission", duration: "Months 11-12" },
  ];

  // Budget data
  const budgetData = [
    { item: "Equipment", description: "Computing resources and software licenses", cost: "$2,500" },
    { item: "Data Collection", description: "Survey tools, participant compensation", cost: "$1,500" },
    { item: "Travel", description: "Conference presentations and fieldwork", cost: "$3,000" },
    { item: "Publication", description: "Open access fees and formatting", cost: "$2,000" },
    { item: "Miscellaneous", description: "Printing, supplies, contingency", cost: "$1,000" },
  ];

  const handleDownload = () => {
    const printWindow = window.open("", "_blank");
    if (!printWindow) return;

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>${proposal.title}</title>
        <style>
          @page {
            margin: 1in;
            size: letter;
          }

          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 2;
            color: #000;
            background: #fff;
          }

          .page {
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            min-height: 11in;
          }

          /* Title Page */
          .title-page {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 9in;
            text-align: center;
            page-break-after: always;
          }

          .title-page h1 {
            font-size: 18pt;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 2rem;
            line-height: 1.4;
          }

          .title-page .author {
            font-size: 14pt;
            margin: 0.5rem 0;
          }

          .title-page .affiliation {
            font-size: 12pt;
            font-style: italic;
            margin: 0.5rem 0;
          }

          .title-page .date {
            font-size: 12pt;
            margin-top: 2rem;
          }

          /* Abstract Page */
          .abstract-page {
            page-break-after: always;
          }

          .abstract-page h2 {
            font-size: 14pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
          }

          .abstract-page p {
            text-align: justify;
            text-indent: 0;
            font-size: 12pt;
            line-height: 2;
          }

          .keywords {
            margin-top: 1.5rem;
            font-size: 12pt;
          }

          .keywords strong {
            font-style: italic;
          }

          /* Main Content */
          h2.section-title {
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
          }

          h3 {
            font-size: 12pt;
            font-weight: bold;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
          }

          p {
            text-align: justify;
            text-indent: 0.5in;
            margin-bottom: 0;
            line-height: 2;
          }

          p.no-indent {
            text-indent: 0;
          }

          ol, ul {
            margin-left: 0.5in;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
          }

          li {
            margin-bottom: 0.25rem;
            line-height: 2;
          }

          /* Tables */
          table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 11pt;
          }

          th, td {
            border: 1px solid #000;
            padding: 0.5rem;
            text-align: left;
          }

          th {
            font-weight: bold;
            background: #f5f5f5;
          }

          /* References */
          .references-section {
            page-break-before: always;
          }

          .reference-item {
            text-indent: -0.5in;
            padding-left: 0.5in;
            margin-bottom: 0.75rem;
            line-height: 2;
          }

          /* Literature Review - page break after */
          .literature-review {
            page-break-after: always;
          }

          /* Page numbers */
          @media print {
            .page-number {
              display: none;
            }
          }
        </style>
      </head>
      <body>
        <!-- TITLE PAGE -->
        <div class="page title-page">
          <h1>${proposal.title}</h1>
          <p class="author">Research Proposal</p>
          <p class="affiliation">Department of Research Studies<br>Academic Institution</p>
          <p class="date">${currentDate}</p>
        </div>

        <!-- ABSTRACT PAGE -->
        <div class="page abstract-page">
          <h2>Abstract</h2>
          <p class="no-indent">${abstractText}</p>
          <p class="keywords"><strong>Keywords:</strong> ${keywords}, research methodology, analysis</p>
        </div>

        <!-- MAIN CONTENT -->
        <div class="page">
          <!-- 1. Introduction -->
          <h2 class="section-title">1. Introduction</h2>

          <h3>1.1 Background and Context</h3>
          <p>${proposal.introduction.split(". ").slice(0, Math.ceil(proposal.introduction.split(". ").length / 4)).join(". ")}.</p>

          <h3>1.2 Problem Statement</h3>
          <p>${proposal.introduction.split(". ").slice(Math.ceil(proposal.introduction.split(". ").length / 4), Math.ceil(proposal.introduction.split(". ").length / 2)).join(". ")}.</p>

          <h3>1.3 Significance of the Study</h3>
          <p>${proposal.introduction.split(". ").slice(Math.ceil(proposal.introduction.split(". ").length / 2), Math.ceil(proposal.introduction.split(". ").length * 3 / 4)).join(". ")}.</p>

          <h3>1.4 Research Gap</h3>
          <p>${proposal.introduction.split(". ").slice(Math.ceil(proposal.introduction.split(". ").length * 3 / 4)).join(". ") || "This research addresses critical gaps identified in the current literature that require further investigation."}</p>

          <!-- 2. Literature Review -->
          <div class="literature-review">
            <h2 class="section-title">2. Literature Review</h2>

            <h3>2.1 Summary of Existing Research</h3>
            <p>${proposal.literature_review.split(". ").slice(0, Math.ceil(proposal.literature_review.split(". ").length / 3)).join(". ")}.</p>

            <h3>2.2 Gaps in Current Knowledge</h3>
            <p>${proposal.literature_review.split(". ").slice(Math.ceil(proposal.literature_review.split(". ").length / 3), Math.ceil(proposal.literature_review.split(". ").length * 2 / 3)).join(". ")}.</p>

            <h3>2.3 Theoretical Framework</h3>
            <p>${proposal.literature_review.split(". ").slice(Math.ceil(proposal.literature_review.split(". ").length * 2 / 3)).join(". ") || "The theoretical framework draws upon established models and paradigms in the field."}</p>
          </div>

          <!-- 3. Research Questions -->
          <h2 class="section-title">3. Research Questions and Objectives</h2>

          <h3>3.1 Research Questions</h3>
          <ol>
            ${proposal.research_questions.map((q) => `<li>${q}</li>`).join("")}
          </ol>

          <h3>3.2 Research Objectives</h3>
          <ol>
            ${proposal.research_questions.map((q) => `<li>${q.replace(/\?$/, "").replace(/^(What|How|Why|When|Where|Which|Can|Does|Do|Is|Are)\s+/i, "To investigate ")}</li>`).join("")}
          </ol>

          <!-- 4. Methodology -->
          <h2 class="section-title">4. Methodology</h2>

          <h3>4.1 Research Design</h3>
          <p>${proposal.methodology.split(". ").slice(0, Math.ceil(proposal.methodology.split(". ").length / 5)).join(". ")}.</p>

          <h3>4.2 Data Collection Methods</h3>
          <p>${proposal.methodology.split(". ").slice(Math.ceil(proposal.methodology.split(". ").length / 5), Math.ceil(proposal.methodology.split(". ").length * 2 / 5)).join(". ")}.</p>

          <h3>4.3 Sample Size and Selection</h3>
          <p>${proposal.methodology.split(". ").slice(Math.ceil(proposal.methodology.split(". ").length * 2 / 5), Math.ceil(proposal.methodology.split(". ").length * 3 / 5)).join(". ") || "Sample selection will follow purposive sampling techniques appropriate for the research design."}</p>

          <h3>4.4 Data Analysis Techniques</h3>
          <p>${proposal.methodology.split(". ").slice(Math.ceil(proposal.methodology.split(". ").length * 3 / 5), Math.ceil(proposal.methodology.split(". ").length * 4 / 5)).join(". ") || "Data analysis will employ both quantitative and qualitative methods as appropriate."}</p>

          <h3>4.5 Tools and Technologies</h3>
          <p>${proposal.methodology.split(". ").slice(Math.ceil(proposal.methodology.split(". ").length * 4 / 5)).join(". ") || "Research tools will include statistical software, data collection instruments, and analysis frameworks."}</p>

          <!-- 5. Expected Outcomes -->
          <h2 class="section-title">5. Expected Outcomes and Contributions</h2>

          <h3>5.1 Anticipated Results</h3>
          <p>${proposal.expected_outcomes.split(". ").slice(0, Math.ceil(proposal.expected_outcomes.split(". ").length / 3)).join(". ")}.</p>

          <h3>5.2 Contribution to the Field</h3>
          <p>${proposal.expected_outcomes.split(". ").slice(Math.ceil(proposal.expected_outcomes.split(". ").length / 3), Math.ceil(proposal.expected_outcomes.split(". ").length * 2 / 3)).join(". ")}.</p>

          <h3>5.3 Potential Applications</h3>
          <p>${proposal.expected_outcomes.split(". ").slice(Math.ceil(proposal.expected_outcomes.split(". ").length * 2 / 3)).join(". ") || "The findings will have practical applications in both academic and industry settings."}</p>

          <!-- 6. Timeline -->
          <h2 class="section-title">6. Timeline and Schedule</h2>
          <table>
            <thead>
              <tr>
                <th>Phase</th>
                <th>Activities</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              ${timelineData.map((row) => `<tr><td>${row.phase}</td><td>${row.activities}</td><td>${row.duration}</td></tr>`).join("")}
            </tbody>
          </table>

          <!-- 7. Budget -->
          <h2 class="section-title">7. Budget</h2>
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Description</th>
                <th>Estimated Cost</th>
              </tr>
            </thead>
            <tbody>
              ${budgetData.map((row) => `<tr><td>${row.item}</td><td>${row.description}</td><td>${row.cost}</td></tr>`).join("")}
            </tbody>
          </table>
          <p class="no-indent" style="margin-top: 0.5rem;"><strong>Total Estimated Budget:</strong> $10,000</p>

          <!-- 8. References -->
          <div class="references-section">
            <h2 class="section-title">8. References</h2>
            ${references.slice(0, 15).map((ref) => `<p class="reference-item">[${ref.number}] ${ref.reference}</p>`).join("")}
          </div>
        </div>
      </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
      printWindow.print();
    }, 300);
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-primary text-primary-foreground">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Research Proposal</CardTitle>
            <p className="text-sm opacity-80 mt-1">
              LaTeX-formatted academic proposal
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={handleDownload}>
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {/* LaTeX-style document preview */}
        <div
          className="bg-white text-black p-8 md:p-12"
          style={{ fontFamily: "'Times New Roman', Times, serif" }}
        >
          {/* Title Page */}
          <div className="text-center py-12 border-b-2 border-dashed border-gray-300 mb-8">
            <h1 className="text-xl md:text-2xl font-bold uppercase tracking-wide leading-relaxed mb-8">
              {proposal.title}
            </h1>
            <p className="text-base mb-2">Research Proposal</p>
            <p className="text-sm italic mb-2">
              Department of Research Studies<br />
              Academic Institution
            </p>
            <p className="text-sm mt-6">{currentDate}</p>
            <p className="text-xs text-gray-400 mt-4 italic">— Page Break —</p>
          </div>

          {/* Abstract */}
          <div className="mb-8 border-b-2 border-dashed border-gray-300 pb-8">
            <h2 className="text-lg font-bold text-center mb-4">Abstract</h2>
            <p className="text-sm leading-8 text-justify">{abstractText}</p>
            <p className="text-sm mt-4">
              <strong className="italic">Keywords:</strong> {keywords}, research methodology, analysis
            </p>
            <p className="text-xs text-gray-400 mt-4 italic text-center">— Page Break —</p>
          </div>

          {/* 1. Introduction */}
          <section className="mb-6">
            <h2 className="text-base font-bold mb-4">1. Introduction</h2>

            <h3 className="text-sm font-bold mb-2">1.1 Background and Context</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.introduction.split(". ").slice(0, Math.ceil(proposal.introduction.split(". ").length / 4)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">1.2 Problem Statement</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.introduction.split(". ").slice(Math.ceil(proposal.introduction.split(". ").length / 4), Math.ceil(proposal.introduction.split(". ").length / 2)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">1.3 Significance of the Study</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.introduction.split(". ").slice(Math.ceil(proposal.introduction.split(". ").length / 2), Math.ceil(proposal.introduction.split(". ").length * 3 / 4)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">1.4 Research Gap</h3>
            <p className="text-sm leading-8 text-justify indent-8">
              {proposal.introduction.split(". ").slice(Math.ceil(proposal.introduction.split(". ").length * 3 / 4)).join(". ") || "This research addresses critical gaps identified in the current literature."}
            </p>
          </section>

          {/* 2. Literature Review */}
          <section className="mb-6 border-b-2 border-dashed border-gray-300 pb-8">
            <h2 className="text-base font-bold mb-4">2. Literature Review</h2>

            <h3 className="text-sm font-bold mb-2">2.1 Summary of Existing Research</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.literature_review.split(". ").slice(0, Math.ceil(proposal.literature_review.split(". ").length / 3)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">2.2 Gaps in Current Knowledge</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.literature_review.split(". ").slice(Math.ceil(proposal.literature_review.split(". ").length / 3), Math.ceil(proposal.literature_review.split(". ").length * 2 / 3)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">2.3 Theoretical Framework</h3>
            <p className="text-sm leading-8 text-justify indent-8">
              {proposal.literature_review.split(". ").slice(Math.ceil(proposal.literature_review.split(". ").length * 2 / 3)).join(". ") || "The theoretical framework draws upon established models."}
            </p>
            <p className="text-xs text-gray-400 mt-4 italic text-center">— Page Break —</p>
          </section>

          {/* 3. Research Questions */}
          <section className="mb-6">
            <h2 className="text-base font-bold mb-4">3. Research Questions and Objectives</h2>

            <h3 className="text-sm font-bold mb-2">3.1 Research Questions</h3>
            <ol className="list-decimal list-inside ml-8 text-sm leading-8 mb-4">
              {proposal.research_questions.map((q, i) => (
                <li key={i} className="mb-1">{q}</li>
              ))}
            </ol>

            <h3 className="text-sm font-bold mb-2">3.2 Research Objectives</h3>
            <ol className="list-decimal list-inside ml-8 text-sm leading-8">
              {proposal.research_questions.map((q, i) => (
                <li key={i} className="mb-1">
                  {q.replace(/\?$/, "").replace(/^(What|How|Why|When|Where|Which|Can|Does|Do|Is|Are)\s+/i, "To investigate ")}
                </li>
              ))}
            </ol>
          </section>

          {/* 4. Methodology */}
          <section className="mb-6">
            <h2 className="text-base font-bold mb-4">4. Methodology</h2>

            <h3 className="text-sm font-bold mb-2">4.1 Research Design</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.methodology.split(". ").slice(0, Math.ceil(proposal.methodology.split(". ").length / 3)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">4.2 Data Collection Methods</h3>
            <p className="text-sm leading-8 text-justify indent-8 mb-4">
              {proposal.methodology.split(". ").slice(Math.ceil(proposal.methodology.split(". ").length / 3), Math.ceil(proposal.methodology.split(". ").length * 2 / 3)).join(". ")}.
            </p>

            <h3 className="text-sm font-bold mb-2">4.3 Data Analysis Techniques</h3>
            <p className="text-sm leading-8 text-justify indent-8">
              {proposal.methodology.split(". ").slice(Math.ceil(proposal.methodology.split(". ").length * 2 / 3)).join(". ") || "Data analysis will employ appropriate quantitative and qualitative methods."}
            </p>
          </section>

          {/* 5. Expected Outcomes */}
          <section className="mb-6">
            <h2 className="text-base font-bold mb-4">5. Expected Outcomes and Contributions</h2>
            <p className="text-sm leading-8 text-justify indent-8">
              {proposal.expected_outcomes}
            </p>
          </section>

          {/* 6. Timeline */}
          <section className="mb-6">
            <h2 className="text-base font-bold mb-4">6. Timeline and Schedule</h2>
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-black p-2 text-left">Phase</th>
                  <th className="border border-black p-2 text-left">Activities</th>
                  <th className="border border-black p-2 text-left">Duration</th>
                </tr>
              </thead>
              <tbody>
                {timelineData.map((row, i) => (
                  <tr key={i}>
                    <td className="border border-black p-2">{row.phase}</td>
                    <td className="border border-black p-2">{row.activities}</td>
                    <td className="border border-black p-2">{row.duration}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {/* 7. Budget */}
          <section className="mb-6">
            <h2 className="text-base font-bold mb-4">7. Budget</h2>
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border border-black p-2 text-left">Item</th>
                  <th className="border border-black p-2 text-left">Description</th>
                  <th className="border border-black p-2 text-left">Cost</th>
                </tr>
              </thead>
              <tbody>
                {budgetData.map((row, i) => (
                  <tr key={i}>
                    <td className="border border-black p-2">{row.item}</td>
                    <td className="border border-black p-2">{row.description}</td>
                    <td className="border border-black p-2">{row.cost}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="text-sm mt-2"><strong>Total Estimated Budget:</strong> $10,000</p>
          </section>

          {/* 8. References */}
          <section className="border-t-2 border-dashed border-gray-300 pt-8">
            <p className="text-xs text-gray-400 mb-4 italic text-center">— Page Break —</p>
            <h2 className="text-base font-bold mb-4">8. References</h2>
            <div className="space-y-2">
              {references.slice(0, 15).map((ref) => (
                <p key={ref.number} className="text-xs leading-6 pl-6" style={{ textIndent: "-1.5rem" }}>
                  [{ref.number}] {ref.reference}
                </p>
              ))}
            </div>
          </section>
        </div>
      </CardContent>
    </Card>
  );
}
