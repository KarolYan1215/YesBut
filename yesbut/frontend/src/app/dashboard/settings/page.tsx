'use client';

import { useState } from 'react';
import { useI18n, useTranslation } from '@/i18n';

type SettingsTab = 'profile' | 'preferences' | 'security';

export default function SettingsPage(): JSX.Element {
  const t = useTranslation();
  const { locale, setLocale } = useI18n();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [defaultMode, setDefaultMode] = useState<'sync' | 'async'>('async');
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    setTimeout(() => setIsSaving(false), 1000);
  };

  const tabs: { id: SettingsTab; label: string }[] = [
    { id: 'profile', label: locale === 'zh' ? '个人资料' : 'Profile' },
    { id: 'preferences', label: locale === 'zh' ? '偏好设置' : 'Preferences' },
    { id: 'security', label: locale === 'zh' ? '安全' : 'Security' },
  ];

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-xl font-semibold text-ink-100 mb-6">{t.settings.title}</h1>

      <div className="flex gap-1 mb-6 border-b border-ink-10">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-ink-100 border-b-2 border-ink-100'
                : 'text-ink-60 hover:text-ink-80'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="bg-white border border-ink-20 rounded-md p-6">
        {activeTab === 'profile' && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">
                {locale === 'zh' ? '显示名称' : 'Display Name'}
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">{t.auth.email}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              />
            </div>
          </div>
        )}

        {activeTab === 'preferences' && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">{t.settings.language}</label>
              <p className="text-xs text-ink-40 mb-2">{t.settings.languageDesc}</p>
              <select
                value={locale}
                onChange={(e) => setLocale(e.target.value as 'en' | 'zh')}
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              >
                <option value="en">{t.settings.english}</option>
                <option value="zh">{t.settings.chinese}</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">
                {locale === 'zh' ? '默认会话模式' : 'Default Session Mode'}
              </label>
              <select
                value={defaultMode}
                onChange={(e) => setDefaultMode(e.target.value as 'sync' | 'async')}
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              >
                <option value="async">{t.sessions.async} ({locale === 'zh' ? '推荐' : 'Recommended'})</option>
                <option value="sync">{t.sessions.sync}</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">{t.settings.theme}</label>
              <select
                value={theme}
                onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'system')}
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              >
                <option value="system">{t.settings.system}</option>
                <option value="light">{t.settings.light}</option>
                <option value="dark">{t.settings.dark}</option>
              </select>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">
                {locale === 'zh' ? '当前密码' : 'Current Password'}
              </label>
              <input
                type="password"
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">
                {locale === 'zh' ? '新密码' : 'New Password'}
              </label>
              <input
                type="password"
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-60 mb-1">{t.auth.confirmPassword}</label>
              <input
                type="password"
                className="w-full px-3 py-2 border border-ink-20 rounded text-sm focus:outline-none focus:border-ink-40"
              />
            </div>
          </div>
        )}

        <div className="mt-6 pt-4 border-t border-ink-10">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 bg-ink-100 text-white text-sm font-medium rounded hover:bg-ink-80 disabled:opacity-50 transition-colors"
          >
            {isSaving ? (locale === 'zh' ? '保存中...' : 'Saving...') : t.common.save}
          </button>
        </div>
      </div>
    </div>
  );
}
