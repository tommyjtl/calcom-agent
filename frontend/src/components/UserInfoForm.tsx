'use client';

import { useState } from 'react';

interface UserInfo {
    name: string;
    email: string;
    timezone: string;
}

interface UserInfoFormProps {
    onSubmit: (userInfo: UserInfo) => void;
}

export default function UserInfoForm({ onSubmit }: UserInfoFormProps) {
    const [formData, setFormData] = useState<UserInfo>({
        name: '',
        email: '',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    });

    const [errors, setErrors] = useState<Partial<UserInfo>>({});

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        // Basic validation
        const newErrors: Partial<UserInfo> = {};
        if (!formData.name.trim()) newErrors.name = 'Name is required';
        if (!formData.email.trim()) newErrors.email = 'Email is required';
        if (!formData.timezone.trim()) newErrors.timezone = 'Timezone is required';

        // Email validation
        if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = 'Please enter a valid email address';
        }

        setErrors(newErrors);

        if (Object.keys(newErrors).length === 0) {
            onSubmit(formData);
        }
    };

    const handleChange = (field: keyof UserInfo, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: undefined }));
        }
    };

    // Get common timezones for the dropdown
    const commonTimezones = [
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Australia/Sydney',
        'UTC',
    ];

    return (
        <div className="min-h-screen bg-gray-400 flex items-center justify-center p-4 font-sans">
            <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
                <div className="text-center mb-6">
                    <h1 className="text-lg font-semibold text-gray-800 mb-2">Welcome to Cal.com Assistant</h1>
                    <p className="text-sm text-gray-600">Please provide your information to get started</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                            Full Name
                        </label>
                        <input
                            type="text"
                            id="name"
                            value={formData.name}
                            onChange={(e) => handleChange('name', e.target.value)}
                            className={`text-sm w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.name ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="Enter your full name"
                        />
                        {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                    </div>

                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={formData.email}
                            onChange={(e) => handleChange('email', e.target.value)}
                            className={`text-sm w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.email ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="Enter your email address"
                        />
                        {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                    </div>

                    <div>
                        <label htmlFor="timezone" className="block text-sm font-medium text-gray-700 mb-1">
                            Timezone
                        </label>
                        <select
                            id="timezone"
                            value={formData.timezone}
                            onChange={(e) => handleChange('timezone', e.target.value)}
                            className={`text-sm w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.timezone ? 'border-red-500' : 'border-gray-300'
                                }`}
                        >
                            {commonTimezones.map((tz) => (
                                <option key={tz} value={tz}>
                                    {tz}
                                </option>
                            ))}
                        </select>
                        {errors.timezone && <p className="text-red-500 text-xs mt-1">{errors.timezone}</p>}
                    </div>

                    <button
                        type="submit"
                        className="text-sm w-full bg-blue-500 text-white py-3 px-4 rounded-md hover:bg-blue-600 transition-colors font-medium"
                    >
                        Continue to Chat
                    </button>
                </form>
            </div>
        </div>
    );
}
