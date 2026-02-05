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
    CheckCircle2
} from 'lucide-react'
import { GlassCard, Button } from '../components/ui'

// Types
interface Credential {
    path: string
    project_id: string
    client_email: string
}

interface Bucket {
    name: string
    location: string
    storage_class: string
}

export default function GCPPage() {
    const [credentials, setCredentials] = useState<Credential[]>([])
    const [selectedCred, setSelectedCred] = useState('')
    const [buckets, setBuckets] = useState<any[]>([])
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // File Explorer State
    const [selectedBucket, setSelectedBucket] = useState<string | null>(null)
    const [objects, setObjects] = useState<any[]>([])

    useEffect(() => {
        loadCredentials()
        checkSession()
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
                loadCredentials() // Reload list
                setCredentials(prev => [...prev, { path: result.data!, project_id: 'New', client_email: 'New' }])
                setSelectedCred(result.data!)
            }
        } catch (e: any) {
            setError(e.message)
        }
    }

    const handleAuthenticate = async (credPathOverride?: string) => {
        const credToUse = credPathOverride || selectedCred
        if (!credToUse) return

        setLoading(true)
        setError(null)

        try {
            const result = await window.electronAPI?.gcp.authenticate(credToUse)
            if (result?.success && result.data.authenticated) {
                setIsAuthenticated(true)
                // Usar la lista devuelta por auth si existe, si no, listar explícitamente
                const bucketList = result.data.buckets || []

                // Formatear simple strings a objetos si es necesario
                const formattedBuckets = bucketList.map((b: any) =>
                    typeof b === 'string' ? { name: b, location: 'UNKNOWN', storage_class: 'STANDARD' } : b
                )
                setBuckets(formattedBuckets)

                // Si no hay buckets en auth response, intentar listBuckets explícito
                if (formattedBuckets.length === 0) {
                    const listResult = await window.electronAPI?.gcp.listBuckets()
                    if (listResult?.success) setBuckets(listResult.data)
                }

            } else {
                setError(result?.error || 'Error de autenticación')
            }
        } catch (e: any) {
            setError(e.message)
        } finally {
            setLoading(false)
        }
    }

    const handleBucketClick = async (bucketName: string) => {
        if (selectedBucket === bucketName) {
            setSelectedBucket(null) // Toggle off
            return
        }

        setSelectedBucket(bucketName)
        loadObjects(bucketName, '')
    }

    const loadObjects = async (bucket: string, prefix: string) => {
        setLoading(true)
        try {
            const result = await window.electronAPI?.gcp.listObjects(bucket, prefix)
            if (result?.success) {
                setObjects(result.data)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    const getFileName = (pathStr: string) => {
        return pathStr.split(/[\\/]/).pop() || pathStr
    }

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-2xl font-bold mb-2 text-white flex items-center gap-2">
                    <Cloud className="text-indigo-400" />
                    Google Cloud Storage
                </h2>
                <p className="text-white/60">Gestiona tus buckets y sincronización</p>
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
                        <Button variant="secondary" onClick={handleUploadCredentials} disabled={loading}>
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
                        disabled={!selectedCred || loading}
                        onClick={() => handleAuthenticate()}
                    >
                        {loading ? <RefreshCw className="animate-spin mr-2" /> : <Cloud className="mr-2" />}
                        {isAuthenticated ? 'Re-conectar a GCP' : 'Conectar a GCP'}
                    </Button>
                </div>
            </GlassCard>

            <AnimatePresence>
                {isAuthenticated && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <GlassCard className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <Database className="text-indigo-400" />
                                    <h3 className="text-lg font-medium">Buckets</h3>
                                    <span className="text-sm text-white/40">{buckets.length} buckets disponibles</span>
                                </div>
                                <Button variant="ghost" size="sm" onClick={() => handleAuthenticate()}>
                                    <RefreshCw size={16} />
                                </Button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {buckets.map((bucket) => (
                                    <div key={bucket.name} className="space-y-2">
                                        <div
                                            className={`p-4 rounded-lg border bg-white/5 border-white/10 hover:border-indigo-500/50 transition-colors cursor-pointer ${selectedBucket === bucket.name ? 'border-indigo-500 bg-indigo-500/10' : ''}`}
                                            onClick={() => handleBucketClick(bucket.name)}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 bg-white/5 rounded-lg">
                                                    <Cloud className="text-white/60" size={20} />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="font-medium truncate">{bucket.name}</p>
                                                    <p className="text-xs text-white/40 uppercase">{bucket.location} • {bucket.storage_class}</p>
                                                </div>
                                                {selectedBucket === bucket.name && <ChevronRight className="ml-auto text-indigo-400" />}
                                            </div>
                                        </div>

                                        {/* File Explorer Inline */}
                                        <AnimatePresence>
                                            {selectedBucket === bucket.name && (
                                                <motion.div
                                                    initial={{ height: 0, opacity: 0 }}
                                                    animate={{ height: 'auto', opacity: 1 }}
                                                    exit={{ height: 0, opacity: 0 }}
                                                    className="overflow-hidden"
                                                >
                                                    <div className="ml-8 p-3 rounded-lg bg-black/20 border border-white/5 text-sm">
                                                        <h4 className="text-xs font-bold text-white/40 mb-2 uppercase flex items-center gap-2">
                                                            <Folder size={12} />
                                                            Archivos en {bucket.name}
                                                        </h4>
                                                        {loading && objects.length === 0 ? (
                                                            <div className="text-center py-2"><RefreshCw className="animate-spin inline mr-2" /> Cargando...</div>
                                                        ) : objects.length === 0 ? (
                                                            <div className="text-white/30 italic">Bucket vacío o sin permisos</div>
                                                        ) : (
                                                            <ul className="space-y-1 max-h-60 overflow-y-auto custom-scrollbar">
                                                                {objects.map((obj, i) => (
                                                                    <li key={i} className="flex items-center gap-2 py-1 px-2 hover:bg-white/5 rounded group cursor-default">
                                                                        <FileText size={14} className="text-indigo-300 group-hover:text-indigo-200" />
                                                                        <span className="truncate flex-1 group-hover:text-white transition-colors">{obj.name}</span>
                                                                        <span className="text-xs text-white/30">{Math.round(obj.size / 1024)} KB</span>
                                                                    </li>
                                                                ))}
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
        </div>
    )
}
