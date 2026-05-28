from __future__ import annotations

import argparse
from datetime import date, datetime

from content_pipeline.config import DEFAULT_EXCEL_PATH, load_openai_settings
from content_pipeline.data_loader import load_all_data
from content_pipeline.generator import GenerateOptions, generate_for_date, schedule_dates


def main() -> None:
    parser = argparse.ArgumentParser(description="BWS 小红书每日内容生成器")
    parser.add_argument("date", nargs="?", help="目标日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--date", dest="date_flag", help="目标日期 YYYY-MM-DD")
    parser.add_argument("--all", action="store_true", help="生成全部排期")
    parser.add_argument("--excel", default=str(DEFAULT_EXCEL_PATH), help="清洗版 Excel 路径")
    parser.add_argument("--ai-plan", action="store_true", help="使用 OpenAI 生成内容策划")
    parser.add_argument("--generate-images", action="store_true", help="调用 OpenAI 生成首图")
    parser.add_argument("--poster", action="store_true", help="生成 Pillow 海报")
    args = parser.parse_args()

    data = load_all_data(DEFAULT_EXCEL_PATH if args.excel == str(DEFAULT_EXCEL_PATH) else args.excel)
    settings = load_openai_settings()
    options = GenerateOptions(
        use_ai_plan=args.ai_plan,
        generate_images=args.generate_images,
        generate_poster=args.poster,
    )

    if args.all:
        targets = schedule_dates(data)
    else:
        date_str = args.date or args.date_flag
        targets = [datetime.strptime(date_str, "%Y-%m-%d").date()] if date_str else [date.today()]

    print(f"加载完成：资源 {len(data['resources'])} 条，排期 {len(data['schedule'])} 条")
    for target in targets:
        out_dir = generate_for_date(target, data, options, settings)
        if out_dir:
            print(f"生成完成：{target.isoformat()} -> {out_dir}")
        else:
            print(f"跳过：{target.isoformat()} 未找到排期或主题")


if __name__ == "__main__":
    main()

