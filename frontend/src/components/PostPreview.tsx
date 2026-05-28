interface Props {
  postText: string
  posterBase64: string | null
}

export default function PostPreview({ postText, posterBase64 }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {posterBase64 && (
        <img
          src={`data:image/jpeg;base64,${posterBase64}`}
          alt="海报"
          className="w-full"
        />
      )}
      <div className="p-5">
        <pre className="whitespace-pre-wrap text-sm leading-relaxed text-gray-800 font-sans">
          {postText}
        </pre>
      </div>
    </div>
  )
}
