// types/item.ts — TypeScript type definitions
//
// Định nghĩa types ở 1 chỗ, dùng ở nhiều nơi.
// Khi API thay đổi, chỉ cần sửa ở đây → TypeScript compiler báo lỗi ở mọi nơi dùng sai.

// Shape của item nhận từ API response
// Phải match với ItemResponse trong backend/schemas.py
export interface ShoppingItem {
  id: string;
  name: string;
  brand: string;
  quantity: number;
  price: number;
  is_purchased: boolean;
  created_at: string; // ISO 8601 string: "2024-01-15T08:30:00Z"
}

// Data gửi lên khi tạo item mới — phải match với ItemCreate trong backend
export interface CreateItemPayload {
  name: string;
  brand?: string;     // ? = optional
  quantity?: number;
  price?: number;
}

// Data gửi lên khi update — tất cả optional vì PATCH chỉ update field có giá trị
export interface UpdateItemPayload {
  name?: string;
  brand?: string;
  quantity?: number;
  price?: number;
  is_purchased?: boolean;
}

// Shape của GET /items response
export interface ItemListResponse {
  items: ShoppingItem[];
  total: number;
}
