import { readdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

const assets = join(import.meta.dirname, '..', 'dist', 'assets')

async function safeWrite(path, content, attempts = 5) {
  for (let i = 0; i < attempts; i++) {
    try {
      await writeFile(path, content, 'utf8')
      return
    } catch (err) {
      if (i === attempts - 1) throw err
      await new Promise((res) => setTimeout(res, 150 * (i + 1)))
    }
  }
}

for (const name of await readdir(assets)) {
  if (!name.endsWith('.js')) continue
  const path = join(assets, name)
  const source = await readFile(path, 'utf8')
  const normalized = source.replace(/[ \t]+$/gm, '')
  if (normalized !== source) await safeWrite(path, normalized)
}
