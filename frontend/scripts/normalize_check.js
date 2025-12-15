function normalize(value, decodedResult) {
  let raw = value ?? decodedResult
  // Represent raw
  console.debug('raw:', raw, 'type:', typeof raw)
  let normalized = ''
  if (typeof value === 'string') {
    normalized = value.trim()
  } else if (decodedResult && typeof decodedResult === 'object') {
    normalized = (decodedResult.decodedText || decodedResult.text || JSON.stringify(decodedResult) || '').trim()
  } else {
    normalized = String(value).trim()
  }
  return normalized
}

// Tests
const cases = [
  {a: 'EMP_3_2d0b007bad15', b: {decodedText: 'EMP_3_2d0b007bad15'}},
  {a: '  EMP_3_2d0b007bad15\n', b: {decodedText: 'EMP_3_2d0b007bad15 '}},
  {a: '\tEMP_3_abc', b: {text: '\tEMP_3_abc'}},
]

for (const c of cases) {
  const n1 = normalize(c.a, null)
  const n2 = normalize(null, c.b)
  console.log('case', c, '->', n1 === n2 ? 'MATCH' : 'MISMATCH', n1, n2)
}
