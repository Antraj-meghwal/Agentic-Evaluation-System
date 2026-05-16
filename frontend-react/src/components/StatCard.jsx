export default function StatCard({ title, value, subtitle, onClick }) {
    return (
        <div
            onClick={onClick}
            className="group relative bg-slate-900/50 backdrop-blur-sm border border-slate-800 hover:border-indigo-500/50 rounded-3xl p-7 transition-all duration-300 cursor-pointer overflow-hidden hover:shadow-[0_8px_30px_rgba(99,102,241,0.1)] hover:-translate-y-1"
        >
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-bl-full transition-transform group-hover:scale-110"></div>
            <h2 className="text-lg font-medium text-slate-400 group-hover:text-indigo-400 transition-colors">
                {title}
            </h2>
            <p className="text-5xl font-bold mt-4 mb-2 text-white">
                {value}
            </p>
            <p className="text-sm text-slate-500 font-medium">
                {subtitle}
            </p>
        </div>
    );
}