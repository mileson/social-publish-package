# 一键发交接合同

## 目标

把用户提供的最终 selection JSON 或 `window.getPublishReviewSelection()` 的评审结果确定性转换为一键发 `shortVideo` 任务。页面选择不等于发布授权；默认只生成任务并执行 `prepare`，随后优先 `fill`。

## 为什么必须按平台拆分

一键发 CLI 的单个任务只有一组 `data.title` 与 `data.tags`，而预发布工作台允许各平台选择不同标签，视频号还需要无特殊符号的独立短标题。因此必须为小红书、抖音、快手、视频号、B 站、YouTube 分别生成任务。执行前读取当前 CLI 能力与适配器字段语义；若当前适配器会把 tags 加入标题，则交接时传空 tags，将话题放在正文后一个空行的描述末尾，保持标题不变；实际填入后仍须核对页面。

## 封面解析

1. 已登记封面直接使用选择结果中的绝对 `path`，并复核文件存在、图片类型、大小和 SHA-256。
2. 临时选择没有浏览器可见的绝对路径。交接脚本使用 `fileName + size + sha256`，在视频目录和 Agent 明确传入的 `--cover-search-root` 内寻找原始文件。
3. 只有唯一匹配才允许交接；没有匹配或存在多个匹配都必须报错。
4. 竖版主封面角色固定为 `cover`，文件必须接近 3:4；小红书、抖音、快手、视频号都必须接收它。
5. 工作台 16:9 横版固定为 `horizontalCover`，不是默认资产；此开关不影响抖音必选的 4:3 封面。只有选择结果显式包含 `horizontalCoverEnabled: true` 时才能解析与下发。
6. 抖音必须在竖版基础上追加已选 4:3（`bilibiliCover` 映射为 CLI `horizontalCover`），缺失时阻止抖音任务生成，禁止以 16:9 替代；视频号可追加已启用横版；小红书、快手只接收 `cover`。横版不得替代竖版。
7. B 站只有一个封面位：优先使用工作台已选的 4:3 `bilibiliCover`，并在 CLI 任务中映射为 `horizontalCover`；若未选 4:3，再使用显式启用的 16:9 `horizontalCover`，最后回退 3:4 `cover`。两个封面角色不得同时进入同一个 B 站任务。
8. 映射前必须按原角色验证尺寸、文件大小与 SHA-256；4:3 选择不能静默改用 16:9 图。离线任务生成成功不代表页面上传成功。

## 任务内容

每个平台任务均包含：

- `type: shortVideo`
- 单个平台 ID
- 对应平台标题；视频号使用不超过 16 字、仅含文字/字母/数字/空格的独立短标题
- 公共正文
- 该平台自己的已选标签
- 视频绝对路径，角色为 `media`
- 经能力矩阵裁剪后的封面资产
- 明确的 `browserContext`

真实发布保持 `publishGuard.requirePublicUrl: true`。当前 CLI 兼容接收但忽略旧 `expectedAccounts`；它不能代替浏览器当前登录态确认。`publish --yes` 只在用户明确授权后执行。

## 终止条件

以下任一情况必须停止，不得猜测或降级为成功：

- 临时封面无法在允许目录内唯一定位；
- 需要竖版的平台缺少合格 3:4 封面，或 YouTube 缺少已启用的 16:9 封面；
- 横版未显式启用却出现在选择结果，或已启用但缺少稳定横版文件；
- 路径不存在、图片格式不支持、大小或 SHA-256 不一致；
- 标题、标签或平台结构超限；
- 视频号短标题包含标点、emoji 或其他特殊符号；
- 未显式选择 `regular` / `incognito`；
- CLI `doctor`、`capabilities`、`prepare` 或平台回执不满足门禁。

封面字段为 `unknown`、弹层未自然关闭、或页面仍显示视频默认帧时，标记 `needs_check` 并保留 requestId；只在页面读回目标封面后报告填入成功。

## YouTube 与执行状态

YouTube 仅接收一个 16:9 horizontalCover，不回退竖图或 4:3。描述与 content 同步，话题去重后追加，tags 为空，标题原样；这不是 Studio 的视频标签。

明确的发布授权在其适用范围内继续有效。任务生成后保存 manifest 与 requestId，逐平台串行执行；恢复任务先读既有 manifest，不重新生成任务编号。

- busy：暂停整个队列，检查已有任务与连接，不启动第二个桥接实例。
- unknown、超时、标签页关闭：保留 requestId，核对已有页面、回执和作品管理页；确认提交状态前不再次提交。
- 用户手动接管：停止同页自动化；用户说已完成后记录 user_confirmed，不重复提交。
- 字段验证失败：读回标题、段落、标签与封面，有明确页面证据才能纠正误报。
- 状态区分 prepared、filled、submitted、review_pending、public_verified、user_confirmed、needs_check，附时间与证据。审核中不等于公开可访问。
- 登录、验证码或站点安全限制构成阻塞时说明原因，不绕过。
