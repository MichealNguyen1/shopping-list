// ItemList.tsx — Hiển thị danh sách items, có filter

import type { ShoppingItem } from "../types/item";
import { ItemCard } from "./ItemCard";

type FilterType = "all" | "pending" | "purchased";

interface Props {
  items: ShoppingItem[];
  onTogglePurchased: (id: string, current: boolean) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function ItemList({ items, onTogglePurchased, onDelete }: Props) {
  // useState cho filter tabs — "all" | "pending" | "purchased"
  const [filter, setFilter] = useState<FilterType>("all");

  // Tính toán từ items prop, không cần state riêng
  // useMemo: chỉ tính lại khi items hoặc filter thay đổi, tránh tính lại mỗi render
  const filtered = useMemo(() => {
    if (filter === "pending") return items.filter((i) => !i.is_purchased);
    if (filter === "purchased") return items.filter((i) => i.is_purchased);
    return items;
  }, [items, filter]);

  // Tổng tiền chỉ tính items chưa mua
  const totalPending = useMemo(() => {
    return items
      .filter((i) => !i.is_purchased)
      .reduce((sum, i) => sum + i.price * i.quantity, 0);
  }, [items]);

  const formattedTotal = new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(totalPending);

  const pendingCount = items.filter((i) => !i.is_purchased).length;

  return (
    <div className="item-list">
      <div className="list-header">
        <h2>
          Danh sách ({pendingCount} chưa mua / {items.length} tổng)
        </h2>
        {totalPending > 0 && (
          <span className="total-price">Cần chi: {formattedTotal}</span>
        )}
      </div>

      {/* Filter tabs */}
      <div className="filter-tabs">
        {(["all", "pending", "purchased"] as FilterType[]).map((f) => (
          <button
            key={f}
            className={filter === f ? "active" : ""}
            onClick={() => setFilter(f)}
          >
            {f === "all" ? "Tất cả" : f === "pending" ? "Chưa mua" : "Đã mua"}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="empty-state">
          {filter === "all" ? "Danh sách trống. Thêm món đồ đầu tiên!" : "Không có items."}
        </p>
      ) : (
        <div className="cards">
          {filtered.map((item) => (
            <ItemCard
              key={item.id}  // key giúp React track từng item khi list thay đổi
              item={item}
              onTogglePurchased={onTogglePurchased}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Import useState và useMemo ở đây để dễ đọc
import { useMemo, useState } from "react";
