import { useState, useEffect, useCallback } from 'react'

const LIGHT = 'light'
const DARK = 'dark'

// No persistence by design (REQ-F-05): always starts in light mode (REQ-F-04)
// and resets on every fresh load/session.
export function useTheme() {
  const [theme, setTheme] = useState(LIGHT)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === LIGHT ? DARK : LIGHT))
  }, [])

  return { theme, toggleTheme }
}
