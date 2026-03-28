// types/item.ts

export type ItemStatus = "considering" | "will_buy" | "purchased" | "skipped";

export interface ShoppingItem {
  id: string;
  name: string;
  category: string;
  shopee_url: string;
  image_url: string;
  quantity: number;
  note: string;
  status: ItemStatus;
  skip_reason: string;
  created_at: string;
}

export interface CreateItemPayload {
  name: string;
  category?: string;
  shopee_url?: string;
  image_url?: string;
  quantity?: number;
  note?: string;
}

export interface UpdateItemPayload {
  name?: string;
  category?: string;
  shopee_url?: string;
  image_url?: string;
  quantity?: number;
  note?: string;
  status?: ItemStatus;
  skip_reason?: string;
}

export interface ItemListResponse {
  items: ShoppingItem[];
  total: number;
}
