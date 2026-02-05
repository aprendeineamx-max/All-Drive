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
    List as ListIcon,
    Trash2,
    ChevronUp,
    ChevronDown
} from 'lucide-react'
import { GlassCard, Button, Input, Toast } from '../components/ui'

declare global {
    interface Window {
        electronAPI: any
    }
}

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
    fileCount?: number
    folderCount?: number
    syncState?: SyncStatus | string
    isLocal?: boolean
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
    syncStatuses,
    lastSyncPath,
    setLastSyncPath
}: {
    bucket: string,
    onClose: () => void,
    electronAPI: any,
    onToast: (msg: string, type: 'success' | 'error' | 'info') => void,
    syncStatuses: Record<string, SyncStatus>,
    lastSyncPath: string | null,
    setLastSyncPath: (path: string | null) => void
}) {
    const [currentLocalPath, setCurrentLocalPath] = useState<string>('')  // Relative path within sync folder
    const [currentPrefix, _setCurrentPrefix] = useState('') // Internal navigation state
    const [objects, setObjects] = useState<GCSObject[]>([])
    const [loading, setLoading] = useState(false)
    const [searchTerm, setSearchTerm] = useState('')
    const [viewType, setViewType] = useState<'list' | 'grid' | 'details'>('list')
    const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' } | null>({ key: 'name', direction: 'asc' })
    const [actionLoading, setActionLoading] = useState(false)
    const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
    const [previewFile, setPreviewFile] = useState<{ name: string, content: string } | null>(null)
    const [autoLaunch, setAutoLaunch] = useState(false)

    // IMMEDIATE VISIBILITY: Listen for sync events to add files in real-time
    useEffect(() => {
        const cleanup = window.electronAPI.gcp.onSyncEvent((event: any) => {
            if (event.type === 'sync_event' && event.file) {
                // 1. Calculate the current visible prefix in GCS terms
                let visiblePrefix = ''
                let rootName = ''

                if (lastSyncPath) {
                    rootName = lastSyncPath.split(/[/\\]/).pop() || 'Desktop'
                    if (currentLocalPath === '') {
                        visiblePrefix = rootName
                    } else {
                        // currentLocalPath is relative inside the sync root
                        // visiblePrefix includes the rootName
                        visiblePrefix = `${rootName}/${currentLocalPath}`.replace(/\\/g, '/')
                    }
                } else {
                    visiblePrefix = currentPrefix
                }

                // 2. Parse the syncing file path
                // event.file is relative to the sync root (e.g. "Desktop/file.txt")
                // Ensure forward slashes
                const syncFile = event.file.replace(/\\/g, '/')

                // 3. Check if this file belongs to the current view
                // Logic: syncFile must start with visiblePrefix

                // Handle root mismatch (if syncFile doesn't start with what we are looking at)
                if (lastSyncPath && !syncFile.startsWith(visiblePrefix)) return

                // Special case: visiblePrefix might be same as syncFile
                if (syncFile === visiblePrefix) return

                let relativePart = ''
                if (lastSyncPath) {
                    // We need to strip "visiblePrefix/"
                    // Example: visiblePrefix="Desktop", syncFile="Desktop/file.txt" -> relative="file.txt"
                    if (syncFile.startsWith(visiblePrefix + '/')) {
                        relativePart = syncFile.substring(visiblePrefix.length + 1)
                    } else if (visiblePrefix === rootName && syncFile.startsWith(rootName + '/')) {
                        // Catch-all for root level matches
                        relativePart = syncFile.substring(rootName.length + 1)
                    } else {
                        return // Not in this path
                    }
                } else {
                    // Non-sync view logic (if event.file is full path)
                    return
                }

                // 4. Determine if it's a file or folder at this level
                const parts = relativePart.split('/')
                const itemName = parts[0]
                const isDirectory = parts.length > 1

                // 5. Optimistic Update
                setObjects(prev => {
                    // Prevent duplicates
                    if (prev.find(p => p.name === itemName)) return prev

                    const newObj: GCSObject = {
                        name: itemName,
                        size: 0,
                        updated: new Date().toISOString(),
                        contentType: isDirectory ? 'directory' : 'application/octet-stream',
                        syncState: 'synced'
                    }
                    return [...prev, newObj]
                })

            }
        })
        return cleanup
    }, [lastSyncPath, currentLocalPath, currentPrefix])


    // Load session and check auto-launch on mount
    useEffect(() => {
        const init = async () => {
            const sess = await electronAPI.gcp.getSession()
            if (sess?.success && sess.data) {
                const { lastSyncPath, lastCredentialPath } = sess.data
                if (lastSyncPath) setLastSyncPath(lastSyncPath)

                // If we have credentials, auto-authenticate
                if (lastCredentialPath) {
                    onToast('Restaurando sesión...', 'info')
                    const authRes = await electronAPI.gcp.authenticate(lastCredentialPath)
                    if (authRes.authenticated) {
                        onToast('Sesión restaurada correctamente', 'success')
                        // Initial load will be triggered by useEffect dependencies
                    }
                }
            }

            const al = await electronAPI.gcp.getAutoLaunch()
            if (al?.success) setAutoLaunch(al.enabled)
        }
        init()
    }, [])

    const handleToggleAutoLaunch = async () => {
        const newState = !autoLaunch
        const res = await electronAPI.gcp.setAutoLaunch(newState)
        if (res.success) {
            setAutoLaunch(newState)
            onToast(newState ? 'Auto-inicio activado' : 'Auto-inicio desactivado', 'success')
        } else {
            onToast('Error al cambiar auto-inicio', 'error')
        }
    }

    // Auto-refresh when sync path or subfolder changes (Local-First trigger)
    useEffect(() => {
        loadObjects(bucket, currentPrefix)
    }, [bucket, currentPrefix, lastSyncPath, currentLocalPath])

    const loadObjects = async (bucketName: string, prefix: string) => {
        setLoading(true)
        try {
            // STRATEGY: Local-First (Google Drive Desktop Style)
            // 1. Get GCS Objects for status reference
            const gcsResult = await electronAPI?.gcp.listObjects(bucketName, prefix)
            const gcsFiles: GCSObject[] = gcsResult?.success ? gcsResult.data : []

            let finalFiles: any[] = []

            // 2. Identify if we are in the Virtual Root or a Synced Folder
            if (lastSyncPath) {
                const rootName = lastSyncPath.split(/[/\\]/).pop() || 'Desktop'

                if (currentLocalPath === '') {
                    // VIRTUAL ROOT: Show the Synced Folder(s) PLUS anything else in the bucket root
                    finalFiles = [{
                        name: rootName,
                        contentType: 'directory',
                        size: 0,
                        updated: new Date().toISOString(),
                        syncState: 'synced'
                    }]

                    // Add GCS files/folders that are NOT under the rootName prefix
                    gcsFiles.forEach(gcs => {
                        // Strip trailing slash for comparison and display
                        const cleanGcsName = gcs.name.replace(/\/$/, '')
                        if (!cleanGcsName) return

                        const baseName = cleanGcsName.split('/')[0]
                        if (!baseName || !baseName.trim()) return

                        if (baseName !== rootName && !finalFiles.find(f => f.name === baseName)) {
                            finalFiles.push({
                                ...gcs,
                                name: baseName, // Use the top-level name
                                isLocal: false,
                                syncState: 'synced'
                            })
                        }
                    })
                } else {
                    // INSIDE A FOLDER (Sync or not)
                    // Calculate real local path relative to the synced folder
                    let relativePath = ''
                    if (currentLocalPath === rootName) {
                        relativePath = ''
                    } else if (currentLocalPath.startsWith(rootName + '/')) {
                        relativePath = currentLocalPath.substring(rootName.length + 1)
                    } else {
                        relativePath = currentLocalPath
                    }

                    const fullLocalPath = relativePath
                        ? `${lastSyncPath}/${relativePath}`.replace(/\\/g, '/')
                        : lastSyncPath

                    const localRes = await electronAPI.gcp.listLocalFolder(fullLocalPath)
                    const localItems = localRes?.success ? localRes.data : []

                    // Merge strategy
                    finalFiles = localItems.map((local: any) => {
                        // Match with GCS using full path
                        const gcsPath = relativePath ? `${relativePath}/${local.name}` : local.name
                        const gcsMatch = gcsFiles.find(g => {
                            const cleanG = g.name.replace(/\/$/, '')
                            return cleanG === gcsPath || cleanG === rootName + '/' + gcsPath
                        })

                        return {
                            ...local,
                            contentType: local.contentType || 'application/octet-stream',
                            syncState: gcsMatch ? 'synced' : 'pending'
                        }
                    })

                    // Add Cloud Only files/folders at this LEVEL
                    gcsFiles.forEach(gcs => {
                        const cleanG = gcs.name.replace(/\/$/, '')
                        if (!cleanG || !cleanG.trim()) return

                        const parts = cleanG.split('/')
                        const gcsName = parts.pop() || cleanG
                        const gcsPrefix = parts.join('/')

                        // Check if this item belongs to the CURRENT prefix
                        const currentPrefix = relativePath ? `${rootName}/${relativePath}` : rootName
                        const matchesCurrentLevel = gcsPrefix === currentPrefix || (relativePath === '' && gcsPrefix === rootName)

                        if (matchesCurrentLevel && gcsName && !finalFiles.find(f => f.name === gcsName)) {
                            finalFiles.push({
                                ...gcs,
                                name: gcsName,
                                isLocal: false,
                                syncState: 'synced'
                            })
                        }
                    })
                }
            } else {
                // Standard Cloud View (No local sync setup)
                finalFiles = gcsFiles.filter(f => {
                    const cleanName = f.name.replace(/\/$/, '').split('/').pop()
                    return cleanName && cleanName.trim().length > 0
                })
            }

            // FINAL SAFETY: Normalize names (Strip trailing slashes) to ensure Renderer works
            finalFiles = finalFiles.map(f => ({
                ...f,
                name: f.name.replace(/[/\\]+$/, '')
            }))

            // FINAL SAFETY FILTER: Prevent ghost folders (empty names) from ANY source
            finalFiles = finalFiles.filter(f => {
                const displayName = f.name.split(/[/\\]/).pop()
                return displayName && displayName.trim().length > 0
            })

            setObjects(finalFiles)
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
                    setLastSyncPath(dirRes.data)
                    // Persist Sync Path
                    window.electronAPI.gcp.saveSession({ lastSyncPath: dirRes.data })

                    onToast(`Sincronización activa: ${dirRes.data}`, 'success')
                    // Immediate refresh to show local files (useEffect will also trigger)
                    loadObjects(bucket, currentPrefix)
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

    // Selection Helpers
    const toggleSelection = (name: string) => {
        setSelectedFiles(prev => {
            const newSet = new Set(prev)
            if (newSet.has(name)) newSet.delete(name)
            else newSet.add(name)
            return newSet
        })
    }

    const selectAll = () => {
        if (selectedFiles.size === filteredObjects.length) {
            setSelectedFiles(new Set())
        } else {
            setSelectedFiles(new Set(filteredObjects.map(o => o.name)))
        }
    }

    // Delete Selected Files
    const handleDeleteSelected = async () => {
        if (selectedFiles.size === 0) return

        const filesToDelete = Array.from(selectedFiles)

        // Check if deleting the sync root
        const rootName = lastSyncPath?.split(/[/\\]/).pop() || ''
        const isDeletingSyncRoot = selectedFiles.has(rootName) && currentLocalPath === ''

        if (isDeletingSyncRoot) {
            const confirmed = window.confirm(
                `La carpeta "${rootName}" está sincronizándose actualmente.\n\n¿Deseas DETENER la sincronización y eliminar esta carpeta de la nube?`
            )
            if (!confirmed) return

            // Stop sync first
            await handleStopSync()
        }

        setActionLoading(true)
        onToast(`Eliminando ${selectedFiles.size} archivos...`, 'info')

        // OPTIMISTIC UI: Remove from list immediately
        setObjects(prev => prev.filter(obj => !selectedFiles.has(obj.name)))
        setSelectedFiles(new Set())
        try {
            for (const name of filesToDelete) {
                const res = await electronAPI.gcp.deleteObject(bucket, name)
                if (!res.success) {
                    onToast(`Error al eliminar ${name}: ${res.error}`, 'error')
                }
            }
            onToast('Eliminación completada', 'success')
        } catch (e: any) {
            onToast(`Error en proceso de eliminación: ${e.message}`, 'error')
        } finally {
            setActionLoading(false)
            // Final refresh to ensure consistency
            loadObjects(bucket, currentPrefix)
        }
    }

    // Stop Sync (Disconnect local folder)
    const handleStopSync = async () => {
        setLastSyncPath(null)
        setCurrentLocalPath('')
        await electronAPI.gcp.saveSession({ lastSyncPath: null })
        onToast('Sincronización detenida', 'info')
        loadObjects(bucket, currentPrefix)
    }

    // Preview File Content
    const handlePreview = async (objectName: string) => {
        setActionLoading(true)
        const res = await electronAPI.gcp.getFileContent(bucket, objectName)
        if (res.success) {
            setPreviewFile({ name: objectName, content: res.content })
        } else {
            onToast('No se pudo previsualizar el archivo', 'error')
        }
        setActionLoading(false)
    }

    const handleFileClick = (obj: any) => {
        if (obj.contentType === 'directory') {
            const newPath = currentLocalPath
                ? `${currentLocalPath}/${obj.name}`.replace(/\/+/g, '/')
                : obj.name
            setCurrentLocalPath(newPath)
        } else {
            // Reconstruct full GCS path for preview
            let fullGcsPath = obj.name
            if (lastSyncPath) {
                if (currentLocalPath === '') {
                    // In Virtual Root, obj.name might be the root folder itself if it's what we clicked
                    // but for files inside gcs root it's just name
                    fullGcsPath = obj.name
                } else {
                    fullGcsPath = `${currentLocalPath}/${obj.name}`.replace(/\/+/g, '/')
                }
            }
            handlePreview(fullGcsPath)
        }
    }

    const handleSort = (key: string) => {
        let direction: 'asc' | 'desc' = 'asc'
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc'
        }
        setSortConfig({ key, direction })
    }

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 B'
        const k = 1024
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return '-'
        return new Date(dateStr).toLocaleString([], {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const sortedObjects = [...objects].sort((a, b) => {
        if (!sortConfig) return 0
        const { key, direction } = sortConfig

        let aValue: any = a[key as keyof GCSObject]
        let bValue: any = b[key as keyof GCSObject]

        // Special case for names to ignore case and path prefix
        if (key === 'name') {
            aValue = a.name.split(/[/\\]/).pop()?.toLowerCase() || ''
            bValue = b.name.split(/[/\\]/).pop()?.toLowerCase() || ''
        }

        if (aValue < bValue) return direction === 'asc' ? -1 : 1
        if (aValue > bValue) return direction === 'asc' ? 1 : -1
        return 0
    })

    const filteredObjects = sortedObjects.filter(obj =>
        obj.name.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="space-y-4 h-full flex flex-col pb-10">
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

                {/* Breadcrumb Path Bar */}
                {lastSyncPath && (
                    <div className="flex items-center gap-1 bg-black/30 px-3 py-2 rounded-lg border border-white/10 text-sm text-white/70 overflow-x-auto">
                        <HardDrive size={14} className="text-indigo-400 flex-shrink-0" />
                        <span
                            className="cursor-pointer hover:text-white"
                            onClick={() => setCurrentLocalPath('')}
                        >
                            Raíz
                        </span>
                        {currentLocalPath && currentLocalPath.split(/[/\\]/).filter(Boolean).map((seg, i, arr) => (
                            <React.Fragment key={i}>
                                <ChevronRight size={12} className="text-white/30" />
                                <span
                                    className="cursor-pointer hover:text-white"
                                    onClick={() => setCurrentLocalPath(arr.slice(0, i + 1).join('/'))}
                                >
                                    {seg}
                                </span>
                            </React.Fragment>
                        ))}
                    </div>
                )}

                {/* Toolbar */}
                <div className="flex flex-wrap items-center gap-2 bg-white/5 p-2 rounded-lg border border-white/10">
                    {/* Upload Actions */}
                    <div className="flex items-center gap-1">
                        <Button size="sm" variant="secondary" onClick={handleUploadFile} disabled={actionLoading}>
                            <UploadCloud size={14} />
                            <span className="hidden sm:inline ml-1">Subir Archivo</span>
                        </Button>
                        <Button size="sm" variant="secondary" onClick={handleUploadFolder} disabled={actionLoading}>
                            <Folder size={14} />
                            <span className="hidden sm:inline ml-1">Subir Carpeta</span>
                        </Button>
                    </div>

                    <div className="h-6 w-px bg-white/20 hidden sm:block" />

                    {/* Sync Actions */}
                    <div className="flex items-center gap-1">
                        <Button size="sm" variant="ghost" onClick={handleStartSync} disabled={actionLoading} className="text-indigo-300 hover:text-indigo-200 hover:bg-indigo-500/20">
                            <RefreshCw size={14} />
                            <span className="hidden md:inline ml-1">Sincronizar</span>
                        </Button>
                        {lastSyncPath && (
                            <Button size="sm" variant="ghost" onClick={handleStopSync} disabled={actionLoading} className="text-red-400 hover:text-red-300 hover:bg-red-500/20">
                                <AlertCircle size={14} />
                                <span className="hidden md:inline ml-1">Detener</span>
                            </Button>
                        )}
                        <Button size="sm" variant="ghost" onClick={async () => {
                            if (window.confirm('⚠️ ¿Estás seguro de eliminar TODO el contenido de este bucket?\n\nEsta acción NO se puede deshacer.')) {
                                setActionLoading(true)
                                onToast('Limpiando bucket...', 'info')
                                await electronAPI.gcp.cleanBucket(bucket)
                                loadObjects(bucket, currentPrefix)
                                onToast('Bucket limpio', 'success')
                                setActionLoading(false)
                            }
                        }} disabled={actionLoading} className="text-orange-400 hover:text-orange-300 hover:bg-orange-500/20">
                            <Trash2 size={14} />
                            <span className="hidden md:inline ml-1">Limpiar</span>
                        </Button>
                    </div>

                    {/* Right Side Controls */}
                    <div className="ml-auto flex items-center gap-2">
                        <label className="flex items-center gap-2 cursor-pointer group">
                            <span className="text-[11px] text-white/40 group-hover:text-white/60 transition-colors uppercase font-medium tracking-wider">
                                Auto-inicio
                            </span>
                            <div
                                onClick={handleToggleAutoLaunch}
                                className={`w-8 h-4 rounded-full p-0.5 transition-colors duration-200 ease-in-out ${autoLaunch ? 'bg-indigo-500' : 'bg-white/10'}`}
                            >
                                <div className={`w-3 h-3 bg-white rounded-full shadow-lg transform transition-transform duration-200 ease-in-out ${autoLaunch ? 'translate-x-4' : 'translate-x-0'}`} />
                            </div>
                        </label>
                        <div className="relative w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" size={14} />
                            <Input
                                value={searchTerm}
                                onChange={setSearchTerm}
                                placeholder="Buscar archivos..."
                                className="pl-9 h-9 text-sm border-0 bg-black/20 focus:bg-black/40"
                            />
                        </div>
                        <div className="flex bg-black/20 rounded-lg p-1 gap-1">
                            <button
                                onClick={() => setViewType('list')}
                                className={`p-1.5 rounded transition-all ${viewType === 'list' ? 'bg-indigo-500/30 text-indigo-300' : 'text-white/40 hover:text-white/70 hover:bg-white/5'}`}
                                title="Lista"
                            >
                                <ListIcon size={16} />
                            </button>
                            <button
                                onClick={() => setViewType('details')}
                                className={`p-1.5 rounded transition-all ${viewType === 'details' ? 'bg-indigo-500/30 text-indigo-300' : 'text-white/40 hover:text-white/70 hover:bg-white/5'}`}
                                title="Detalles"
                            >
                                <FileText size={16} />
                            </button>
                            <button
                                onClick={() => setViewType('grid')}
                                className={`p-1.5 rounded transition-all ${viewType === 'grid' ? 'bg-indigo-500/30 text-indigo-300' : 'text-white/40 hover:text-white/70 hover:bg-white/5'}`}
                                title="Cuadrícula"
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
                        <>
                            {/* Action Bar */}
                            {selectedFiles.size > 0 && (
                                <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-lg mb-2">
                                    <span className="text-xs text-red-300">{selectedFiles.size} seleccionados</span>
                                    <Button size="sm" variant="secondary" onClick={handleDeleteSelected} disabled={actionLoading} className="bg-red-500/20 hover:bg-red-500/40 text-red-300 border-red-500/30">
                                        <Trash2 size={14} className="mr-1" /> Eliminar
                                    </Button>
                                </div>
                            )}

                            {viewType === 'grid' ? (
                                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                    {filteredObjects.map((obj, i) => (
                                        <motion.div
                                            key={i}
                                            whileHover={{ scale: 1.02 }}
                                            onClick={() => handleFileClick(obj)}
                                            className="p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 hover:border-white/20 transition-all flex flex-col items-center gap-3 text-center cursor-pointer group"
                                        >
                                            <div className="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center text-indigo-400 group-hover:text-white group-hover:bg-indigo-500 transition-all relative">
                                                {obj.contentType === 'directory' ? <Folder size={24} className="text-yellow-500" /> : <FileText size={24} />}
                                                <div className="absolute top-0 right-0 p-1">
                                                    <StatusIcon status={syncStatuses[obj.name] || (obj as any).syncState} />
                                                </div>
                                            </div>
                                            <div className="min-w-0 w-full">
                                                <p className="text-xs font-medium truncate text-white/80 group-hover:text-white mb-1" title={obj.name}>
                                                    {obj.name.split(/[/\\]/).pop()}
                                                </p>
                                                <p className="text-[10px] text-white/40">{formatSize(obj.size)}</p>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            ) : (
                                <table className="w-full text-sm text-left border-separate border-spacing-0">
                                    <thead className="text-[10px] text-white/30 uppercase tracking-wider sticky top-0 bg-black/40 backdrop-blur-md z-10">
                                        <tr>
                                            <th className="px-2 py-3 border-b border-white/5 w-10">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedFiles.size === filteredObjects.length && filteredObjects.length > 0}
                                                    onChange={selectAll}
                                                    className="w-4 h-4 rounded border-white/20 bg-transparent accent-indigo-500"
                                                />
                                            </th>
                                            <th className="px-4 py-3 border-b border-white/5 font-bold cursor-pointer hover:text-white transition-colors group" onClick={() => handleSort('name')}>
                                                <div className="flex items-center gap-2">
                                                    Nombre
                                                    {sortConfig?.key === 'name' && (sortConfig.direction === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />)}
                                                </div>
                                            </th>
                                            {viewType === 'details' && (
                                                <th className="px-4 py-3 border-b border-white/5 font-bold cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('updated')}>
                                                    <div className="flex items-center gap-2">
                                                        Fecha de modificación
                                                        {sortConfig?.key === 'updated' && (sortConfig.direction === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />)}
                                                    </div>
                                                </th>
                                            )}
                                            <th className="px-4 py-3 border-b border-white/5 font-bold cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('contentType')}>
                                                <div className="flex items-center gap-2">
                                                    Tipo
                                                    {sortConfig?.key === 'contentType' && (sortConfig.direction === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />)}
                                                </div>
                                            </th>
                                            <th className="px-4 py-3 border-b border-white/5 font-bold cursor-pointer hover:text-white transition-colors" onClick={() => handleSort('size')}>
                                                <div className="flex items-center gap-2">
                                                    Tamaño
                                                    {sortConfig?.key === 'size' && (sortConfig.direction === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />)}
                                                </div>
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5">
                                        {filteredObjects.map((obj, i) => (
                                            <tr
                                                key={i}
                                                className="hover:bg-white/5 group transition-colors cursor-pointer"
                                                onClick={(e) => {
                                                    // Don't trigger if clicking checkbox
                                                    if ((e.target as HTMLElement).tagName === 'INPUT') return
                                                    handleFileClick(obj)
                                                }}
                                                onDoubleClick={() => {
                                                    handleFileClick(obj)
                                                }}
                                            >
                                                <td className="px-2 py-2">
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedFiles.has(obj.name)}
                                                        onChange={(e) => {
                                                            e.stopPropagation()
                                                            toggleSelection(obj.name)
                                                        }}
                                                        className="w-4 h-4 rounded border-white/20 bg-transparent accent-indigo-500"
                                                    />
                                                </td>
                                                <td className="px-4 py-2 flex items-center gap-3 text-white/80 group-hover:text-white">
                                                    <div className="relative flex-shrink-0">
                                                        {obj.contentType === 'directory' ? (
                                                            <Folder size={16} className="text-yellow-500" />
                                                        ) : (
                                                            <FileText size={16} className="text-indigo-400" />
                                                        )}
                                                        <div className="absolute -bottom-1 -right-1">
                                                            <StatusIcon status={syncStatuses[obj.name] || (obj as any).syncState} />
                                                        </div>
                                                    </div>
                                                    <span
                                                        className="truncate max-w-[250px] font-medium"
                                                        title={obj.name}
                                                    >
                                                        {obj.name.split(/[/\\]/).pop()}
                                                    </span>
                                                </td>
                                                {viewType === 'details' && (
                                                    <td className="px-4 py-2 text-white/50 text-xs whitespace-nowrap">
                                                        {formatDate(obj.updated)}
                                                    </td>
                                                )}
                                                <td className="px-4 py-2 text-white/40 text-xs truncate max-w-[200px]">
                                                    {obj.contentType === 'directory' ? (
                                                        <span className="flex items-center gap-1">
                                                            <span>{obj.fileCount || 0} archivos</span>
                                                            <span className="text-white/20">•</span>
                                                            <span>{obj.folderCount || 0} carpetas</span>
                                                        </span>
                                                    ) : (
                                                        obj.contentType?.split('/').pop() || 'Archivo'
                                                    )}
                                                </td>
                                                <td className="px-4 py-2 text-white/50 font-mono text-xs whitespace-nowrap">
                                                    {formatSize(obj.size)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </>
                    )}
                </div>
            </GlassCard>

            {/* Preview Modal */}
            <AnimatePresence>
                {previewFile && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
                        onClick={() => setPreviewFile(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0.9 }}
                            className="bg-gray-900/90 border border-white/10 rounded-xl max-w-3xl w-full max-h-[80vh] overflow-hidden shadow-2xl m-4"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
                                <h3 className="text-white font-semibold truncate">{previewFile.name.split(/[/\\]/).pop()}</h3>
                                <Button size="sm" variant="ghost" onClick={() => setPreviewFile(null)}>✕</Button>
                            </div>
                            <pre className="p-4 text-xs text-white/80 font-mono overflow-auto max-h-[65vh] whitespace-pre-wrap">
                                {previewFile.content}
                            </pre>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div >
    )
}

// Sub-component: Professional Glass Terminal
function GlassControlCenter({
    logs,
    syncStatuses,
    isMinimized,
    setIsMinimized,
    onClose,
    onClear
}: {
    logs: string[],
    syncStatuses: Record<string, SyncStatus>,
    isMinimized: boolean,
    setIsMinimized: (v: boolean) => void,
    onClose: () => void,
    onClear: () => void
}) {
    const scrollRef = React.useRef<HTMLDivElement>(null)
    const uploadingCount = Object.values(syncStatuses).filter(s => s === 'uploading').length
    const syncedCount = Object.values(syncStatuses).filter(s => s === 'synced').length

    useEffect(() => {
        if (scrollRef.current && !isMinimized) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [logs, isMinimized])

    if (isMinimized) return null // Handled by SyncFooter

    return (
        <motion.div
            layout
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-10 left-0 right-0 p-4 z-40"
        >
            <GlassCard
                className="h-[300px] flex flex-col shadow-2xl overflow-hidden p-0 border-white/10 bg-black/60 backdrop-blur-3xl rounded-t-2xl border-b-0"
            >
                <div
                    className="flex items-center justify-between p-3 bg-white/5 border-b border-white/10"
                >
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <div className={`w-2 h-2 rounded-full ${uploadingCount > 0 ? 'bg-indigo-400 animate-pulse' : 'bg-green-500'}`} />
                            {uploadingCount > 0 && (
                                <div className="absolute -inset-1 bg-indigo-400/20 rounded-full animate-ping" />
                            )}
                        </div>
                        <h3 className="text-[10px] font-bold uppercase tracking-widest text-white/50 group-hover:text-indigo-300 transition-colors">
                            {isMinimized ? 'Sincronización en curso' : 'Centro de Control de Sincronización'}
                        </h3>
                        {isMinimized && (
                            <div className="flex items-center gap-2 ml-2">
                                <div className="flex items-center gap-1 bg-indigo-500/20 px-2 py-0.5 rounded-full border border-indigo-500/30">
                                    <RefreshCw size={10} className="text-indigo-400 animate-spin" />
                                    <span className="text-[10px] text-indigo-300 font-mono">{uploadingCount}</span>
                                </div>
                                <div className="flex items-center gap-1 bg-green-500/20 px-2 py-0.5 rounded-full border border-green-500/30">
                                    <Cloud size={10} className="text-green-400" />
                                    <span className="text-[10px] text-green-300 font-mono">{syncedCount}</span>
                                </div>
                            </div>
                        )}
                    </div>
                    <div className="flex items-center gap-1">
                        {!isMinimized && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onClear() }}
                                className="p-1.5 hover:bg-white/10 rounded-lg text-white/30 hover:text-white transition-colors"
                                title="Limpiar Consola"
                            >
                                <RefreshCw size={14} />
                            </button>
                        )}
                        <button
                            onClick={() => setIsMinimized(true)}
                            className="p-1.5 hover:bg-white/10 rounded-lg text-white/30 hover:text-white transition-colors"
                        >
                            <ChevronRight className="rotate-90" size={16} />
                        </button>
                        {!isMinimized && (
                            <button
                                onClick={(e) => { e.stopPropagation(); onClose() }}
                                className="p-1.5 hover:bg-white/10 rounded-lg text-red-500/40 hover:text-red-500 transition-colors"
                            >
                                <AlertCircle size={16} />
                            </button>
                        )}
                    </div>
                </div>

                {/* Content */}
                <AnimatePresence>
                    {!isMinimized && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex-1 flex flex-col min-h-0"
                        >
                            <div className="flex items-center gap-4 px-4 py-2 bg-black/40 border-b border-white/5">
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] text-white/30 uppercase font-medium">Estado:</span>
                                    <span className="flex items-center gap-1.5 text-[10px] py-0.5 px-2 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 font-bold">
                                        CONECTADO
                                    </span>
                                </div>
                                <div className="h-3 w-px bg-white/10" />
                                <div className="flex items-center gap-4 text-[10px]">
                                    <span className="text-indigo-300">En espera: {Object.values(syncStatuses).filter(s => s === 'pending').length}</span>
                                    <span className="text-indigo-400">Subiendo: {uploadingCount}</span>
                                    <span className="text-green-400">Completados: {syncedCount}</span>
                                </div>
                            </div>
                            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed custom-scrollbar selection:bg-indigo-500/30">
                                {logs.length === 0 && (
                                    <div className="h-full flex flex-col items-center justify-center text-white/10 gap-2 select-none">
                                        <Cloud size={32} />
                                        <p className="italic">Escuchando eventos de sincronización...</p>
                                    </div>
                                )}
                                {logs.map((log, i) => (
                                    <div key={i} className="flex gap-4 group py-0.5 px-2 hover:bg-white/5 rounded transition-colors border-l-2 border-transparent hover:border-indigo-500/40">
                                        <span className="text-white/20 select-none w-16 tabular-nums">{new Date().toLocaleTimeString()}</span>
                                        <span className={`${log.includes('[ERROR]') ? 'text-red-400' : log.includes('[WATCHER]') ? 'text-indigo-300' : 'text-zinc-400'} break-all`}>
                                            {log}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </GlassCard>
        </motion.div>
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

    // Logs & Sync Status
    const [logs, setLogs] = useState<string[]>([])
    const [showLogs, setShowLogs] = useState(false)
    const [isTerminalMinimized, setIsTerminalMinimized] = useState(false)
    const [syncStatuses, setSyncStatuses] = useState<Record<string, SyncStatus>>({})
    const [lastSyncPath, setLastSyncPath] = useState<string | null>(null)
    const [isFooterVisible, setIsFooterVisible] = useState(true)

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
        const cleanupLog = window.electronAPI.gcp.onLog((msg: string) => {
            setLogs(prev => [...prev, msg])
            setShowLogs(true)
        })

        // Subscribe to sync events
        const cleanupSync = window.electronAPI.gcp.onSyncEvent((event: any) => {
            if (event.type === 'sync_event' && event.file) {
                setSyncStatuses(prev => ({
                    ...prev,
                    [event.file]: event.status
                }))
            }
        })

        return () => {
            if (cleanupLog) cleanupLog()
            if (cleanupSync) cleanupSync()
        }
    }, [])

    const checkSession = async () => {
        try {
            const result = await window.electronAPI?.gcp.loadSession()
            if (result?.success) {
                const session = result.data
                if (session.lastCredentialPath) {
                    console.log('Restoring auth:', session.lastCredentialPath)
                    setSelectedCred(session.lastCredentialPath)
                    handleAuthenticate(session.lastCredentialPath)
                }
                if (session.lastSyncPath) {
                    console.log('Restoring sync path:', session.lastSyncPath)
                    setLastSyncPath(session.lastSyncPath)
                    // Note: We don't auto-start sync here to avoid issues, but UI will reflect the path state
                    // and allow "Merged View" to work immediately
                }
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
                            lastSyncPath={lastSyncPath}
                            setLastSyncPath={setLastSyncPath}
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

                {/* Sync Footer & Status Bar */}
                <AnimatePresence>
                    {isFooterVisible ? (
                        <motion.div
                            initial={{ y: 50 }}
                            animate={{ y: 0 }}
                            exit={{ y: 50 }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="fixed bottom-0 left-0 right-0 z-50"
                        >
                            <SyncFooter
                                lastSyncPath={lastSyncPath}
                                logsCount={logs.length}
                                uploadingCount={Object.values(syncStatuses).filter(s => s === 'uploading').length}
                                showLogs={showLogs}
                                setShowLogs={setShowLogs}
                                isMinimized={isTerminalMinimized}
                                setIsMinimized={setIsTerminalMinimized}
                                onHide={() => setIsFooterVisible(false)}
                            />
                        </motion.div>
                    ) : (
                        <motion.button
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            whileHover={{ scale: 1.1 }}
                            onClick={() => setIsFooterVisible(true)}
                            className="fixed bottom-4 left-4 z-50 p-2 bg-indigo-600/50 hover:bg-indigo-600 backdrop-blur-md rounded-full text-white shadow-lg border border-white/20 transition-all"
                            title="Mostrar Barra de Estado"
                        >
                            <ChevronRight className="-rotate-90" size={14} />
                        </motion.button>
                    )}
                </AnimatePresence>

                {/* Glass Control Center Overlay */}
                <AnimatePresence>
                    {(showLogs && !isTerminalMinimized) && (
                        <GlassControlCenter
                            logs={logs}
                            syncStatuses={syncStatuses}
                            isMinimized={isTerminalMinimized}
                            setIsMinimized={setIsTerminalMinimized}
                            onClose={() => setShowLogs(false)}
                            onClear={() => setLogs([])}
                        />
                    )}
                </AnimatePresence>
            </>
        )
    }

    // New Component: Footer Status Bar
    function SyncFooter({
        lastSyncPath,
        logsCount,
        uploadingCount,
        showLogs,
        setShowLogs,
        isMinimized,
        setIsMinimized,
        onHide
    }: any) {
        return (
            <div className="h-7 bg-indigo-950/60 backdrop-blur-xl border-t border-white/10 px-4 flex items-center justify-between safe-area-bottom group/footer shadow-[0_-4px_20px_rgba(0,0,0,0.5)]">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onHide}
                        className="opacity-0 group-hover/footer:opacity-100 p-1 hover:bg-white/10 rounded transition-all text-white/30 hover:text-white"
                        title="Ocultar Barra"
                    >
                        <ChevronRight className="rotate-90" size={12} />
                    </button>
                    {lastSyncPath ? (
                        <div className="flex items-center gap-2">
                            <div className={`w-1 h-1 rounded-full ${uploadingCount > 0 ? 'bg-indigo-400 animate-pulse' : 'bg-green-500'}`} />
                            <span className="text-[9px] text-white/40 uppercase tracking-tighter font-medium">Sync:</span>
                            <span className="text-[9px] text-indigo-300/70 font-mono truncate max-w-sm" title={lastSyncPath}>
                                {lastSyncPath}
                            </span>
                        </div>
                    ) : (
                        <span className="text-[9px] text-white/20 uppercase tracking-tighter font-mono tracking-widest">Idle</span>
                    )}
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => {
                            if (!showLogs) setShowLogs(true)
                            setIsMinimized(!isMinimized)
                        }}
                        className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full transition-all group ${(showLogs && !isMinimized) ? 'bg-indigo-500/30 text-indigo-300' : 'hover:bg-white/10 text-white/40'
                            }`}
                    >
                        <RefreshCw size={10} className={uploadingCount > 0 ? 'animate-spin' : ''} />
                        <span className="text-[9px] uppercase font-bold tracking-widest group-hover:text-white transition-colors">
                            {uploadingCount > 0 ? `${uploadingCount}` : 'Consola'}
                        </span>
                        {logsCount > 0 && <span className="w-1 h-1 rounded-full bg-indigo-400" />}
                    </button>
                </div>
            </div>
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
                                            <p className="font-medium text-sm text-indigo-300">{cred.path.split(/[\\/]/).pop()}</p>
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

            {/* Glass Control Center Overlay (Global for Dashboard) */}
            <AnimatePresence>
                {showLogs && (
                    <GlassControlCenter
                        logs={logs}
                        syncStatuses={syncStatuses}
                        isMinimized={isTerminalMinimized}
                        setIsMinimized={setIsTerminalMinimized}
                        onClose={() => setShowLogs(false)}
                        onClear={() => setLogs([])}
                    />
                )}
            </AnimatePresence>
        </div>
    )
}
