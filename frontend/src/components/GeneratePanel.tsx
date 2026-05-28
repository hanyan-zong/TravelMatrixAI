import { useState } from 'react'
import type { ScheduleEntry } from '../types'

interface Props {
  entry: ScheduleEntry
  generating: boolean
  onGenerate: (opts: { use_ai_plan: boolean; generate_images: boolean; generate_poster: boolean }) => void
}

function Toggle({ label, desc, checked, onChange }: { label: string; desc: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-center justify-between py-3">
      <div>
        <p className="text-sm font-medium text-gray-700">{label}</p>
        <p className="text-xs text-gray-400">{desc}</p>
      </div>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${checked ? 'bg-cyan-600' : 'bg-gray-300'}`}
      >
        <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${checked ? 'translate-x-5' : ''}`} />
      </button>
    </label>
  )
}

export default function GeneratePanel({ entry, generating, onGenerate }: Props) {
  const [poster, setPoster] = useState(true)
  const [aiPlan, setAiPlan] = useState(false)
  const [aiImages, setAiImages] = useState(false)

  return (
    <div className="flex items-center justify-center h-full">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 w-full max-w-md">
        <h3 className="text-lg font-bold text-gray-800 mb-1">为 {entry.date} 生成内容</h3>
        <p className="text-sm text-gray-500 mb-6">{entry.theme_name}</p>

        <div className="divide-y divide-gray-100">
          <Toggle label="生成海报" desc="使用 Pillow 生成宣传海报" checked={poster} onChange={setPoster} />
          <Toggle label="AI 策划" desc="使用 OpenAI 智能选品和文案（需 API 额度）" checked={aiPlan} onChange={setAiPlan} />
          <Toggle label="AI 图片" desc="使用 gpt-image-1 生成图片（需 API 额度）" checked={aiImages} onChange={setAiImages} />
        </div>

        <button
          onClick={() => onGenerate({ use_ai_plan: aiPlan, generate_images: aiImages, generate_poster: poster })}
          disabled={generating}
          className="w-full mt-6 py-3 bg-cyan-600 text-white font-medium rounded-lg hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? '生成中...' : '生成内容'}
        </button>
      </div>
    </div>
  )
}
