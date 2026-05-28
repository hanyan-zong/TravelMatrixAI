# BWS 印尼旅游社交媒体内容平台

## 项目目标
从 BWS 旅行社 Excel 产品表自动生成小红书风格的图文内容（文案 + 海报）。

## 架构分层

| 层 | 状态 | 说明 |
|----|------|------|
| 数据层 | 已完成 | Excel → Parser → JSON (`parsers/` + `data/`) |
| 内容策划层 | 待建 | OpenAI API 跨资源智能组合选题 |
| 视觉层 | 待建 | gpt-image-1 生成氛围图/场景图 |
| 海报层 | 待建 | Pillow 模板引擎叠加文字/价格/logo |
| 调度层 | 待建 | 定时执行 |

## 数据层

### 数据源
- Excel: `BWS碎片化整理 - 适配AI模板.xlsx`（9 个 sheet）
- 解析后 JSON: `data/` 目录，含 `all_resources.json` 合并版（153 条）

### 资源类型
| 类型 | 数量 | 对应 sheet |
|------|------|-----------|
| transport | 53 | 巴厘岛车费 |
| day_tour + guide | 14+1 | 巴厘岛一日游 |
| multi_day_tour | 6 | 泗水 |
| komodo_tour | 3 | 科莫多 |
| hotel (standard) | 39 | 巴厘岛酒店 |
| hotel (luxury) | 10 | 高端酒店 |
| afternoon_tea | 11 | 高端下午茶 |
| wellness | 16 | 疗愈+瑜伽 |

### Parser 架构
- 每个 sheet 有独立 parser（`parsers/*.py`），通过 `parsers/__init__.py` 的 `PARSERS` 字典注册
- 合并单元格通过 `utils.build_merged_map()` 统一解析
- 自动标签系统 `utils.auto_tags()` 从内容关键词提取标签
- 旺季附加费从"注意事项" sheet 自动关联到各资源的 `surcharge_note` 字段

### 命令
```bash
python parse_excel.py                    # 解析默认 Excel
python parse_excel.py path/to/other.xlsx # 指定文件
```

## 环境配置

`.env` 变量（从 `.env.example` 复制后填入真实值）:
```
OPENAI_API_KEY        # OpenAI API 密钥
OPENAI_MODEL_CONTENT  # 文案生成模型（默认 gpt-4o）
OPENAI_MODEL_IMAGE    # 图片生成模型（默认 gpt-image-1）
OPENAI_IMAGE_SIZE     # 图片尺寸（默认 1024x1536，竖版适配小红书）
OPENAI_IMAGE_QUALITY  # 图片质量（默认 high）
```

## API 分工
- Codex Opus: 代码生成（Codex 默认）
- OpenAI: 内容策划（gpt-4o）+ 图片生成（gpt-image-1）

## 技术栈
Python 3.12 / Pydantic v2 / openpyxl / OpenAI API / Pillow
