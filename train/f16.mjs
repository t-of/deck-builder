// float32 → float16（偶数への丸め。numpy の np.float16 と同じ結果）
const f32 = new Float32Array(1);
const u32 = new Uint32Array(f32.buffer);
export function toF16(v) {
  f32[0] = v;
  const x = u32[0];
  const sign = (x >>> 16) & 0x8000;
  const e = ((x >>> 23) & 255) - 127 + 15;
  const m = x & 0x7fffff;
  if (e >= 31) return sign | 0x7c00;
  if (e <= 0) {
    if (e < -10) return sign;
    const mm = (m | 0x800000) >> (1 - e);
    return sign | ((mm + 0xfff + ((mm >> 13) & 1)) >> 13);
  }
  return sign | ((e << 10) + ((m + 0xfff + ((m >> 13) & 1)) >> 13));
}
