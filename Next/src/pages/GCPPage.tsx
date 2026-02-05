import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Cloud,
    Key,
    CheckCircle2,
    AlertCircle,
    Folder,
    Upload,
    RefreshCw
} from 'lucide-react'
import { GlassCard, Button, StatusBadge } from '../components/ui'

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
    const [selectedCred, setSelectedCred] = useState<string | null>(null)
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [buckets, setBuckets] = useState<Bucket[]>([])
    const [selectedBucket, setSelectedBucket] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Cargar credenciales al montar
    useEffect(() => {
        loadCredentials()
    }, [])

    const loadCredentials = async () => {
        try {
            const result = await window.electronAPI?.gcp.listCredentials()
            if (result?.success) {
                setCredentials(result.data)
                if (result.data.length === 1) {
                    setSelectedCred(result.data[0].path)
                }
            } else {
                setError(result?.error || 'Error al listar credenciales')
            }
        } catch (e: any) {
            setError(e.message)
        }
    }

    const handleAuthenticate = async () => {
        if (!selectedCred) return
        setLoading(true)
        setError(null)

        try {
            const result = await window.electronAPI?.gcp.authenticate(selectedCred)
            if (result?.success && result.data.authenticated) {
                setIsAuthenticated(true)
                const bucketsResult = await window.electronAPI?.gcp.listBuckets()
                if (bucketsResult?.success) {
                    setBuckets(bucketsResult.data)
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

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                        <Cloud className="w-7 h-7 text-accent-400" />
                        Google Cloud Storage
                    </h1>
                    <p className="text-white/50 mt-1">Gestiona tus buckets y sincronización</p>
                </div>

                <StatusBadge
                    status={isAuthenticated ? 'active' : 'inactive'}
                    label={isAuthenticated ? 'Conectado' : 'Desconectado'}
                    pulse={isAuthenticated}
                />
            </div>

            {/* Error Alert */}
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex items-center gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-lg"
                    >
                        <AlertCircle className="w-5 h-5 text-red-400" />
                        <span className="text-red-300">{error}</span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Authentication Section */}
            <GlassCard>
                <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 bg-accent-500/20 rounded-lg">
                        <Key className="w-5 h-5 text-accent-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-semibold text-white">Autenticación</h2>
                        <p className="text-sm text-white/50">Selecciona tus credenciales de servicio</p>
                    </div>
                </div>

                <div className="space-y-4">
                    {/* Credential Selection */}
                    <div className="space-y-2">
                        {credentials.map((cred) => (
                            <motion.div
                                key={cred.path}
                                whileHover={{ scale: 1.01 }}
                                onClick={() => setSelectedCred(cred.path)}
                                className={`p-3 rounded-lg cursor-pointer transition-colors flex items-center gap-3
                  ${selectedCred === cred.path
                                        ? 'bg-accent-600/20 border border-accent-500/50'
                                        : 'bg-white/5 border border-transparent hover:bg-white/10'}`}
                            >
                                <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center
                  ${selectedCred === cred.path ? 'border-accent-500' : 'border-white/30'}`}>
                                    {selectedCred === cred.path && (
                                        <div className="w-2 h-2 rounded-full bg-accent-500" />
                                    )}
                                </div>
                                <div className="flex-1">
                                    <p className="text-white font-medium">{cred.project_id}</p>
                                    <p className="text-sm text-white/50">{cred.client_email}</p>
                                </div>
                                {isAuthenticated && selectedCred === cred.path && (
                                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                                )}
                            </motion.div>
                        ))}

                        {credentials.length === 0 && (
                            <div className="text-center py-8">
                                <Folder className="w-12 h-12 text-white/20 mx-auto mb-3" />
                                <p className="text-white/50">No se encontraron credenciales</p>
                                <Button variant="secondary" size="sm" className="mt-3">
                                    <Upload className="w-4 h-4" />
                                    Cargar credenciales
                                </Button>
                            </div>
                        )}
                    </div>

                    {/* Connect Button */}
                    {credentials.length > 0 && !isAuthenticated && (
                        <Button
                            onClick={handleAuthenticate}
                            loading={loading}
                            disabled={!selectedCred}
                            className="w-full"
                        >
                            <Cloud className="w-4 h-4" />
                            Conectar a GCP
                        </Button>
                    )}
                </div>
            </GlassCard>

            {/* Buckets Section - Only show when authenticated */}
            <AnimatePresence>
                {isAuthenticated && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                    >
                        <GlassCard>
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-blue-500/20 rounded-lg">
                                        <Folder className="w-5 h-5 text-blue-400" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-semibold text-white">Buckets</h2>
                                        <p className="text-sm text-white/50">{buckets.length} buckets disponibles</p>
                                    </div>
                                </div>

                                <Button variant="ghost" size="sm" onClick={() => { }}>
                                    <RefreshCw className="w-4 h-4" />
                                </Button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                {buckets.map((bucket) => (
                                    <motion.div
                                        key={bucket.name}
                                        whileHover={{ scale: 1.02 }}
                                        onClick={() => setSelectedBucket(bucket.name)}
                                        className={`p-4 rounded-lg cursor-pointer transition-all
                      ${selectedBucket === bucket.name
                                                ? 'bg-accent-600/20 border border-accent-500/50'
                                                : 'bg-white/5 border border-transparent hover:bg-white/10'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-white/10 rounded-lg">
                                                <Cloud className="w-4 h-4 text-white/70" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-white font-medium truncate">{bucket.name}</p>
                                                <p className="text-xs text-white/40">{bucket.location} • {bucket.storage_class}</p>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </GlassCard>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
