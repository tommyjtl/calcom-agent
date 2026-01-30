export default function MessageSkeleton() {
    return (
        <div className="w-full flex justify-start mb-4">
            <div className="max-w-[80%] min-w-[60%] p-3 rounded-lg bg-gray-200 rounded-bl-none animate-pulse">
                <div className="space-y-2">
                    <div className="h-4 bg-gray-300 rounded w-full"></div>
                    {/* <div className="h-4 bg-gray-300 rounded w-4/5"></div>
                    <div className="h-4 bg-gray-300 rounded w-3/5"></div> */}
                </div>
            </div>
        </div>
    );
}
