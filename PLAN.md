## 在 `OEA_XLeRobot` 中接入 `xlerobot_2wheels_remote` HAL Driver

### Summary
- 在不改你现有部署拓扑的前提下打通链路：`3090(OEA + HAL Watchdog)` 通过 ZMQ 控制 `Orin(XLerobot2WheelsHost)`。
- 基于你已完成的 editable 安装（`OEA`、`lerobot`）继续开发，仅补 `pyzmq` 作为环境前置。
- 首版只做原子动作能力：底盘、双臂、头、夹爪；不在 driver 内实现视觉抓取状态机。

### Key Changes
1. 环境与启动前置
- 统一使用 `conda activate OEA_XLeRobot`。
- 安装缺失依赖：`pyzmq`。
- 运行时要求 `Orin` 先手动启动 `xlerobot_2wheels_host`，3090 侧再启动 `hal_watchdog`。

2. 新增 HAL 驱动（内置）
- 新增 `xlerobot_2wheels_remote` 驱动（`BaseDriver` 子类），内部封装 `XLerobot2WheelsClient`。
- 驱动配置来源为环境变量：
- `OEA_XLEROBOT_REMOTE_IP`（必填）
- `OEA_XLEROBOT_CMD_PORT`（默认 `5555`）
- `OEA_XLEROBOT_OBS_PORT`（默认 `5556`）
- `OEA_XLEROBOT_ROBOT_ID`（默认 `xlerobot_2wheels_001`）
- `OEA_XLEROBOT_LOOP_HZ`（默认 `20`）
- `OEA_XLEROBOT_MAX_MOVE_DURATION_S`（默认 `10`）
- `OEA_XLEROBOT_SAFE_MAX_LINEAR_M_S`（默认 `0.4`）
- `OEA_XLEROBOT_SAFE_MAX_ANGULAR_DEG_S`（默认 `120`）
- `OEA_LEROBOT_SRC`（默认 `/home/ubuntu/lerobot/src`）

3. 动作接口（对 Agent/Critic 的稳定契约）
- `connect_robot`：建立 ZMQ 连接并探活。
- `check_connection`：拉取 observation 做健康检查。
- `disconnect_robot`：安全断连并停止底盘。
- `move_base`：参数 `x_vel_m_s`、`theta_deg_s`、`duration_s`，驱动按 `loop_hz` 循环发送并到时自动 `stop`。
- `stop`：立即发送零速。
- `set_joint_targets`：参数 `joints`（如 `left_arm_shoulder_pan.pos`）。
- `set_gripper`：参数 `side`(`left|right`) 与 `value`，映射到 `left_arm_gripper.pos` 或 `right_arm_gripper.pos`。
- `robot_id` 若提供且与驱动配置不一致，直接拒绝并返回错误字符串（避免误控）。

4. OEA HAL 注册与 Profile
- 在驱动注册表中加入 `xlerobot_2wheels_remote`。
- 新增 `hal/profiles/xlerobot_2wheels_remote.md`，声明支持动作、参数约束、速度上限与自动停车语义。
- `get_runtime_state()` 按 OEA 结构回写 `robots.<robot_id>.connection_state`、`nav_state`、`robot_pose`（首版位姿可占位，保证结构稳定）。

5. 健壮性与失败处理
- 无法导入 `lerobot`、缺 IP、连接失败、host 无响应都返回可诊断错误信息。
- 任何异常路径都调用 `stop` 防止底盘残留运动。
- `move_base` 期间若中途异常或中断，立即停车并返回失败原因。

### Test Plan
1. 环境测试
- `OEA_XLeRobot` 内验证 `import OEA`、`import lerobot`、`import zmq` 全通过。
- 验证 `from lerobot.robots.xlerobot_2wheels import XLerobot2WheelsClient` 可导入。

2. 驱动单测（mock client）
- `connect_robot/check_connection/disconnect_robot` 正常与异常分支。
- `move_base(duration)` 发送循环次数符合 `loop_hz`，结束后必发 `stop`。
- `set_joint_targets/set_gripper` 字段映射正确。
- `robot_id` 不匹配时拒绝执行。
- `get_runtime_state` 输出包含 `connection_state/nav_state/robot_pose`。

3. HAL 闭环测试
- 通过 `ACTION.md` 触发上述动作，`hal_watchdog` 执行后正确清空 `ACTION.md`。
- `ENVIRONMENT.md` 中 `robots.<robot_id>` 运行态字段持续更新且不破坏现有 `objects/scene_graph`。

4. 端到端人工验收
- Orin 启动 host，3090 启动 OEA + watchdog。
- 在 `OEA agent` 下完成一次串行动作：连接 -> 底盘短运动 -> 双臂/头位姿 -> 夹爪动作 -> 停车 -> 断连。

### Assumptions
- 首版本体固定为 `xlerobot_2wheels`，模式固定 `single`。
- Orin 侧 host 进程首版手动启动，不做 systemd。
- 视觉导航与抓取状态机继续由上层工作流编排，不放入 HAL driver。
