// ItemTable.tsx — Bảng danh sách, group theo phân loại (giống Google Sheets)

import { useMemo, useState } from "react";
import type { ShoppingItem } from "../types/item";

type FilterType = "all" | "pending" | "purchased";

interface Props {
  items: ShoppingItem[];
  onTogglePurchased: (id: string, current: boolean) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function ItemTable({ items, onTogglePurchased, onDelete }: Props) {
  const [filter, setFilter] = useState<FilterType>("all");

  const filtered = useMemo(() => {
    if (filter === "pending") return items.filter((i) => !i.is_purchased);
    if (filter === "purchased") return items.filter((i) => i.is_purchased);
    return items;
  }, [items, filter]);

  // Group items theo category, giữ nguyên thứ tự xuất hiện đầu tiên
  const grouped = useMemo(() => {
    const map = new Map<string, ShoppingItem[]>();
    for (const item of filtered) {
      const cat = item.category || "Khác";
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)!.push(item);
    }
    return map;
  }, [filtered]);

  const fmt = (p: number) =>
    p > 0 ? new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(p) : "—";

  const pendingCount = items.filter((i) => !i.is_purchased).length;
  const totalPending = items
    .filter((i) => !i.is_purchased)
    .reduce((s, i) => s + i.price * i.quantity, 0);

  return (
    <div className="table-section">
      <div className="table-header">
        <div className="table-title">
          <h2>Danh sách mua sắm</h2>
          <span className="badge">{pendingCount} chưa mua / {items.length} tổng</span>
          {totalPending > 0 && (
            <span className="total-amount">
              Cần chi: {new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(totalPending)}
            </span>
          )}
        </div>
        <div className="filter-tabs">
          {(["all", "pending", "purchased"] as FilterType[]).map((f) => (
            <button key={f} className={filter === f ? "active" : ""} onClick={() => setFilter(f)}>
              {f === "all" ? "Tất cả" : f === "pending" ? "Chưa mua" : "Đã mua"}
            </button>
          ))}
        </div>
      </div>

      <div className="table-wrapper">
        <table className="shopping-table">
          <thead>
            <tr>
              <th className="col-check"></th>
              <th className="col-category">Phân loại</th>
              <th className="col-name">Tên sản phẩm</th>
              <th className="col-qty">SL</th>
              <th className="col-price">Đơn giá</th>
              <th className="col-total">Thành tiền</th>
              <th className="col-note">Ghi chú</th>
              <th className="col-link">Link Shopee</th>
              <th className="col-action"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={9} className="empty-row">
                  {filter === "all" ? "Chưa có sản phẩm nào." : "Không có items."}
                </td>
              </tr>
            ) : (
              Array.from(grouped.entries()).map(([category, categoryItems]) => (
                categoryItems.map((item, idx) => (
                  <tr key={item.id} className={item.is_purchased ? "row-purchased" : ""}>
                    <td className="col-check">
                      <input
                        type="checkbox"
                        checked={item.is_purchased}
                        onChange={() => onTogglePurchased(item.id, item.is_purchased)}
                      />
                    </td>

                    {/* Phân loại: chỉ hiện ở row đầu tiên của group, rowSpan = số items */}
                    {idx === 0 && (
                      <td className="col-category" rowSpan={categoryItems.length}>
                        {category}
                      </td>
                    )}

                    <td className="col-name">
                      <span className="item-name">{item.name}</span>
                      {item.brand && <span className="item-brand"> · {item.brand}</span>}
                    </td>
                    <td className="col-qty">{item.quantity}</td>
                    <td className="col-price">{fmt(item.price)}</td>
                    <td className="col-total">
                      {item.price > 0 ? fmt(item.price * item.quantity) : "—"}
                    </td>
                    <td className="col-note">{item.note || "—"}</td>
                    <td className="col-link">
                      {item.shopee_url ? (
                        <a href={item.shopee_url} target="_blank" rel="noopener noreferrer"
                          className="shopee-link">
                          🛒 Mua
                        </a>
                      ) : "—"}
                    </td>
                    <td className="col-action">
                      <button className="delete-btn" onClick={() => onDelete(item.id)}>✕</button>
                    </td>
                  </tr>
                ))
              ))
            )}
          </tbody>

          {filtered.length > 0 && (
            <tfoot>
              <tr className="total-row">
                <td colSpan={5} className="total-label">Tổng cộng ({filtered.length} sản phẩm)</td>
                <td className="total-value">
                  {fmt(filtered.reduce((s, i) => s + i.price * i.quantity, 0))}
                </td>
                <td colSpan={3}></td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
}
