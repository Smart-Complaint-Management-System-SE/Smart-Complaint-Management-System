import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { StatusBadge } from '../components/StatusBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { ComplaintTimeline } from '../components/ComplaintTimeline';

describe('StatusBadge Component', () => {
  it('renders Pending status badge correctly', () => {
    const { container } = render(<StatusBadge status="Pending" />);
    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('bg-amber-50');
  });

  it('renders In Progress status badge correctly', () => {
    const { container } = render(<StatusBadge status="In Progress" />);
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('bg-blue-50');
  });

  it('renders Resolved status badge correctly', () => {
    const { container } = render(<StatusBadge status="Resolved" />);
    expect(screen.getByText('Resolved')).toBeInTheDocument();
    expect(container.firstChild).toHaveClass('bg-emerald-50');
  });
});

describe('CategoryBadge Component', () => {
  it('renders Academic category', () => {
    render(<CategoryBadge category="Academic" />);
    expect(screen.getByText('Academic')).toBeInTheDocument();
  });

  it('renders Hostel category', () => {
    render(<CategoryBadge category="Hostel" />);
    expect(screen.getByText('Hostel')).toBeInTheDocument();
  });

  it('renders Technical category', () => {
    render(<CategoryBadge category="Technical" />);
    expect(screen.getByText('Technical')).toBeInTheDocument();
  });
});

describe('ComplaintTimeline Component', () => {
  it('renders 3 steps in timeline', () => {
    render(
      <ComplaintTimeline
        status="In Progress"
        createdAt="2026-10-15T10:00:00Z"
        updatedAt="2026-10-16T12:00:00Z"
      />
    );
    expect(screen.getByText('Submitted')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Resolved')).toBeInTheDocument();
    expect(screen.getByText('Current')).toBeInTheDocument();
  });
});
