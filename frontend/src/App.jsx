import { useState } from "react";
import axios from "axios";
import {
  Activity,
  Wind,
  Droplets,
  Trash2,
  ShieldCheck,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/analyze";

function App() {
  const [form, setForm] = useState({
    area: "Demo Area",
    aqi: 187,
    ph: 6.2,
    dissolved_oxygen: 3.5,
    turbidity: 12,
    litter_count: 25,
    severe_litter: true,
  });

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [wasteImage, setWasteImage] = useState(null);
  const [imagePreview, setImagePreview] = useState("");

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleImageChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      setWasteImage(null);
      setImagePreview("");
      return;
    }

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setWasteImage(null);
      setImagePreview("");
      setError("Please select a JPEG, PNG, or WEBP image.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setWasteImage(null);
      setImagePreview("");
      setError("Please select an image smaller than 5 MB.");
      return;
    }

    setError("");
    setWasteImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const runAnalysis = async () => {
    setLoading(true);
    setError("");

    try {
      const payload = {
        area: form.area,
        air: {
          aqi: Number(form.aqi),
        },
        water: {
          ph: Number(form.ph),
          dissolved_oxygen: Number(form.dissolved_oxygen),
          turbidity: Number(form.turbidity),
        },
        waste: {
          litter_count: Number(form.litter_count),
          severe_litter: form.severe_litter,
        },
      };

      let response;
      if (wasteImage) {
        const formData = new FormData();
        Object.entries(payload).forEach(([group, values]) => {
          if (typeof values === "object") {
            Object.entries(values).forEach(([key, value]) => {
              formData.append(key, String(value));
            });
          } else {
            formData.append(group, String(values));
          }
        });
        formData.append("image", wasteImage);
        response = await axios.post("http://127.0.0.1:8000/api/analyze-image", formData);
      } else {
        response = await axios.post(API_URL, payload);
      }
      const data = response.data;

      setReport({
        ...data,
        contributors: data.coordinator.contributors,
        specialist_reports: [data.air, data.water, data.waste],
      });
    } catch (err) {
      console.error(err);
      setError(
        "Unable to connect to EcoSentinel backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  const getRiskClass = (risk) => {
    if (risk === "HIGH") return "risk-high";
    if (risk === "MEDIUM") return "risk-medium";
    return "risk-low";
  };

  const getAgentIcon = (agent) => {
    if (agent === "air") return <Wind size={20} />;
    if (agent === "water") return <Droplets size={20} />;
    return <Trash2 size={20} />;
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={28} />
          </div>

          <div>
            <h1>EcoSentinel</h1>
            <p>Multi-Agent Environmental Monitoring System</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Ready
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <div className="eyebrow">ENVIRONMENTAL INTELLIGENCE</div>

          <h2>Area Risk Dashboard</h2>

          <p className="hero-text">
            Three specialist agents analyze air, water and waste signals.
            The coordinator combines their findings into one environmental
            risk report.
          </p>
        </section>

        <section className="input-card">
          <div className="section-heading">
            <div>
              <span className="section-label">ANALYSIS INPUT</span>
              <h3>Environmental Signals</h3>
            </div>

            <ShieldCheck size={28} />
          </div>

          <div className="form-grid">
            <div className="input-group full">
              <label>Area Name</label>
              <input
                type="text"
                name="area"
                value={form.area}
                onChange={handleChange}
                placeholder="Enter area name"
              />
            </div>

            <div className="input-group">
              <label>AQI</label>
              <input
                type="number"
                name="aqi"
                value={form.aqi}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="input-group">
              <label>pH</label>
              <input
                type="number"
                name="ph"
                value={form.ph}
                onChange={handleChange}
                step="0.1"
              />
            </div>

            <div className="input-group">
              <label>Dissolved Oxygen (mg/L)</label>
              <input
                type="number"
                name="dissolved_oxygen"
                value={form.dissolved_oxygen}
                onChange={handleChange}
                step="0.1"
              />
            </div>

            <div className="input-group">
              <label>Turbidity (NTU)</label>
              <input
                type="number"
                name="turbidity"
                value={form.turbidity}
                onChange={handleChange}
                step="0.1"
              />
            </div>

            <div className="input-group">
              <label>Litter Count</label>
              <input
                type="number"
                name="litter_count"
                value={form.litter_count}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="input-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="severe_litter"
                  checked={form.severe_litter}
                  onChange={handleChange}
                />
                Severe litter detected
              </label>
            </div>

            <div className="input-group full image-input-group">
              <label htmlFor="waste-image">Waste / Environment Image</label>
              <input
                id="waste-image"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleImageChange}
              />
              {imagePreview && (
                <img className="image-preview" src={imagePreview} alt="Selected waste analysis preview" />
              )}
              <small>Optional. JPEG, PNG, or WEBP up to 5 MB.</small>
            </div>
          </div>

          <button
            className="run-button"
            onClick={runAnalysis}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={19} className="spin" />
                Analyzing Environment...
              </>
            ) : (
              <>
                <ShieldCheck size={19} />
                Run Analysis
              </>
            )}
          </button>
        </section>

        {error && (
          <div className="error-box">
            <AlertTriangle size={20} />
            {error}
          </div>
        )}

        {!report && !error && (
          <section className="empty-card">
            <ShieldCheck size={46} />
            <h3>No analysis yet</h3>
            <p>
              Enter environmental signals above and click Run Analysis to
              send them through the multi-agent pipeline.
            </p>
          </section>
        )}

        {report && (
          <>
            <section className="report-card">
              <div className="report-label">ENVIRONMENTAL RISK REPORT</div>

              <div className="report-header">
                <div>
                  <h3>{report.area}</h3>
                  <p>{report.coordinator?.reasoning}</p>
                </div>

                <div className={`risk-badge ${getRiskClass(report.overall_risk)}`}>
                  {report.overall_risk}
                </div>
              </div>

              <div className="score-section">
                <div className="score">
                  {report.coordinator?.score}
                </div>
                <span>Combined Risk Score</span>
              </div>

              <div className="contributors">
                <strong>Contributing signals:</strong>

                {report.contributors.map((contributor) => (
                  <span key={contributor} className="signal-pill">
                    {contributor}
                  </span>
                ))}
              </div>
            </section>

            {report.rag?.enabled && report.rag.context?.length > 0 && (
              <section className="rag-card">
                <div className="report-label">RETRIEVED GUIDANCE</div>
                <h3>Environmental Context</h3>
                <p className="rag-method">
                  Local knowledge retrieved with TF-IDF similarity.
                </p>

                <div className="rag-context-grid">
                  {report.rag.context.map((item) => (
                    <article className="rag-context" key={`${item.title}-${item.text}`}>
                      <h4>{item.title}</h4>
                      <p>{item.text}</p>
                      <a href={item.url} target="_blank" rel="noreferrer">
                        {item.source}
                      </a>
                    </article>
                  ))}
                </div>
              </section>
            )}

            <section className="agents-grid">
              {report.specialist_reports.map((agent) => (
                <div className="agent-card" key={agent.agent}>
                  <div className="agent-header">
                    <div className="agent-title">
                      <div className="agent-icon">
                        {getAgentIcon(agent.agent)}
                      </div>

                      <div>
                        <h3>{agent.agent} Agent</h3>
                        <p>Specialist environmental analysis</p>
                      </div>
                    </div>

                    <span className={`risk-badge ${getRiskClass(agent.risk_level)}`}>
                      {agent.risk_level}
                    </span>
                  </div>

                  <div className="agent-stats">
                    <div>
                      <span>Risk Score</span>
                      <strong>{agent.score}</strong>
                    </div>

                    <div>
                      <span>Confidence</span>
                      <strong>{Math.round(agent.confidence * 100)}%</strong>
                    </div>
                  </div>

                  <p className="finding">{agent.finding}</p>

                  {agent.details && agent.details.length > 0 && (
                    <div className="details">
                      <strong>Findings</strong>

                      {agent.details.map((detail, index) => (
                        <div className="detail-item" key={index}>
                          <AlertTriangle size={14} />
                          {detail}
                        </div>
                      ))}
                    </div>
                  )}

                  {agent.image_analysis && (
                    <div className="image-analysis">
                      <strong>Image analysis</strong>
                      <span>
                        Approximate foreground regions: {agent.image_analysis.approximate_detected_litter_count}
                      </span>
                      <span>
                        Quality: {agent.image_analysis.analysis_quality}
                      </span>
                    </div>
                  )}

                  <div className="recommendation">
                    {agent.recommended_action}
                  </div>
                </div>
              ))}
            </section>

            <div className="success-box">
              <ShieldCheck size={18} />
              Multi-agent analysis completed successfully.
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
