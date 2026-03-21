# 投标文件审核系统 - AI 辅助开发文档

## 项目概述

这是一个基于 HiAgent API 的投标文件智能审核系统，使用 Vue3 + Vite（前端）+ Flask + Python（后端）实现。

## Design Context

### Users
企业内部审核团队，包括采购人员、法务人员等专业审核人员。他们在日常工作中使用该系统进行投标文件的智能审核，需要高效、专业的界面来提高工作效率。

标书员，需要在日常工作中进行投标文件审核和任务管理的企业内部人员。他们需要在不同的招标项目中快速应用标准化的审核流程，同时也要能根据具体项目需求进行灵活调整。

### Brand Personality
专业 + 高效 + 极简。传达可靠、精准、快速的审核体验，让用户对系统有信心，同时享受现代极简设计带来的清晰体验。

### Aesthetic Direction
**Vercel 风格 + Next.js 文档风格**。以极简黑白配色为主，仅在头部保留蓝色渐变作为品牌识别。

参考元素：
- **Vercel 官网**：极简黑白、高对比度、1px 细边框、极小圆角 (2px)
- **Next.js 文档站**：清晰的排版、柔和的背景分隔、精致的间距系统

**核心设计语言**：
- 极简黑白配色（#000000, #ffffff, #fafafa, #eaeaea）
- 1px 细边框（无 2px 粗边框）
- 极小圆角（rounded-sm 或完全不圆角）
- 几乎无阴影
- 高对比度文字
- 精细的间距系统
- 柔和的背景分隔（使用极浅灰色区分区域）

### Design Principles

1. **极简至上** (Minimalism First)
   - 使用纯黑、纯白、极浅灰配色
   - 1px 细边框，极小圆角 (2px)
   - 移除不必要的阴影和装饰
   - 让内容本身成为视觉焦点

2. **品牌识别** (Brand Recognition)
   - 头部保留蓝色渐变作为品牌标识
   - 其他区域使用极简黑白风格
   - 品牌蓝 (#0070f3) 仅用于交互状态（悬停、选中）

3. **清晰层级** (Clear Hierarchy)
   - 使用 1px 边框 + 背景色区分区域
   - 柔和的背景分隔（#fafafa, #f4f4f5）
   - 高对比度文字，确保可读性
   - 精细的间距系统构建视觉节奏

4. **状态传达** (Status Communication)
   - 使用 Vercel 品牌蓝 (#0070f3) 和黑色表达不同状态
   - 通过：品牌蓝填充 + 白色图标/文字
   - 不通过：黑色填充 + 白色图标/文字
   - 待确认：浅灰背景 + 黑色文字

5. **交互反馈** (Immediate Feedback)
   - 交互元素（按钮、输入框）悬停时显示品牌蓝边框
   - 选中状态使用品牌蓝高亮
   - 过渡动画流畅（200ms）
   - 极简的加载动画

### Design Tokens

#### 主色调
```css
--color-black: #000000;
--color-white: #ffffff;
--color-gray-50: #fafafa;
--color-gray-100: #f4f4f5;
--color-gray-200: #eaeaea;
--color-gray-300: #d4d4d8;
--color-gray-400: #a1a1aa;
--color-gray-500: #71717a;
```

#### 品牌色
```css
--color-vercel-blue: #0070f3;
--color-vercel-blue-hover: #0051b3;
--color-vercel-blue-light: rgba(0, 112, 243, 0.1);
```

#### 状态色（Vercel 风格）
```css
--status-pass-bg: #0070f3;        /* 品牌蓝填充 */
--status-pass-text: #ffffff;
--status-fail-bg: #000000;        /* 黑色填充 */
--status-fail-text: #ffffff;
--status-pending-bg: #f4f4f5;    /* 浅灰背景 */
--status-pending-text: #000000;
```

#### Typography
```css
font-family: 'Noto Sans SC', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;        /* 16px */
--text-lg: 1.125rem;      /* 18px */
--text-xl: 1.25rem;       /* 20px */
--text-2xl: 1.5rem;      /* 24px */
```

#### Spacing
```css
--spacing-1: 0.25rem;   /* 4px */
--spacing-2: 0.5rem;    /* 8px */
--spacing-3: 0.75rem;   /* 12px */
--spacing-4: 1rem;      /* 16px */
--spacing-5: 1.25rem;   /* 20px */
--spacing-6: 1.5rem;    /* 24px */
--spacing-8: 2rem;      /* 32px */
```

#### Border Radius
```css
--radius-sm: 0.125rem;   /* 2px - Vercel 风格 */
--radius-md: 0.25rem;    /* 4px */
--radius-lg: 0.5rem;     /* 8px */
```

#### Borders
```css
--border-thin: 1px solid #eaeaea;
--border-brand: 1px solid #0070f3;
--border-black: 1px solid #000000;
```

#### Shadows
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
```
Vercel 风格通常不使用阴影或仅使用极浅阴影。

#### Transitions
```css
--transition-fast: 150ms ease-out;
--transition-base: 200ms ease-in-out;
--transition-slow: 300ms ease-in-out;
```

### Layout Structure

三栏布局（35% + 30% + 35%）：
- **左侧**：招标信息输入 + 文件上传
- **中间**：任务列表
- **右侧**：审核详情

响应式考虑：小屏幕时切换为单栏堆叠布局。

**头部区域**：
- 左侧头部：蓝色渐变背景（保留品牌识别）
- 中间/右侧头部：白色背景 + 1px 底边框

**内容区域**：
- 白色卡片 + 1px 边框
- 使用浅灰背景分隔区域

### Accessibility

- 所有交互元素都有明确的焦点状态（品牌蓝边框）
- 颜色对比度符合 WCAG AA 标准
- 支持键盘导航
- 为重要状态提供视觉和非视觉提示（颜色 + 图标 + 文字）
- 最小点击区域：44×44px

---

## 模版功能设计上下文

### Users
标书员，需要在日常工作中进行投标文件审核和任务管理的企业内部人员。他们需要在不同的招标项目中快速应用标准化的审核流程，同时也要能根据具体项目需求进行灵活调整。

### Brand Personality
专业 + 高效 + 灵活。传达可靠、快速、易用的审核体验，让用户对模版功能有信心并愿意长期使用。

### Aesthetic Direction
简约现代风格。基于现有的蓝色系主色调，保持与当前设计语言的一致性。模版功能应该自然融入现有界面，通过清晰的视觉层次、柔和的阴影和流畅的动画来提升用户体验。

### Design Principles（模版专属）

1. **快速检索** (Quick Discovery)
   - 模版库采用标签 + 搜索的组合方式，支持多标签筛选和关键词搜索
   - 提供模版预览功能，让用户在不应用模版的情况下了解其内容
   - 常用模版优先展示，支持收藏功能

2. **灵活应用** (Flexible Application)
   - 采用追加式应用，将模版任务追加到现有任务列表末尾
   - 保留现有任务，支持后续调整和删除
   - 应用后提供撤销功能，避免误操作

3. **双路径创建** (Dual Creation Paths)
   - 支持从头创建新模版：手动添加、编辑、删除任务，拖拽排序
   - 支持从现有项目生成：将已完成的审核任务列表快速保存为模版
   - 两种方式都应提供简单直观的操作流程

4. **轻量编辑** (Lightweight Editing)
   - 提供基础编辑能力：添加、删除、修改任务内容，拖拽排序
   - 编辑器界面简洁，避免过度复杂
   - 实时预览编辑结果

5. **视觉延续** (Visual Continuity)
   - 模版功能沿用现有设计 tokens 和组件样式
   - 保持与任务列表、审核详情等现有模块的视觉一致性
   - 使用相同的状态标签、卡片样式和交互动效

### 模版功能设计规范

#### 功能范围

**1. 模版库管理**
- 模版列表展示（卡片形式）
- 标签筛选和关键词搜索
- 模版预览（查看任务列表）
- 模版收藏/取消收藏
- 模版编辑和删除

**2. 模版创建**
- **手动创建**：新建模版 → 添加任务 → 编辑任务 → 拖拽排序 → 保存
- **从项目生成**：选择已完成的审核项目 → 确认任务列表 → 输入模版名称 → 添加标签 → 保存

**3. 模版编辑**
- 模版基本信息编辑（名称、描述、标签）
- 任务列表编辑（添加、删除、修改内容）
- 拖拽排序任务
- 实时预览

**4. 模版应用**
- 从模版库选择模版
- 预览模版内容
- 确认应用（追加到现有任务列表）
- 支持撤销最近一次应用

#### UI 结构建议

**模版库入口**：
- 在左侧输入区顶部添加「模版库」入口（图标 + 文字）
- 点击后展开模版库抽屉或弹窗

**模版库布局**：
- 顶部：搜索框 + 标签筛选器
- 中间：模版卡片网格（展示名称、标签、任务数量）
- 底部：创建新模版按钮

**模版编辑器**：
- 左侧：任务列表（可拖拽排序）
- 右侧：基本信息编辑 + 任务详情编辑

#### Design Tokens 扩展（模版专属）

**颜色**
- 模版标签背景：bg-blue-50, bg-purple-50, bg-green-50, bg-orange-50
- 模版标签文字：text-blue-700, text-purple-700, text-green-700, text-orange-700

**图标**
- 模版库：文档堆叠图标
- 收藏：星形图标（空心/实心）
- 拖拽：六个点的图标
- 添加任务：加号图标
- 预览：眼睛图标

**交互动效**
- 模版卡片悬停：轻微上移 + 阴影加深（0.5s）
- 拖拽排序：平滑移动效果（0.2s）
- 抽屉展开/收起：滑入滑出（0.3s）

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
