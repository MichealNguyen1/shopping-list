// ItemCard.tsx — Hiển thị 1 item trong danh sách

import type { ShoppingItem } from "../types/item";

interface Props {
  item: ShoppingItem;
  // Callbacks: component con không tự gọi API — báo lên parent xử lý
  // Pattern này giúp state tập trung ở 1 chỗ (App.tsx), dễ debug hơn
  onTogglePurchased: (id: string, current: boolean) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function ItemCard({ item, onTogglePurchased, onDelete }: Props) {
  // Format giá tiền kiểu Việt Nam: 85000 → "85.000 ₫"
  const formattedPrice = new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(item.price);

  return (
    <div className={`item-card ${item.is_purchased ? "purchased" : ""}`}>
      <div className="item-main">
        {/* Checkbox đánh dấu đã mua */}
        <input
          type="checkbox"
          checked={item.is_purchased}
          onChange={() => onTogglePurchased(item.id, item.is_purchased)}
          title={item.is_purchased ? "Đánh dấu chưa mua" : "Đánh dấu đã mua"}
        />

        <div className="item-info">
          {/* Gạch ngang tên khi đã mua */}
          <span className="item-name">{item.name}</span>
          {item.brand && <span className="item-brand">{item.brand}</span>}
        </div>
      </div>

      <div className="item-meta">
        <span className="item-quantity">x{item.quantity}</span>
        {item.price > 0 && <span className="item-price">{formattedPrice}</span>}

        <button
          className="delete-btn"
          onClick={() => onDelete(item.id)}
          title="Xóa"
          aria-label={`Xóa ${item.name}`}
        >
          ✕
        </button>
      </div>
    </div>
  );
}
