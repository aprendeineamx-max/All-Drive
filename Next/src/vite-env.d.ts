/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_DEV_SERVER_URL: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}

declare global {
    interface Window {
        electronAPI: {
            minimize: () => void
            maximize: () => void
            close: () => void
            getVersion: () => Promise<string>
            getAppName: () => Promise<string>
            gcp: {
                listCredentials: () => Promise<{ success: boolean; data: any; error?: string }>
                authenticate: (credPath: string) => Promise<{ success: boolean; data: any; error?: string }>
                listBuckets: () => Promise<{ success: boolean; data: any; error?: string }>
                listObjects: (bucket: string, prefix: string) => Promise<{ success: boolean; data: any; error?: string }>
                mountBucket: (bucket: string, drive: string) => Promise<{ success: boolean; data: any; error?: string }>
                unmountDrive: (drive: string) => Promise<{ success: boolean; data: any; error?: string }>
                startSync: (localPath: string, bucketName: string) => Promise<{ success: boolean; data: any; error?: string }>
                openDirectory: () => Promise<{ success: boolean; data?: string }>
                uploadCredentials: () => Promise<{ success: boolean; data?: string; error?: string }>
                uploadFile: (bucket: string, prefix: string) => Promise<{ success: boolean; cancelled?: boolean; error?: string }>
                uploadFolder: (bucket: string, prefix: string) => Promise<{ success: boolean; cancelled?: boolean; count?: number; error?: string }>
                onLog: (callback: (message: string) => void) => () => void
                loadSession: () => Promise<{ success: boolean; data?: any }>
            }
        }
    }
}

```
