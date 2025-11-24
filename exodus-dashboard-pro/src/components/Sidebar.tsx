import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Target, 
  Users, 
  Phone, 
  History, 
  PhoneOff, 
  Bot,
  Settings as SettingsIcon,
  Moon,
  Sun
} from 'lucide-react'
import { useStore } from '../lib/store'
import { motion } from 'framer-motion'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Campaigns', href: '/campaigns', icon: Target },
  { name: 'Leads', href: '/leads', icon: Users },
  { name: 'Live Calls', href: '/live-calls', icon: Phone },
  { name: 'Call History', href: '/call-history', icon: History },
  { name: 'DNC List', href: '/dnc', icon: PhoneOff },
  { name: 'Bots / Agents', href: '/bots', icon: Bot },
  { name: 'Settings', href: '/settings', icon: SettingsIcon },
]

export default function Sidebar() {
  const { darkMode, toggleDarkMode, sidebarOpen } = useStore()

  return (
    <>
      {/* Desktop Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: sidebarOpen ? 0 : -280 }}
        className="hidden md:flex md:flex-col w-[280px] glass-card border-r border-dark-3 m-4 rounded-3xl overflow-hidden"
      >
        {/* Logo */}
        <div className="p-6 border-b border-dark-3/50">
          <h1 className="text-4xl font-black tracking-wide text-[#4A90E2] whitespace-nowrap text-center" style={{ fontFamily: 'Arial, sans-serif', letterSpacing: '0.05em', fontWeight: 900 }}>
            EXODUS AI
          </h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-ios-blue text-white shadow-lg shadow-ios-blue/20'
                    : 'text-ios-gray-2 hover:bg-dark-3 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* AI Network Visualization */}
        <div className="px-4 pb-4">
          <div className="relative w-3/4 mx-auto aspect-square flex items-center justify-center">
            <img 
              src="/ai-network.svg" 
              alt="AI Network" 
              className="w-full h-full object-contain"
            />
          </div>
        </div>

        {/* Dark Mode Toggle */}
        <div className="p-4 border-t border-dark-3/50">
          <button
            onClick={toggleDarkMode}
            className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-dark-3 hover:bg-dark-4 transition-colors"
          >
            <span className="text-sm font-medium">Theme</span>
            <div className="flex items-center gap-2">
              {darkMode ? (
                <Moon className="w-4 h-4 text-ios-blue" />
              ) : (
                <Sun className="w-4 h-4 text-ios-orange" />
              )}
            </div>
          </button>
        </div>
      </motion.aside>
    </>
  )
}
