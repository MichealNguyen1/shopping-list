// LoginScreen.tsx — Màn hình nhập mật khẩu đơn giản

import { useState } from "react";

// Mật khẩu lấy từ env var VITE_APP_PASSWORD
// Nếu không set thì không cần mật khẩu (dev mode)
const APP_PASSWORD = import.meta.env.VITE_APP_PASSWORD ?? "";

interface Props {
  onUnlock: () => void;
}

export function LoginScreen({ onUnlock }: Props) {
  const [input, setInput] = useState("");
  const [error, setError] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (input === APP_PASSWORD) {
      // Lưu vào sessionStorage — hết khi đóng tab
      sessionStorage.setItem("dbt_auth", "1");
      onUnlock();
    } else {
      setError(true);
      setInput("");
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>🛒 Dun Bá Tước</h1>
        <p>Nhập mật khẩu để vào danh sách</p>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            placeholder="Mật khẩu"
            value={input}
            onChange={(e) => { setInput(e.target.value); setError(false); }}
            autoFocus
          />
          {error && <p className="login-error">Sai mật khẩu, thử lại nhé</p>}
          <button type="submit" disabled={!input}>Vào</button>
        </form>
      </div>
    </div>
  );
}

// Hàm kiểm tra đã auth chưa — dùng trong App.tsx
export function isAuthenticated(): boolean {
  if (!APP_PASSWORD) return true; // không có password → không cần login
  return sessionStorage.getItem("dbt_auth") === "1";
}
