export default function LoadingSpinner() {
    return (
        <div className="flex items-center justify-center py-20">
            <div className="w-12 h-12 border-4 border-teal-200 border-t-teal-500 rounded-full animate-spin" />
        </div>
    );
}
