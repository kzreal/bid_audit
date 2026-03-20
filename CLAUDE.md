# 投标文件审核系统 - AI 辅助开发文档

## 项目概述

这是一个基于 HiAgent API 的投标文件智能审核系统，使用 Vue3 + Vite（前端）+ Flask + Python（后端）实现。

## Design Context

### Users
企业内部审核团队，包括采购人员、法务人员等专业审核人员。他们在日常工作中使用该系统进行投标文件的智能审核，需要高效、专业的界面来提高工作效率。

### Brand Personality
专业 + 高效。传达可靠、精准、快速的审核体验，让用户对系统有信心。

### Aesthetic Direction
简约现代风格。基于现有的蓝色系主色调进行优化升级，使用大量留白、清晰层次、柔和阴影和微妙的过渡动画。参考现代企业级 SaaS 产品如 Linear、Notion 的设计语言。

### Design Principles

1. **清晰优先** (Clarity First)
   - 信息层级分明，重要内容突出显示
   - 使用留白区分内容区块
   - 状态通过颜色明确传达（绿色-通过、红色-不通过、黄色-待确认）

2. **高效交互** (Efficient Interaction)
   - 减少用户操作步骤，提供快捷操作
   - 加载状态清晰可见，避免用户等待焦虑
   - 错误提示具体且可操作

3. **专业可信** (Professional Trust)
   - 色彩使用克制，以蓝色系为主
   - 字体清晰易读，使用 Noto Sans SC 中文无衬线字体
   - 界面元素一致，遵循统一的设计规范

4. **渐进披露** (Progressive Disclosure)
   - 关键信息优先展示，详细信息按需展开
   - 长文本使用折叠或截断处理
   - 避免信息过载

5. **反馈及时** (Immediate Feedback)
   - 所有交互都有视觉反馈（悬停、点击、加载）
   - 操作结果及时通知用户
   - 动画过渡流畅自然（200-300ms）

### Design Tokens

#### Colors
- Primary: Blue-600 (#2563eb) → Blue-700 (#1d4ed8)
- Background: Gray-50 (#f9fafb)
- Surface: White (#ffffff)
- Border: Gray-200 (#e5e7eb)
- Success: Green-600 (#059669)
- Error: Red-600 (#dc2626)
- Warning: Yellow-600 (#d97706)

#### Typography
- Font Family: 'Noto Sans SC', 'Inter', system-ui, sans-serif
- Line Height: 1.5 (leading-relaxed)
- Font Sizes: text-xs (12px), text-sm (14px), text-base (16px), text-lg (18px), text-xl (20px)

#### Spacing
- Gap: 3 (0.75rem), 4 (1rem), 6 (1.5rem)
- Padding: 3 (0.75rem), 4 (1rem), 6 (1.5rem)
- Border Radius: rounded-md (0.375rem), rounded-lg (0.5rem), rounded-xl (0.75rem)

#### Shadows
- Default: shadow-sm
- Hover: shadow-md
- Elevated: shadow-lg

#### Transitions
- Duration: 200ms for micro-interactions, 300ms for layout changes
- Easing: ease-in-out

### Layout Structure

三栏布局（35% + 30% + 35%）：
- **左侧**：招标信息输入 + 文件上传
- **中间**：任务列表
- **右侧**：审核详情

响应式考虑：小屏幕时切换为单栏堆叠布局。

### Accessibility

- 所有交互元素都有明确的焦点状态
- 颜色对比度符合 WCAG AA 标准
- 支持键盘导航
- 为重要状态提供视觉和非视觉提示（颜色 + 图标 + 文字）

---

## 技术栈

### 前端
- Vue 3 (Composition API)
- Vite (构建工具)
- Pinia (状态管理)
- Tailwind CSS (样式框架)
- Axios (HTTP 客户端)

### 后端
- Flask (Web 框架)
- Flask-CORS (跨域支持)
- requests (HTTP 客户端)

### API
- HiAgent API (智能审核服务)

## 快速启动

详细启动指南请参考 `mvp-guide.md` 或 `guide.md` 文件。
