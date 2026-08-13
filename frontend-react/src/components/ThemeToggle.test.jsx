import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ThemeToggle from './ThemeToggle'

describe('ThemeToggle', () => {
  it('shows a moon icon and "switch to dark" label in light mode (REQ-F-02 / AC-1)', () => {
    render(<ThemeToggle theme="light" onToggle={() => {}} />)
    const btn = screen.getByRole('button', { name: /switch to dark mode/i })
    expect(btn).toHaveTextContent('🌙')
  })

  it('shows a sun icon and "switch to light" label in dark mode (REQ-F-02 / AC-1)', () => {
    render(<ThemeToggle theme="dark" onToggle={() => {}} />)
    const btn = screen.getByRole('button', { name: /switch to light mode/i })
    expect(btn).toHaveTextContent('☀️')
  })

  it('calls onToggle when clicked (REQ-F-03 / AC-2)', () => {
    const onToggle = vi.fn()
    render(<ThemeToggle theme="light" onToggle={onToggle} />)

    fireEvent.click(screen.getByRole('button'))

    expect(onToggle).toHaveBeenCalledTimes(1)
  })
})
