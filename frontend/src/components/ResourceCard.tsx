import type { ContentResource } from '../types'

const BADGE_COLORS: Record<string, string> = {
  cyan: 'bg-cyan-100 text-cyan-700',
  amber: 'bg-amber-100 text-amber-700',
  emerald: 'bg-emerald-100 text-emerald-700',
}

interface Props {
  resource: ContentResource
  label: string
  color: string
}

export default function ResourceCard({ resource, label, color }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${BADGE_COLORS[color] || BADGE_COLORS.cyan}`}>
          {label}
        </span>
        <span className="text-xs text-gray-400">{resource.resource_type}</span>
      </div>

      <h4 className="font-medium text-gray-800 text-sm">{resource.product_name_cn}</h4>
      <p className="text-xs text-gray-500 mt-1">{resource.area} · {resource.destination}</p>

      {resource.price_text && (
        <p className="text-sm font-medium text-cyan-700 mt-2 whitespace-pre-line">{resource.price_text}</p>
      )}

      {resource.highlights && (
        <p className="text-xs text-gray-500 mt-2 line-clamp-3 whitespace-pre-line">{resource.highlights}</p>
      )}
    </div>
  )
}
