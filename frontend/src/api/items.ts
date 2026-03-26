// api/items.ts — Tất cả HTTP calls đến backend
//
// Tách API calls ra file riêng thay vì viết thẳng trong component.
// Lợi ích: component không cần biết API URL hay cách gọi fetch — chỉ cần gọi hàm.
// Khi backend thay đổi, chỉ sửa ở đây, không đụng đến component.

import type {
  CreateItemPayload,
  ItemListResponse,
  ShoppingItem,
  UpdateItemPayload,
} from "../types/item";

// Đọc API URL từ environment variable
// import.meta.env: cách Vite expose env vars (khác với process.env của Node.js)
// Prefix VITE_: bắt buộc để Vite bundle vào frontend (bảo mật — tránh leak server-side vars)
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

// Helper function: gọi fetch và xử lý lỗi tập trung
// Tại sao cần helper này?
// fetch() không throw error khi status 4xx/5xx — chỉ throw khi network fail.
// Phải tự check response.ok để biết có lỗi không.
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  // Nếu status 4xx hoặc 5xx → throw error với message từ server
  if (!response.ok) {
    // Backend FastAPI trả error dạng: { "detail": "Item xyz không tồn tại" }
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail ?? `HTTP ${response.status}`);
  }

  // 204 No Content (DELETE thành công) không có body → không parse JSON
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Lấy danh sách tất cả items
export async function fetchItems(): Promise<ItemListResponse> {
  return request<ItemListResponse>("/items/");
}

// Lấy 1 item theo ID
export async function fetchItem(id: string): Promise<ShoppingItem> {
  return request<ShoppingItem>(`/items/${id}`);
}

// Tạo item mới — trả về item đã tạo (có id và created_at từ server)
export async function createItem(data: CreateItemPayload): Promise<ShoppingItem> {
  return request<ShoppingItem>("/items/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Update item — chỉ gửi field muốn thay đổi
export async function updateItem(
  id: string,
  data: UpdateItemPayload
): Promise<ShoppingItem> {
  return request<ShoppingItem>(`/items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// Xóa item — không có return value (204 No Content)
export async function deleteItem(id: string): Promise<void> {
  return request<void>(`/items/${id}`, { method: "DELETE" });
}
