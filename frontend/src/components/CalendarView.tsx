// CalendarView.tsx — Main pregnancy calendar view
import React, { useState, useEffect } from 'react';
import { useMilestones, Milestone } from '../api/useMilestones';
import './CalendarView.css';

export const CalendarView: React.FC<{ onNavigateToShopping?: () => void }> = ({ onNavigateToShopping }) => {
  const { milestones, loading, fetchMilestones } = useMilestones();
  const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchMilestones();
  }, []);

  const handleSelectMilestone = (milestone: Milestone) => {
    setSelectedMilestone(milestone);
    setIsModalOpen(true);
  };

  return (
    <div className="calendar-view">
      <h1>📅 Lịch Thai Kỳ</h1>
      
      {loading && <p>Đang tải...</p>}
      
      <div className="milestones-grid">
        {milestones.map(m => (
          <div key={m.id} className="milestone-card" onClick={() => handleSelectMilestone(m)}>
            <h3>{m.title}</h3>
            <p>Tuần {m.week}</p>
            <p>{m.description}</p>
            <span className={`status status-${m.status}`}>{m.status}</span>
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
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{selectedMilestone.title}</h2>
            <p><strong>Tuần:</strong> {selectedMilestone.week}</p>
            <p><strong>Mô tả:</strong> {selectedMilestone.description}</p>
            <p><strong>Ghi chú:</strong> {selectedMilestone.notes}</p>
            <button onClick={() => setIsModalOpen(false)}>Đóng</button>
          </div>
        </div>
      )}
    </div>
  );
};
