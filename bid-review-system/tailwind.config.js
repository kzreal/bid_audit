/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Vercel 风格颜色
      colors: {
        // 主色调
        black: '#000000',
        white: '#ffffff',
        gray: {
          50: '#fafafa',
          100: '#f4f4f5',
          200: '#eaeaea',
          300: '#d4d4d8',
          400: '#a1a1aa',
          500: '#71717a',
        },
        // Vercel 品牌蓝
        vercel: {
          blue: '#0070f3',
          'blue-hover': '#0051b3',
          'blue-light': 'rgba(0, 112, 243, 0.1)',
        },
        // 状态色（Vercel 风格）
        status: {
          pass: '#0070f3',
          fail: '#000000',
          pending: '#f4f4f5',
        },
      },
      // 边框圆角（Vercel 风格）
      borderRadius: {
        'vercel-sm': '2px',  // Vercel 风格极小圆角
        'vercel-md': '4px',
      },
      // 边框宽度
      borderWidth: {
        vercel: '1px',
      },
      // 阴影（极浅）
      boxShadow: {
        'vercel-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'vercel-md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      },
      // 过渡动画
      transitionDuration: {
        '150': '150ms',
      },
      transitionTimingFunction: {
        'ease-out-fast': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
