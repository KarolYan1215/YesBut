import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['IBM Plex Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['IBM Plex Mono', 'JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1.25' }],    // 12px
        'sm': ['0.875rem', { lineHeight: '1.5' }],   // 14px
        'base': ['1rem', { lineHeight: '1.5' }],     // 16px
        'lg': ['1.25rem', { lineHeight: '1.25' }],   // 20px
        'xl': ['1.5rem', { lineHeight: '1.25' }],    // 24px
        '2xl': ['2rem', { lineHeight: '1.25' }],     // 32px
        '3xl': ['2.5rem', { lineHeight: '1.25' }],   // 40px
      },
      colors: {
        // Ink Color Palette - Monochrome Depth
        ink: {
          100: 'var(--ink-100)',
          80: 'var(--ink-80)',
          60: 'var(--ink-60)',
          40: 'var(--ink-40)',
          20: 'var(--ink-20)',
          10: 'var(--ink-10)',
          '05': 'var(--ink-05)',
        },
        paper: 'var(--paper)',
        // Base colors (legacy compatibility)
        background: 'var(--bg)',
        surface: 'var(--surface)',
        border: 'var(--border)',
        foreground: 'var(--text)',
        muted: 'var(--text-muted)',
        primary: {
          DEFAULT: '#2563EB',
          hover: '#1D4ED8',
        },
        // Signal colors
        signal: {
          info: 'var(--signal-info)',
          success: 'var(--signal-success)',
          warning: 'var(--signal-warning)',
          critical: 'var(--signal-critical)',
          synthesis: 'var(--signal-synthesis)',
        },
        // Phase colors
        phase: {
          diverge: 'var(--phase-diverge)',
          filter: 'var(--phase-filter)',
          converge: 'var(--phase-converge)',
        },
        // Node type colors
        node: {
          goal: 'var(--node-goal)',
          claim: 'var(--node-claim)',
          fact: 'var(--node-fact)',
          constraint: 'var(--node-constraint)',
          atomic: 'var(--node-atomic)',
          pending: 'var(--node-pending)',
          synthesis: 'var(--node-synthesis)',
        },
        // Edge type colors
        edge: {
          support: 'var(--edge-support)',
          attack: 'var(--edge-attack)',
          conflict: 'var(--edge-conflict)',
          entail: 'var(--edge-entail)',
          decompose: 'var(--edge-decompose)',
        },
      },
      spacing: {
        '1': '0.25rem',   // 4px
        '2': '0.5rem',    // 8px
        '3': '0.75rem',   // 12px
        '4': '1rem',      // 16px
        '5': '1.25rem',   // 20px
        '6': '1.5rem',    // 24px
        '8': '2rem',      // 32px
        '10': '2.5rem',   // 40px
        '12': '3rem',     // 48px
        '16': '4rem',     // 64px
      },
      borderRadius: {
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 2px 4px 0 rgb(0 0 0 / 0.1)',
      },
      transitionDuration: {
        'instant': '100ms',
        'fast': '150ms',
        'normal': '200ms',
        'slow': '300ms',
      },
      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'ease-in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      animation: {
        'pulse-slow': 'pulse-slow 2s ease-in-out infinite',
        'fade-in': 'fadeIn 200ms ease-out',
        'slide-in': 'slideIn 200ms ease-out',
        'node-create': 'nodeCreate 200ms ease-out',
      },
      keyframes: {
        'pulse-slow': {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        nodeCreate: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
