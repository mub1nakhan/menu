import React from 'react'

interface Column {
  key: string
  title: string
  render?: (row: any) => React.ReactNode
}

export default function Table({ columns, data }: { columns: Column[]; data: any[] }) {
  return (
    <div className="overflow-x-auto">
      <div className="glass rounded-2xl p-3">
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key} className="text-left text-sm font-medium text-gray-600 p-3">{c.title}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx} className="border-t">
                {columns.map((c) => (
                  <td key={c.key} className="p-3 text-sm text-gray-700">{c.render ? c.render(row) : row[c.key]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
