export default function StatCard({ title, value, subtitle, onClick, accent = "teal" }) {
    const accents = {
        teal: "from-teal-500/10 to-indigo-500/5 group-hover:border-teal-300 group-hover:shadow-teal-500/10",
        orange: "from-orange-500/10 to-amber-500/5 group-hover:border-orange-300 group-hover:shadow-orange-500/10",
        violet: "from-violet-500/10 to-fuchsia-500/5 group-hover:border-violet-300 group-hover:shadow-violet-500/10",
    };

    return (
        <div
            onClick={onClick}
            className={`group relative card rounded-3xl p-7 transition-all duration-300 cursor-pointer overflow-hidden hover:-translate-y-1 hover:shadow-xl bg-gradient-to-br ${accents[accent] || accents.teal}`}
        >
            <div className="absolute -top-6 -right-6 w-28 h-28 rounded-full bg-gradient-to-br from-teal-400/10 to-violet-400/10 transition-transform group-hover:scale-125" />
            <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide group-hover:text-teal-600 transition-colors">
                {title}
            </h2>
            <p className="text-5xl font-extrabold mt-3 mb-2 text-slate-800 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-teal-600 group-hover:to-violet-600 transition-all">
                {value}
            </p>
            <p className="text-sm text-slate-500 font-medium">{subtitle}</p>
        </div>
    );
}
