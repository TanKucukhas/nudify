'use client'

import {
  Sidebar,
  SidebarBody,
  SidebarHeader,
  SidebarItem,
  SidebarLabel,
  SidebarSection,
} from '@/components/sidebar'
import { SidebarLayout } from '@/components/sidebar-layout'
import {
  HomeIcon,
  SparklesIcon,
  Square3Stack3DIcon,
  PhotoIcon,
  CpuChipIcon,
} from '@heroicons/react/20/solid'
import { usePathname } from 'next/navigation'

export function ApplicationLayout({ children }: { children: React.ReactNode }) {
  let pathname = usePathname()

  return (
    <SidebarLayout
      sidebar={
        <Sidebar>
          <SidebarHeader>
            <SidebarItem href="/">
              <CpuChipIcon className="size-6" />
              <SidebarLabel className="font-bold text-lg">AI Image Lab</SidebarLabel>
            </SidebarItem>
          </SidebarHeader>

          <SidebarBody>
            <SidebarSection>
              <SidebarItem href="/" current={pathname === '/'}>
                <HomeIcon />
                <SidebarLabel>Dashboard</SidebarLabel>
              </SidebarItem>
              <SidebarItem href="/generate" current={pathname === '/generate'}>
                <SparklesIcon />
                <SidebarLabel>Generate</SidebarLabel>
              </SidebarItem>
              <SidebarItem href="/batch" current={pathname === '/batch'}>
                <Square3Stack3DIcon />
                <SidebarLabel>Batch</SidebarLabel>
              </SidebarItem>
              <SidebarItem href="/gallery" current={pathname.startsWith('/gallery')}>
                <PhotoIcon />
                <SidebarLabel>Gallery</SidebarLabel>
              </SidebarItem>
              <SidebarItem href="/models" current={pathname.startsWith('/models')}>
                <CpuChipIcon />
                <SidebarLabel>Models</SidebarLabel>
              </SidebarItem>
            </SidebarSection>
          </SidebarBody>
        </Sidebar>
      }
    >
      {children}
    </SidebarLayout>
  )
}
