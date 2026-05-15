export default function StatusBadge({

    status
}) {

    return (

        <span className={`

            px-4 py-1 rounded-full text-sm font-semibold

            ${status === "uploaded"
                ? "bg-yellow-500/20 text-yellow-300"

                : status === "ocr_complete"
                ? "bg-green-500/20 text-green-300"

                : status === "grading"
                ? "bg-blue-500/20 text-blue-300"

                : "bg-slate-700 text-slate-300"
            }

        `}>

            {status}

        </span>
    )
}