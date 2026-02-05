import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Cloud,
    Database,
    Folder,
    Key,
    RefreshCw,
    Check,
    AlertCircle,
    ChevronRight,
    UploadCloud,
    FileText,
    CheckCircle2,
    ArrowLeft,
    HardDrive,
    Search,
    Grid,
    List as ListIcon
} from 'lucide-react'
import { GlassCard, Button, Input, Toast } from '../components/ui'

// Types
interface Credential {
    path: string
    project_id: string
    client_email: string
}


interface GCSObject {
    name: string
    size: number
    updated: string
    contentType: string
}

type SyncStatus = 'pending' | 'uploading' | 'synced'

// Status Icon Component
function StatusIcon({ status }: { status?: SyncStatus }) {
    if (!status) return null

    return (
        <AnimatePresence mode="wait">
            <motion.div
                key={status}
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 1.5, opacity: 0 }}
                transition={{ duration: 0.2 }}
            >
                {status === 'pending' && (
                    <div className="w-2 h-2 rounded-full bg-zinc-500 animate-pulse" />
                )}
                {status === 'uploading' && (
                    <RefreshCw className="text-indigo-400 animate-spin" size={14} />
                )}
                {status === 'synced' && (
                    <Cloud className="text-indigo-400 fill-indigo-400/20" size={14} />
                )}
            </motion.div>
        </AnimatePresence>
    )
}

// Sub-component: File Explorer (Full View)
function FileExplorer({
    bucket,
    onClose,
    electronAPI,
    onToast,
    syncStatuses
}: {
    bucket: string,
    onClose: () => void,
    electronAPI: any,
    onToast: (msg: string, type: 'success' | 'error' | 'info') => void,
    syncStatuses: Record<string, SyncStatus>
}) {
    const [objects, setObjects] = useState<GCSObject[]>([])
    const [loading, setLoading] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const [viewType, setViewType] = useState<'list' | 'grid'>('list')
    const [currentPrefix] = useState('')
    const [actionLoading, setActionLoading] = useState(false)

    useEffect(() => {
        loadObjects(bucket, currentPrefix)
    }, [bucket, currentPrefix])

    const loadObjects = async (bucketName: string, prefix: string) => {
        setLoading(true)
        setObjects([]) // Clear immediately to avoid stale data
        try {
            const result = await electronAPI?.gcp.listObjects(bucketName, prefix)
            if (result?.success) {
                setObjects(result.data)
            }
        } catch (e) {
            console.error(e)
            onToast('Error al cargar objetos', 'error')
        } finally {
            setLoading(false)
        }
    }

    const handleUploadFile = async () => {
        setActionLoading(true)
        try {
            const res = await electronAPI.gcp.uploadFile(bucket, currentPrefix)
            if (res.success) {
                onToast('Archivo subido correctamente', 'success')
                await loadObjects(bucket, currentPrefix)
            } else if (!res.cancelled) {
                onToast(res.error || 'Error al subir archivo', 'error')
            }
        } catch (e: any) {
            onToast(e.message, 'error')
        } finally {
            setActionLoading(false)
        }
    }

    const handleUploadFolder = async () => {
        setActionLoading(true)
        try {
            const res = await electronAPI.gcp.uploadFolder(bucket, currentPrefix)
            if (res.success) {
                onToast(`Carpeta subida (${res.count} archivos)`, 'success')
                await loadObjects(bucket, currentPrefix)
            } else if (!res.cancelled) {
                onToast(res.error || 'Error al subir carpeta', 'error')
            }
        } catch (e: any) {
            onToast(e.message, 'error')
        } finally {
            setActionLoading(false)
        }
    }

    const handleStartSync = async () => {
        try {
            const dirRes = await electronAPI.gcp.openDirectory()
            if (dirRes.success && dirRes.data) {
                setActionLoading(true)
                // Optimistic UI: notify start immediately
                onToast('Iniciando sincronización en segundo plano...', 'info')

                const syncRes = await electronAPI.gcp.startSync(dirRes.data, bucket)
                if (syncRes.success) {
                    onToast(`Sincronización activa: ${dirRes.data}`, 'success')
                } else {
                    onToast(syncRes.error || 'Error al iniciar sync', 'error')
                }
            }
        } catch (e: any) {
            onToast(e.message, 'error')
        } finally {
            setActionLoading(false)
        }
    }

    const filteredObjects = objects.filter(obj =>
        obj.name.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="space-y-4 h-full flex flex-col">
            <div className="flex flex-col gap-4 mb-2">
                {/* Header Top */}
                <div className="flex items-center gap-4">
                    <Button variant="ghost" onClick={onClose} size="sm">
                        <ArrowLeft size={20} />
                    </Button>
                    <div>
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Database className="text-indigo-400" size={20} />
                            {bucket}
                        </h2>
                        <p className="text-xs text-white/50">{objects.length} archivos • {currentPrefix || 'Raíz'}</p>
                    </div>
                    <div className="ml-auto flex items-center gap-2">
                        <Button variant="secondary" size="sm" onClick={() => loadObjects(bucket, currentPrefix)} loading={loading}>
                            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        </Button>
                    </div>
                </div>

                {/* Toolbar */}
                <div className="flex items-center gap-3 bg-white/5 p-2 rounded-lg border border-white/10">
                    <Button size="sm" variant="secondary" onClick={handleUploadFile} disabled={actionLoading}>
                        <UploadCloud size={16} className="mr-2" />
                        Subir Archivo
                    </Button>
                    <Button size="sm" variant="secondary" onClick={handleUploadFolder} disabled={actionLoading}>
                        <Folder size={16} className="mr-2" />
                        Subir Carpeta
                    </Button>
                    <div className="h-6 w-px bg-white/20 mx-1" />
                    <Button size="sm" variant="ghost" onClick={handleStartSync} disabled={actionLoading} className="text-indigo-300 hover:text-indigo-200 hover:bg-indigo-500/20">
                        <RefreshCw size={16} className="mr-2" />
                        Sincronizar Carpeta Local
                    </Button>

                    <div className="ml-auto flex items-center gap-2">
                        <div className="relative w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" size={14} />
                            <Input
                                value={searchTerm}
                                onChange={setSearchTerm}
                                placeholder="Buscar archivos..."
                                className="pl-9 h-9 text-sm border-0 bg-black/20 focus:bg-black/40"
                            />
                        </div>
                        <div className="flex bg-black/20 rounded-lg p-1">
                            <button
                                onClick={() => setViewType('list')}
                                className={`p-1.5 rounded ${viewType === 'list' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white/70'}`}
                            >
                                <ListIcon size={16} />
                            </button>
                            <button
                                onClick={() => setViewType('grid')}
                                className={`p-1.5 rounded ${viewType === 'grid' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white/70'}`}
                            >
                                <Grid size={16} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <GlassCard className="flex-1 overflow-hidden p-0 border-0 bg-black/20">
                <div className="h-full overflow-y-auto custom-scrollbar p-4">
                    {loading && objects.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-white/40 gap-3">
                            <RefreshCw className="animate-spin" size={32} />
                            <p>Cargando contenidos...</p>
                        </div>
                    ) : filteredObjects.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-white/30 gap-3">
                            <Folder size={48} className="opacity-20" />
                            <p>Carpeta vacía o sin resultados</p>
                        </div>
                    ) : (
                        viewType === 'list' ? (
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-white/40 uppercase border-b border-white/10">
                                    <tr>
                                        <th className="px-4 py-3 font-medium">Nombre</th>
                                        <th className="px-4 py-3 font-medium">Tamaño</th>
                                        <th className="px-4 py-3 font-medium">Tipo</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {filteredObjects.map((obj, i) => (
                                        <tr key={i} className="hover:bg-white/5 group transition-colors">
                                            <td className="px-4 py-3 flex items-center gap-3 text-white/80 group-hover:text-white">
                                                <div className="relative">
                                                    <FileText size={16} className="text-indigo-400" />
                                                    <div className="absolute -bottom-1 -right-1">
                                                        <StatusIcon status={syncStatuses[obj.name]} />
                                                    </div>
                                                </div>
                                                <span className="truncate max-w-[300px]">{obj.name}</span>
                                            </td>
                                            <td className="px-4 py-3 text-white/50 font-mono text-xs">
                                                {(obj.size / 1024).toFixed(1)} KB
                                            </td>
                                            <td className="px-4 py-3 text-white/40 text-xs truncate max-w-[150px]">
                                                {obj.contentType || 'application/octet-stream'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                {filteredObjects.map((obj, i) => (
                                    <motion.div
                                        key={i}
                                        whileHover={{ scale: 1.02 }}
                                        className="p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 hover:border-white/20 transition-all flex flex-col items-center gap-3 text-center cursor-pointer group"
                                    >
                                        <div className="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center text-indigo-400 group-hover:text-white group-hover:bg-indigo-500 transition-all relative">
                                            <FileText size={24} />
                                            <div className="absolute top-0 right-0 p-1">
                                                <StatusIcon status={syncStatuses[obj.name]} />
                                            </div>
                                        </div>
                                        <div className="min-w-0 w-full">
                                            <p className="text-xs font-medium truncate text-white/80 group-hover:text-white mb-1">{obj.name}</p>
                                            <p className="text-[10px] text-white/40">{(obj.size / 1024).toFixed(1)} KB</p>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        )
                    )}
                </div>
            </GlassCard>
        </div>
    )
}

// Log Terminal Component
function LogTerminal({ logs, onClose, clearLogs }: { logs: string[], onClose: () => void, clearLogs: () => void }) {
    const scrollRef = React.useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [logs])

    return (
        <GlassCard className="fixed bottom-0 left-0 right-0 h-48 m-4 border-t border-white/10 flex flex-col shadow-2xl z-40 bg-black/90 backdrop-blur-xl">
            <div className="flex items-center justify-between p-2 border-b border-white/10 bg-white/5">
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <h3 className="text-xs font-mono uppercase text-white/60">Terminal de Sincronización</h3>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={clearLogs} className="p-1 hover:bg-white/10 rounded text-white/40 hover:text-white" title="Limpiar logs">
                        <RefreshCw size={12} />
                    </button>
                    <button onClick={onClose} className="p-1 hover:bg-white/10 rounded text-white/40 hover:text-white">
                        <ChevronRight className="rotate-90" size={14} />
                    </button>
                </div>
            </div>
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 font-mono text-xs text-green-400/80 space-y-1">
                {logs.length === 0 && <span className="text-white/20 italic">Esperando actividad...</span>}
                {logs.map((log, i) => (
                    <div key={i} className="break-all border-l-2 border-transparent hover:border-white/20 pl-2">
                        <span className="text-white/30 mr-2">[{new Date().toLocaleTimeString()}]</span>
                        {log}
                    </div>
                ))}
            </div>
        </GlassCard>
    )
}

export default function GCPPage() {
    const [credentials, setCredentials] = useState<Credential[]>([])
    const [selectedCred, setSelectedCred] = useState('')
    const [buckets, setBuckets] = useState<any[]>([])
    const [isAuthenticated, setIsAuthenticated] = useState(false)

    // Split loading states correctly
    const [authLoading, setAuthLoading] = useState(false)
    const [dataLoading, setDataLoading] = useState(false)

    const [error, setError] = useState<string | null>(null)

    // View Management
    const [currentView, setCurrentView] = useState<'dashboard' | 'explorer'>('dashboard')
    const [activeExplorerBucket, setActiveExplorerBucket] = useState<string | null>(null)

    // Inline Preview State (Dashboard)
    const [selectedPreviewBucket, setSelectedPreviewBucket] = useState<string | null>(null)
    const [previewObjects, setPreviewObjects] = useState<any[]>([])

    // Notifications
    const [toasts, setToasts] = useState<{ id: string, message: string, type: 'success' | 'error' | 'info' }[]>([])

    // Logs
    const [logs, setLogs] = useState<string[]>([])
    const [showLogs, setShowLogs] = useState(false)

    const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
        const id = Math.random().toString(36).substr(2, 9)
        setToasts(prev => [...prev, { id, message, type }])
    }

    const removeToast = (id: string) => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }

    useEffect(() => {
        loadCredentials()
        checkSession()

        // Subscribe to logs
        const cleanup = window.electronAPI?.gcp.onLog((msg) => {
            setLogs(prev => [...prev, msg])
            setShowLogs(true) // Auto-show logs on activity
        })

        return () => {
            if (cleanup) cleanup()
        }
    }, [])

    const checkSession = async () => {
        try {
            const result = await window.electronAPI?.gcp.loadSession()
            if (result?.success && result.data.lastCredentialPath) {
                console.log('Restoring session:', result.data.lastCredentialPath)
                setSelectedCred(result.data.lastCredentialPath)
                handleAuthenticate(result.data.lastCredentialPath)
            }
        } catch (e) {
            console.error('Session restore failed', e)
        }
    }

    const loadCredentials = async () => {
        try {
            const result = await window.electronAPI?.gcp.listCredentials()
            if (result?.success) {
                setCredentials(result.data)
                // If no session restored yet and only 1 cred, select it
                if (result.data.length === 1 && !selectedCred) {
                    setSelectedCred(result.data[0].path)
                }
            } else {
                setError(result?.error || 'Error al listar credenciales')
            }
        } catch (e: any) {
            setError(e.message)
        }
    }

    const handleUploadCredentials = async () => {
        try {
            const result = await window.electronAPI?.gcp.uploadCredentials()
            if (result?.success) {
                loadCredentials()
                setCredentials(prev => [...prev, { path: result.data!, project_id: 'New', client_email: 'New' }])
                setSelectedCred(result.data!)
                showToast('Credencial importada correctamente', 'success')
            }
        } catch (e: any) {
            setError(e.message)
            showToast('Error al importar credencial', 'error')
        }
    }

    const handleAuthenticate = async (credPathOverride?: string) => {
        const credToUse = credPathOverride || selectedCred
        if (!credToUse) return

        setAuthLoading(true)
        setError(null)

        try {
            const result = await window.electronAPI?.gcp.authenticate(credToUse)
            if (result?.success && result.data.authenticated) {
                setIsAuthenticated(true)
                const bucketList = result.data.buckets || []
                const formattedBuckets = bucketList.map((b: any) =>
                    typeof b === 'string' ? { name: b, location: 'UNKNOWN', storage_class: 'STANDARD' } : b
                )
                setBuckets(formattedBuckets)

                if (formattedBuckets.length === 0) {
                    const listResult = await window.electronAPI?.gcp.listBuckets()
                    if (listResult?.success) setBuckets(listResult.data)
                }

                if (!credPathOverride) {
                    showToast('Conectado a Google Cloud Platform', 'success')
                }

            } else {
                const errMsg = result?.error || 'Error de autenticación'
                setError(errMsg)
                showToast(errMsg, 'error')
            }
        } catch (e: any) {
            setError(e.message)
            showToast(e.message, 'error')
        } finally {
            setAuthLoading(false)
        }
    }

    const [hasAutoSynced, setHasAutoSynced] = useState(false)

    useEffect(() => {
        if (isAuthenticated && buckets.length > 0 && !hasAutoSynced) {
            handleAutoSync()
        }
    }, [isAuthenticated, buckets, hasAutoSynced])

    const handleAutoSync = async () => {
        setHasAutoSynced(true)
        try {
            const desktopPath = await window.electronAPI.gcp.getDesktopPath()
            const targetBucket = buckets[0].name

            showToast(`🚀 Iniciando AUTO-SYNC del Escritorio a ${targetBucket}...`, 'info')

            // Auto open logs
            setShowLogs(true)

            const syncRes = await window.electronAPI.gcp.startSync(desktopPath, targetBucket)
            if (syncRes.success) {
                showToast(`Sincronización activa: ${desktopPath}`, 'success')
            } else {
                showToast(syncRes.error || 'Error al iniciar sync automática', 'error')
            }
        } catch (e: any) {
            console.error("Auto sync failed", e)
            showToast("Falló la auto-sincronización", 'error')
        }
    }

    const handlePreviewClick = async (bucketName: string) => {
        if (selectedPreviewBucket === bucketName) {
            setSelectedPreviewBucket(null) // Toggle off
            return
        }

        setSelectedPreviewBucket(bucketName)
        setPreviewObjects([]) // Clear STALE data immediately

        setDataLoading(true)
        try {
            const result = await window.electronAPI?.gcp.listObjects(bucketName, '')
            if (result?.success) {
                setPreviewObjects(result.data || [])
            }
        } catch (e) {
            console.error(e)
        } finally {
            setDataLoading(false)
        }
    }

    const openExplorer = (bucketName: string) => {
        setActiveExplorerBucket(bucketName)
        setCurrentView('explorer')
    }

    const getFileName = (pathStr: string) => {
        return pathStr.split(/[\\/]/).pop() || pathStr
    }

    // Render Logic
    if (currentView === 'explorer' && activeExplorerBucket) {
        return (
            <>
                <AnimatePresence mode="wait">
                    <motion.div
                        key="explorer"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="h-[calc(100vh-100px)]"
                    >
                        <FileExplorer
                            bucket={activeExplorerBucket}
                            onClose={() => setCurrentView('dashboard')}
                            electronAPI={window.electronAPI}
                            onToast={showToast}
                            syncStatuses={syncStatuses}
                        />
                    </motion.div>
                </AnimatePresence>

                {/* Toast Container */}
                <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
                    <AnimatePresence>
                        {toasts.map(toast => (
                            <div key={toast.id} className="pointer-events-auto">
                                <Toast
                                    message={toast.message}
                                    type={toast.type}
                                    onClose={() => removeToast(toast.id)}
                                />
                            </div>
                        ))}
                    </AnimatePresence>
                </div>

                {/* Log Terminal Overlay */}
                <AnimatePresence>
                    {showLogs && (
                        <motion.div
                            initial={{ y: 200, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: 200, opacity: 0 }}
                        >
                            <LogTerminal
                                logs={logs}
                                onClose={() => setShowLogs(false)}
                                clearLogs={() => setLogs([])}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
            </>
        )
    }

    return (
        <div className="space-y-6 relative min-h-screen">
            <header>
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold mb-2 text-white flex items-center gap-2">
                            <Cloud className="text-indigo-400" />
                            Google Cloud Storage
                        </h2>
                        <p className="text-white/60">Gestiona tus buckets y sincronización</p>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => setShowLogs(!showLogs)} className={showLogs ? 'bg-white/10' : ''}>
                        <FileText size={16} className="mr-2" />
                        Logs
                    </Button>
                </div>
            </header>

            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg flex items-center gap-2"
                    >
                        <AlertCircle size={20} />
                        <span>{error}</span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Credential Card */}
            <GlassCard className="p-6">
                <div className="flex items-center gap-4 mb-4">
                    <div className={`p-3 rounded-lg ${isAuthenticated ? 'bg-green-500/20 text-green-400' : 'bg-indigo-500/20 text-indigo-400'}`}>
                        {isAuthenticated ? <Check size={24} /> : <Key size={24} />}
                    </div>
                    <div>
                        <h3 className="text-lg font-medium">Autenticación</h3>
                        <p className="text-sm text-white/60">Selecciona tus credenciales de servicio</p>
                    </div>
                    <div className="ml-auto">
                        <Button variant="secondary" onClick={handleUploadCredentials} disabled={authLoading}>
                            <UploadCloud size={16} className="mr-2" />
                            Importar Credencial
                        </Button>
                    </div>
                </div>

                <div className="space-y-4">
                    {credentials.length === 0 ? (
                        <div className="text-center py-8 text-white/40 border-2 border-dashed border-white/10 rounded-lg">
                            <Folder size={48} className="mx-auto mb-2 opacity-50" />
                            <p>No se encontraron credenciales</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {credentials.map((cred) => (
                                <div
                                    key={cred.path}
                                    onClick={() => setSelectedCred(cred.path)}
                                    className={`p-4 rounded-lg border cursor-pointer transition-all ${selectedCred === cred.path
                                        ? 'bg-indigo-500/20 border-indigo-500/50'
                                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="font-medium text-sm text-indigo-300">{getFileName(cred.path)}</p>
                                            <p className="text-xs text-white/40 mt-1">{cred.client_email}</p>
                                        </div>
                                        <div className={`w-4 h-4 rounded-full border ${selectedCred === cred.path ? 'border-indigo-500 bg-indigo-500' : 'border-white/30'
                                            }`} />
                                    </div>

                                    {selectedCred === cred.path && isAuthenticated && (
                                        <div className="absolute right-14 top-1/2 -translate-y-1/2">
                                            <CheckCircle2 className="text-green-500" size={20} />
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    <Button
                        className="w-full"
                        disabled={!selectedCred || authLoading}
                        onClick={() => handleAuthenticate()}
                    >
                        {authLoading ? <RefreshCw className="animate-spin mr-2" /> : <Cloud className="mr-2" />}
                        {isAuthenticated ? 'Re-conectar a GCP' : 'Conectar a GCP'}
                    </Button>
                </div>
            </GlassCard>

            {/* Buckets Section */}
            <AnimatePresence>
                {isAuthenticated && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <GlassCard className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <HardDrive className="text-indigo-400" />
                                    <h3 className="text-lg font-medium">Buckets</h3>
                                    <span className="text-sm text-white/40">{buckets.length} buckets disponibles</span>
                                </div>
                                <Button variant="ghost" size="sm" onClick={() => handleAuthenticate()}>
                                    <RefreshCw size={16} />
                                </Button>
                            </div>

                            <div className="space-y-4">
                                {buckets.map((bucket) => (
                                    <div key={bucket.name} className="flex flex-col gap-2 p-4 rounded-lg border bg-white/5 border-white/10 hover:border-indigo-500/50 transition-colors">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-white/5 rounded-lg">
                                                <HardDrive className="text-white/60" size={20} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-medium truncate">{bucket.name}</p>
                                                <p className="text-xs text-white/40 uppercase">{bucket.location} • {bucket.storage_class}</p>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <Button
                                                    size="sm"
                                                    variant="secondary"
                                                    onClick={() => openExplorer(bucket.name)}
                                                >
                                                    <Folder size={14} className="mr-2 text-indigo-400" />
                                                    Abrir Explorador
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    onClick={() => handlePreviewClick(bucket.name)}
                                                    className={selectedPreviewBucket === bucket.name ? 'bg-white/10' : ''}
                                                >
                                                    {selectedPreviewBucket === bucket.name ? <ChevronRight className="rotate-90" /> : <ChevronRight />}
                                                </Button>
                                            </div>
                                        </div>

                                        {/* File Explorer Inline Preview */}
                                        <AnimatePresence>
                                            {selectedPreviewBucket === bucket.name && (
                                                <motion.div
                                                    initial={{ height: 0, opacity: 0 }}
                                                    animate={{ height: 'auto', opacity: 1 }}
                                                    exit={{ height: 0, opacity: 0 }}
                                                    className="overflow-hidden"
                                                >
                                                    <div className="ml-8 mt-2 p-3 rounded-lg bg-black/20 border border-white/5 text-sm">
                                                        <h4 className="text-xs font-bold text-white/40 mb-2 uppercase flex items-center gap-2">
                                                            <Folder size={12} />
                                                            Vista Rápida
                                                        </h4>
                                                        {dataLoading && previewObjects.length === 0 ? (
                                                            <div className="text-center py-2"><RefreshCw className="animate-spin inline mr-2" /> Cargando...</div>
                                                        ) : previewObjects.length === 0 ? (
                                                            <div className="text-white/30 italic">Carpeta vacía o sin resultados</div>
                                                        ) : (
                                                            <ul className="space-y-1 max-h-40 overflow-y-auto custom-scrollbar">
                                                                {previewObjects.slice(0, 5).map((obj, i) => (
                                                                    <li key={i} className="flex items-center gap-2 py-1 px-2 hover:bg-white/5 rounded group cursor-default">
                                                                        <FileText size={14} className="text-indigo-300 group-hover:text-indigo-200" />
                                                                        <span className="truncate flex-1 group-hover:text-white transition-colors">{obj.name}</span>
                                                                        <span className="text-xs text-white/30">{(obj.size / 1024).toFixed(1)} KB</span>
                                                                    </li>
                                                                ))}
                                                                {previewObjects.length > 5 && (
                                                                    <li className="text-center pt-2">
                                                                        <button onClick={() => openExplorer(bucket.name)} className="text-xs text-indigo-400 hover:text-indigo-300">
                                                                            Ver {previewObjects.length - 5} archivos más...
                                                                        </button>
                                                                    </li>
                                                                )}
                                                            </ul>
                                                        )}
                                                    </div>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                ))}
                            </div>
                        </GlassCard>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Log Terminal Overlay (Global for Dashboard) */}
            <AnimatePresence>
                {showLogs && (
                    <motion.div
                        initial={{ y: 200, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 200, opacity: 0 }}
                    >
                        <LogTerminal
                            logs={logs}
                            onClose={() => setShowLogs(false)}
                            clearLogs={() => setLogs([])}
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
