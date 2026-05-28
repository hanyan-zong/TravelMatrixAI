import { useState, useEffect } from 'react'
import type { ScheduleEntry, ContentData } from '../types'
import GeneratePanel, { MODE_OPTS } from './GeneratePanel'
import PostPreview from './PostPreview'
import ResourceCard from './ResourceCard'
import ImagePromptsPanel from './ImagePromptsPanel'

interface Props {
  entry: ScheduleEntry | null
  content: ContentData | null
  loading: boolean
  generating: boolean
  onGenerate: (opts: { use_ai_plan: boolean; generate_images: boolean; generate_poster: boolean }) => void
  onCopy: () => void
  onDownloadPoster: () => void
}

export default function ContentView({ entry, content, loading, generating, onGenerate, onCopy, onDownloadPoster }: Props) {
  if (!entry) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <p className="text-lg">选择左侧日期查看内容</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-4 border-cyan-200 border-t-cyan-600 rounded-full" />
        <span className="ml-3 text-gray-500">加载中...</span>
      </div>
    )
  }

  if (!content && !generating) {
    return <GeneratePanel entry={entry} onGenerate={onGenerate} />
  }

  if (generating) {
    return <GeneratingIndicator />
  }

  if (!content) return null

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* 顶部标题 */}
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-bold text-gray-800">{entry.date}</h2>
          <span className="text-sm px-2 py-0.5 rounded bg-cyan-100 text-cyan-700">{content.theme_name}</span>
          {content.selection_mode && (
            <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-500">{content.selection_mode}</span>
          )}
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-3 mb-6">
        <button onClick={onCopy} className="px-4 py-2 text-sm bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors">
          复制文案
        </button>
        {content.poster_base64 && (
          <button onClick={onDownloadPoster} className="px-4 py-2 text-sm bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            下载海报
          </button>
        )}
        <button onClick={() => onGenerate(MODE_OPTS.ai)} className="px-4 py-2 text-sm bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
          AI 重新生成
        </button>
        <button onClick={() => onGenerate(MODE_OPTS.rules)} className="px-4 py-2 text-sm bg-white border border-gray-200 text-gray-400 rounded-lg hover:bg-gray-50 transition-colors">
          规则模式
        </button>
      </div>

      {/* 双栏布局 */}
      <div className="flex gap-6">
        {/* 左栏：文案预览 */}
        <div className="flex-1 min-w-0">
          <PostPreview postText={content.full_post_text} posterBase64={content.poster_base64} />
        </div>

        {/* 右栏：资源卡片 */}
        <div className="w-80 flex-shrink-0 space-y-4">
          <ResourceCard resource={content.main_resource} label="主资源" color="cyan" />
          {content.mix1_resource && <ResourceCard resource={content.mix1_resource} label="搭配 1" color="amber" />}
          {content.mix2_resource && <ResourceCard resource={content.mix2_resource} label="搭配 2" color="emerald" />}
        </div>
      </div>

      {/* 图片 Prompt */}
      <div className="mt-6">
        <ImagePromptsPanel prompts={content.image_prompts} imagesBase64={content.images_base64} />
      </div>
    </div>
  )
}


function GeneratingIndicator() {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <div className="animate-spin w-12 h-12 border-4 border-cyan-200 border-t-cyan-600 rounded-full" />
      <p className="text-gray-600 font-medium">正在生成内容，请稍候...</p>
      <p className="text-sm text-gray-400">
        已等待 {elapsed} 秒
        {elapsed < 10 && '，AI 生成通常需要 20-40 秒'}
        {elapsed >= 10 && elapsed < 30 && '，AI 正在策划选品...'}
        {elapsed >= 30 && elapsed < 60 && '，AI 正在生成图片...'}
        {elapsed >= 60 && '，仍在处理中，请耐心等待'}
      </p>
    </div>
  )
}
