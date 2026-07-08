import { useEffect, useMemo, useState } from "react";
import {
  Bell,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  ClipboardCheck,
  Code2,
  Cpu,
  Loader2,
  Lock,
  LogOut,
  Mail,
  RefreshCw,
  Save,
  Send,
  Sparkles,
  TimerReset,
  TrendingUp,
} from "lucide-react";
import { format, parseISO, subDays } from "date-fns";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api";
const ACCESS_KEY = "prep_tracker_access_code";

const sessionMeta = [
  {
    key: "morning",
    title: "Morning DSA",
    time: "9:00 AM - 1:00 PM",
    accent: "border-l-teal-600",
  },
  {
    key: "afternoon",
    title: "Afternoon DSA",
    time: "1:05 PM - 5:30 PM",
    accent: "border-l-sky-600",
  },
  {
    key: "evening",
    title: "Evening DSA",
    time: "5:35 PM - 9:30 PM",
    accent: "border-l-amber-500",
  },
];

const emailJobs = [
  ["morning_dsa", "9:00 AM", "DSA before 1 PM"],
  ["midday_check", "1:00 PM", "Morning check"],
  ["afternoon_dsa", "1:05 PM", "DSA before 5:30 PM"],
  ["evening_dsa", "5:35 PM", "DSA before 9:30 PM"],
  ["behavioral_prep", "9:30 PM", "Behavioral prep"],
  ["daily_log_reminder", "10:15 PM", "Fill tracker"],
  ["weekly_resume_start", "Sat 9:00 AM", "Resume prep"],
  ["weekly_resume_check", "Sun 10:00 PM", "Resume check"],
];

function todayKey() {
  return format(new Date(), "yyyy-MM-dd");
}

function classNames(...items) {
  return items.filter(Boolean).join(" ");
}

async function apiFetch(path, code, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-App-Code": code,
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }
  return data;
}

function getCompletion(log) {
  if (!log) return { done: 0, total: 0, percent: 0 };

  const values = [
    log.sessions?.morning?.cf_done,
    log.sessions?.morning?.lc_done,
    log.sessions?.afternoon?.cf_done,
    log.sessions?.afternoon?.lc_done,
    log.sessions?.evening?.cf_done,
    log.sessions?.evening?.lc_done,
    log.striver?.done,
    log.jobs?.applications_done,
    log.jobs?.recruiters_done,
    log.behavioral?.done,
    log.ml_research?.done,
    log.daily_review?.filled,
  ];

  const weekday = parseISO(log.date).getDay();
  if (weekday === 0 || weekday === 6) values.push(log.resume?.done);

  const total = values.length;
  const done = values.filter(Boolean).length;
  return { done, total, percent: total ? Math.round((done / total) * 100) : 0 };
}

function cloneLog(log) {
  return typeof structuredClone === "function" ? structuredClone(log) : JSON.parse(JSON.stringify(log));
}

function CodeGate({ initialCode, onUnlock }) {
  const [code, setCode] = useState(initialCode || "");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setStatus("checking");
    setError("");
    try {
      await apiFetch("/config", code);
      localStorage.setItem(ACCESS_KEY, code);
      onUnlock(code);
    } catch (err) {
      setError(err.message);
      localStorage.removeItem(ACCESS_KEY);
    } finally {
      setStatus("idle");
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <form
        onSubmit={submit}
        className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-panel"
      >
        <div className="mb-5 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-lg bg-slate-900 text-white">
            <Lock size={22} />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-950">Prep Tracker</h1>
            <p className="text-sm text-slate-500">Enter your access code.</p>
          </div>
        </div>

        <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="access-code">
          Access code
        </label>
        <input
          id="access-code"
          value={code}
          onChange={(event) => setCode(event.target.value)}
          type="password"
          inputMode="numeric"
          autoFocus
          className="mb-3 h-11 w-full rounded-md border border-slate-300 px-3 text-base text-slate-950 shadow-sm"
          placeholder="Enter code"
        />

        {error ? <p className="mb-3 text-sm text-rose-600">{error}</p> : null}

        <button
          type="submit"
          disabled={status === "checking" || !code.trim()}
          className="flex h-11 w-full items-center justify-center gap-2 rounded-md bg-teal-700 px-4 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {status === "checking" ? <Loader2 className="animate-spin" size={18} /> : <Check size={18} />}
          Unlock
        </button>
      </form>
    </main>
  );
}

function CheckboxRow({ checked, title, description, onChange }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className="flex w-full items-start gap-3 rounded-md border border-slate-200 bg-white px-3 py-3 text-left transition hover:border-slate-300 hover:bg-slate-50"
    >
      <span className="task-checkbox mt-0.5 shrink-0" data-checked={checked}>
        {checked ? <Check size={15} strokeWidth={3} /> : null}
      </span>
      <span>
        <span className="block text-sm font-semibold text-slate-950">{title}</span>
        <span className="block text-xs leading-5 text-slate-500">{description}</span>
      </span>
    </button>
  );
}

function SessionCard({ session, meta, onChange }) {
  return (
    <section className={classNames("rounded-lg border border-slate-200 border-l-4 bg-white p-4 shadow-sm", meta.accent)}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-slate-950">{meta.title}</h2>
          <p className="text-sm text-slate-500">{meta.time}</p>
        </div>
        <Code2 className="mt-1 shrink-0 text-slate-400" size={20} />
      </div>

      <div className="space-y-3">
        <CheckboxRow
          checked={Boolean(session?.cf_done)}
          title="1 Codeforces question"
          description="Mark Yes when this block's CF problem is done."
          onChange={(value) => onChange("cf_done", value)}
        />
        <CheckboxRow
          checked={Boolean(session?.lc_done)}
          title="1 LC Hard or 2 LC Mediums"
          description="Either path counts for the LeetCode target."
          onChange={(value) => onChange("lc_done", value)}
        />
      </div>

      <textarea
        value={session?.notes || ""}
        onChange={(event) => onChange("notes", event.target.value)}
        className="mt-3 min-h-20 w-full resize-y rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-800"
        placeholder="Notes for this session"
      />
    </section>
  );
}

function MetricCard({ icon: Icon, title, children }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Icon size={19} className="text-teal-700" />
        <h2 className="text-base font-semibold text-slate-950">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function NumberField({ value, onChange, min = 0, label }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>
      <input
        type="number"
        min={min}
        value={value ?? 0}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm text-slate-950"
      />
    </label>
  );
}

function TrackerApp({ accessCode, onLock }) {
  const [config, setConfig] = useState(null);
  const [selectedDate, setSelectedDate] = useState(todayKey());
  const [log, setLog] = useState(null);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState("loading");
  const [saving, setSaving] = useState("saved");
  const [error, setError] = useState("");
  const [emailStatus, setEmailStatus] = useState("");

  const completion = useMemo(() => getCompletion(log), [log]);

  useEffect(() => {
    apiFetch("/config", accessCode)
      .then(setConfig)
      .catch((err) => setError(err.message));
  }, [accessCode]);

  useEffect(() => {
    let active = true;
    setStatus("loading");
    setError("");

    const end = selectedDate;
    const start = format(subDays(parseISO(selectedDate), 6), "yyyy-MM-dd");

    Promise.all([
      apiFetch(`/logs/${selectedDate}`, accessCode),
      apiFetch(`/logs?start=${start}&end=${end}`, accessCode),
    ])
      .then(([dayLog, range]) => {
        if (!active) return;
        setLog(dayLog);
        setHistory(range);
        setStatus("ready");
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message);
        setStatus("error");
      });

    return () => {
      active = false;
    };
  }, [accessCode, selectedDate]);

  async function persist(nextLog) {
    setSaving("saving");
    try {
      const saved = await apiFetch(`/logs/${selectedDate}`, accessCode, {
        method: "PUT",
        body: JSON.stringify(nextLog),
      });
      setLog(saved);
      setSaving("saved");
      const start = format(subDays(parseISO(selectedDate), 6), "yyyy-MM-dd");
      const range = await apiFetch(`/logs?start=${start}&end=${selectedDate}`, accessCode);
      setHistory(range);
    } catch (err) {
      setSaving("error");
      setError(err.message);
    }
  }

  function updateLog(mutator) {
    if (!log) return;
    const next = cloneLog(log);
    mutator(next);
    setLog(next);
    persist(next);
  }

  async function sendEmail(jobKey) {
    setEmailStatus(`Sending ${jobKey}...`);
    try {
      const result = await apiFetch(`/email/send/${jobKey}`, accessCode, { method: "POST" });
      setEmailStatus(`${result.status}: ${result.subject}`);
    } catch (err) {
      setEmailStatus(err.message);
    }
  }

  if (status === "loading" || !log) {
    return (
      <main className="grid min-h-screen place-items-center">
        <div className="flex items-center gap-3 text-slate-600">
          <Loader2 className="animate-spin" size={24} />
          Loading tracker
        </div>
      </main>
    );
  }

  const selectedWeekday = parseISO(selectedDate).getDay();
  const showResume = selectedWeekday === 0 || selectedWeekday === 6;

  return (
    <main className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-5 flex flex-col gap-4 rounded-lg border border-slate-200 bg-white px-4 py-4 shadow-sm lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-1 flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide text-teal-700">
              <span>IST tracker</span>
              <span className="h-1 w-1 rounded-full bg-slate-300" />
              <span>{config?.timezone || "Asia/Kolkata"}</span>
            </div>
            <h1 className="text-2xl font-semibold text-slate-950 sm:text-3xl">Prep Tracker</h1>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
              <CalendarDays size={17} />
              <input
                type="date"
                value={selectedDate}
                onChange={(event) => setSelectedDate(event.target.value)}
                className="bg-transparent text-slate-950"
              />
            </label>

            <div className="flex h-10 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600">
              {saving === "saving" ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
              {saving}
            </div>

            <button
              type="button"
              onClick={onLock}
              title="Lock tracker"
              className="grid h-10 w-10 place-items-center rounded-md border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {error ? (
          <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-5">
            <section className="rounded-lg border border-slate-200 bg-slate-950 p-5 text-white shadow-panel">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-slate-300">{format(parseISO(selectedDate), "EEEE, MMM d, yyyy")}</p>
                  <h2 className="mt-1 text-xl font-semibold">Daily completion: {completion.percent}%</h2>
                </div>
                <div className="min-w-36 rounded-md bg-white/10 px-4 py-3">
                  <p className="text-3xl font-semibold">{completion.done}/{completion.total}</p>
                  <p className="text-sm text-slate-300">items marked</p>
                </div>
              </div>
              <div className="mt-5 h-3 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-teal-400 transition-all"
                  style={{ width: `${completion.percent}%` }}
                />
              </div>
            </section>

            <div className="grid gap-4 xl:grid-cols-2">
              <MetricCard icon={Sparkles} title="Striver A2Z Revision">
                <div className="space-y-3">
                  <CheckboxRow
                    checked={Boolean(log.striver?.done)}
                    title="1 hour revised"
                    description="Daily A2Z sheet revision target."
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.striver.done = value;
                      })
                    }
                  />
                  <NumberField
                    label="Minutes"
                    value={log.striver?.minutes}
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.striver.minutes = value;
                      })
                    }
                  />
                  <textarea
                    value={log.striver?.notes || ""}
                    onChange={(event) =>
                      updateLog((draft) => {
                        draft.striver.notes = event.target.value;
                      })
                    }
                    className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Striver notes"
                  />
                </div>
              </MetricCard>

              <MetricCard icon={BriefcaseBusiness} title="Job Applications">
                <div className="space-y-3">
                  <CheckboxRow
                    checked={Boolean(log.jobs?.applications_done)}
                    title="Applied to jobs"
                    description="LinkedIn, email, Instahyre, Naukri, and similar platforms."
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.jobs.applications_done = value;
                      })
                    }
                  />
                  <CheckboxRow
                    checked={Boolean(log.jobs?.recruiters_done)}
                    title="Messaged 5 recruiters"
                    description="Proper, personalized recruiter outreach."
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.jobs.recruiters_done = value;
                      })
                    }
                  />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <NumberField
                      label="Applications"
                      value={log.jobs?.applications_count}
                      onChange={(value) =>
                        updateLog((draft) => {
                          draft.jobs.applications_count = value;
                        })
                      }
                    />
                    <NumberField
                      label="Recruiters"
                      value={log.jobs?.recruiters_count}
                      onChange={(value) =>
                        updateLog((draft) => {
                          draft.jobs.recruiters_count = value;
                        })
                      }
                    />
                  </div>
                </div>
              </MetricCard>
            </div>

            <div className="grid gap-4 xl:grid-cols-3">
              {sessionMeta.map((meta) => (
                <SessionCard
                  key={meta.key}
                  meta={meta}
                  session={log.sessions?.[meta.key]}
                  onChange={(field, value) =>
                    updateLog((draft) => {
                      draft.sessions[meta.key][field] = value;
                    })
                  }
                />
              ))}
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <MetricCard icon={Cpu} title="ML / Research / AI">
                <div className="space-y-3">
                  <CheckboxRow
                    checked={Boolean(log.ml_research?.done)}
                    title="Focused session completed"
                    description="Inference optimization, paper review, experiments, or another meaningful AI topic."
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.ml_research.done = value;
                      })
                    }
                  />
                  <NumberField
                    label="Minutes"
                    value={log.ml_research?.minutes}
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.ml_research.minutes = value;
                      })
                    }
                  />
                  <input
                    type="text"
                    value={log.ml_research?.focus || ""}
                    onChange={(event) =>
                      updateLog((draft) => {
                        draft.ml_research.focus = event.target.value;
                      })
                    }
                    className="h-10 w-full rounded-md border border-slate-200 px-3 text-sm text-slate-950"
                    placeholder="Focus topic, e.g. inference optimization"
                  />
                  <textarea
                    value={log.ml_research?.notes || ""}
                    onChange={(event) =>
                      updateLog((draft) => {
                        draft.ml_research.notes = event.target.value;
                      })
                    }
                    className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Research notes or outcomes"
                  />
                </div>
              </MetricCard>

              <MetricCard icon={TimerReset} title="Behavioral Interview">
                <div className="space-y-3">
                  <CheckboxRow
                    checked={Boolean(log.behavioral?.done)}
                    title="30 minutes completed"
                    description="AI mock prep plus internet, LinkedIn, Reddit, and company-specific resources."
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.behavioral.done = value;
                      })
                    }
                  />
                  <NumberField
                    label="Minutes"
                    value={log.behavioral?.minutes}
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.behavioral.minutes = value;
                      })
                    }
                  />
                </div>
              </MetricCard>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <MetricCard icon={ClipboardCheck} title={showResume ? "Weekly Resume Prep" : "Resume Prep"}>
                <div className="space-y-3">
                  <CheckboxRow
                    checked={Boolean(log.resume?.done)}
                    title="Weekly resume work done"
                    description={showResume ? "Saturday start and Sunday night check-in." : "Main reminder comes on the weekend."}
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.resume.done = value;
                      })
                    }
                  />
                  <CheckboxRow
                    checked={Boolean(log.daily_review?.filled)}
                    title="Daily tracker filled"
                    description="End-of-day honesty pass for what was completed or missed."
                    onChange={(value) =>
                      updateLog((draft) => {
                        draft.daily_review.filled = value;
                      })
                    }
                  />
                  <textarea
                    value={log.daily_review?.notes || ""}
                    onChange={(event) =>
                      updateLog((draft) => {
                        draft.daily_review.notes = event.target.value;
                      })
                    }
                    className="min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Daily review notes"
                  />
                </div>
              </MetricCard>
            </div>

          </div>

          <aside className="space-y-5">
            <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Mail size={19} className="text-teal-700" />
                  <h2 className="text-base font-semibold text-slate-950">Email Console</h2>
                </div>
                <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                  {config?.email_dry_run ? "dry run" : "live"}
                </span>
              </div>

              <div className="space-y-2">
                {emailJobs.map(([key, time, label]) => (
                  <div key={key} className="flex items-center justify-between gap-3 rounded-md border border-slate-200 px-3 py-2">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-900">{label}</p>
                      <p className="text-xs text-slate-500">{time} IST</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => sendEmail(key)}
                      title={`Send ${label}`}
                      className="grid h-9 w-9 shrink-0 place-items-center rounded-md border border-slate-200 text-slate-600 transition hover:bg-slate-50"
                    >
                      <Send size={16} />
                    </button>
                  </div>
                ))}
              </div>

              {emailStatus ? <p className="mt-3 text-sm text-slate-600">{emailStatus}</p> : null}
            </section>

            <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <Bell size={19} className="text-teal-700" />
                <h2 className="text-base font-semibold text-slate-950">Reminder Rules</h2>
              </div>
              <div className="space-y-3 text-sm text-slate-600">
                <p>Every email includes Striver A2Z, recruiter outreach, ML/AI, and motivation reminders.</p>
                <p>Resume prep starts Saturday morning and gets checked Sunday night.</p>
                <p>Daily tracker fill reminder goes out at 10:15 PM IST.</p>
              </div>
            </section>

            <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <RefreshCw size={19} className="text-teal-700" />
                  <h2 className="text-base font-semibold text-slate-950">Last 7 Days</h2>
                </div>
              </div>

              <div className="space-y-2">
                {history.map((item) => {
                  const itemCompletion = getCompletion(item);
                  return (
                    <button
                      type="button"
                      key={item.date}
                      onClick={() => setSelectedDate(item.date)}
                      className={classNames(
                        "flex w-full items-center justify-between rounded-md border px-3 py-2 text-left transition",
                        item.date === selectedDate
                          ? "border-teal-600 bg-teal-50"
                          : "border-slate-200 bg-white hover:bg-slate-50",
                      )}
                    >
                      <span>
                        <span className="block text-sm font-medium text-slate-950">
                          {format(parseISO(item.date), "MMM d")}
                        </span>
                        <span className="block text-xs text-slate-500">{format(parseISO(item.date), "EEE")}</span>
                      </span>
                      <span className="text-sm font-semibold text-slate-700">{itemCompletion.percent}%</span>
                    </button>
                  );
                })}
              </div>
            </section>
          </aside>
        </div>

        <section className="mt-5 rounded-lg border border-teal-200 bg-teal-50 p-5 shadow-sm">
          <div className="flex items-start gap-3">
            <TrendingUp className="mt-0.5 shrink-0 text-teal-700" size={22} />
            <div>
              <h2 className="text-base font-semibold text-slate-950">Daily Motivation</h2>
              <p className="mt-1 text-sm leading-6 text-slate-700">
                Keep doing it daily without missing even one day. The consistency will be
                exponentially beneficial after a few months.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

export default function App() {
  const [accessCode, setAccessCode] = useState(() => localStorage.getItem(ACCESS_KEY) || "");
  const [unlocked, setUnlocked] = useState(Boolean(accessCode));

  function lock() {
    localStorage.removeItem(ACCESS_KEY);
    setAccessCode("");
    setUnlocked(false);
  }

  if (!unlocked) {
    return (
      <CodeGate
        initialCode={accessCode}
        onUnlock={(code) => {
          setAccessCode(code);
          setUnlocked(true);
        }}
      />
    );
  }

  return <TrackerApp accessCode={accessCode} onLock={lock} />;
}
