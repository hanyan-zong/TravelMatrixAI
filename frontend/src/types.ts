export interface ScheduleEntry {
  date: string
  theme_id: string
  theme_name: string
  title: string
  has_generated: boolean
}

export interface ScheduleResponse {
  dates: ScheduleEntry[]
}

export interface ContentResource {
  resource_id: string
  resource_type: string
  destination: string
  area: string
  product_name_cn: string
  price_text: string
  highlights: string
  includes?: string
  excludes?: string
  suitable_for?: string
}

export interface ImagePrompt {
  prompt_type: string
  filled_prompt: string
  negative: string
  aspect: string
}

export interface GenerateRequest {
  date: string
  use_ai_plan: boolean
  generate_images: boolean
  generate_poster: boolean
}

export interface ContentData {
  date: string
  selection_mode?: string
  selection_reason?: string
  theme_id: string
  theme_name: string
  main_resource: ContentResource
  mix1_resource: ContentResource | null
  mix2_resource: ContentResource | null
  filled_copy_modules: Record<string, string>
  full_post_text: string
  image_prompts: ImagePrompt[]
  poster_base64: string | null
  images_base64: Record<string, string>
}
