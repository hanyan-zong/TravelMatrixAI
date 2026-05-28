# AI Prompts

`prompts.json` 保存 MVP 第一版 AI 任务模板。

任务：

- `generate_platform_post`
- `generate_video_script`
- `compliance_check`
- `rewrite_for_account_matrix`

后续建议把这些模板接入 API 的 AI Gateway，并为每次调用保存：

- 输入产品信息
- 平台和账号定位
- 使用的模板版本
- 模型名称
- 原始输出
- 结构化结果
- 审核结果
