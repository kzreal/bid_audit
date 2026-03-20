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
