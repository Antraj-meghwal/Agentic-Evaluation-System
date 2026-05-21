import { useCallback, useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import API from "../services/api";

export default function ReviewPage() {
    const [queue, setQueue] = useState([]);
    const [selected, setSelected] = useState(null);
    const [overrideScore, setOverrideScore] = useState("");
    const [notes, setNotes] = useState("");
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [message, setMessage] = useState("");

    const fetchQueue = useCallback(async () => {
        try {
            setLoading(true);
            const res = await API.get("/api/review/review-queue");
            setQueue(res.data);
            setSelected((prev) => {
                if (!res.data.length) return null;
                if (prev && res.data.find((q) => q.grading_result_id === prev.grading_result_id)) {
                    return prev;
                }
                return res.data[0];
            });
            if (res.data.length) {
                setOverrideScore(String(res.data[0].score));
            }
        } catch {
            setMessage("Failed to load review queue.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchQueue();
    }, [fetchQueue]);

    const selectNext = useCallback(
        (delta) => {
            if (!queue.length || !selected) return;
            const idx = queue.findIndex(
                (q) => q.grading_result_id === selected.grading_result_id
            );
            const next = queue[idx + delta];
            if (next) {
                setSelected(next);
                setOverrideScore(String(next.score));
                setNotes("");
            }
        },
        [queue, selected]
    );

    const handleApprove = useCallback(async () => {
        if (!selected || actionLoading) return;
        setActionLoading(true);
        setMessage("");
        try {
            await API.post(`/api/review/approve/${selected.grading_result_id}`);
            setMessage("Approved.");
            const remaining = queue.filter(
                (q) => q.grading_result_id !== selected.grading_result_id
            );
            setQueue(remaining);
            setSelected(remaining[0] || null);
            if (remaining[0]) setOverrideScore(String(remaining[0].score));
        } catch {
            setMessage("Approve failed.");
        } finally {
            setActionLoading(false);
        }
    }, [selected, actionLoading, queue]);

    const handleOverride = useCallback(async () => {
        if (!selected || actionLoading) return;
        setActionLoading(true);
        setMessage("");
        try {
            await API.post(`/api/review/override/${selected.grading_result_id}`, {
                updated_score: Number(overrideScore),
                review_notes: notes,
            });
            setMessage("Score overridden.");
            const remaining = queue.filter(
                (q) => q.grading_result_id !== selected.grading_result_id
            );
            setQueue(remaining);
            setSelected(remaining[0] || null);
            if (remaining[0]) setOverrideScore(String(remaining[0].score));
        } catch {
            setMessage("Override failed.");
        } finally {
            setActionLoading(false);
        }
    }, [selected, actionLoading, queue, overrideScore, notes]);

    useEffect(() => {
        function onKey(e) {
            if (!selected || actionLoading) return;

            const tag = e.target.tagName;
            const inField = tag === "INPUT" || tag === "TEXTAREA";

            if ((e.key === "a" || e.key === "A") && !inField) {
                e.preventDefault();
                handleApprove();
                return;
            }
            if (e.key === "o" || e.key === "O") {
                e.preventDefault();
                if (inField && e.target.id === "override-score") {
                    handleOverride();
                } else {
                    document.getElementById("override-score")?.focus();
                }
                return;
            }
            if (inField) return;

            if (e.key === "j" || e.key === "J") {
                e.preventDefault();
                selectNext(1);
            }
            if (e.key === "k" || e.key === "K") {
                e.preventDefault();
                selectNext(-1);
            }
        }
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [selected, actionLoading, handleApprove, handleOverride, selectNext]);

    const apiBase = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    const imageSrc = selected?.crop_image_url
        ? `${apiBase}${selected.crop_image_url}`
        : null;

    return (
        <div className="page-bg">
            <Navbar />
            <div className="p-6 max-w-[1600px] mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-extrabold heading-gradient-warm">
                            Human Review Queue
                        </h1>
                        <p className="text-muted mt-2 text-sm">
                            Shortcuts: <kbd className="kbd">A</kbd> approve ·{" "}
                            <kbd className="kbd">O</kbd> override ·{" "}
                            <kbd className="kbd">J</kbd>/<kbd className="kbd">K</kbd> next/prev
                        </p>
                    </div>
                    <span className="px-4 py-2 rounded-full bg-orange-50 border border-orange-200 text-orange-700 font-bold text-sm">
                        {queue.length} pending
                    </span>
                </div>

                {message && (
                    <p className="mb-4 text-sm font-semibold text-emerald-600">{message}</p>
                )}

                {loading ? (
                    <p className="text-muted">Loading queue…</p>
                ) : queue.length === 0 ? (
                    <div className="card-lg text-center py-12 text-muted">
                        No items need review. Run{" "}
                        <code className="text-violet-600 font-medium">POST /grading/run/:id</code> on an upload first.
                    </div>
                ) : (
                    <div className="grid lg:grid-cols-12 gap-6">
                        <div className="lg:col-span-3 space-y-2 max-h-[75vh] overflow-y-auto pr-1">
                            {queue.map((item) => (
                                <button
                                    key={item.grading_result_id}
                                    type="button"
                                    onClick={() => {
                                        setSelected(item);
                                        setOverrideScore(String(item.score));
                                        setNotes("");
                                    }}
                                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                                        selected?.grading_result_id === item.grading_result_id
                                            ? "border-orange-400 bg-orange-50 shadow-md"
                                            : "border-slate-200 bg-white hover:border-orange-200 hover:shadow-sm"
                                    }`}
                                >
                                    <p className="font-semibold text-slate-800">
                                        Q{item.question_id} · Upload #{item.upload_id}
                                    </p>
                                    <p className="text-sm text-muted mt-1">
                                        {item.score}/{item.max_score} · conf{" "}
                                        {(item.confidence * 100).toFixed(0)}%
                                    </p>
                                </button>
                            ))}
                        </div>

                        {selected && (
                            <div className="lg:col-span-9 grid md:grid-cols-2 gap-6">
                                <div className="card p-5">
                                    <h2 className="text-lg font-bold text-slate-800 mb-3">Student answer</h2>
                                    {imageSrc ? (
                                        <img
                                            src={imageSrc}
                                            alt="Crop"
                                            className="w-full rounded-xl border border-slate-200 shadow-sm"
                                        />
                                    ) : (
                                        <p className="text-muted text-sm">No image</p>
                                    )}
                                    {selected.ocr_text && (
                                        <pre className="mt-4 text-xs text-slate-500 whitespace-pre-wrap max-h-40 overflow-auto bg-slate-50 p-3 rounded-xl border border-slate-100">
                                            {selected.ocr_text}
                                        </pre>
                                    )}
                                </div>

                                <div className="card p-6 space-y-4">
                                    <h2 className="text-lg font-bold text-slate-800">AI grade</h2>
                                    <p className="text-4xl font-extrabold text-orange-500">
                                        {selected.score}
                                        <span className="text-slate-400 text-2xl font-semibold">
                                            /{selected.max_score}
                                        </span>
                                    </p>
                                    <p className="text-slate-600 text-sm leading-relaxed">{selected.feedback}</p>

                                    {selected.criteria_breakdown?.length > 0 && (
                                        <ul className="text-sm space-y-2">
                                            {selected.criteria_breakdown.map((c) => (
                                                <li
                                                    key={c.criterion_id}
                                                    className="border-b border-slate-100 pb-2"
                                                >
                                                    <span className="font-semibold text-orange-600">
                                                        {c.awarded_points}/{c.max_points}
                                                    </span>{" "}
                                                    <span className="text-slate-600">{c.reasoning}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    )}

                                    {selected.escalation_reasons?.length > 0 && (
                                        <div className="text-amber-700 text-xs font-medium bg-amber-50 px-3 py-2 rounded-lg border border-amber-100">
                                            Escalation: {selected.escalation_reasons.join("; ")}
                                        </div>
                                    )}

                                    {selected.plagiarism_flags?.length > 0 && (
                                        <div className="bg-rose-50 border border-rose-200 rounded-xl p-3 text-xs text-rose-700">
                                            <p className="font-bold mb-1">Plagiarism flags</p>
                                            <ul className="list-disc ml-4 space-y-1">
                                                {selected.plagiarism_flags.map((f, i) => (
                                                    <li key={i}>
                                                        {f.upload_a != null
                                                            ? `Upload #${f.upload_a} ↔ #${f.upload_b}`
                                                            : `Q${f.question_a} ↔ Q${f.question_b}`}{" "}
                                                        · {(f.similarity * 100).toFixed(0)}% similar
                                                        {f.reason ? ` — ${f.reason}` : ""}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    <div className="flex gap-3 pt-4">
                                        <button
                                            type="button"
                                            disabled={actionLoading}
                                            onClick={handleApprove}
                                            className="btn-success flex-1"
                                        >
                                            Approve (A)
                                        </button>
                                    </div>

                                    <div className="border-t border-slate-100 pt-4 space-y-3">
                                        <label className="label-text">Override score (O)</label>
                                        <input
                                            id="override-score"
                                            type="number"
                                            min={0}
                                            max={selected.max_score}
                                            value={overrideScore}
                                            onChange={(e) => setOverrideScore(e.target.value)}
                                            className="input-field"
                                        />
                                        <textarea
                                            placeholder="Review notes"
                                            value={notes}
                                            onChange={(e) => setNotes(e.target.value)}
                                            className="input-field text-sm"
                                            rows={2}
                                        />
                                        <button
                                            type="button"
                                            disabled={actionLoading}
                                            onClick={handleOverride}
                                            className="btn-warning w-full"
                                        >
                                            Override &amp; next
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
