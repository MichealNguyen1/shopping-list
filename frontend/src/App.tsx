// App.tsx — Root component, quản lý state và gọi API

import { useEffect, useState } from "react";
import type { ShoppingItem, UpdateItemPayload } from "./types/item";
import * as api from "./api/items";
import { ItemForm } from "./components/ItemForm";
import { ItemTable } from "./components/ItemTable";
import "./App.css";

export default function App() {
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadItems();
  }, []);

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

  async function handleAdd(data: Parameters<typeof api.createItem>[0]) {
    const newItem = await api.createItem(data);
    setItems((prev) => [newItem, ...prev]);
  }

  // Cập nhật status (và skip_reason nếu cần) của item
  async function handleUpdateStatus(id: string, payload: UpdateItemPayload) {
    const updated = await api.updateItem(id, payload);
    setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
  }

  async function handleDelete(id: string) {
    await api.deleteItem(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
  }

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
        <h1>🛒 Danh sách mua sắm</h1>
      </header>

      <main className="app-main">
        <ItemForm onAdd={handleAdd} />
        <ItemTable
          items={items}
          onUpdateStatus={handleUpdateStatus}
          onDelete={handleDelete}
        />
      </main>
    </div>
  );
}
