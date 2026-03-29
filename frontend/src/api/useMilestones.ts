// useMilestones.ts — Hook để gọi Pregnancy Calendar API
import { useState, useCallback } from 'react';

export interface Milestone {
  id: string;
  week: number;
  title: string;
  category: 'checkup' | 'shopping' | 'preparation' | 'booking' | 'other';
  due_date: string;
  description: string;
  notes: string;
  tasks: Task[];
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string | null;
  name: string;
  is_done: boolean;
  due_date: string | null;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const useMilestones = () => {
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMilestones = useCallback(async (filters?: {
    week?: number;
    status?: string;
    category?: string;
  }) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filters?.week) params.append('week', filters.week.toString());
      if (filters?.status) params.append('status', filters.status);
      if (filters?.category) params.append('category', filters.category);

      const response = await fetch(`${API_BASE_URL}/milestones?${params}`);
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setMilestones(data.milestones);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setLoading(false);
    }
  }, []);

  const createMilestone = useCallback(async (payload: any) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/milestones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Failed to create');
      const newMilestone = await response.json();
      setMilestones([...milestones, newMilestone]);
      return newMilestone;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
      return null;
    } finally {
      setLoading(false);
    }
  }, [milestones]);

  const updateMilestone = useCallback(async (id: string, payload: any) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/milestones/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Failed to update');
      const updated = await response.json();
      setMilestones(milestones.map(m => m.id === id ? updated : m));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
      return null;
    } finally {
      setLoading(false);
    }
  }, [milestones]);

  const deleteMilestone = useCallback(async (id: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/milestones/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete');
      setMilestones(milestones.filter(m => m.id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
      return false;
    } finally {
      setLoading(false);
    }
  }, [milestones]);

  return { milestones, loading, error, fetchMilestones, createMilestone, updateMilestone, deleteMilestone };
};
