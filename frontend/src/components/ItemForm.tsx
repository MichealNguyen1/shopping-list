// ItemForm.tsx

import { useEffect, useRef, useState } from "react";
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

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

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
  const [fetchingImage, setFetchingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  // Debounce ref: tránh gọi API mỗi lần gõ phím
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Tự động fetch ảnh khi shopeeUrl thay đổi
  useEffect(() => {
    if (!shopeeUrl.trim().startsWith("http")) {
      return;
    }
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setFetchingImage(true);
      try {
        const res = await fetch(
          `${API_BASE}/items/shopee-image?url=${encodeURIComponent(shopeeUrl.trim())}`
        );
        if (res.ok) {
          const data = await res.json();
          if (data.image_url) setImageUrl(data.image_url);
        }
      } catch {
        // silent fail — user vẫn có thể nhập tay
      } finally {
        setFetchingImage(false);
      }
    }, 800); // chờ 800ms sau khi ngừng gõ

    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [shopeeUrl]);

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
        <input type="url" placeholder="Link Shopee (tự lấy ảnh)" value={shopeeUrl}
          onChange={(e) => setShopeeUrl(e.target.value)} className="input-url" />
        <input type="number" placeholder="SL" value={quantity} min={1} max={999}
          onChange={(e) => setQuantity(Number(e.target.value))}
          style={{ width: 64, flex: "none" }} />
      </div>

      {/* Preview ảnh tự động */}
      {(fetchingImage || imageUrl) && (
        <div className="image-preview-row">
          {fetchingImage ? (
            <span className="fetch-status">⏳ Đang lấy ảnh...</span>
          ) : imageUrl ? (
            <>
              <img src={imageUrl} alt="preview" className="image-preview" />
              <span className="fetch-status" style={{ color: "#059669" }}>✓ Đã lấy ảnh</span>
              <button type="button" className="btn-toggle"
                onClick={() => setImageUrl("")}>Xoá ảnh</button>
            </>
          ) : null}
        </div>
      )}

      <button type="button" className="btn-toggle"
        onClick={() => setExpanded(!expanded)}>
        {expanded ? "▲ Ẩn" : "▼ Ghi chú / size / màu"}
      </button>

      {expanded && (
        <div className="form-row">
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
