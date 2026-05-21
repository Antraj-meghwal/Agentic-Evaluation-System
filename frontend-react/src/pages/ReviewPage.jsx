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

    useEffect(() => {
        function onKey(e) {
            if (!selected) return;
            if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

            if (e.key === "a" || e.key === "A") {
                e.preventDefault();
                handleApprove();
            }
            if (e.key === "o" || e.key === "O") {
                e.preventDefault();
                document.getElementById("override-score")?.focus();
            }
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
    });

    function selectNext(delta) {
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
    }

    async function handleApprove() {
        if (!selected) return;
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
    }

    async function handleOverride() {
        if (!selected) return;
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
    }

    const apiBase = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    const imageSrc = selected?.crop_image_url
        ? `${apiBase}${selected.crop_image_url}`
        : null;

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="p-6 max-w-[1600px] mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-4xl font-bold">Human Review Queue</h1>
                        <p className="text-slate-400 mt-1 text-sm">
                            Shortcuts: <kbd className="px-1 bg-slate-800 rounded">A</kbd> approve ·{" "}
                            <kbd className="px-1 bg-slate-800 rounded">O</kbd> override ·{" "}
                            <kbd className="px-1 bg-slate-800 rounded">J</kbd>/<kbd className="px-1 bg-slate-800 rounded">K</kbd> next/prev
                        </p>
                    </div>
                    <span className="text-slate-400">{queue.length} pending</span>
                </div>

                {message && (
                    <p className="mb-4 text-sm text-emerald-400">{message}</p>
                )}

                {loading ? (
                    <p className="text-slate-400">Loading queue…</p>
                ) : queue.length === 0 ? (
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-10 text-center text-slate-400">
                        No items need review. Run{" "}
                        <code className="text-indigo-400">POST /grading/run/:id</code> on an upload first.
                    </div>
                ) : (
                    <div className="grid lg:grid-cols-12 gap-6">
                        <div className="lg:col-span-3 space-y-2 max-h-[75vh] overflow-y-auto">
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
                                            ? "border-orange-500 bg-orange-500/10"
                                            : "border-slate-800 bg-slate-900 hover:border-slate-600"
                                    }`}
                                >
                                    <p className="font-medium">
                                        Q{item.question_id} · Upload #{item.upload_id}
                                    </p>
                                    <p className="text-sm text-slate-400 mt-1">
                                        {item.score}/{item.max_score} · conf{" "}
                                        {(item.confidence * 100).toFixed(0)}%
                                    </p>
                                </button>
                            ))}
                        </div>

                        {selected && (
                            <div className="lg:col-span-9 grid md:grid-cols-2 gap-6">
                                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
                                    <h2 className="text-lg font-semibold mb-3">Student answer</h2>
                                    {imageSrc ? (
                                        <img
                                            src={imageSrc}
                                            alt="Crop"
                                            className="w-full rounded-lg border border-slate-700"
                                        />
                                    ) : (
                                        <p className="text-slate-500 text-sm">No image</p>
                                    )}
                                    {selected.ocr_text && (
                                        <pre className="mt-4 text-xs text-slate-400 whitespace-pre-wrap max-h-40 overflow-auto">
                                            {selected.ocr_text}
                                        </pre>
                                    )}
                                </div>

                                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                                    <h2 className="text-lg font-semibold">AI grade</h2>
                                    <p className="text-3xl font-bold text-orange-400">
                                        {selected.score}
                                        <span className="text-slate-500 text-xl">
                                            /{selected.max_score}
                                        </span>
                                    </p>
                                    <p className="text-slate-300 text-sm">{selected.feedback}</p>

                                    {selected.criteria_breakdown?.length > 0 && (
                                        <ul className="text-sm space-y-2">
                                            {selected.criteria_breakdown.map((c) => (
                                                <li
                                                    key={c.criterion_id}
                                                    className="border-b border-slate-800 pb-2"
                                                >
                                                    <span className="text-orange-300">
                                                        {c.awarded_points}/{c.max_points}
                                                    </span>{" "}
                                                    {c.reasoning}
                                                </li>
                                            ))}
                                        </ul>
                                    )}

                                    {selected.escalation_reasons?.length > 0 && (
                                        <div className="text-amber-400 text-xs">
                                            Escalation: {selected.escalation_reasons.join("; ")}
                                        </div>
                                    )}

                                    {selected.plagiarism_flags?.length > 0 && (
                                        <div className="bg-red-500/10 border border-red-500/40 rounded-xl p-3 text-xs text-red-300">
                                            <p className="font-semibold mb-1">Plagiarism flags</p>
                                            <ul className="list-disc ml-4 space-y-1">
                                                {selected.plagiarism_flags.map((f, i) => (
                                                    <li key={i}>
                                                        Q{f.question_a} ↔ Q{f.question_b} ·{" "}
                                                        similarity {(f.similarity * 100).toFixed(0)}%
                                                        {f.method ? ` (${f.method})` : ""}
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
                                            className="flex-1 bg-emerald-600 hover:bg-emerald-500 py-3 rounded-xl font-medium"
                                        >
                                            Approve (A)
                                        </button>
                                    </div>

                                    <div className="border-t border-slate-800 pt-4 space-y-3">
                                        <label className="text-sm text-slate-400">
                                            Override score (O)
                                        </label>
                                        <input
                                            id="override-score"
                                            type="number"
                                            min={0}
                                            max={selected.max_score}
                                            value={overrideScore}
                                            onChange={(e) => setOverrideScore(e.target.value)}
                                            className="w-full p-3 rounded-xl bg-slate-950 border border-slate-700"
                                        />
                                        <textarea
                                            placeholder="Review notes"
                                            value={notes}
                                            onChange={(e) => setNotes(e.target.value)}
                                            className="w-full p-3 rounded-xl bg-slate-950 border border-slate-700 text-sm"
                                            rows={2}
                                        />
                                        <button
                                            type="button"
                                            disabled={actionLoading}
                                            onClick={handleOverride}
                                            className="w-full bg-orange-600 hover:bg-orange-500 py-3 rounded-xl font-medium"
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
