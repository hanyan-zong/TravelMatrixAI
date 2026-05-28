export type Platform =
  | "xiaohongshu"
  | "douyin"
  | "wechat_channels"
  | "toutiao"
  | "weibo"
  | "douban";

export type PublishMethod = "api" | "enterprise_api" | "manual_assist";

export interface PlatformPost {
  platform: Platform;
  accountName: string;
  title: string;
  body: string;
  hashtags: string[];
  mediaUrls: string[];
  scheduledAt?: string;
}

export interface PlatformCapabilities {
  supportsApiPublish: boolean;
  supportsSchedule: boolean;
  supportsMetricsFetch: boolean;
  supportsVideo: boolean;
  supportsImages: boolean;
  maxTextLength?: number;
  maxImages?: number;
  allowedRatios?: string[];
  defaultPublishMethod: PublishMethod;
}

export interface ValidationResult {
  valid: boolean;
  issues: string[];
}

export interface PublishResult {
  success: boolean;
  status: "published" | "failed" | "manual_required";
  remotePostId?: string;
  publishedUrl?: string;
  message?: string;
}

export interface ManualPackage {
  platform: Platform;
  accountName: string;
  title: string;
  body: string;
  hashtags: string[];
  mediaUrls: string[];
  instructions: string[];
}

export interface PlatformMetrics {
  views: number;
  likes: number;
  saves: number;
  comments: number;
  shares: number;
  leads: number;
}

export interface PublisherAdapter {
  platform: Platform;
  capabilities(): PlatformCapabilities;
  validate(post: PlatformPost): Promise<ValidationResult>;
  publish(post: PlatformPost): Promise<PublishResult>;
  exportManualPackage(post: PlatformPost): Promise<ManualPackage>;
  fetchMetrics?(remotePostId: string): Promise<PlatformMetrics>;
}
