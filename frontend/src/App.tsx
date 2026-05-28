import { useState, useEffect } from 'react'
import type { ScheduleEntry, ContentData } from './types'
import { api } from './api'
import Schedule from './components/Schedule'
import ContentView from './components/ContentView'

export default function App() {
  const [schedule, setSchedule] = useState<ScheduleEntry[]>([])
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [content, setContent] = useState<ContentData | null>(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null)

  useEffect(() => {
    api.getSchedule().then(r => setSchedule(r.dates)).catch(() => {})
  }, [])

  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 3000)
      return () => clearTimeout(t)
    }
  }, [toast])

  const selectedEntry = schedule.find(e => e.date === selectedDate) ?? null

  const handleSelect = async (date: string) => {
    setSelectedDate(date)
    setContent(null)
    const entry = schedule.find(e => e.date === date)

    if (entry?.has_generated) {
      setLoading(true)
      try {
        const data = await api.getContent(date)
        setContent(data)
      } catch {
        setContent(null)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleGenerate = async (opts: { use_ai_plan: boolean; generate_images: boolean; generate_poster: boolean }) => {
    if (!selectedDate) return
    setGenerating(true)

    try {
      const result = await api.generate({ date: selectedDate, ...opts })
      setContent(result)
      setSchedule(prev => prev.map(e => e.date === selectedDate ? { ...e, has_generated: true } : e))
      setToast({ msg: '内容生成成功', ok: true })
    } catch (err) {
      setToast({ msg: `生成失败: ${(err as Error).message}`, ok: false })
    } finally {
      setGenerating(false)
    }
  }

  const handleCopy = async () => {
    if (!content) return
    await navigator.clipboard.writeText(content.full_post_text)
    setToast({ msg: '文案已复制到剪贴板', ok: true })
  }

  const handleDownloadPoster = () => {
    if (!content?.poster_base64) return
    const a = document.createElement('a')
    a.href = `data:image/jpeg;base64,${content.poster_base64}`
    a.download = `BWS_poster_${content.date}.jpg`
    a.click()
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <aside className="w-72 flex-shrink-0 border-r border-gray-200 bg-white flex flex-col">
        <div className="px-5 py-4 border-b border-gray-200">
          <h1 className="text-lg font-bold text-cyan-700">BWS 内容工作台</h1>
          <p className="text-xs text-gray-400 mt-0.5">小红书自动内容生成</p>
        </div>
        <Schedule entries={schedule} selectedDate={selectedDate} onSelect={handleSelect} />
      </aside>

      {/* 主区域 */}
      <main className="flex-1 overflow-auto">
        <ContentView
          entry={selectedEntry}
          content={content}
          loading={loading}
          generating={generating}
          onGenerate={handleGenerate}
          onCopy={handleCopy}
          onDownloadPoster={handleDownloadPoster}
        />
      </main>

      {/* Toast */}
      {toast && (
        <div className={`fixed bottom-6 right-6 px-4 py-3 rounded-lg shadow-lg text-white text-sm transition-all ${toast.ok ? 'bg-emerald-500' : 'bg-red-500'}`}>
          {toast.msg}
        </div>
      )}
    </div>
  )
}
