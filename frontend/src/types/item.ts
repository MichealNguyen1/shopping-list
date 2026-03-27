// types/item.ts — TypeScript type definitions

// 4 trạng thái quyết định của mỗi item — phải match với backend ItemStatus
export type ItemStatus = "considering" | "will_buy" | "purchased" | "skipped";

// Shape của item nhận từ API response — match với ItemResponse trong backend/schemas.py
export interface ShoppingItem {
  id: string;
  name: string;
  category: string;
  shopee_url: string;
  note: string;
  status: ItemStatus;
  skip_reason: string;
  created_at: string;
}

// Data gửi lên khi tạo item mới — match với ItemCreate trong backend
export interface CreateItemPayload {
  name: string;
  category?: string;
  shopee_url?: string;
  note?: string;
}

// Data gửi lên khi update — tất cả optional vì PATCH chỉ update field có giá trị
export interface UpdateItemPayload {
  name?: string;
  category?: string;
  shopee_url?: string;
  note?: string;
  status?: ItemStatus;
  skip_reason?: string;
}

// Shape của GET /items response
export interface ItemListResponse {
  items: ShoppingItem[];
  total: number;
}
