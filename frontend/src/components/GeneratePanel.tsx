import { useState } from 'react'
import type { ScheduleEntry } from '../types'

type Mode = 'ai' | 'rules'

export const MODE_OPTS = {
  ai:    { use_ai_plan: true,  generate_images: true,  generate_poster: false },
  rules: { use_ai_plan: false, generate_images: false, generate_poster: true },
} as const

interface Props {
  entry: ScheduleEntry
  onGenerate: (opts: { use_ai_plan: boolean; generate_images: boolean; generate_poster: boolean }) => void
}

export default function GeneratePanel({ entry, onGenerate }: Props) {
  const [mode, setMode] = useState<Mode>('ai')

  const handleGenerate = () => onGenerate(MODE_OPTS[mode])

  return (
    <div className="flex items-center justify-center h-full">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 w-full max-w-md text-center">
        <h3 className="text-lg font-bold text-gray-800 mb-1">{entry.theme_name}</h3>
        <p className="text-sm text-gray-400 mb-6">{entry.date}</p>

        {/* 模式切换 */}
        <div className="inline-flex rounded-lg bg-gray-100 p-1 mb-6">
          <button
            onClick={() => setMode('ai')}
            className={`px-4 py-2 text-sm rounded-md transition-colors ${mode === 'ai' ? 'bg-cyan-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            AI 生成
          </button>
          <button
            onClick={() => setMode('rules')}
            className={`px-4 py-2 text-sm rounded-md transition-colors ${mode === 'rules' ? 'bg-gray-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            规则模式
          </button>
        </div>

        <p className="text-xs text-gray-400 mb-6">
          {mode === 'ai'
            ? <>OpenAI 智能选品 + gpt-image-1 生成图片（<span className="text-amber-500">消耗 API 额度</span>）</>
            : '模板规则选品 + Pillow 生成海报（不消耗额度）'}
        </p>

        <button
          onClick={handleGenerate}
          className="w-full py-3 bg-cyan-600 text-white font-medium rounded-lg hover:bg-cyan-700 transition-colors"
        >
          生成内容
        </button>
      </div>
    </div>
  )
}
