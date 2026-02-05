import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'
import path from 'path'
import { spawn } from 'child_process'

export default defineConfig({
    plugins: [
        react(),
        electron([
            {
                entry: 'electron/main.ts',
                onstart(args) {
                    const electronBin = path.resolve(__dirname, 'node_modules/electron-bin/dist/electron.exe')
                    console.log(`Starting Electron from: ${electronBin}`)
                    spawn(`"${electronBin}"`, ['.'], { stdio: 'inherit', shell: true })
                },
                vite: {
                    resolve: {
                        alias: {
                            'electron': path.resolve(__dirname, 'node_modules/electron-bin/index.js')
                        }
                    }
                }
            },
            {
                entry: 'electron/preload.ts',
                onstart(args) {
                    args.reload()
                },
                vite: {
                    resolve: {
                        alias: {
                            'electron': path.resolve(__dirname, 'node_modules/electron-bin/index.js')
                        }
                    }
                }
            }
        ]),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src')
        }
    }
})
