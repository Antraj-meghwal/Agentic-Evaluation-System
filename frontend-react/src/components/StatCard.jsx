export default function StatCard({

    title,

    value,

    subtitle,

    onClick
}) {

    return (

        <div
            onClick={onClick}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-blue-500 transition-all cursor-pointer"
        >

            <h2 className="text-2xl font-semibold">

                {title}

            </h2>

            <p className="text-5xl font-bold mt-5">

                {value}

            </p>

            <p className="text-slate-400 mt-3">

                {subtitle}

            </p>

        </div>
    )
}