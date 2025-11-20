import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Target, Phone, Bot } from 'lucide-react'
import { motion } from 'framer-motion'

const mobileNav = [
  { name: 'Home', href: '/', icon: LayoutDashboard },
  { name: 'Campaigns', href: '/campaigns', icon: Target },
  { name: 'Live', href: '/live-calls', icon: Phone },
  { name: 'Bots', href: '/bots', icon: Bot },
]

export default function MobileNav() {
  return (
    <motion.nav
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="md:hidden fixed bottom-0 left-0 right-0 glass-card border-t border-dark-3 px-2 py-3 safe-area-bottom z-50"
    >
      <div className="flex items-center justify-around max-w-md mx-auto">
        {mobileNav.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all ${
                isActive
                  ? 'text-ios-blue'
                  : 'text-ios-gray-2 active:scale-95'
              }`
            }
          >
            <item.icon className="w-6 h-6" />
            <span className="text-xs font-medium">{item.name}</span>
          </NavLink>
        ))}
      </div>
    </motion.nav>
  )
}
