import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    RefreshCw,
    Folder,
    Play,
    Square,
    HardDrive,
    Clock,
    CheckCircle2,
    AlertCircle,
    Upload
} from 'lucide-react'
import { GlassCard, Button, Select, Input, StatusBadge } from '../components/ui'

interface SyncLog {
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    message: string
    timestamp: Date
}

interface SyncPanelProps {
    buckets: { name: string }[]
    onBucketSelect?: (bucket: string) => void
}

export default function SyncPanel({ buckets = [] }: SyncPanelProps) {
    const [localPath, setLocalPath] = useState('')
    const [selectedBucket, setSelectedBucket] = useState('')
    const [driveLetter, setDriveLetter] = useState('Z')
    const [isSyncing, setIsSyncing] = useState(false)
    const [isMounted, setIsMounted] = useState(false)
    const [logs, setLogs] = useState<SyncLog[]>([])

    // Available drive letters
    const driveLetters = ['Z', 'Y', 'X', 'W', 'V', 'U', 'T', 'S', 'R', 'Q']
        .map(l => ({ value: l, label: `${l}:` }))

    const addLog = (type: SyncLog['type'], message: string) => {
        setLogs(prev => [...prev, {
            id: Date.now().toString(),
            type,
            message,
            timestamp: new Date()
        }].slice(-50)) // Keep last 50 logs
    }

    const handleBrowse = async () => {
        try {
            const result = await window.electronAPI?.gcp.openDirectory()
            if (result?.success && result.data) {
                setLocalPath(result.data)
                addLog('info', `Carpeta seleccionada: ${result.data}`)
            }
        } catch (e: any) {
            addLog('error', `Error al seleccionar carpeta: ${e.message}`)
        }
    }

    const handleMount = async () => {
        if (!selectedBucket || !driveLetter) return

        addLog('info', `Montando ${selectedBucket} en ${driveLetter}:...`)

        try {
            const result = await window.electronAPI?.gcp.mountBucket(selectedBucket, driveLetter)
            if (result?.success) {
                setIsMounted(true)
                addLog('success', `✓ Bucket montado exitosamente en ${driveLetter}:`)
            } else {
                addLog('error', `Error al montar: ${result?.error || 'Error desconocido'}`)
            }
        } catch (e: any) {
            addLog('error', `Excepción al montar: ${e.message}`)
        }
    }

    const handleUnmount = async () => {
        addLog('info', `Desmontando ${driveLetter}:...`)

        try {
            const result = await window.electronAPI?.gcp.unmountDrive(driveLetter)
            if (result?.success) {
                setIsMounted(false)
                addLog('success', `✓ Unidad ${driveLetter}: desmontada`)
            } else {
                addLog('error', `Error al desmontar: ${result?.error || 'Error desconocido'}`)
            }
        } catch (e: any) {
            addLog('error', `Excepción al desmontar: ${e.message}`)
        }
    }

    const handleToggleSync = async () => {
        if (isSyncing) {
            setIsSyncing(false)
            addLog('info', '⏹ Sincronización detenida')
        } else {
            if (!localPath || !selectedBucket) {
                addLog('error', 'Selecciona una carpeta y un bucket primero')
                return
            }

            addLog('info', `Iniciando sincronización...`)
            try {
                const result = await window.electronAPI?.gcp.startSync(localPath, selectedBucket)
                if (result?.success) {
                    setIsSyncing(true)
                    addLog('success', `▶ Sincronización activa: ${selectedBucket}`)
                } else {
                    addLog('error', `Error al iniciar sync: ${result?.error || 'Error desconocido'}`)
                }
            } catch (e: any) {
                addLog('error', `Excepción en sync: ${e.message}`)
            }
        }
    }

    const getLogIcon = (type: SyncLog['type']) => {
        switch (type) {
            case 'success': return <CheckCircle2 className="w-4 h-4 text-green-400" />
            case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-400" />
            case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />
            default: return <Clock className="w-4 h-4 text-white/40" />
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <RefreshCw className={`w-7 h-7 text-accent-400 ${isSyncing ? 'animate-spin' : ''}`} />
                        Sincronización Automática
                    </h1>
                    <p className="text-white/50 mt-1">Sincroniza carpetas locales con GCP Storage</p>
                </div>

                <StatusBadge
                    status={isSyncing ? 'active' : 'inactive'}
                    label={isSyncing ? 'Sincronizando' : 'Detenido'}
                    pulse={isSyncing}
                />
            </div>

            {/* Configuration */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Source & Destination */}
                <GlassCard>
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Folder className="w-5 h-5 text-accent-400" />
                        Configuración
                    </h2>

                    <div className="space-y-4">
                        {/* Local Path */}
                        <div>
                            <label className="block text-sm text-white/60 mb-2">Carpeta Local</label>
                            <div className="flex gap-2">
                                <Input
                                    value={localPath}
                                    onChange={setLocalPath}
                                    placeholder="C:\Users\MiCarpeta"
                                    className="flex-1"
                                    disabled={isSyncing}
                                />
                                <Button variant="secondary" onClick={handleBrowse} disabled={isSyncing}>
                                    <Folder className="w-4 h-4" />
                                </Button>
                            </div>
                        </div>

                        {/* Bucket Selection */}
                        <div>
                            <label className="block text-sm text-white/60 mb-2">Bucket GCP</label>
                            <Select
                                value={selectedBucket}
                                onChange={setSelectedBucket}
                                options={buckets.map(b => ({ value: b.name, label: b.name }))}
                                placeholder="Selecciona un bucket..."
                                disabled={isSyncing}
                            />
                        </div>

                        {/* Sync Button */}
                        <Button
                            onClick={handleToggleSync}
                            variant={isSyncing ? 'danger' : 'primary'}
                            className="w-full"
                            disabled={!localPath || !selectedBucket}
                        >
                            {isSyncing ? (
                                <>
                                    <Square className="w-4 h-4" />
                                    Detener Sincronización
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4" />
                                    Iniciar Sincronización
                                </>
                            )}
                        </Button>
                    </div>
                </GlassCard>

                {/* Mount Drive */}
                <GlassCard>
                    <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <HardDrive className="w-5 h-5 text-blue-400" />
                        Montar como Unidad
                    </h2>

                    <div className="space-y-4">
                        {/* Drive Letter */}
                        <div>
                            <label className="block text-sm text-white/60 mb-2">Letra de Unidad</label>
                            <Select
                                value={driveLetter}
                                onChange={setDriveLetter}
                                options={driveLetters}
                                disabled={isMounted}
                            />
                        </div>

                        {/* Mount Status */}
                        <div className="p-3 rounded-lg bg-white/5">
                            <div className="flex items-center justify-between">
                                <span className="text-white/70">Estado:</span>
                                <StatusBadge
                                    status={isMounted ? 'active' : 'inactive'}
                                    label={isMounted ? `Montado en ${driveLetter}:` : 'No montado'}
                                />
                            </div>
                        </div>

                        {/* Mount/Unmount Buttons */}
                        <div className="flex gap-2">
                            <Button
                                onClick={handleMount}
                                disabled={isMounted || !selectedBucket}
                                className="flex-1"
                            >
                                <HardDrive className="w-4 h-4" />
                                Montar
                            </Button>
                            <Button
                                variant="secondary"
                                onClick={handleUnmount}
                                disabled={!isMounted}
                                className="flex-1"
                            >
                                Desmontar
                            </Button>
                        </div>

                        {isMounted && (
                            <Button variant="ghost" className="w-full">
                                <Folder className="w-4 h-4" />
                                Abrir en Explorador
                            </Button>
                        )}
                    </div>
                </GlassCard>
            </div>

            {/* Activity Log */}
            <GlassCard>
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5 text-white/60" />
                    Actividad Reciente
                </h2>

                <div className="max-h-64 overflow-y-auto space-y-1">
                    {logs.length === 0 ? (
                        <p className="text-white/40 text-center py-8">No hay actividad reciente</p>
                    ) : (
                        logs.slice().reverse().map((log) => (
                            <motion.div
                                key={log.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5"
                            >
                                {getLogIcon(log.type)}
                                <span className="flex-1 text-white/80 text-sm">{log.message}</span>
                                <span className="text-xs text-white/30">
                                    {log.timestamp.toLocaleTimeString()}
                                </span>
                            </motion.div>
                        ))
                    )}
                </div>
            </GlassCard>
        </div>
    )
}
