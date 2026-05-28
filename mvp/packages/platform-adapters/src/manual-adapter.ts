import type {
  ManualPackage,
  Platform,
  PlatformCapabilities,
  PlatformPost,
  PublishResult,
  PublisherAdapter,
  ValidationResult,
} from "./types";

const platformLimits: Record<Platform, Partial<PlatformCapabilities>> = {
  xiaohongshu: { maxTextLength: 1000, maxImages: 18, supportsVideo: true, supportsImages: true },
  douyin: { maxTextLength: 500, maxImages: 0, supportsVideo: true, supportsImages: false },
  wechat_channels: { maxTextLength: 1000, maxImages: 9, supportsVideo: true, supportsImages: true },
  toutiao: { maxTextLength: 5000, maxImages: 50, supportsVideo: true, supportsImages: true },
  weibo: { maxTextLength: 2000, maxImages: 18, supportsVideo: true, supportsImages: true },
  douban: { maxTextLength: 5000, maxImages: 20, supportsVideo: false, supportsImages: true },
};

export class ManualAssistAdapter implements PublisherAdapter {
  constructor(public platform: Platform) {}

  capabilities(): PlatformCapabilities {
    return {
      supportsApiPublish: false,
      supportsSchedule: false,
      supportsMetricsFetch: false,
      supportsVideo: true,
      supportsImages: true,
      defaultPublishMethod: "manual_assist",
      ...platformLimits[this.platform],
    };
  }

  async validate(post: PlatformPost): Promise<ValidationResult> {
    const issues: string[] = [];
    const capabilities = this.capabilities();

    if (!post.title.trim()) issues.push("标题不能为空");
    if (!post.body.trim()) issues.push("正文不能为空");
    if (capabilities.maxTextLength && post.body.length > capabilities.maxTextLength) {
      issues.push(`正文超过平台建议长度 ${capabilities.maxTextLength}`);
    }
    if (capabilities.maxImages !== undefined && post.mediaUrls.length > capabilities.maxImages) {
      issues.push(`素材数量超过平台限制 ${capabilities.maxImages}`);
    }

    return { valid: issues.length === 0, issues };
  }

  async publish(): Promise<PublishResult> {
    return {
      success: false,
      status: "manual_required",
      message: "该平台当前默认使用人工确认发布包，不执行自动发布。",
    };
  }

  async exportManualPackage(post: PlatformPost): Promise<ManualPackage> {
    return {
      platform: this.platform,
      accountName: post.accountName,
      title: post.title,
      body: post.body,
      hashtags: post.hashtags,
      mediaUrls: post.mediaUrls,
      instructions: [
        "确认账号登录状态。",
        "复制标题、正文和标签。",
        "上传已审核素材。",
        "发布前再次核对价格、授权和联系方式。",
        "发布后回填链接和基础数据。",
      ],
    };
  }
}
