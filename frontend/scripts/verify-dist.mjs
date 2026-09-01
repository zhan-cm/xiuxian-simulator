import { access, readFile, stat } from 'node:fs/promises'
import { join } from 'node:path'

const dist = join(import.meta.dirname, '..', 'dist')
const index = await readFile(join(dist, 'index.html'), 'utf8')
const scripts = [...index.matchAll(/(?:src|href)="\/assets\/([^"]+\.js)"/g)].map((match) => match[1])

if (new Set(scripts).size < 4) throw new Error('生产界面未按职责拆分为至少四个脚本。')

for (const name of new Set(scripts)) {
  const path = join(dist, 'assets', name)
  const info = await stat(path)
  if (info.size >= 500_000) throw new Error(`生产脚本过大：${name}（${info.size} bytes）`)
  const source = await readFile(path, 'utf8')
  if (/[ \t]+$/m.test(source)) throw new Error(`生产脚本含行尾空白：${name}`)
}

await access(join(dist, 'third-party-licenses.md'))
if (!/href="\/assets\/[^"]+\.css"/.test(index)) throw new Error('生产界面缺少样式资源。')

console.log(`生产资源验证通过：${new Set(scripts).size} 个脚本块，第三方许可已就绪。`)
