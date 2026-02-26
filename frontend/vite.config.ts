import { defineConfig, Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

function serveDataPlugin(): Plugin {
  const dataDir = path.resolve(__dirname, '../data')
  return {
    name: 'serve-data',
    configureServer(server) {
      server.middlewares.use('/data', (req, res, next) => {
        const filePath = path.join(dataDir, req.url || '')
        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
          res.setHeader('Content-Type', 'application/json')
          fs.createReadStream(filePath).pipe(res)
        } else if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
          const files = fs.readdirSync(filePath)
            .filter(f => f.endsWith('.json'))
            .map(f => f.replace('.json', ''))
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(files))
        } else {
          res.statusCode = 404
          res.end('Not found')
        }
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), serveDataPlugin()],
  server: {
    port: 8080,
  },
})
