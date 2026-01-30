interface ErrorCardProps {
    title: string;
    message: string;
    type?: 'error' | 'warning';
}

export default function ErrorCard({ title, message, type = 'error' }: ErrorCardProps) {
    const isError = type === 'error';

    return (
        <div className={`${isError ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4 mt-3`}>
            <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                    <div className={`w-8 h-8 ${isError ? 'bg-red-100' : 'bg-yellow-100'} rounded-full flex items-center justify-center`}>
                        <svg className={`w-4 h-4 ${isError ? 'text-red-600' : 'text-yellow-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {isError ? (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            ) : (
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                            )}
                        </svg>
                    </div>
                </div>
                <div className="flex-1 min-w-0">
                    <h4 className={`text-sm font-medium ${isError ? 'text-red-900' : 'text-yellow-900'} mb-1`}>{title}</h4>
                    <p className={`text-xs ${isError ? 'text-red-700' : 'text-yellow-700'}`}>{message}</p>
                </div>
            </div>
        </div>
    );
}
