// ItemForm.tsx — Form thêm item mới vào danh sách đang xem xét

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
        note: note.trim(),
      });
      setName(""); setShopeeUrl(""); setNote("");
      setExpanded(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="item-form">
      <h2>Thêm sản phẩm đang xem xét</h2>
      {error && <p className="error">{error}</p>}

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

      <button type="button" className="btn-toggle"
        onClick={() => setExpanded(!expanded)}>
        {expanded ? "▲ Ẩn" : "▼ Thêm ghi chú"}
      </button>

      {expanded && (
        <div className="form-row">
          <input type="text" placeholder="Ghi chú" value={note}
            onChange={(e) => setNote(e.target.value)} style={{ flex: 1 }} />
        </div>
      )}

      <button type="submit" disabled={loading || !name.trim()} className="btn-submit">
        {loading ? "Đang thêm..." : "+ Thêm vào danh sách xem xét"}
      </button>
    </form>
  );
}
