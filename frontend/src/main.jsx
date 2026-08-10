import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck,
  LayoutDashboard,
  Target,
  ScanLine,
  FileText,
  Settings,
  Terminal,
  Menu,
  X,
  Plus,
  Play,
  AlertTriangle,
  CheckCircle2,
  Download,
  RefreshCw,
  Server,
  Search,
  LogOut
} from "lucide-react";

import { api, BASE } from "./services/api";
import "./index.css";

const NAV = [
  ["Dashboard", LayoutDashboard],
  ["Targets", Target],
  ["Scans", ScanLine],
  ["Findings", AlertTriangle],
  ["Reports", FileText],
  ["System", Settings]
];

const sevColor = {
  Critical: "text-red-400",
  High: "text-orange-400",
  Medium: "text-yellow-300",
  Low: "text-blue-300",
  Info: "text-slate-400"
};

/* =========================================================
   MAIN APP
========================================================= */

function App() {
  const [page, setPage] = useState("Dashboard");
  const [targets, setTargets] = useState([]);
  const [scans, setScans] = useState([]);
  const [findings, setFindings] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [mobile, setMobile] = useState(false);
  const [modal, setModal] = useState(false);
  const [toast, setToast] = useState("");

  const load = async () => {
    try {
      const [t, s, f, c] = await Promise.all([
        api("/api/targets"),
        api("/api/scans"),
        api("/api/findings"),
        api("/api/scanner-catalog")
      ]);

      setTargets(Array.isArray(t) ? t : []);
      setScans(Array.isArray(s) ? s : []);
      setFindings(Array.isArray(f) ? f : []);
      setCatalog(Array.isArray(c) ? c : []);
    } catch (e) {
      setToast(e?.message || "API connection failed");
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    if (!toast) return;

    const id = setTimeout(() => {
      setToast("");
    }, 4000);

    return () => clearTimeout(id);
  }, [toast]);

  const logout = () => {
    localStorage.removeItem("nexo_logged");
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex">

      {/* SIDEBAR */}
      <aside
        className={
          mobile
            ? "fixed inset-y-0 left-0 z-50 w-72 bg-[#070b0f] border-r border-[#18232d] flex flex-col"
            : "hidden md:flex w-64 bg-[#070b0f] border-r border-[#18232d] flex-col"
        }
      >
        <div className="p-5 flex justify-between items-center">

          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[#00FF9C] text-black grid place-items-center">
              <ShieldCheck />
            </div>

            <div>
              <b>NEXO</b>
              <div className="text-[10px] text-slate-500 tracking-[.22em]">
                BUG HUNTER
              </div>
            </div>
          </div>

          {mobile && (
            <button onClick={() => setMobile(false)}>
              <X />
            </button>
          )}
        </div>

        <div className="px-3 space-y-1">
          {NAV.map(([name, Icon]) => (
            <button
              key={name}
              onClick={() => {
                setPage(name);
                setMobile(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm ${
                page === name
                  ? "bg-[#0d1b17] text-[#00FF9C]"
                  : "text-slate-400 hover:bg-[#0d1318]"
              }`}
            >
              <Icon size={17} />
              {name}
            </button>
          ))}
        </div>

        <div className="mt-auto p-4">
          <div className="panel p-3">
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">
                SECURITY ENGINE
              </span>

              <span className="text-[#00FF9C]">
                ONLINE
              </span>
            </div>

            <div className="mono text-[10px] text-slate-600 mt-2">
              Evidence-backed mode
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="flex-1 min-w-0">

        <header className="h-16 border-b border-[#18232d] bg-[#070b0fe8] backdrop-blur sticky top-0 z-20 flex items-center justify-between px-4 md:px-7">

          <div className="flex items-center gap-3">

            <button
              className="md:hidden btn"
              onClick={() => setMobile(true)}
            >
              <Menu size={18} />
            </button>

            <div>
              <div className="font-semibold">
                {page}
              </div>

              <div className="mono text-[10px] text-slate-500">
                Automated Web Security Intelligence
              </div>
            </div>

          </div>

          <div className="flex items-center gap-3">

            <span className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
              <i className="w-2 h-2 rounded-full bg-[#00FF9C] shadow-[0_0_10px_#00FF9C]" />
              API operational
            </span>

            <button
              className="btn"
              onClick={logout}
              title="Logout"
            >
              <LogOut size={15} />
            </button>

          </div>
        </header>

        <div className="p-4 md:p-7 max-w-[1550px] mx-auto">

          {toast && (
            <div className="fixed top-20 right-4 z-50 panel p-3 text-sm border border-red-500/30 text-red-200">
              {toast}
            </div>
          )}

          {page === "Dashboard" && (
            <Dashboard
              targets={targets}
              scans={scans}
              findings={findings}
              catalog={catalog}
              go={setPage}
            />
          )}

          {page === "Targets" && (
            <Targets
              targets={targets}
              reload={load}
              modal={modal}
              setModal={setModal}
            />
          )}

          {page === "Scans" && (
            <Scans
              targets={targets}
              scans={scans}
              reload={load}
              catalog={catalog}
            />
          )}

          {page === "Findings" && (
            <Findings
              findings={findings}
              reload={load}
            />
          )}

          {page === "Reports" && (
            <Reports findings={findings} />
          )}

          {page === "System" && (
            <System catalog={catalog} />
          )}

        </div>
      </main>
    </div>
  );
}

/* =========================================================
   STAT
========================================================= */

function Stat({
  label,
  value,
  color = "text-white",
  sub = ""
}) {
  return (
    <div className="panel p-5">
      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className={`text-3xl font-semibold mt-2 ${color}`}>
        {value}
      </div>

      {sub && (
        <div className="text-[11px] text-slate-600 mt-1">
          {sub}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard({
  targets,
  scans,
  findings,
  catalog,
  go
}) {
  const sev = useMemo(
    () =>
      Object.fromEntries(
        ["Critical", "High", "Medium", "Low", "Info"].map(
          s => [
            s,
            findings.filter(f => f.severity === s).length
          ]
        )
      ),
    [findings]
  );

  return (
    <div className="grid-bg rounded-2xl p-1">

      <div className="flex flex-col md:flex-row md:items-end justify-between mb-6 gap-4">

        <div>
          <div className="text-[#00FF9C] mono text-xs mb-2">
            NEXO / SECURITY OPERATIONS
          </div>

          <h1 className="text-2xl md:text-3xl font-semibold">
            Executive Security Overview
          </h1>

          <p className="text-slate-500 text-sm mt-1">
            Real telemetry from authorized assessment jobs.
            No synthetic findings.
          </p>
        </div>

        <button
          onClick={() => go("Scans")}
          className="btn btn-primary flex items-center gap-2 w-fit"
        >
          <Play size={16} />
          New assessment
        </button>

      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-5">

        <Stat
          label="Assets monitored"
          value={targets.length}
        />

        <Stat
          label="Total scans"
          value={scans.length}
        />

        <Stat
          label="Open findings"
          value={findings.filter(
            f => f.status === "Open"
          ).length}
        />

        <Stat
          label="Critical"
          value={sev.Critical}
          color="text-red-400"
        />

        <Stat
          label="High"
          value={sev.High}
          color="text-orange-400"
        />

      </div>

      <div className="grid lg:grid-cols-3 gap-4">

        <div className="panel p-5 lg:col-span-2">

          <div className="flex justify-between mb-5">

            <div>
              <b>Recent scan activity</b>

              <div className="text-xs text-slate-500 mt-1">
                Live job state
              </div>
            </div>

            <button
              className="btn"
              onClick={() => window.location.reload()}
            >
              <RefreshCw size={15} />
            </button>

          </div>

          {scans.slice(0, 7).map(s => (
            <div key={s.id} className="mb-4">

              <div className="flex justify-between text-sm">

                <span className="mono">
                  SCAN-{String(s.id).padStart(4, "0")}
                </span>

                <span className="text-slate-500">
                  {s.current_stage} · {s.progress}%
                </span>

              </div>

              <div className="h-1.5 bg-[#111a21] rounded mt-2 overflow-hidden">

                <div
                  className="h-full bg-[#00FF9C] transition-all"
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(100, Number(s.progress) || 0)
                    )}%`
                  }}
                />

              </div>

            </div>
          ))}

          {!scans.length && (
            <Empty text="No assessment jobs yet." />
          )}

        </div>

        <div className="panel p-5">

          <b>Severity distribution</b>

          <div className="space-y-3 mt-5">

            {Object.entries(sev).map(([severity, count]) => {

              const percentage = findings.length
                ? Math.max(
                    4,
                    (count / findings.length) * 100
                  )
                : 0;

              const bar =
                severity === "Critical"
                  ? "bg-red-400"
                  : severity === "High"
                  ? "bg-orange-400"
                  : severity === "Medium"
                  ? "bg-yellow-300"
                  : severity === "Low"
                  ? "bg-blue-300"
                  : "bg-slate-500";

              return (
                <div key={severity}>

                  <div className="flex justify-between text-xs mb-1">

                    <span className={sevColor[severity]}>
                      {severity}
                    </span>

                    <span className="text-slate-500">
                      {count}
                    </span>

                  </div>

                  <div className="h-2 bg-[#111a21] rounded">

                    <div
                      className={`h-full rounded ${bar}`}
                      style={{
                        width: `${percentage}%`
                      }}
                    />

                  </div>

                </div>
              );
            })}

          </div>
        </div>

      </div>
    </div>
  );
}

/* =========================================================
   TARGETS
========================================================= */

function Targets({
  targets,
  reload,
  modal,
  setModal
}) {
  return (
    <>
      <div className="flex justify-between items-center mb-5">

        <div>
          <h2 className="text-xl font-semibold">
            Target Manager
          </h2>

          <p className="text-sm text-slate-500">
            Ownership and explicit authorization are enforced.
          </p>
        </div>

        <button
          className="btn btn-primary flex gap-2"
          onClick={() => setModal(true)}
        >
          <Plus size={16} />
          Add target
        </button>

      </div>

      {modal && (
        <TargetModal
          close={() => setModal(false)}
          reload={reload}
        />
      )}

      <div className="panel overflow-auto">

        <table className="w-full text-sm">

          <thead className="text-xs text-slate-500">

            <tr>
              {[
                "Name",
                "Target",
                "Scope",
                "Authorization",
                "Created"
              ].map(h => (
                <th
                  key={h}
                  className="text-left p-4"
                >
                  {h}
                </th>
              ))}
            </tr>

          </thead>

          <tbody>

            {targets.map(t => (
              <tr
                key={t.id}
                className="border-t border-[#121b22]"
              >

                <td className="p-4">
                  {t.name}
                </td>

                <td className="p-4 mono text-xs">
                  {t.target}
                </td>

                <td className="p-4 text-slate-400">
                  {t.scope || "Default target scope"}
                </td>

                <td className="p-4 text-[#00FF9C]">

                  <span className="flex items-center gap-1">
                    <CheckCircle2 size={14} />
                    Confirmed
                  </span>

                </td>

                <td className="p-4 text-slate-500">
                  {t.created_at
                    ? new Date(
                        t.created_at
                      ).toLocaleDateString()
                    : "—"}
                </td>

              </tr>
            ))}

          </tbody>
        </table>

        {!targets.length && (
          <Empty text="No authorized assets." />
        )}

      </div>
    </>
  );
}

/* =========================================================
   TARGET MODAL
========================================================= */

function TargetModal({
  close,
  reload
}) {
  const [form, setForm] = useState({
    name: "",
    target: "",
    scope: "",
    notes: "",
    authorization_confirmed: false
  });

  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const update = (key, value) => {
    setForm(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const save = async () => {

    if (!form.name.trim()) {
      setErr("Asset name is required.");
      return;
    }

    if (!form.target.trim()) {
      setErr("Target URL is required.");
      return;
    }

    if (!form.authorization_confirmed) {
      setErr("Authorization confirmation is required.");
      return;
    }

    try {

      setBusy(true);
      setErr("");

      await api("/api/targets", {
        method: "POST",
        body: JSON.stringify(form)
      });

      close();
      await reload();

    } catch (e) {
      setErr(
        e?.message || "Unable to create target."
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/75 z-50 grid place-items-center p-4">

      <div className="panel w-full max-w-xl p-6">

        <div className="flex justify-between">

          <div>
            <h3 className="text-lg font-semibold">
              Add authorized target
            </h3>

            <p className="text-xs text-slate-500 mt-1">
              Only test assets you are authorized to assess.
            </p>
          </div>

          <button onClick={close}>
            <X />
          </button>

        </div>

        {err && (
          <div className="text-red-300 text-sm mt-3">
            {err}
          </div>
        )}

        <div className="space-y-3 mt-5">

          <input
            placeholder="Asset name"
            value={form.name}
            onChange={e =>
              update("name", e.target.value)
            }
          />

          <input
            placeholder="https://example.com"
            value={form.target}
            onChange={e =>
              update("target", e.target.value)
            }
          />

          <textarea
            rows="3"
            placeholder="Scope / allowed paths / exclusions"
            value={form.scope}
            onChange={e =>
              update("scope", e.target.value)
            }
          />

          <textarea
            rows="2"
            placeholder="Notes"
            value={form.notes}
            onChange={e =>
              update("notes", e.target.value)
            }
          />

          <label className="flex gap-3 text-sm items-start p-3 border border-[#18232d] rounded-lg">

            <input
              type="checkbox"
              className="w-4 mt-1"
              checked={form.authorization_confirmed}
              onChange={e =>
                update(
                  "authorization_confirmed",
                  e.target.checked
                )
              }
            />

            <span>
              I have authorization to test this target.
            </span>

          </label>

        </div>

        <div className="flex justify-end gap-2 mt-5">

          <button
            className="btn"
            onClick={close}
          >
            Cancel
          </button>

          <button
            disabled={
              !form.authorization_confirmed ||
              busy
            }
            className="btn btn-primary disabled:opacity-40"
            onClick={save}
          >
            {busy ? "Saving…" : "Save target"}
          </button>

        </div>

      </div>
    </div>
  );
}

/* =========================================================
   SCANS
========================================================= */

function Scans({
  targets,
  scans,
  reload,
  catalog
}) {
  const [target, setTarget] = useState("");
  const [profile, setProfile] = useState("Quick");
  const [selected, setSelected] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const active = catalog.filter(
    x =>
      x &&
      (x.name === "headers" ||
        x.name === "technology")
  );

  const run = async () => {

    if (!target) {
      setErr("Select an authorized target.");
      return;
    }

    try {

      setBusy(true);
      setErr("");

      const scanners = selected.length
        ? selected
        : ["headers", "technology"];

      await api("/api/scans", {
        method: "POST",
        body: JSON.stringify({
          target_id: Number(target),
          profile,
          scanners
        })
      });

      setSelected([]);
      await reload();

    } catch (e) {
      setErr(
        e?.message || "Unable to start scan."
      );
    } finally {
      setBusy(false);
    }
  };

  const toggleScanner = (name, checked) => {
    setSelected(prev => {
      if (checked) {
        return prev.includes(name)
          ? prev
          : [...prev, name];
      }

      return prev.filter(x => x !== name);
    });
  };

  return (
    <>
      <div className="grid lg:grid-cols-[1.2fr_.8fr] gap-4 mb-5">

        <div className="panel p-5">

          <div className="flex items-center gap-2 mb-4">
            <ScanLine
              size={18}
              className="text-[#00FF9C]"
            />
            <b>Create assessment job</b>
          </div>

          <div className="space-y-3">

            <select
              value={target}
              onChange={e =>
                setTarget(e.target.value)
              }
            >
              <option value="">
                Select authorized target
              </option>

              {targets.map(t => (
                <option
                  key={t.id}
                  value={t.id}
                >
                  {t.name} — {t.target}
                </option>
              ))}
            </select>

            <select
              value={profile}
              onChange={e =>
                setProfile(e.target.value)
              }
            >
              <option>Quick</option>
              <option>Standard</option>
              <option>Deep</option>
            </select>

            <div className="grid sm:grid-cols-2 gap-2">

              {active.map(scanner => (
                <label
                  key={scanner.name}
                  className="border border-[#18232d] rounded-lg p-3 text-xs flex gap-2"
                >

                  <input
                    type="checkbox"
                    className="w-4"
                    checked={selected.includes(
                      scanner.name
                    )}
                    onChange={e =>
                      toggleScanner(
                        scanner.name,
                        e.target.checked
                      )
                    }
                  />

                  <span>
                    <b>{scanner.name}</b>
                    <br />

                    <span className="text-slate-500">
                      {scanner.description}
                    </span>
                  </span>

                </label>
              ))}

            </div>

            {err && (
              <div className="text-red-300 text-sm">
                {err}
              </div>
            )}

            <button
              disabled={!target || busy}
              className="btn btn-primary w-full disabled:opacity-40 flex justify-center gap-2"
              onClick={run}
            >
              <Play size={15} />
              {busy
                ? "Starting…"
                : "Start authorized scan"}
            </button>

          </div>
        </div>

        <div className="panel p-5">

          <b>Pipeline</b>

          <div className="mono text-xs mt-4 space-y-3 text-slate-400">

            {[
              "Target validation",
              "HTTP discovery",
              "Technology detection",
              "Passive checks",
              "OWASP testing",
              "Finding normalization",
              "Report generation"
            ].map((step, i) => (
              <div
                className="flex gap-2"
                key={step}
              >
                <span className="text-[#00FF9C]">
                  [{i < 2 ? "✓" : " "}]
                </span>

                {step}
              </div>
            ))}

          </div>
        </div>

      </div>

      <div className="panel p-5">

        <div className="flex justify-between mb-4">

          <b>Scan queue</b>

          <span className="text-xs text-slate-500">
            {scans.length} jobs
          </span>

        </div>

        {scans.map(s => (
          <div
            key={s.id}
            className="border border-[#18232d] rounded-lg p-4 mb-3"
          >

            <div className="flex justify-between">

              <span className="mono text-xs">
                SCAN-{String(s.id).padStart(4, "0")}
              </span>

              <span className="text-xs text-slate-400">
                {s.status}
              </span>

            </div>

            <div className="text-xs text-slate-500 mt-2">
              {s.current_stage}
            </div>

            <div className="h-1.5 bg-[#111a21] rounded mt-2">

              <div
                className="h-full bg-[#00FF9C] rounded transition-all"
                style={{
                  width: `${Math.max(
                    0,
                    Math.min(
                      100,
                      Number(s.progress) || 0
                    )
                  )}%`
                }}
              />

            </div>

          </div>
        ))}

        {!scans.length && (
          <Empty text="No jobs queued." />
        )}

      </div>
    </>
  );
}

/* =========================================================
   FINDINGS
========================================================= */

function Findings({
  findings
}) {
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");

  const filtered = findings.filter(f => {

    const searchText = [
      f.title,
      f.target,
      f.owasp_category
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return (
      (!q ||
        searchText.includes(
          q.toLowerCase()
        )) &&
      (!status || f.status === status)
    );
  });

  return (
    <>
      <div className="flex flex-col md:flex-row justify-between gap-3 mb-5">

        <div>
          <h2 className="text-xl font-semibold">
            Findings
          </h2>

          <p className="text-sm text-slate-500">
            Evidence-backed vulnerability records.
          </p>
        </div>

        <div className="flex gap-2">

          <div className="relative">

            <Search
              size={15}
              className="absolute left-3 top-3 text-slate-500"
            />

            <input
              className="pl-9"
              placeholder="Search findings"
              value={q}
              onChange={e =>
                setQ(e.target.value)
              }
            />

          </div>

          <select
            value={status}
            onChange={e =>
              setStatus(e.target.value)
            }
          >
            <option value="">
              All status
            </option>

            {[
              "Open",
              "Confirmed",
              "False Positive",
              "Fixed",
              "Accepted Risk"
            ].map(x => (
              <option key={x}>
                {x}
              </option>
            ))}

          </select>

        </div>
      </div>

      <div className="panel overflow-auto">

        <table className="w-full text-sm">

          <thead className="text-xs text-slate-500">

            <tr>
              {[
                "Finding",
                "Severity",
                "Confidence",
                "OWASP",
                "Target",
                "Status"
              ].map(h => (
                <th
                  key={h}
                  className="text-left p-4"
                >
                  {h}
                </th>
              ))}
            </tr>

          </thead>

          <tbody>

            {filtered.map(f => (
              <tr
                key={f.id}
                className="border-t border-[#121b22]"
              >

                <td className="p-4 font-medium">
                  {f.title}
                </td>

                <td
                  className={`p-4 ${
                    sevColor[f.severity] ||
                    "text-slate-400"
                  }`}
                >
                  {f.severity}
                </td>

                <td className="p-4 text-slate-400">
                  {f.confidence}
                </td>

                <td className="p-4 text-slate-400">
                  {f.owasp_category}
                </td>

                <td className="p-4 mono text-xs">
                  {f.target}
                </td>

                <td className="p-4">
                  {f.status}
                </td>

              </tr>
            ))}

          </tbody>

        </table>

        {!filtered.length && (
          <Empty text="No evidence-backed findings match the current filter." />
        )}

      </div>
    </>
  );
}

/* =========================================================
   REPORTS
========================================================= */

function Reports({
  findings
}) {
  const download = async ext => {

    try {

      const response = await fetch(
        `${BASE}/api/exports/findings.${ext}`
      );

      if (!response.ok) {
        throw new Error(
          `Export failed (${response.status})`
        );
      }

      const blob = await response.blob();

      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");

      a.href = url;
      a.download = `nexo-findings.${ext}`;

      document.body.appendChild(a);
      a.click();
      a.remove();

      URL.revokeObjectURL(url);

    } catch (e) {
      console.error(e);
      alert(
        e?.message ||
        "Unable to export report."
      );
    }
  };

  return (
    <div className="grid lg:grid-cols-3 gap-4">

      <div className="panel p-5 lg:col-span-2">

        <div className="flex gap-2 items-center">

          <FileText
            className="text-[#00FF9C]"
          />

          <b>Report center</b>

        </div>

        <p className="text-sm text-slate-500 mt-2">
          Export current stored findings.
        </p>

        <div className="flex flex-wrap gap-2 mt-5">

          <button
            className="btn flex gap-2"
            onClick={() => download("json")}
          >
            <Download size={15} />
            JSON
          </button>

          <button
            className="btn flex gap-2"
            onClick={() => download("csv")}
          >
            <Download size={15} />
            CSV
          </button>

        </div>

      </div>

      <div className="panel p-5">

        <b>Current evidence set</b>

        <div className="text-3xl mt-3">
          {findings.length}
        </div>

        <div className="text-xs text-slate-500 mt-1">
          stored findings
        </div>

      </div>

    </div>
  );
}

/* =========================================================
   SYSTEM
========================================================= */

function System({
  catalog
}) {
  return (
    <div className="grid md:grid-cols-2 gap-4">

      <div className="panel p-5">

        <div className="flex items-center gap-2">

          <Server
            className="text-[#00FF9C]"
          />

          <b>Platform health</b>

        </div>

        <div className="space-y-2 text-sm text-slate-400 mt-5">

          <p>✓ Frontend operational</p>
          <p>✓ Target authorization gate</p>
          <p>✓ Rate limiting</p>
          <p>✓ SSRF destination filtering</p>
          <p>✓ Generic error responses</p>
          <p>✓ Environment-based configuration</p>

        </div>

      </div>

      <div className="panel p-5">

        <div className="flex items-center gap-2">

          <Terminal
            className="text-[#00B8FF]"
          />

          <b>Scanner catalog</b>

        </div>

        <div className="space-y-2 mt-4">

          {catalog.map(scanner => (
            <div
              key={scanner.name}
              className="flex justify-between border-b border-[#121b22] py-2 text-sm"
            >

              <span>
                {scanner.name}
              </span>

              <span
                className={
                  scanner.enabled
                    ? "text-[#00FF9C]"
                    : "text-slate-600"
                }
              >
                {scanner.enabled
                  ? "enabled"
                  : "module"}
              </span>

            </div>
          ))}

          {!catalog.length && (
            <div className="text-sm text-slate-600">
              Scanner catalog unavailable.
            </div>
          )}

        </div>

        <a
          href={`${BASE}/docs`}
          target="_blank"
          rel="noreferrer"
          className="text-[#00FF9C] text-sm inline-block mt-5"
        >
          Open API documentation →
        </a>

      </div>

    </div>
  );
}

/* =========================================================
   EMPTY
========================================================= */

function Empty({
  text
}) {
  return (
    <div className="text-center py-10 text-slate-600 text-sm">
      {text}
    </div>
  );
}

/* =========================================================
   FRONTEND LOGIN
   ID: Nexo
   PASSWORD: admin
========================================================= */

function Auth({
  onLogin
}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = e => {

    e.preventDefault();

    setError("");
    setBusy(true);

    const id = username.trim();

    if (id === "Nexo" && password === "admin") {

      localStorage.setItem(
        "nexo_logged",
        "true"
      );

      setBusy(false);
      onLogin();

      return;
    }

    setBusy(false);
    setError(
      "Invalid NEXO ID or password."
    );
  };

  return (
    <div className="min-h-screen grid place-items-center p-4 grid-bg">

      <form
        onSubmit={submit}
        className="panel p-7 w-full max-w-md"
      >

        <div className="flex gap-3 items-center mb-7">

          <div className="w-10 h-10 bg-[#00FF9C] text-black rounded-lg grid place-items-center">
            <ShieldCheck />
          </div>

          <div>

            <b className="text-lg">
              NEXO Bug Hunter
            </b>

            <p className="text-xs text-slate-500">
              Automated Web Security Intelligence
            </p>

          </div>

        </div>

        {error && (
          <div className="text-red-300 text-sm mb-4">
            {error}
          </div>
        )}

        <div className="space-y-3">

          <input
            type="text"
            required
            autoComplete="username"
            placeholder="NEXO ID"
            value={username}
            onChange={e =>
              setUsername(e.target.value)
            }
          />

          <input
            type="password"
            required
            autoComplete="current-password"
            placeholder="Password"
            value={password}
            onChange={e =>
              setPassword(e.target.value)
            }
          />

          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={busy}
          >
            {busy
              ? "Authenticating…"
              : "Login"}
          </button>

        </div>

        <div className="text-center text-xs text-slate-600 mt-5">
          NEXO Security Operations
        </div>

      </form>

    </div>
  );
}

/* =========================================================
   ROOT
========================================================= */

function Root() {

  const [
    logged,
    setLogged
  ] = useState(
    localStorage.getItem(
      "nexo_logged"
    ) === "true"
  );

  const handleLogin = () => {
    setLogged(true);
  };

  return logged ? (
    <App />
  ) : (
    <Auth onLogin={handleLogin} />
  );
}

/* =========================================================
   START
========================================================= */

createRoot(
  document.getElementById("root")
).render(
  <Root />
);
