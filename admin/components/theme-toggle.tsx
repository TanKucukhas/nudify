'use client'

import { Dropdown, DropdownButton, DropdownItem, DropdownLabel, DropdownMenu } from '@/components/dropdown'
import { CheckIcon, ComputerDesktopIcon, MoonIcon, SunIcon } from '@heroicons/react/16/solid'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  const getCurrentIcon = () => {
    switch (theme) {
      case 'light':
        return <SunIcon />
      case 'dark':
        return <MoonIcon />
      default:
        return <ComputerDesktopIcon />
    }
  }

  return (
    <Dropdown>
      <DropdownButton plain aria-label="Theme">
        {getCurrentIcon()}
      </DropdownButton>
      <DropdownMenu anchor="bottom end">
        <DropdownItem onClick={() => setTheme('light')}>
          <SunIcon />
          <DropdownLabel>Light</DropdownLabel>
          {theme === 'light' && <CheckIcon />}
        </DropdownItem>
        <DropdownItem onClick={() => setTheme('dark')}>
          <MoonIcon />
          <DropdownLabel>Dark</DropdownLabel>
          {theme === 'dark' && <CheckIcon />}
        </DropdownItem>
        <DropdownItem onClick={() => setTheme('system')}>
          <ComputerDesktopIcon />
          <DropdownLabel>System</DropdownLabel>
          {theme === 'system' && <CheckIcon />}
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  )
}
