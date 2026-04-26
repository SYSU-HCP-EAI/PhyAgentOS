# PhyAgentOS 文档体系重构计划

## 一、诊断摘要

### 现有文档清单
| 文件 | 当前语言 | 状态 |
|---|---|---|
| `README.md` | 英文 | 内容陈旧，结构过时 |
| `README_zh.md` | 中文 | 内容陈旧，结构过时 |
| `docs/README_paos_env.md` | 中文 | 仅 59 行，过于简陋 |
| `docs/plans/Report.md` | 中文 | 完整但缺英文版 |
| `docs/user_manual/README.md` | 中文 | 较完整但缺英文版 |
| `docs/user_manual/appendix/*` | 中文 | 较完整 |
| `docs/user_development_guide/README.md` | 中文 | 较完整但缺英文版 |
| `docs/user_development_guide/COMMUNICATION.md` | 中英混合 | 风格不统一 |
| `docs/user_development_guide/PLUGIN_DEVELOPMENT_GUIDE.md` | 英文 | 完整 |
| `docs/user_development_guide/PLUGIN_DEVELOPMENT_GUIDE_zh.md` | 中文 | 完整 |
| `docs/user_development_guide/REKEP_PLUGIN_DEPLOYMENT_zh.md` | 中文 | 完整但缺英文版 |

### 核心问题
1. 根目录 README 信息陈旧（项目结构图、roadmap 与实际不匹配）
2. 中英文覆盖严重失衡（多份主文档仅有中文）
3. `docs/README_paos_env.md` 过于简陋，仅覆盖基本启动
4. 各本体（机械臂/移动机器人/双臂/人形仿真/IoT）调用指南分散
5. 文档间交叉引用混乱，缺少统一"文档地图"
6. COMMUNICATION.md 中英混合，不利于独立维护

---

## 二、重构架构设计

### 2.1 根目录 README（重写为 5 阶段渐进式关键指引）

根目录 README 承担"漏斗"角色，按 5 个阶段引导用户：

```
Stage 0: 5 分钟了解 PhyAgentOS
  ↓ 特性速览、架构图、支持设备表
Stage 1: 15 分钟跑通仿真闭环
  ↓ 安装 → onboard → watchdog + agent → 第一条指令
Stage 2: 30 分钟接入真实机器人或仿真本体
  ↓ 机械臂 / 移动机器人 / 双臂 / 人形仿真 / IoT
Stage 3: 1 小时开发自定义插件
  ↓ 插件结构 → manifest → driver → runtime → 部署
Stage 4: 深入 Fleet 多机协同 + 感知导航 + ROS2
  ↓ 多机器人配置 → 语义导航 → 感知管线 → 渠道接入
```

每个阶段末尾给出**明确的"下一步读什么"**超链接，直达 `docs/` 下对应专题文档。

### 2.2 `docs/` 目录结构（重构后）

```text
docs/
├── README.md                          # 文档总览/地图（新增，英文）
├── README_zh.md                       # 文档总览/地图（新增，中文）
├── README_paos_env.md               # 仿真环境完整指南（重写，英文）
├── README_paos_env_zh.md            # 仿真环境完整指南（新增，中文）
│
├── plans/
│   ├── Report.md                    # 技术报告（保留/更新，中文）
│   └── Report_en.md               # 技术报告（新增，英文）
│
├── user_manual/
│   ├── README.md                    # 手册总览+阅读路径（重写，英文）
│   ├── README_zh.md                 # 手册总览+阅读路径（新增，中文）
│   ├── 01_INSTALLATION.md           # 安装与环境准备（新增，英文）
│   ├── 01_INSTALLATION_zh.md        # 安装与环境准备（新增，中文）
│   ├── 02_BASIC_USAGE.md            # 基本使用与命令速查（新增，英文）
│   ├── 02_BASIC_USAGE_zh.md         # 基本使用与命令速查（新增，中文）
│   ├── 03_FLEET_MODE.md             # Fleet 多机器人模式（新增，英文）
│   ├── 03_FLEET_MODE_zh.md          # Fleet 多机器人模式（新增，中文）
│   ├── 04_EMBODIMENTS.md            # 各本体统一接入指南（新增，英文）
│   ├── 04_EMBODIMENTS_zh.md         # 各本体统一接入指南（新增，中文）
│   └── appendix/                    # 保留现有 Franka 附录
│
└── user_development_guide/
    ├── README.md                    # 开发指南总览（重写，英文）
    ├── README_zh.md                 # 开发指南总览（新增，中文）
    ├── COMMUNICATION.md             # 通信架构（拆分为纯英文，或保留对照）
    ├── COMMUNICATION_zh.md          # 通信架构（新增纯中文）
    ├── PLUGIN_DEVELOPMENT_GUIDE.md  # 插件开发（保留，已是英文）
    ├── PLUGIN_DEVELOPMENT_GUIDE_zh.md# 插件开发（保留，已是中文）
    ├── REKEP_PLUGIN_DEPLOYMENT.md   # ReKep 部署（新增，英文）
    ├── REKEP_PLUGIN_DEPLOYMENT_zh.md# ReKep 部署（保留/重命名，中文）
    ├── HAL_DRIVER.md                # HAL 驱动开发专题（新增，英文）
    ├── HAL_DRIVER_zh.md             # HAL 驱动开发专题（新增，中文）
    ├── PERCEPTION_NAVIGATION.md     # 感知与导航专题（新增，英文）
    ├── PERCEPTION_NAVIGATION_zh.md  # 感知与导航专题（新增，中文）
    └── ROS2_INTEGRATION.md          # ROS2 集成专题（新增，英文，标记开发中）
    └── ROS2_INTEGRATION_zh.md       # ROS2 集成专题（新增，中文，标记开发中）
```

### 2.3 核心设计原则

- **中英文严格配对**：每个功能文档都有 `*.md`（默认英文）和 `*_zh.md`（中文）双版本
- **根目录 README 做"漏斗"**：只放最关键的信息和明确的阅读路径
- **docs 下各手册做"专题"**：每个专题聚焦单一主题，避免单文件过大
- **统一的文档地图**：`docs/README.md` 作为所有文档的统一入口，按读者角色分流
- **交叉引用标准化**：所有内部链接使用相对路径，统一格式

---

## 三、待确认事项

1. **英文默认策略**：`*.md` = 英文, `*_zh.md` = 中文。是否同意？
2. **COMMUNICATION.md 的处理**：当前中英混合。是保持"双语对照"风格，还是拆分为两个独立文件？
3. **新增专题优先级**：HAL 驱动开发、感知导航、ROS2 集成中，ROS2 是否可以标为"开发中"，内容从现有开发指南迁移？
