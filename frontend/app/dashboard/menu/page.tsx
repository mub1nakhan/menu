 'use client'
import { useState } from 'react'
import Image from 'next/image'
import PageHeader from '@/components/ui/page-header'
import Button from '@/components/ui/button'
import Table from '@/components/ui/table'
import Modal from '@/components/ui/modal'
import Input from '@/components/ui/input'
import Textarea from '@/components/ui/textarea'
import Select from '@/components/ui/select'
import Field from '@/components/ui/field'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { menuApi } from '@/lib/api'
import { toast } from '@/lib/toast'

type ProductRow = {
  id?: string
  name?: string
  price?: number | string
  category?: { id?: string; name?: string } | null
  available?: boolean
  description?: string
  image?: string
  image_url?: string
}

type CategoryRow = { id: string; name: string }
type ProductFormPayload = { name: string; price: number; category: string | null; description: string }

export default function MenuListPage() {
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<ProductRow | null>(null)
  const [name, setName] = useState('')
  const [price, setPrice] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)

  const qc = useQueryClient()
  const { data: res, isLoading } = useQuery({ queryKey: ['menu', 'products'], queryFn: () => menuApi.products.list() })
  const { data: catRes } = useQuery({ queryKey: ['menu', 'categories'], queryFn: () => menuApi.categories.list() })
  const categories = (catRes?.data ?? []) as CategoryRow[]
  const products = (res?.data ?? []) as ProductRow[]

  const createMut = useMutation({
    mutationFn: (payload: FormData | ProductFormPayload) => menuApi.products.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['menu', 'products'] }),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: FormData | ProductFormPayload }) => menuApi.products.update(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['menu', 'products'] }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: string) => menuApi.products.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['menu', 'products'] }),
  })

  const isSaving = createMut.isPending || updateMut.isPending

  const columns = [
    { key: 'name', title: 'Nomi' },
    { key: 'price', title: 'Narx', render: (r: ProductRow) => `₸ ${r.price}` },
    { key: 'category', title: 'Kategoriya', render: (r: ProductRow) => r.category?.name ?? '-' },
    { key: 'available', title: 'Holat', render: (r: ProductRow) => (r.available ? 'Mavjud' : 'Off') },
    { key: 'actions', title: 'Amallar', render: (r: ProductRow) => (
      <div className="flex gap-2">
        <Button variant="ghost" onClick={() => handleEdit(r)}>Tahrirlash</Button>
        <Button variant="danger" onClick={() => handleDelete(r.id)}>O&apos;chirish</Button>
      </div>
    ) },
  ]

  function resetForm() {
    setEditing(null)
    setName('')
    setPrice('')
    setCategory('')
    setDescription('')
    setImageFile(null)
    setPreview(null)
  }

  function openNew() {
    resetForm()
    setOpen(true)
  }

  function handleEdit(row: ProductRow) {
    resetForm()
    setEditing(row)
    setName(row.name || '')
    setPrice(String(row.price ?? ''))
    setCategory(row.category?.id ?? '')
    setDescription(row.description || '')
    setPreview(row.image || row.image_url || null)
    setOpen(true)
  }

  function closeModal() {
    setOpen(false)
    resetForm()
  }

  async function handleSave() {
    if (!name.trim()) return toast.error("Nomi bo'sh bo'lishi mumkin emas")
    const p = Number(price)
    if (isNaN(p)) return toast.error("Narx raqam bo'lishi kerak")
    try {
      if (imageFile) {
        const fd = new FormData()
        fd.append('name', name)
        fd.append('price', String(p))
        if (category) fd.append('category', category)
        fd.append('description', description)
        fd.append('image', imageFile)

        if (editing?.id) await updateMut.mutateAsync({ id: editing.id, payload: fd })
        else await createMut.mutateAsync(fd)
      } else {
        const payload = { name, price: p, category: category || null, description }
        if (editing?.id) await updateMut.mutateAsync({ id: editing.id, payload })
        else await createMut.mutateAsync(payload)
      }
      toast.success('Saqlandi')
      closeModal()
    } catch {
      toast.error('Xatolik')
    }
  }

  async function handleDelete(id?: string) {
    if (!id) return
    if (!confirm("Rostdan ham o'chirmoqchimisiz?")) return
    try {
      await deleteMut.mutateAsync(id)
      toast.success('O\'chirildi')
    } catch {
      toast.error('O\'chirishda xatolik')
    }
  }

  return (
    <div className="p-6">
      <PageHeader title="Menyu" subtitle="Taomlarni boshqarish" actions={[{ title: 'Yangi mahsulot', onClick: openNew }]} />

      <div className="rounded-2xl">
        {isLoading ? (
          <div className="glass rounded-2xl p-6 text-sm text-gray-600">Yuklanmoqda...</div>
        ) : products.length ? (
          <Table columns={columns} data={products} />
        ) : (
          <div className="glass rounded-2xl p-6 text-sm text-gray-600">Hozircha mahsulotlar yo‘q.</div>
        )}
      </div>

      <Modal open={open} onClose={closeModal} title={editing ? 'Mahsulotni tahrirlash' : "Yangi mahsulot qo'shish"}>
        <div className="space-y-4">
          <Field label="Nomi"><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Taom nomi" /></Field>
          <Field label="Narx"><Input value={price} onChange={(e) => setPrice(e.target.value)} placeholder="Narx" /></Field>
          <Field label="Kategoriya">
            <Select value={category} onChange={(e) => setCategory(e.target.value)}>
              <option value="">-- Tanlang --</option>
              {categories.map((c: CategoryRow) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </Select>
          </Field>
          <Field label="Rasm">
            <input type="file" accept="image/*" onChange={(e) => {
              const f = e.target.files?.[0] ?? null
              if (preview?.startsWith('blob:')) URL.revokeObjectURL(preview)
              setImageFile(f)
              setPreview(f ? URL.createObjectURL(f) : null)
            }} />
            {preview ? <Image src={preview} alt="preview" width={160} height={112} className="mt-2 h-28 w-auto rounded" /> : null}
          </Field>
          <Field label="Tavsif"><Textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Taom haqida" /></Field>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={closeModal}>Bekor</Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? 'Saqlanmoqda...' : 'Saqlash'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
