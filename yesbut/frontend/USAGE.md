# YesBut 前端使用文档

## 概述

YesBut 是一个基于多智能体协同的头脑风暴系统，前端采用 React/Next.js 技术栈。本文档涵盖组件架构、使用模式和集成指南。

## 快速开始

```bash
# 安装依赖
npm install

# 开发服务器
npm run dev

# 类型检查
npm run type-check

# 生产构建
npm run build
```

## 架构

### 目录结构

```
src/
├── app/                    # Next.js App Router 页面
│   ├── (auth)/            # 认证相关页面
│   ├── api/               # API 路由 (BFF 代理)
│   └── dashboard/         # 主应用页面
├── components/
│   ├── graph/             # 图形可视化组件
│   │   ├── nodes/         # 自定义节点类型
│   │   ├── edges/         # 自定义边类型
│   │   └── panels/        # 侧边面板
│   ├── layout/            # 布局组件
│   ├── session/           # 会话相关组件
│   ├── input/             # 输入组件
│   └── ui/                # 基础 UI 组件
├── hooks/                 # 自定义 React Hooks
├── services/              # API 和 SSE 服务
└── store/                 # Zustand 状态存储
```

## 组件

### 图形组件

#### GraphCanvas
用于可视化层状图网络的主 React Flow 画布。

```tsx
import { GraphCanvas } from '@/components/graph/graph-canvas';

<GraphCanvas
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  onNodeClick={(nodeId) => setSelectedNodeId(nodeId)}
  isCurrentBranchLocked={false}
  lockingAgentName="BM-1"
/>
```

#### 节点类型

| 类型 | 组件 | 描述 |
|------|-----------|-------------|
| `goal` | GoalNode | 表示决策目标的根节点 |
| `claim` | ClaimNode | 智能体生成的推理结论 |
| `fact` | FactNode | 经外部验证的事实 |
| `constraint` | ConstraintNode | 用户定义的约束（硬/软） |
| `atomic` | AtomicTopicNode | 不可再分的原子议题 |
| `pending` | PendingNode | 等待自底向上匹配 |
| `preview` | PreviewNode | 生成过程中的流式预览 |
| `synthesis` | SynthesisNode | 黑格尔辩证综合节点 |

```tsx
// 节点数据结构
interface NodeData {
  label: string;
  confidence: number;
  validity?: number;
  utility?: number;
  novelty?: number;
  agentType?: string;
  isPreview?: boolean;
}
```

#### 边类型

| 类型 | 组件 | 视觉样式 | 描述 |
|------|-----------|--------|-------------|
| `support` | SupportEdge | 绿色实线 | 正向证据支持 |
| `attack` | AttackEdge | 红色实线 | 削弱可信度 |
| `conflict` | ConflictEdge | 橙色虚线 | 互斥关系 |
| `decompose` | DecomposeEdge | 灰色实线 | 父子层级关系 |
| `entail` | EntailEdge | 蓝色实线 | 逻辑蕴含 |
| `critical` | CriticalEdge | 动态样式 | 基于敏感度分析 |

### 面板组件

#### NodeDetailPanel
显示选中节点的详细信息。

```tsx
import { NodeDetailPanel } from '@/components/graph/panels/node-detail-panel';

<NodeDetailPanel
  selectedNodeId={selectedNodeId}
  onClose={() => setSelectedNodeId(null)}
  isOpen={!!selectedNodeId}
  canEdit={!isLocked}
  nodeData={{
    type: 'claim',
    label: '节点内容',
    confidence: 0.85,
    validity: 0.9,
    utility: 0.7,
    novelty: 0.6,
  }}
/>
```

#### BranchPanel
管理推理图中的分支。

```tsx
import { BranchPanel } from '@/components/graph/panels/branch-panel';

<BranchPanel
  branches={branches}
  selectedBranchId={selectedBranchId}
  onSelectBranch={(id) => setSelectedBranchId(id)}
  onForkBranch={(nodeId) => handleFork(nodeId)}
  onMergeBranches={(id1, id2) => handleMerge(id1, id2)}
  onPruneBranch={(id) => handlePrune(id)}
  isOpen={showBranchPanel}
  onClose={() => setShowBranchPanel(false)}
/>
```

#### AgentActivityPanel
实时智能体活动日志，支持流式更新。

```tsx
import { AgentActivityPanel } from '@/components/graph/panels/agent-activity-panel';

<AgentActivityPanel
  activities={activities}
  activeAgentId={activeAgentId}
  isOpen={showActivityPanel}
  onClose={() => setShowActivityPanel(false)}
  onInterruptAgent={(agentId) => handleInterrupt(agentId)}
  maxEntries={50}
/>
```

#### SensitivityPanel
稳定性和敏感度分析结果展示。

```tsx
import { SensitivityPanel } from '@/components/graph/panels/sensitivity-panel';

<SensitivityPanel
  sessionId={sessionId}
  criticalNodes={criticalNodes}
  pathAnalysis={pathAnalysis}
  stabilityScore={0.75}
  isOpen={showSensitivity}
  onClose={() => setShowSensitivity(false)}
  onHighlightNode={(nodeId) => highlightNode(nodeId)}
  onRunSimulation={(nodeId, confidence) => runSimulation(nodeId, confidence)}
/>
```

## Hooks

### useSession
会话状态管理。

```tsx
import { useSession } from '@/hooks/use-session';

const {
  session,
  isLoading,
  error,
  refetch,
  updateSession,
  toggleMode,
  pauseSession,
  resumeSession,
} = useSession(sessionId);
```

### useGraph
图形操作和状态管理。

```tsx
import { useGraph } from '@/hooks/use-graph';

const {
  nodes,
  edges,
  isLoading,
  error,
  addNode,
  updateNode,
  removeNode,
  addEdge,
  removeEdge,
  getAncestors,
  getDescendants,
  getCausalPath,
  applyLayout,
  fitView,
} = useGraph(sessionId);
```

### useSSE
Server-Sent Events 连接管理。

```tsx
import { useSSE } from '@/hooks/use-sse';

const {
  connectionState,
  error,
  subscribe,
  reconnect,
  disconnect,
  lastEventId,
} = useSSE(sessionId, {
  autoConnect: true,
  reconnectDelay: 3000,
  maxReconnectAttempts: 10,
});

// 订阅事件
useEffect(() => {
  const unsubscribe = subscribe('node_finalized', (data) => {
    console.log('节点已确认:', data);
  });
  return unsubscribe;
}, [subscribe]);
```

## 服务

### API 客户端

```tsx
import { apiClient } from '@/services/api-client';

// GET 请求
const session = await apiClient.get<Session>(`/sessions/${id}`);

// POST 请求
const newSession = await apiClient.post<Session>('/sessions', { title: '新会话' });

// PUT 请求
await apiClient.put(`/sessions/${id}`, { status: 'active' });

// DELETE 请求
await apiClient.delete(`/sessions/${id}`);
```

### SSE 服务

```tsx
import { SSEService, createSessionSSE } from '@/services/sse-service';

const sse = createSessionSSE(sessionId);
sse.connect();

sse.subscribe('message', (event) => {
  console.log('收到消息:', event.data);
});

sse.onStateChange((state) => {
  console.log('连接状态:', state);
});

// 清理
sse.disconnect();
```

## 状态管理

### Graph Store

```tsx
import { useGraphStore } from '@/store/graph-store';

const {
  nodes,
  edges,
  selectedNodeId,
  setNodes,
  setEdges,
  addNode,
  updateNode,
  removeNode,
  setSelectedNode,
} = useGraphStore();
```

### Session Store

```tsx
import { useSessionStore } from '@/store/session-store';

const {
  currentSession,
  sessions,
  setCurrentSession,
  updateSession,
} = useSessionStore();
```

### Lock Store

```tsx
import { useLockStore } from '@/store/lock-store';

const {
  isLocked,
  lockingAgent,
  acquireLock,
  releaseLock,
} = useLockStore();
```

## 设计系统

### 色彩系统 (Ink 墨色系统)

| Token | 值 | 用途 |
|-------|-------|-------|
| `ink-100` | #1a1a1a | 主要文本 |
| `ink-80` | #404040 | 次要文本 |
| `ink-60` | #666666 | 辅助文本 |
| `ink-40` | #999999 | 弱化文本 |
| `ink-20` | #cccccc | 边框 |
| `ink-10` | #e6e6e6 | 浅边框 |
| `ink-05` | #f2f2f2 | 背景 |

### 节点类型颜色

| 类型 | 颜色变量 |
|------|----------------|
| 目标节点 | `--node-goal` |
| 主张节点 | `--node-claim` |
| 事实节点 | `--node-fact` |
| 约束节点 | `--node-constraint` |
| 原子议题节点 | `--node-atomic` |
| 待验证节点 | `--node-pending` |
| 综合节点 | `--node-synthesis` |

### 信号颜色

| 信号 | 变量 | 用途 |
|--------|----------|-------|
| 成功 | `--signal-success` | 正向状态 |
| 警告 | `--signal-warning` | 警示状态 |
| 危险 | `--signal-critical` | 错误状态 |
| 信息 | `--signal-info` | 信息提示 |

## 页面

### 认证页面

- `/login` - 用户登录（邮箱/密码）
- `/register` - 新用户注册（含密码强度指示器）

### 仪表板页面

- `/dashboard` - 主仪表板概览
- `/dashboard/sessions` - 会话列表
- `/dashboard/sessions/new` - 创建新会话
- `/dashboard/sessions/[id]` - 会话工作区（含图形画布）
- `/dashboard/sessions/[id]/graph` - 全屏图形视图
- `/dashboard/settings` - 用户设置（个人资料、偏好、安全）

## API 代理

前端包含一个 BFF（Backend-for-Frontend）代理，路径为 `/api/[...proxy]`，用于将请求转发到 FastAPI 后端。

```tsx
// 前端请求
fetch('/api/v1/sessions/123');

// 代理到后端
// http://localhost:8000/api/v1/sessions/123
```

环境变量：`BACKEND_URL`（默认值：`http://localhost:8000`）

## 测试

```bash
# 类型检查
npm run type-check

# 代码检查
npm run lint

# 生产构建（包含类型检查）
npm run build
```

## 构建产物

```
路由 (app)                              大小     首次加载 JS
┌ ○ /                                    184 B          96.2 kB
├ ○ /dashboard                           184 B          96.2 kB
├ ○ /dashboard/sessions                  1.88 kB        97.9 kB
├ ƒ /dashboard/sessions/[id]             3.96 kB         145 kB
├ ƒ /dashboard/sessions/[id]/graph       2.67 kB         144 kB
├ ○ /dashboard/sessions/new              2.86 kB        98.9 kB
├ ○ /dashboard/settings                  1.03 kB        88.4 kB
├ ○ /login                               1.33 kB        97.4 kB
└ ○ /register                            1.6 kB         97.6 kB
```

## 环境变量

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | API 基础 URL | `/api/v1` |
| `BACKEND_URL` | 后端服务器 URL | `http://localhost:8000` |

## 许可证

MIT
