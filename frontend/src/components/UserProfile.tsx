'use client';

import { useState } from 'react';

interface UserInfo {
    name: string;
    email: string;
    timezone: string;
}

interface UserProfileProps {
    userInfo: UserInfo;
}

export default function UserProfile({ userInfo }: UserProfileProps) {
    const [showTooltip, setShowTooltip] = useState(false);

    const handleMouseEnter = () => setShowTooltip(true);
    const handleMouseLeave = () => setShowTooltip(false);

    return (
        <div
            className="relative"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            <div className="flex items-center space-x-2 cursor-pointer">
                {/* <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {userInfo.name.charAt(0).toUpperCase()}
                </div> */}
                <span className="text-sm font-medium text-gray-700">Hi, {userInfo.name}!</span>
            </div>

            {showTooltip && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-10">
                    <div className="space-y-2">
                        <div>
                            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Name</label>
                            <p className="text-sm text-gray-800">{userInfo.name}</p>
                        </div>
                        <div>
                            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Email</label>
                            <p className="text-sm text-gray-800">{userInfo.email}</p>
                        </div>
                        <div>
                            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Timezone</label>
                            <p className="text-sm text-gray-800">{userInfo.timezone}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
