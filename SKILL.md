---
name: social-publish-package
description: 为视频、字幕、逐字稿或主题材料准备标题、正文和逐平台话题，生成可编辑的本地视频预发布工作台。用户选择后可复制发布信息；明确要求时再生成可选的一键发交接任务。
---

# 视频预发布工作台

把一条视频的标题、正文、话题和封面放到同一个本地页面，让用户选好再发布。使用步骤、依赖与完整能力见 [README.zh-CN.md](README.zh-CN.md)；English documentation: [README.md](README.md)。

## 三种模式

- `title-only`：基于用户材料生成恰好 10 个不同方向的标题，推荐 Top 3，并说明理由。标题中的数字、亲测、经历和效果必须有材料依据。
- `video-prepublish`：默认模式。生成 5 个公共标题、3–4 个正文版本、逐平台话题和一个本地 HTML。终点是用户评审、编辑与复制。
- `publish-handoff`：用户已选好并明确要求交接时，读取最新 selection，把它转换为逐平台任务 JSON。任务生成成功只代表离线转换通过；脚本不会实际发布。

公开版没有内置账号、发布凭证、私人偏好或执行历史；不要求安装作者的其他 Skill。视频转写、素材制作、平台采样和真实发布均依赖用户已授权、实际可用的外部能力。

## 读取合同

- 生成工作台前读 `references/platform-copy-contract.md`、`references/review-payload.schema.json`。
- 文案检查读 `references/distribution-risk-review.md` 和 `references/distribution-risk-knowledge.md`。
- 标签配置读 `data/platform-tag-library.json`，默认为空，用户可自行添加有依据的条目。
- 交接前读 `references/publish-selection.schema.json` 和 `references/yijianfa-handoff-contract.md`。
- 合成输入参考 `examples/demo-input.json`；旧文件名 `examples/opc-fde-review-input.json` 仅保留测试兼容，其内容也是合成桌面整理示例。

## 生成流程

1. 确认视频、已有字幕或逐字稿、受众、核心观点和禁止夸大的事实。复用已有材料；没有转写工具时说明缺口，不假装读过音频。
2. 有授权的平台样本时，同批记录标题、可获取正文、真实标签、来源和时间。缺失值记 null，不从标题推测正文，不伪造热度或平台认可。
3. 写恰好 5 个不同方向的公共标题，每个最多 16 个 Unicode 字符、附一句说明；写 3–4 个不同侧重的正文版本。上述长度是当前工作台默认配置，不代表全部平台实时规则。
4. 根据本条内容生成逐平台话题，保留准确产品名和依据，不硬塞活动或凑满额度。用户配置了活动目录时可在授权范围读取，并核对平台、有效期及参与条件；没有目录时用内容相关标签，明确未验证热度。无默认外部目录、无强制私人偏好。
5. 写符合 schema 的 JSON。新任务使用六个平台；兼容旧四／五平台输入。每个平台话题数量不超过工作台配置：小红书 10、抖音 5、快手 4、视频号 7、B 站 10、YouTube 60。实际发布前核对当前平台规则；修改默认值时同步 schema、两个验证器与测试。
6. 可登记 3:4 `cover`、4:3 `bilibiliCover`、16:9 `horizontalCover`；候选和默认选择都按角色匹配。没有竖版候选时，构建器用 FFmpeg 将第一帧居中裁为 3:4。第一帧仅是稳定回退，不保证构图合适。其他比例可留空。
7. 使用绝对路径校验再构建。输出 HTML 引用本机视频和封面，不上传；平台图标与视频缩略图内嵌。保持媒体文件原位置。分享前删除个人路径和私密素材。

```bash
python3 scripts/validate_publish_review.py --input /absolute/path/review-input.json --video /absolute/path/video.mp4
python3 scripts/build_publish_review.py --input /absolute/path/review-input.json --video /absolute/path/video.mp4 --output /absolute/path/project/review.html
```

输入必须包含非空主题、核心观点、5 个标题、默认选择、正文和平台列表。`title_limit` 使用 16；`selected_title` 和 `selected_body` 指向现有候选。封面文件存在且符合比例，不能用不同角色的图片替代。

## 页面与用户选择

统一预览和四个缩略项：3:4、4:3、16:9、视频。用户可切换预览、选择或拖入封面、编辑标题、切换并编辑正文、逐平台勾选话题。计数超限显示提示，正式构建遇到超限须失败，不静默截断。

标题和正文编辑保存在当前浏览器草稿中，不写回原 HTML。复制使用当前最新选择；AI 交接可读取页面 `window.getPublishReviewSelection()`，由用户或有权限的 Agent 保存 JSON。临时上传图片需在本机允许目录通过文件名、大小与 SHA-256 找到唯一原文件，页面预览可用不代表交接资产已就绪。

用户页面编辑后重新交接，必须读取最新 selection；不得用初稿覆盖用户选择。有需要时按当前选择额外生成发布文案 Markdown，但不能声称生成器已自动完成该文件。

## 可选发布交接

`build_yijianfa_tasks.py` 只生成 JSON。一键发不是本地工作台的默认依赖，也未在本仓库发布流程中验证全部平台的真实提交。

```bash
python3 scripts/build_yijianfa_tasks.py --selection /absolute/path/publish-selection.json --video /absolute/path/video.mp4 --browser-context regular --output-dir /absolute/path/tasks
```

- 明确选择 `regular` 或 `incognito`，核对实际安装 CLI 的 doctor/capabilities、目标登录态和字段语义；版本不兼容时停止。
- 逐平台拆分标题、标签和封面；视频号短标题最多 16 字，仅文字、数字、字母和空格。
- 当前离线合同中抖音需要 3:4 加 4:3，YouTube 需要启用的 16:9。B 站优先 4:3，其次启用的 16:9，再回退竖版。
- YouTube 话题写入描述，task tags 留空；必须在真实页面读回确认，不能据离线测试宣称适配器已兼容。
- 默认 `--mode fill` 仅写出填入命令。`--mode publish` 会在生成的任务中带公开链接保护，但仍不执行命令。只有明确授权、核对账号和能力后才运行真实发布；不得绕过登录或站点限制。
- 状态 unknown 或超时时保留 requestId，先核对已有提交，不能重复发送。用户接管页面后停止自动操作。

## 隐私和验证

不把真实字幕、账号、私人目录或回执提交到公开仓库。默认标签库和记忆文件为空；私有配置放仓库之外。页面无网络请求和凭证配置，剪贴板与本地存储可能受浏览器权限限制。

```bash
python3 scripts/test_build_publish_review.py
python3 scripts/test_yijianfa_handoff.py
```

测试默认离线；仅明确设置 `RUN_YIJIANFA_INTEGRATION=1` 才允许调用已安装 CLI 的 prepare。脚本测试不能代替实际浏览器操作和真实发布验收。交付时区分：本地生成、已人工评审、任务生成、已填入、已提交、公开链接已核验。
