import { readdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

const assets = join(import.meta.dirname, '..', 'dist', 'assets')

for (const name of await readdir(assets)) {
  if (!name.endsWith('.js')) continue
  const path = join(assets, name)
  const source = await readFile(path, 'utf8')
  const normalized = source.replace(/[ \t]+$/gm, '')
  if (normalized !== source) await writeFile(path, normalized, 'utf8')
}
