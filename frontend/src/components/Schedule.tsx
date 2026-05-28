import type { ScheduleEntry } from '../types'

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

function formatDate(iso: string) {
  const d = new Date(iso + 'T00:00:00')
  const m = d.getMonth() + 1
  const day = d.getDate()
  const w = WEEKDAYS[d.getDay()]
  return { label: `${m}月${day}日`, weekday: `周${w}` }
}

interface Props {
  entries: ScheduleEntry[]
  selectedDate: string | null
  onSelect: (date: string) => void
}

export default function Schedule({ entries, selectedDate, onSelect }: Props) {
  const today = new Date().toISOString().slice(0, 10)

  return (
    <div className="flex-1 overflow-auto">
      {entries.map(e => {
        const { label, weekday } = formatDate(e.date)
        const isSelected = e.date === selectedDate
        const isToday = e.date === today

        return (
          <button
            key={e.date}
            onClick={() => onSelect(e.date)}
            className={`w-full text-left px-5 py-3 border-b border-gray-100 transition-colors
              ${isSelected ? 'bg-cyan-50 border-l-4 border-l-cyan-600' : 'hover:bg-gray-50 border-l-4 border-l-transparent'}
              ${isToday && !isSelected ? 'border-l-4 border-l-amber-400' : ''}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-800">
                {label} <span className="text-gray-400 font-normal">{weekday}</span>
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${e.has_generated ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-400'}`}>
                {e.has_generated ? '已生成' : '未生成'}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1 truncate">{e.theme_name}</p>
          </button>
        )
      })}
    </div>
  )
}
