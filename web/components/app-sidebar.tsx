"use client"

import * as React from "react"
import {
  Monitor,
  Grid3x3,
  Settings2,
  Activity,
  Zap,
  BookOpen,
  Github,
  FileText,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: Monitor,
      isActive: true,
      items: [
        {
          title: "Overview",
          url: "/dashboard",
        },
        {
          title: "System Status",
          url: "/dashboard#status",
        },
      ],
    },
    {
      title: "Widgets",
      url: "/dashboard/widgets",
      icon: Grid3x3,
      items: [
        {
          title: "Clock",
          url: "/dashboard/widgets#clock",
        },
        {
          title: "Weather",
          url: "/dashboard/widgets#weather",
        },
        {
          title: "Calendar",
          url: "/dashboard/widgets#calendar",
        },
      ],
    },
    {
      title: "Settings",
      url: "/dashboard/settings",
      icon: Settings2,
      items: [
        {
          title: "Display",
          url: "/dashboard/settings#display",
        },
        {
          title: "Bluetooth",
          url: "/dashboard/settings#bluetooth",
        },
        {
          title: "Cloud Sync",
          url: "/dashboard/settings#cloud",
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Documentation",
      url: "https://github.com/postysh/lumy",
      icon: BookOpen,
    },
    {
      title: "GitHub",
      url: "https://github.com/postysh/lumy",
      icon: Github,
    },
  ],
  projects: [
    {
      name: "Activity Logs",
      url: "/dashboard/logs",
      icon: Activity,
    },
    {
      name: "Quick Actions",
      url: "/dashboard#actions",
      icon: Zap,
    },
    {
      name: "API Docs",
      url: "/dashboard/api",
      icon: FileText,
    },
  ],
}

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  user: {
    id: string
    email?: string
  }
}

export function AppSidebar({ user, ...props }: AppSidebarProps) {
  const userForNav = {
    name: user.email?.split('@')[0] || 'User',
    email: user.email || 'user@lumy.local',
    avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${user.email}`,
  }

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/dashboard">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Monitor className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Lumy</span>
                  <span className="truncate text-xs">E-Paper Display</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={userForNav} />
      </SidebarFooter>
    </Sidebar>
  )
}
