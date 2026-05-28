import { useState } from 'react'
import type { ImagePrompt } from '../types'

interface Props {
  prompts: ImagePrompt[]
  imagesBase64: Record<string, string>
}

export default function ImagePromptsPanel({ prompts, imagesBase64 }: Props) {
  const [open, setOpen] = useState(false)

  if (!prompts.length) return null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-5 py-4 flex items-center justify-between text-left"
      >
        <span className="text-sm font-medium text-gray-700">图片 Prompt ({prompts.length})</span>
        <svg className={`w-4 h-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="px-5 pb-5 space-y-4">
          {prompts.map((p, i) => (
            <div key={i} className="border border-gray-100 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600 font-medium">{p.prompt_type}</span>
                <span className="text-xs text-gray-400">{p.aspect}</span>
              </div>
              <p className="text-xs text-gray-600 font-mono leading-relaxed">{p.filled_prompt}</p>
              {p.negative && <p className="text-xs text-red-400 mt-1">Negative: {p.negative}</p>}

              {imagesBase64[p.prompt_type] && (
                <img
                  src={`data:image/png;base64,${imagesBase64[p.prompt_type]}`}
                  alt={p.prompt_type}
                  className="mt-3 rounded-lg max-w-xs"
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
