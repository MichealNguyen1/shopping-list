// ItemForm.tsx — Form thêm item mới

import { useState } from "react";
import type { CreateItemPayload } from "../types/item";

// Danh mục mặc định từ sheet gốc
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
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState(0);
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
        quantity,
        price,
        note: note.trim(),
      });
      setName(""); setShopeeUrl(""); setQuantity(1); setPrice(0); setNote("");
      setExpanded(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="item-form">
      <h2>Thêm sản phẩm mới</h2>
      {error && <p className="error">{error}</p>}

      {/* Row chính: phân loại + tên + link Shopee */}
      <div className="form-row">
        <select value={category} onChange={(e) => setCategory(e.target.value)}
          className="input-category">
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        <input type="text" placeholder="Tên sản phẩm *" value={name}
          onChange={(e) => setName(e.target.value)} required className="input-name" />

        <input type="url" placeholder="Link Shopee" value={shopeeUrl}
          onChange={(e) => setShopeeUrl(e.target.value)} className="input-url" />
      </div>

      {/* Toggle thêm chi tiết */}
      <button type="button" className="btn-toggle"
        onClick={() => setExpanded(!expanded)}>
        {expanded ? "▲ Ẩn" : "▼ Thêm SL, giá, ghi chú"}
      </button>

      {expanded && (
        <div className="form-row">
          <input type="number" placeholder="Số lượng" value={quantity} min={1}
            onChange={(e) => setQuantity(Number(e.target.value))} className="input-sm" />
          <input type="number" placeholder="Giá (VNĐ)" value={price} min={0}
            onChange={(e) => setPrice(Number(e.target.value))} />
          <input type="text" placeholder="Ghi chú" value={note}
            onChange={(e) => setNote(e.target.value)} />
        </div>
      )}

      <button type="submit" disabled={loading || !name.trim()} className="btn-submit">
        {loading ? "Đang thêm..." : "+ Thêm vào danh sách"}
      </button>
    </form>
  );
}
