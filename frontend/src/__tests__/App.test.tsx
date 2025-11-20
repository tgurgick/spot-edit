/**
 * Tests for App component
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders the app header', () => {
    render(<App />)
    expect(screen.getByText('Spot Edit')).toBeInTheDocument()
    expect(screen.getByText('AI-Powered Document Editor')).toBeInTheDocument()
  })

  it('renders the welcome message', () => {
    render(<App />)
    expect(screen.getByText('Welcome to Spot Edit')).toBeInTheDocument()
    expect(screen.getByText('Frontend is ready for development')).toBeInTheDocument()
  })

  it('has the correct page structure', () => {
    const { container } = render(<App />)
    expect(container.querySelector('header')).toBeInTheDocument()
    expect(container.querySelector('main')).toBeInTheDocument()
  })
})
