// ItemForm.tsx

import { useState } from "react";
import type { CreateItemPayload } from "../types/item";

const CATEGORIES = [
  "1. Đồ cho bé ăn",
  "2. Sản phẩm vệ sinh",
  "3. Tủ thuốc",
  "4. Bìm, khăn ướt",
  "5. Đồ vải cho bé",
  "6. Máy móc",
  "7. Quần áo cho bé",
  "Khác",
];

interface Props {
  onAdd: (data: CreateItemPayload) => Promise<void>;
}

export function ItemForm({ onAdd }: Props) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [shopeeUrl, setShopeeUrl] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await onAdd({
        name: name.trim(),
        category,
        shopee_url: shopeeUrl.trim(),
        image_url: imageUrl.trim(),
        quantity,
        note: note.trim(),
      });
      setName(""); setShopeeUrl(""); setImageUrl(""); setQuantity(1); setNote("");
      setExpanded(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="item-form">
      <h2>Thêm sản phẩm</h2>
      {error && <p className="error" style={{ marginBottom: 8 }}>{error}</p>}

      {/* Row 1: category + tên */}
      <div className="form-row">
        <select value={category} onChange={(e) => setCategory(e.target.value)}
          className="input-category">
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input type="text" placeholder="Tên sản phẩm *" value={name}
          onChange={(e) => setName(e.target.value)} required className="input-name" />
      </div>

      {/* Row 2: link Shopee + số lượng */}
      <div className="form-row">
        <input type="url" placeholder="Link Shopee" value={shopeeUrl}
          onChange={(e) => setShopeeUrl(e.target.value)} className="input-url" />
        <input type="number" placeholder="SL" value={quantity} min={1} max={999}
          onChange={(e) => setQuantity(Number(e.target.value))}
          style={{ width: 64, flex: "none" }} />
      </div>

      <button type="button" className="btn-toggle"
        onClick={() => setExpanded(!expanded)}>
        {expanded ? "▲ Ẩn" : "▼ Thêm ảnh & ghi chú"}
      </button>

      {expanded && (
        <div className="form-row">
          <input type="url" placeholder="Link ảnh sản phẩm (paste từ Shopee)" value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)} style={{ flex: 2 }} />
          <input type="text" placeholder="Ghi chú / size / màu" value={note}
            onChange={(e) => setNote(e.target.value)} style={{ flex: 1 }} />
        </div>
      )}

      <button type="submit" disabled={loading || !name.trim()} className="btn-submit">
        {loading ? "Đang thêm..." : "+ Thêm vào danh sách"}
      </button>
    </form>
  );
}
