import Navbar from "../components/Navbar";

export default function About() {
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-main)", color: "var(--text-primary)" }}>
      <Navbar />

      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "60px 24px" }} className="animate-fade-up">
        <h1 style={{
          fontSize: "clamp(32px, 5vw, 48px)",
          fontWeight: 800,
          letterSpacing: "-1.5px",
          marginBottom: "24px",
          background: "linear-gradient(135deg, #eaedf5 30%, #8b8fa8)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}>
          About NeuralChat
        </h1>

        <p style={{
          fontSize: "17px",
          color: "var(--text-secondary)",
          lineHeight: "1.8",
          marginBottom: "30px"
        }}>
          NeuralChat is an advanced multi-agent AI assistant designed to provide accurate, domain-specialized responses. By utilizing a smart keyword routing mechanism, your questions are automatically routed to the single best agent or crew suited for the job.
        </p>

        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "16px", color: "var(--text-light)" }}>
          Specialized Expert Pipelines
        </h2>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "16px",
          marginBottom: "40px"
        }}>
          {[
            { title: "💻 Coding Agent", desc: "Complexity-aware multi-step programming assistant." },
            { title: "🎓 College Predictor", desc: "TG EAMCET dataset based predictor for secure admissions." },
            { title: "💊 Medical Agent", desc: "Symptom checker with lifestyle tips and disclaimer safeguards." },
            { title: "📚 Education Agent", desc: "Key facts, examples, definitions, and exam preparation tips." },
            { title: "📄 PDF Q&A", desc: "Grounded Q&A system from uploaded documents with citation logs." },
            { title: "🌐 General Assistant", desc: "General knowledge reasoning for arbitrary conversational queries." }
          ].map((item, idx) => (
            <div key={idx} style={{
              backgroundColor: "var(--bg-sidebar)",
              border: "1px solid var(--border-color)",
              padding: "16px",
              borderRadius: "var(--radius-md)"
            }}>
              <h3 style={{ fontSize: "14.5px", fontWeight: 600, marginBottom: "6px", color: "var(--text-light)" }}>{item.title}</h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", lineHeight: "1.5" }}>{item.desc}</p>
            </div>
          ))}
        </div>

        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "16px", color: "var(--text-light)" }}>
          How the Router Works
        </h2>
        
        <p style={{
          fontSize: "15px",
          color: "var(--text-secondary)",
          lineHeight: "1.7",
          marginBottom: "16px"
        }}>
          When you enter a message, the system uses an efficient router to scan and analyze the query content. It assigns a classification index based on domain keywords and structural context. If the system detects a PDF is loaded, it overrides routing to focus exclusively on grounded retrieval QA.
        </p>

        <p style={{
          fontSize: "15px",
          color: "var(--text-secondary)",
          lineHeight: "1.7"
        }}>
          This design ensures that instead of using a single large general-purpose model for specialized tasks, the platform runs domain-tailored agents to output structured response models (definitions, college list tables, code snippets, etc.), yielding higher accuracy and faster response times.
        </p>
      </div>
    </div>
  );
}