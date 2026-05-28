# BWS 社交媒体内容平台上下文

更新时间：2026-05-27

## 项目目标

从 BWS 旅行社的 Excel 产品资源表，自动生成小红书风格的图文内容包，目标产物包括：

- 小红书文案
- 图片生成 prompt 或真实图片
- 海报成图
- 每日排期输出

## 当前项目状态

### 已完成

- 数据层已经基本完成：`Excel -> parsers -> data/*.json -> data/all_resources.json`
- `data/all_resources.json` 当前为 153 条结构化资源
- `daily_post_generator.py` 已经实现每日内容生成雏形
- `output/2026-05-25` 到 `output/2026-06-07` 已存在每日内容包

### 进行中/待建设

- 内容策划层：已新增 OpenAI 结构化策划模块，但默认仍使用规则模式；需要真实 API 验证与提示词迭代
- 视觉层：已新增 `gpt-image-1` 图片生成模块，默认关闭；需要真实 API 验证
- 海报层：已新增 Pillow 海报骨架，支持无底图 fallback 和生成图叠字
- 调度层：还没有实现定时执行

## 关键文件

- `AGENTS.md`：项目目标、架构、运行约定，作为当前主要说明入口
- `models.py`：Pydantic 数据模型
- `parse_excel.py`：解析原始产品 Excel 并输出 `data/*.json`
- `parsers/`：每个 sheet 的独立 parser
- `data/all_resources.json`：合并后的产品资源库，153 条
- `daily_post_generator.py`：当前每日小红书内容包生成器
- `generate_daily_content.py`：新的分层内容生成 CLI，建议后续优先使用
- `content_pipeline/`：新的分层管线模块
- `output/YYYY-MM-DD/`：每日生成结果

## 新管线模块

- `content_pipeline/config.py`：路径与 OpenAI 环境变量配置
- `content_pipeline/data_loader.py`：读取清洗版 Excel 的资源库、主题库、排期和模板
- `content_pipeline/selection.py`：规则选品，已按发布日期固定随机种子，避免同一天重复生成不一致
- `content_pipeline/copywriter.py`：文案上下文、模板填充、规则文案生成
- `content_pipeline/prompt_builder.py`：图片 prompt 填充
- `content_pipeline/ai_planner.py`：OpenAI 结构化内容策划，返回 `ContentPlan`
- `content_pipeline/image_generator.py`：OpenAI 图片生成，输出 `generated_cover.png`
- `content_pipeline/image_generator.py`：OpenAI 图片生成，按 prompt 组输出 `image_01_*.png`、`image_02_*.png` 等
- `content_pipeline/poster.py`：Pillow 海报生成，输出 `poster.jpg`
- `content_pipeline/generator.py`：管线编排与输出落盘

## Excel 文件分工

- `BWS碎片化整理 - 适配AI模板.xlsx`
  - 原始适配 AI 模板的产品资源 Excel
  - `parse_excel.py` 默认读取它

- `BWS碎片化整理 - 2026年05月25日 chatGPT清洗过的.xlsx`
  - 当前 `daily_post_generator.py` 默认读取它
  - 包含辅助 sheet：`统一资源库`、`内容主题库`、`每日选题模板`、`图片Prompt模板`、`小红书文案模板`

- `BWS碎片化整理 - 2026年05月25日 增加排期数据.xlsx`
  - 在清洗版基础上增加了 `7天内容排期_v1`、`发帖文案样例_v1`
  - 后续可作为排期策略参考

## 数据概况

`data/all_resources.json` 类型分布：

- `transport`: 53
- `hotel`: 49
- `wellness`: 16
- `day_tour`: 14
- `afternoon_tea`: 11
- `multi_day_tour`: 6
- `komodo_tour`: 3
- `guide`: 1

清洗版 Excel 辅助数据：

- `统一资源库`: 222 条
- `内容主题库`: 7 个主题
- `每日选题模板`: 14 行排期
- `图片Prompt模板`: 5 种
- `小红书文案模板`: 6 个模块

## 当前生成流程

旧版 `daily_post_generator.py` 的流程：

1. 读取清洗版 Excel 的统一资源库和辅助模板
2. 根据日期找到 `每日选题模板` 中的主题
3. 根据主题 ID 匹配主资源类型
4. 选择主资源、搭配资源 1、搭配资源 2
5. 填充小红书文案模板
6. 填充图片 prompt 模板
7. 输出到 `output/YYYY-MM-DD/`

每个日期目录包含：

- `content_data.json`
- `post_text.txt`
- `image_prompts.txt`
- `preview.html`

新版 `generate_daily_content.py` 默认使用规则模式，输出同样的核心文件，并可额外生成：

- `poster.jpg`
- `image_01_*.png` 等多张小红书展开图（仅在开启 OpenAI 图片生成且调用成功时）

## 已验证事项

- 系统 PATH 中没有可直接调用的 `python` 或 `py`
- 可使用 Codex bundled Python：
  - `C:\Users\Liu_Lei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
- 已用 bundled Python 验证：
  - `models.py`、`parse_excel.py`、`daily_post_generator.py` 可以通过 `py_compile`
  - `data/all_resources.json` 可以正常读取中文
  - `daily_post_generator.py --date 2026-05-26` 可以跑通
  - `generate_daily_content.py --date 2026-05-27 --poster` 可以跑通
  - `content_pipeline/` 与 `generate_daily_content.py` 可以通过 `compileall`
  - `generate_daily_content.py --date 2026-05-27 --ai-plan --generate-images --poster` 已真实打到 OpenAI，但当前账号额度不足：
    - 内容策划返回 `insufficient_quota`
    - 图片生成返回 `billing_hard_limit_reached`

## 注意事项

- PowerShell 里直接 `Get-Content` 中文会显示乱码，但文件本身是 UTF-8 正常中文
- 如果需要查看中文内容，优先用 bundled Python 读取并打印，或直接在编辑器里打开
- 旧版 `daily_post_generator.py` 当前资源选择含随机性，同一天重复生成可能覆盖输出并选出不同资源
- 新版 `generate_daily_content.py` 已按发布日期固定随机种子，规则模式同一天会稳定选同一组资源
- 2026-05-26 的输出已在本次阅读项目时被重新生成过一次
- 2026-05-27 的输出已在 2026-05-27 重构验证时被新版管线重新生成过一次
- 当前 `poster.jpg` 若没有成功生成真实底图，会使用 Pillow fallback 背景，不代表最终视觉质量

## 新命令

```bash
# 规则模式，生成指定日期
python generate_daily_content.py --date 2026-05-27

# 规则模式 + Pillow 海报
python generate_daily_content.py --date 2026-05-27 --poster

# OpenAI 策划模式
python generate_daily_content.py --date 2026-05-27 --ai-plan

# OpenAI 策划 + 图片生成 + 海报
python generate_daily_content.py --date 2026-05-27 --ai-plan --generate-images --poster

# 生成全部排期
python generate_daily_content.py --all --poster
```

当前本机命令行未必有 `python`，Codex 环境可用：

```bash
C:\Users\Liu_Lei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe generate_daily_content.py --date 2026-05-27 --poster
```

## 明天优先建议

1. 用真实 OpenAI API 跑一次 `--ai-plan`，检查结构化策划质量
2. 用真实 OpenAI API 跑一次 `--generate-images`，确认 `gpt-image-1` 图片返回格式和尺寸
3. 当前 API key/账户需要先解决额度或 billing hard limit，才能真正评估 AI 文案和图片质量
4. 继续优化 Pillow 海报模板，包括品牌 logo、价格样式、底图裁切和多版式
5. 决定是否将旧 `daily_post_generator.py` 迁移为新版 CLI 的兼容入口
6. 最后做调度层
