export default function StatusBadge({ status }) {
    const styles = {
        uploaded: "bg-amber-50 text-amber-700 border-amber-200",
        ocr_complete: "bg-emerald-50 text-emerald-700 border-emerald-200",
        grading: "bg-sky-50 text-sky-700 border-sky-200",
        processing: "bg-violet-50 text-violet-700 border-violet-200",
        graded: "bg-teal-50 text-teal-700 border-teal-200",
        failed: "bg-rose-50 text-rose-700 border-rose-200",
    };

    return (
        <span
            className={`inline-flex px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border ${
                styles[status] || "bg-slate-100 text-slate-600 border-slate-200"
            }`}
        >
            {status?.replace(/_/g, " ")}
        </span>
    );
}
