// ItemForm.tsx — Form thêm item mới vào danh sách

import { useState } from "react";
import type { CreateItemPayload } from "../types/item";

interface Props {
  // Callback được gọi khi user submit form thành công
  // Parent component quyết định làm gì với data (gọi API, update state...)
  onAdd: (data: CreateItemPayload) => Promise<void>;
}

export function ItemForm({ onAdd }: Props) {
  // State cho từng field trong form
  // useState<string>("") = state là string, initial value là ""
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState(0);

  // Loading state: disable button khi đang gọi API, tránh submit nhiều lần
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    // preventDefault: ngăn browser reload trang (behavior mặc định của form submit)
    e.preventDefault();

    if (!name.trim()) return; // Không submit nếu tên rỗng

    setLoading(true);
    setError(null);

    try {
      await onAdd({ name: name.trim(), brand: brand.trim(), quantity, price });
      // Reset form sau khi thêm thành công
      setName("");
      setBrand("");
      setQuantity(1);
      setPrice(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Có lỗi xảy ra");
    } finally {
      // finally luôn chạy dù success hay error → đảm bảo loading = false
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="item-form">
      <h2>Thêm món đồ mới</h2>

      {/* Hiển thị lỗi nếu có */}
      {error && <p className="error">{error}</p>}

      <div className="form-row">
        <input
          type="text"
          placeholder="Tên món đồ *"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Thương hiệu"
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
        />
      </div>

      <div className="form-row">
        <input
          type="number"
          placeholder="Số lượng"
          value={quantity}
          min={1}
          onChange={(e) => setQuantity(Number(e.target.value))}
        />
        <input
          type="number"
          placeholder="Giá (VNĐ)"
          value={price}
          min={0}
          onChange={(e) => setPrice(Number(e.target.value))}
        />
      </div>

      {/* disabled khi loading hoặc tên rỗng */}
      <button type="submit" disabled={loading || !name.trim()}>
        {loading ? "Đang thêm..." : "Thêm vào danh sách"}
      </button>
    </form>
  );
}
