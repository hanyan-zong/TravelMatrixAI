import { ManualAssistAdapter } from "./manual-adapter";
import type { Platform, PublisherAdapter } from "./types";

export function createPublisherAdapter(platform: Platform): PublisherAdapter {
  return new ManualAssistAdapter(platform);
}

export * from "./types";
