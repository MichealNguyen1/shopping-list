// ItemTable.tsx — Bảng quyết định mua sắm, group theo phân loại

import { useMemo, useState } from "react";
import type { ItemStatus, ShoppingItem, UpdateItemPayload } from "../types/item";

// Nhãn hiển thị cho từng trạng thái
const STATUS_LABEL: Record<ItemStatus, string> = {
  considering: "Đang xem xét",
  will_buy: "Sẽ mua",
  purchased: "Đã mua",
  skipped: "Bỏ qua",
};

// Màu badge cho từng trạng thái
const STATUS_COLOR: Record<ItemStatus, string> = {
  considering: "#f59e0b",  // vàng
  will_buy: "#2563eb",      // xanh dương
  purchased: "#059669",     // xanh lá
  skipped: "#9ca3af",       // xám
};

type FilterType = "all" | ItemStatus;

interface Props {
  items: ShoppingItem[];
  onUpdateStatus: (id: string, payload: UpdateItemPayload) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function ItemTable({ items, onUpdateStatus, onDelete }: Props) {
  const [filter, setFilter] = useState<FilterType>("all");
  // skipReasonInput: lưu tạm lý do skip trước khi confirm
  const [skipReasonInput, setSkipReasonInput] = useState<Record<string, string>>({});
  // showSkipInput: id của item đang hiện ô nhập lý do skip
  const [showSkipInput, setShowSkipInput] = useState<string | null>(null);
  // loadingId: item đang chờ API response
  const [loadingId, setLoadingId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    if (filter === "all") return items;
    return items.filter((i) => i.status === filter);
  }, [items, filter]);

  // Group theo category, giữ thứ tự sort từ backend
  const grouped = useMemo(() => {
    const map = new Map<string, ShoppingItem[]>();
    for (const item of filtered) {
      const cat = item.category || "Khác";
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)!.push(item);
    }
    return map;
  }, [filtered]);

  // Counts cho filter tabs
  const counts: Record<FilterType, number> = useMemo(() => ({
    all: items.length,
    considering: items.filter((i) => i.status === "considering").length,
    will_buy: items.filter((i) => i.status === "will_buy").length,
    purchased: items.filter((i) => i.status === "purchased").length,
    skipped: items.filter((i) => i.status === "skipped").length,
  }), [items]);

  async function changeStatus(id: string, status: ItemStatus, skipReason?: string) {
    setLoadingId(id);
    try {
      await onUpdateStatus(id, {
        status,
        ...(status === "skipped" ? { skip_reason: skipReason ?? "" } : { skip_reason: "" }),
      });
      setShowSkipInput(null);
      setSkipReasonInput((prev) => { const next = { ...prev }; delete next[id]; return next; });
    } finally {
      setLoadingId(null);
    }
  }

  function handleSkipClick(id: string) {
    setShowSkipInput(id);
    setSkipReasonInput((prev) => ({ ...prev, [id]: "" }));
  }

  function handleSkipConfirm(id: string) {
    changeStatus(id, "skipped", skipReasonInput[id] ?? "");
  }

  const filterTabs: { key: FilterType; label: string }[] = [
    { key: "all", label: "Tất cả" },
    { key: "considering", label: "Đang xem xét" },
    { key: "will_buy", label: "Sẽ mua" },
    { key: "purchased", label: "Đã mua" },
    { key: "skipped", label: "Bỏ qua" },
  ];

  return (
    <div className="table-section">
      <div className="table-header">
        <div className="table-title">
          <h2>Danh sách</h2>
          <span className="badge">{items.length} sản phẩm</span>
          <span className="badge" style={{ background: "#fef3c7", color: "#d97706" }}>
            {counts.will_buy} sẽ mua
          </span>
        </div>
        <div className="filter-tabs">
          {filterTabs.map(({ key, label }) => (
            <button key={key} className={filter === key ? "active" : ""}
              onClick={() => setFilter(key)}>
              {label} {counts[key] > 0 && <span style={{ opacity: 0.7 }}>({counts[key]})</span>}
            </button>
          ))}
        </div>
      </div>

      <div className="table-wrapper">
        <table className="shopping-table">
          <thead>
            <tr>
              <th className="col-category">Phân loại</th>
              <th className="col-name">Tên sản phẩm</th>
              <th className="col-note">Ghi chú / Lý do bỏ</th>
              <th className="col-link">Link Shopee</th>
              <th className="col-status">Trạng thái</th>
              <th className="col-actions">Hành động</th>
              <th className="col-action"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-row">
                  {filter === "all" ? "Chưa có sản phẩm nào." : "Không có items trong mục này."}
                </td>
              </tr>
            ) : (
              Array.from(grouped.entries()).map(([category, categoryItems]) =>
                categoryItems.map((item, idx) => (
                  <tr key={item.id} className={`row-${item.status}`}>
                    {/* Category chỉ hiện ở row đầu tiên của group */}
                    {idx === 0 && (
                      <td className="col-category" rowSpan={categoryItems.length}>
                        {category}
                      </td>
                    )}

                    <td className="col-name">
                      <span className="item-name">{item.name}</span>
                    </td>

                    <td className="col-note">
                      {showSkipInput === item.id ? (
                        <div className="skip-input-row">
                          <input
                            type="text"
                            placeholder="Lý do bỏ qua (tuỳ chọn)"
                            value={skipReasonInput[item.id] ?? ""}
                            onChange={(e) =>
                              setSkipReasonInput((prev) => ({ ...prev, [item.id]: e.target.value }))
                            }
                            autoFocus
                          />
                          <button className="btn-confirm-skip"
                            onClick={() => handleSkipConfirm(item.id)}
                            disabled={loadingId === item.id}>
                            Xác nhận
                          </button>
                          <button className="btn-cancel-skip"
                            onClick={() => setShowSkipInput(null)}>
                            Huỷ
                          </button>
                        </div>
                      ) : (
                        <span>
                          {item.status === "skipped" && item.skip_reason
                            ? `⚠️ ${item.skip_reason}`
                            : item.note || "—"}
                        </span>
                      )}
                    </td>

                    <td className="col-link">
                      {item.shopee_url ? (
                        <a href={item.shopee_url} target="_blank" rel="noopener noreferrer"
                          className="shopee-link">
                          🛒 Xem
                        </a>
                      ) : "—"}
                    </td>

                    <td className="col-status">
                      <span className="status-badge"
                        style={{ background: STATUS_COLOR[item.status] + "22", color: STATUS_COLOR[item.status] }}>
                        {STATUS_LABEL[item.status]}
                      </span>
                    </td>

                    {/* Nút hành động — chỉ hiện các trạng thái khả dụng */}
                    <td className="col-actions">
                      {item.status !== "will_buy" && item.status !== "purchased" && item.status !== "skipped" && (
                        <button className="action-btn will-buy"
                          disabled={loadingId === item.id}
                          onClick={() => changeStatus(item.id, "will_buy")}>
                          ✓ Sẽ mua
                        </button>
                      )}
                      {item.status !== "purchased" && item.status !== "skipped" && (
                        <button className="action-btn purchased"
                          disabled={loadingId === item.id}
                          onClick={() => changeStatus(item.id, "purchased")}>
                          ✓ Đã mua
                        </button>
                      )}
                      {item.status !== "skipped" && (
                        <button className="action-btn skip"
                          disabled={loadingId === item.id}
                          onClick={() => handleSkipClick(item.id)}>
                          ✕ Bỏ qua
                        </button>
                      )}
                      {(item.status === "purchased" || item.status === "skipped") && (
                        <button className="action-btn reset"
                          disabled={loadingId === item.id}
                          onClick={() => changeStatus(item.id, "considering")}>
                          ↩ Xem lại
                        </button>
                      )}
                    </td>

                    <td className="col-action">
                      <button className="delete-btn" onClick={() => onDelete(item.id)}>✕</button>
                    </td>
                  </tr>
                ))
              )
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
