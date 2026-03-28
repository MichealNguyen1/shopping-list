// ItemTable.tsx — Card layout theo category, phong cách Shopee

import { useMemo, useState } from "react";
import type { ItemStatus, ShoppingItem, UpdateItemPayload } from "../types/item";

const STATUS_LABEL: Record<ItemStatus, string> = {
  considering: "Đang xem xét",
  will_buy: "Sẽ mua",
  purchased: "Đã mua",
  skipped: "Bỏ qua",
};

const STATUS_CLASS: Record<ItemStatus, string> = {
  considering: "status-considering",
  will_buy: "status-will-buy",
  purchased: "status-purchased",
  skipped: "status-skipped",
};

type FilterType = "all" | ItemStatus;

interface EditState {
  name: string;
  shopee_url: string;
  note: string;
}

interface Props {
  items: ShoppingItem[];
  onUpdateStatus: (id: string, payload: UpdateItemPayload) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function ItemTable({ items, onUpdateStatus, onDelete }: Props) {
  const [filter, setFilter] = useState<FilterType>("all");
  const [skipReasonInput, setSkipReasonInput] = useState<Record<string, string>>({});
  const [showSkipInput, setShowSkipInput] = useState<string | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editState, setEditState] = useState<EditState>({ name: "", shopee_url: "", note: "" });

  const filtered = useMemo(() => {
    if (filter === "all") return items;
    return items.filter((i) => i.status === filter);
  }, [items, filter]);

  const grouped = useMemo(() => {
    const map = new Map<string, ShoppingItem[]>();
    for (const item of filtered) {
      const cat = item.category || "Khác";
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)!.push(item);
    }
    return map;
  }, [filtered]);

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
        skip_reason: status === "skipped" ? (skipReason ?? "") : "",
      });
      setShowSkipInput(null);
      setSkipReasonInput((prev) => { const n = { ...prev }; delete n[id]; return n; });
    } finally {
      setLoadingId(null);
    }
  }

  function startEdit(item: ShoppingItem) {
    setEditingId(item.id);
    setEditState({ name: item.name, shopee_url: item.shopee_url, note: item.note });
    setShowSkipInput(null);
  }

  async function saveEdit(id: string) {
    if (!editState.name.trim()) return;
    setLoadingId(id);
    try {
      await onUpdateStatus(id, {
        name: editState.name.trim(),
        shopee_url: editState.shopee_url.trim(),
        note: editState.note.trim(),
      });
      setEditingId(null);
    } finally {
      setLoadingId(null);
    }
  }

  const filterTabs: { key: FilterType; label: string }[] = [
    { key: "all", label: "Tất cả" },
    { key: "considering", label: "Đang xem xét" },
    { key: "will_buy", label: "Sẽ mua" },
    { key: "purchased", label: "Đã mua" },
    { key: "skipped", label: "Bỏ qua" },
  ];

  return (
    <div className="list-container">
      {/* Filter tabs */}
      <div className="filter-tabs-wrap">
        <div className="filter-tabs">
          {filterTabs.map(({ key, label }) => (
            <button key={key}
              className={`filter-tab${filter === key ? " active" : ""}`}
              onClick={() => setFilter(key)}>
              {label}
              {counts[key] > 0 && (
                <span className="tab-count">{counts[key]}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="list-summary">
        <span>{filtered.length} sản phẩm</span>
        {counts.will_buy > 0 && (
          <span className="summary-will-buy">· {counts.will_buy} sẽ mua</span>
        )}
      </div>

      {/* Empty state */}
      {filtered.length === 0 && (
        <div className="empty-state">
          <p>Không có sản phẩm nào.</p>
        </div>
      )}

      {/* Category cards */}
      {Array.from(grouped.entries()).map(([category, categoryItems]) => (
        <div key={category} className="category-card">
          {/* Card header */}
          <div className="category-header">
            <span className="category-name">{category}</span>
            <span className="category-count">{categoryItems.length} sản phẩm</span>
          </div>

          {/* Item rows */}
          {categoryItems.map((item, idx) => {
            const isEditing = editingId === item.id;
            const isLoading = loadingId === item.id;

            return (
              <div key={item.id}
                className={`item-row item-${item.status}${isEditing ? " item-editing" : ""}`}>

                {/* Divider (trừ row đầu) */}
                {idx > 0 && <div className="item-divider" />}

                <div className="item-main">
                  {/* Tên + ghi chú */}
                  <div className="item-info">
                    {isEditing ? (
                      <input className="edit-input edit-name"
                        value={editState.name}
                        onChange={(e) => setEditState((s) => ({ ...s, name: e.target.value }))}
                        autoFocus placeholder="Tên sản phẩm" />
                    ) : (
                      <span className="item-name" onClick={() => startEdit(item)}>
                        {item.name}
                      </span>
                    )}

                    {isEditing ? (
                      <input className="edit-input edit-note"
                        value={editState.note}
                        onChange={(e) => setEditState((s) => ({ ...s, note: e.target.value }))}
                        placeholder="Ghi chú" />
                    ) : (
                      item.note && <span className="item-note">{item.note}</span>
                    )}

                    {/* Skip reason */}
                    {!isEditing && item.status === "skipped" && item.skip_reason && (
                      <span className="item-skip-reason">⚠️ {item.skip_reason}</span>
                    )}
                  </div>

                  {/* Phải: link + status + xoá */}
                  <div className="item-right">
                    {isEditing ? (
                      <input className="edit-input edit-url"
                        value={editState.shopee_url}
                        onChange={(e) => setEditState((s) => ({ ...s, shopee_url: e.target.value }))}
                        placeholder="Link Shopee" />
                    ) : item.shopee_url ? (
                      <a href={item.shopee_url} target="_blank" rel="noopener noreferrer"
                        className="shopee-link">🛒 Shopee</a>
                    ) : null}

                    <span className={`status-tag ${STATUS_CLASS[item.status]}`}>
                      {STATUS_LABEL[item.status]}
                    </span>

                    <button className="delete-btn" onClick={() => onDelete(item.id)}>✕</button>
                  </div>
                </div>

                {/* Skip input */}
                {showSkipInput === item.id && (
                  <div className="skip-input-row">
                    <input type="text" placeholder="Lý do bỏ qua (tuỳ chọn)"
                      value={skipReasonInput[item.id] ?? ""}
                      onChange={(e) => setSkipReasonInput((p) => ({ ...p, [item.id]: e.target.value }))}
                      autoFocus />
                    <button className="btn-sm btn-gray"
                      onClick={() => changeStatus(item.id, "skipped", skipReasonInput[item.id])}
                      disabled={isLoading}>Xác nhận</button>
                    <button className="btn-sm btn-outline"
                      onClick={() => setShowSkipInput(null)}>Huỷ</button>
                  </div>
                )}

                {/* Action buttons */}
                <div className="item-actions">
                  {isEditing ? (
                    <>
                      <button className="btn-action btn-save"
                        onClick={() => saveEdit(item.id)}
                        disabled={isLoading || !editState.name.trim()}>Lưu</button>
                      <button className="btn-action btn-cancel-edit"
                        onClick={() => setEditingId(null)}>Huỷ</button>
                    </>
                  ) : (
                    <>
                      {item.status === "considering" && (
                        <button className="btn-action btn-will-buy" disabled={isLoading}
                          onClick={() => changeStatus(item.id, "will_buy")}>✓ Sẽ mua</button>
                      )}
                      {item.status !== "purchased" && item.status !== "skipped" && (
                        <button className="btn-action btn-purchased" disabled={isLoading}
                          onClick={() => changeStatus(item.id, "purchased")}>✓ Đã mua</button>
                      )}
                      {item.status !== "skipped" && (
                        <button className="btn-action btn-skip" disabled={isLoading}
                          onClick={() => { setShowSkipInput(item.id); setEditingId(null); }}>✕ Bỏ qua</button>
                      )}
                      {(item.status === "purchased" || item.status === "skipped") && (
                        <button className="btn-action btn-reset" disabled={isLoading}
                          onClick={() => changeStatus(item.id, "considering")}>↩ Xem lại</button>
                      )}
                      <button className="btn-action btn-edit" disabled={isLoading}
                        onClick={() => startEdit(item)}>✎ Sửa</button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}
