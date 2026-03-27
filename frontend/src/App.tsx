// App.tsx — Root component, nơi quản lý toàn bộ state và gọi API
//
// State management pattern ở đây: "lift state up"
// items state nằm ở App vì cả ItemForm lẫn ItemList đều cần đọc/ghi nó.
// Component con nhận state qua props, báo thay đổi qua callback props.

import { useEffect, useState } from "react";
import type { ShoppingItem } from "./types/item";
import * as api from "./api/items";
import { ItemForm } from "./components/ItemForm";
import { ItemTable } from "./components/ItemTable";
import "./App.css";

export default function App() {
  // items: danh sách shopping items — source of truth cho toàn app
  const [items, setItems] = useState<ShoppingItem[]>([]);

  // Global loading state khi fetch lần đầu
  const [loading, setLoading] = useState(true);

  // Global error state
  const [error, setError] = useState<string | null>(null);

  // useEffect với [] dependency: chạy 1 lần sau lần render đầu tiên
  // Giống viewDidLoad trong iOS, nhưng dành cho side effects (API call, subscription...)
  useEffect(() => {
    loadItems();
  }, []); // [] = chỉ chạy 1 lần khi component mount

  async function loadItems() {
    try {
      setLoading(true);
      setError(null);
      const response = await api.fetchItems();
      setItems(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải danh sách");
    } finally {
      setLoading(false);
    }
  }

  // Thêm item mới: gọi API → prepend vào đầu list (không fetch lại toàn bộ)
  async function handleAdd(data: Parameters<typeof api.createItem>[0]) {
    const newItem = await api.createItem(data);
    // Thêm item mới vào đầu mảng (mới nhất ở trên)
    // Không mutate state trực tiếp — luôn tạo array mới
    setItems((prev) => [newItem, ...prev]);
  }

  // Toggle trạng thái đã mua / chưa mua
  async function handleTogglePurchased(id: string, current: boolean) {
    const updated = await api.updateItem(id, { is_purchased: !current });
    // Thay thế item cũ bằng item mới trong array
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
  }

  // Xóa item: gọi API → remove khỏi local state
  async function handleDelete(id: string) {
    await api.deleteItem(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
  }

  // Render states
  if (loading) return <div className="center">Đang tải...</div>;
  if (error) return (
    <div className="center error">
      <p>{error}</p>
      <button onClick={loadItems}>Thử lại</button>
    </div>
  );

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛒 Shopping List</h1>
      </header>

      <main className="app-main">
        <ItemForm onAdd={handleAdd} />
        <ItemTable
          items={items}
          onTogglePurchased={handleTogglePurchased}
          onDelete={handleDelete}
        />
      </main>
    </div>
  );
}
