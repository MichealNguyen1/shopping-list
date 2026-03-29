// CalendarView.tsx — Main pregnancy calendar view
import React, { useState, useEffect } from 'react';
import { useMilestones, Milestone } from '../api/useMilestones';
import './CalendarView.css';

// Mock data for demo when backend is not available
const MOCK_MILESTONES: Milestone[] = [
  {
    id: '1',
    week: 4,
    title: 'Kiểm tra thai nhi lần đầu',
    category: 'checkup',
    due_date: '2024-04-15',
    description: 'Siêu âm kiểm tra xác nhận thai nhi',
    notes: 'Mang đầy đủ giấy tờ',
    tasks: [{ id: '1', title: 'Đặt lịch bác sĩ', completed: false }],
    status: 'pending',
    priority: 'high',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    week: 12,
    title: 'Siêu âm hình thái',
    category: 'checkup',
    due_date: '2024-06-15',
    description: 'Kiểm tra hình thái thai nhi',
    notes: 'Có thể biết giới tính bé',
    tasks: [],
    status: 'pending',
    priority: 'high',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    week: 20,
    title: 'Mua đồ cho bé',
    category: 'shopping',
    due_date: '2024-07-15',
    description: 'Mua tã, bình sữa, quần áo',
    notes: 'Nên mua từ các cửa hàng uy tín',
    tasks: [
      { id: '1', title: 'Tã con', completed: false },
      { id: '2', title: 'Bình sữa', completed: false },
    ],
    status: 'pending',
    priority: 'medium',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '4',
    week: 28,
    title: 'Kiểm tra glucose',
    category: 'checkup',
    due_date: '2024-08-15',
    description: 'Test chẩn đoán tiểu đường thai kỳ',
    notes: 'Nhịn ăn trước 3 tiếng',
    tasks: [],
    status: 'pending',
    priority: 'medium',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '5',
    week: 36,
    title: 'Chuẩn bị sinh',
    category: 'preparation',
    due_date: '2024-09-15',
    description: 'Chuẩn bị túi sinh, giấy tờ',
    notes: 'Lên bệnh viện khi có dấu hiệu',
    tasks: [
      { id: '1', title: 'Chuẩn bị túi sinh', completed: false },
      { id: '2', title: 'Sắp xếp thời gian', completed: false },
    ],
    status: 'pending',
    priority: 'high',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export const CalendarView: React.FC<{ onNavigateToShopping?: () => void }> = ({ onNavigateToShopping }) => {
  const { milestones, loading, error, fetchMilestones } = useMilestones();
  const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [useMockData, setUseMockData] = useState(false);

  useEffect(() => {
    fetchMilestones();
  }, []);

  // Auto-enable mock data if no real data after 2 seconds
  useEffect(() => {
    if (!loading && milestones.length === 0 && error && !useMockData) {
      const timer = setTimeout(() => {
        setUseMockData(true);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [loading, milestones, error, useMockData]);

  // Show mock data if API is not available
  const displayMilestones = milestones.length > 0 ? milestones : (useMockData ? MOCK_MILESTONES : []);

  const handleSelectMilestone = (milestone: Milestone) => {
    setSelectedMilestone(milestone);
    setIsModalOpen(true);
  };

  const categoryEmoji = (cat: string) => {
    const map: Record<string, string> = {
      checkup: '🏥',
      shopping: '🛍️',
      preparation: '🎁',
      booking: '📅',
      other: '📝',
    };
    return map[cat] || '📌';
  };

  const statusText = (status: string) => {
    const map: Record<string, string> = {
      pending: '⏳ Chưa làm',
      in_progress: '⚙️ Đang tiến hành',
      completed: '✅ Đã hoàn thành',
    };
    return map[status] || status;
  };

  return (
    <div className="calendar-view">
      <div className="calendar-header">
        <h1>📅 Lịch Thai Kỳ - Hướng Dẫn Thai Kỳ</h1>
        <p className="subtitle">Theo dõi các mốc quan trọng và nhiệm vụ cần làm trong thai kỳ</p>
      </div>

      {loading && milestones.length === 0 && !useMockData && (
        <div className="loading">⏳ Đang tải dữ liệu từ server...</div>
      )}

      {error && !useMockData && (
        <div className="error-box">
          <p>⚠️ Không thể kết nối tới server. {error}</p>
          <button 
            className="btn-mock"
            onClick={() => setUseMockData(true)}
          >
            Xem dữ liệu mẫu (Demo Mode)
          </button>
        </div>
      )}

      {!loading && displayMilestones.length === 0 && !useMockData && (
        <div className="empty-state">
          <p>Không có dữ liệu. Vui lòng kiểm tra kết nối.</p>
          <button 
            className="btn-mock"
            onClick={() => setUseMockData(true)}
          >
            Xem dữ liệu mẫu
          </button>
        </div>
      )}

      {useMockData && (
        <div className="demo-badge">📌 Chế độ Demo - Dữ liệu mẫu</div>
      )}

      <div className="milestones-grid">
        {displayMilestones.map(m => (
          <div 
            key={m.id} 
            className={`milestone-card category-${m.category}`}
            onClick={() => handleSelectMilestone(m)}
          >
            <div className="card-header">
              <span className="category-badge">{categoryEmoji(m.category)}</span>
              <span className="priority-badge">
                {m.priority === 'high' ? '🔴 Quan trọng' : m.priority === 'medium' ? '🟡 Bình thường' : '🟢 Thấp'}
              </span>
            </div>
            <h3>{m.title}</h3>
            <div className="card-meta">
              <p className="week">📍 Tuần {m.week}</p>
              <p className="status">{statusText(m.status)}</p>
            </div>
            <p className="description">{m.description}</p>
            {m.tasks && m.tasks.length > 0 && (
              <div className="tasks-count">
                📋 {m.tasks.length} nhiệm vụ
              </div>
            )}
          </div>
        ))}
      </div>

      {onNavigateToShopping && (
        <button onClick={onNavigateToShopping} className="btn-back">
          🛒 Quay lại Shopping
        </button>
      )}

      {isModalOpen && selectedMilestone && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal milestone-modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setIsModalOpen(false)}>✕</button>
            
            <div className="modal-header">
              <span className="modal-category">{categoryEmoji(selectedMilestone.category)}</span>
              <h2>{selectedMilestone.title}</h2>
            </div>

            <div className="modal-content">
              <div className="info-row">
                <strong>📍 Tuần:</strong>
                <span>{selectedMilestone.week}</span>
              </div>
              
              <div className="info-row">
                <strong>📅 Ngày dự kiến:</strong>
                <span>{new Date(selectedMilestone.due_date).toLocaleDateString('vi-VN')}</span>
              </div>

              <div className="info-row">
                <strong>🏷️ Loại:</strong>
                <span>{categoryEmoji(selectedMilestone.category)} {selectedMilestone.category}</span>
              </div>

              <div className="info-row">
                <strong>⚡ Ưu tiên:</strong>
                <span>{selectedMilestone.priority === 'high' ? '🔴 Quan trọng' : selectedMilestone.priority === 'medium' ? '🟡 Bình thường' : '🟢 Thấp'}</span>
              </div>

              <div className="info-row">
                <strong>📋 Trạng thái:</strong>
                <span>{statusText(selectedMilestone.status)}</span>
              </div>

              {selectedMilestone.description && (
                <div className="info-section">
                  <strong>ℹ️ Mô tả:</strong>
                  <p>{selectedMilestone.description}</p>
                </div>
              )}

              {selectedMilestone.notes && (
                <div className="info-section">
                  <strong>📝 Ghi chú:</strong>
                  <p>{selectedMilestone.notes}</p>
                </div>
              )}

              {selectedMilestone.tasks && selectedMilestone.tasks.length > 0 && (
                <div className="info-section">
                  <strong>✓ Nhiệm vụ cần làm:</strong>
                  <ul className="tasks-list">
                    {selectedMilestone.tasks.map((task, idx) => (
                      <li key={idx} className={task.completed ? 'completed' : ''}>
                        <input type="checkbox" checked={task.completed} readOnly />
                        <span>{task.title}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-close" onClick={() => setIsModalOpen(false)}>Đóng</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
