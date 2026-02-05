import { useState } from 'react'
import { motion } from 'framer-motion'
import {
    Cloud,
    HardDrive,
    Settings,
    Folder,
    RefreshCw,
    Minus,
    Square,
    X,
    ChevronRight
} from 'lucide-react'

// Type definitions for Electron API
declare global {
    interface Window {
        electronAPI?: {
            minimize: () => void
            maximize: () => void
            close: () => void
            getVersion: () => Promise<string>
            getAppName: () => Promise<string>
        }
    }
}

// Sidebar navigation items
const navItems = [
    { id: 'dashboard', icon: Cloud, label: 'Dashboard' },
    { id: 'sync', icon: RefreshCw, label: 'Sincronización' },
    { id: 'drives', icon: HardDrive, label: 'Unidades' },
    { id: 'files', icon: Folder, label: 'Archivos' },
    { id: 'settings', icon: Settings, label: 'Configuración' },
]

function App() {
    const [activeTab, setActiveTab] = useState('dashboard')

    // Window control handlers
    const handleMinimize = () => window.electronAPI?.minimize()
    const handleMaximize = () => window.electronAPI?.maximize()
    const handleClose = () => window.electronAPI?.close()

    return (
        <div className="h-screen w-screen bg-dark-900 flex flex-col overflow-hidden">
            {/* Custom Titlebar */}
            <div className="titlebar h-10 bg-dark-950/80 flex items-center justify-between px-4 border-b border-white/5">
                <div className="flex items-center gap-2">
                    <Cloud className="w-5 h-5 text-accent-400" />
                    <span className="text-sm font-medium text-white/80">VultrDrive Next</span>
                </div>

                <div className="flex gap-1">
                    <button
                        onClick={handleMinimize}
                        className="p-2 hover:bg-white/10 rounded transition-colors"
                    >
                        <Minus className="w-4 h-4 text-white/60" />
                    </button>
                    <button
                        onClick={handleMaximize}
                        className="p-2 hover:bg-white/10 rounded transition-colors"
                    >
                        <Square className="w-3 h-3 text-white/60" />
                    </button>
                    <button
                        onClick={handleClose}
                        className="p-2 hover:bg-red-500/80 rounded transition-colors"
                    >
                        <X className="w-4 h-4 text-white/60" />
                    </button>
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <aside className="w-64 bg-dark-950/50 border-r border-white/5 flex flex-col">
                    <div className="p-4 flex-1">
                        <nav className="space-y-1">
                            {navItems.map((item) => (
                                <motion.button
                                    key={item.id}
                                    whileHover={{ x: 4 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setActiveTab(item.id)}
                                    className={`sidebar-item w-full ${activeTab === item.id ? 'sidebar-item-active' : ''
                                        }`}
                                >
                                    <item.icon className="w-5 h-5" />
                                    <span>{item.label}</span>
                                    {activeTab === item.id && (
                                        <ChevronRight className="w-4 h-4 ml-auto" />
                                    )}
                                </motion.button>
                            ))}
                        </nav>
                    </div>

                    {/* Sidebar Footer - Storage Status */}
                    <div className="p-4 border-t border-white/5">
                        <div className="glass-card">
                            <div className="flex items-center gap-2 mb-2">
                                <Cloud className="w-4 h-4 text-accent-400" />
                                <span className="text-sm text-white/80">Almacenamiento</span>
                            </div>
                            <div className="h-2 bg-dark-800 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: '35%' }}
                                    transition={{ duration: 1, ease: 'easeOut' }}
                                    className="h-full bg-gradient-to-r from-accent-500 to-accent-400 rounded-full"
                                />
                            </div>
                            <p className="text-xs text-white/50 mt-1">3.5 GB de 10 GB usados</p>
                        </div>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 p-6 overflow-auto">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        {activeTab === 'dashboard' && <DashboardView />}
                        {activeTab === 'sync' && <SyncView />}
                        {activeTab === 'drives' && <DrivesView />}
                        {activeTab === 'files' && <FilesView />}
                        {activeTab === 'settings' && <SettingsView />}
                    </motion.div>
                </main>
            </div>
        </div>
    )
}

// Dashboard View Component
function DashboardView() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass-card"
                >
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-green-500/20 rounded-lg">
                            <RefreshCw className="w-5 h-5 text-green-400" />
                        </div>
                        <span className="text-white/80">Estado de Sync</span>
                    </div>
                    <p className="text-2xl font-bold text-white">Activo</p>
                    <p className="text-sm text-white/50">Última sincronización: hace 2 min</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card"
                >
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-accent-500/20 rounded-lg">
                            <HardDrive className="w-5 h-5 text-accent-400" />
                        </div>
                        <span className="text-white/80">Unidades Montadas</span>
                    </div>
                    <p className="text-2xl font-bold text-white">2</p>
                    <p className="text-sm text-white/50">Z: y V: activas</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card"
                >
                    <div className="flex items-center gap-3 mb-3">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                            <Folder className="w-5 h-5 text-blue-400" />
                        </div>
                        <span className="text-white/80">Archivos Sincronizados</span>
                    </div>
                    <p className="text-2xl font-bold text-white">1,247</p>
                    <p className="text-sm text-white/50">Hoy: +23 archivos</p>
                </motion.div>
            </div>

            {/* Recent Activity */}
            <div className="glass-card">
                <h2 className="text-lg font-semibold text-white mb-4">Actividad Reciente</h2>
                <div className="space-y-2">
                    {[
                        { file: 'documento.pdf', action: 'Subido', time: 'hace 2 min' },
                        { file: 'imagen.png', action: 'Sincronizado', time: 'hace 5 min' },
                        { file: 'proyecto.zip', action: 'Subido', time: 'hace 10 min' },
                    ].map((item, i) => (
                        <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-white/5 transition-colors">
                            <div className="flex items-center gap-3">
                                <Folder className="w-4 h-4 text-white/40" />
                                <span className="text-white/80">{item.file}</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-accent-400">{item.action}</span>
                                <span className="text-sm text-white/40">{item.time}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

// Placeholder views
function SyncView() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Sincronización</h1>
            <div className="glass-card">
                <p className="text-white/60">Configuración de sincronización en tiempo real...</p>
            </div>
        </div>
    )
}

function DrivesView() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Unidades</h1>
            <div className="glass-card">
                <p className="text-white/60">Gestión de unidades montadas...</p>
            </div>
        </div>
    )
}

function FilesView() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Archivos</h1>
            <div className="glass-card">
                <p className="text-white/60">Explorador de archivos...</p>
            </div>
        </div>
    )
}

function SettingsView() {
    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Configuración</h1>
            <div className="glass-card">
                <p className="text-white/60">Ajustes de la aplicación...</p>
            </div>
        </div>
    )
}

export default App
