/**
 * Bundle Size Analysis Script
 * Estimates animation feature bundle size
 */

const fs = require('fs');
const path = require('path');

const animationFiles = [
  'src/types/animation.types.ts',
  'src/types/search.types.ts',
  'src/stores/animationStore.ts',
  'src/lib/searchClient.ts',
  'src/lib/analytics.ts',
  'src/hooks/animation/useAnimationController.ts',
  'src/hooks/animation/useSlowResponseHandler.ts',
  'src/hooks/animation/useFastResponseAcceleration.ts',
  'src/hooks/animation/useFocusTrap.ts',
  'src/hooks/animation/useAnimationAnalytics.ts',
  'src/hooks/useSearchAPI.ts',
  'src/components/search/animation/config/animationConfig.ts',
  'src/components/search/animation/config/errorMessages.ts',
  'src/components/search/animation/AnimationCard.tsx',
  'src/components/search/animation/SearchStage.tsx',
  'src/components/search/animation/ConnectionLine.tsx',
  'src/components/search/animation/ProgressBar.tsx',
  'src/components/search/animation/StageCounter.tsx',
  'src/components/search/animation/CancelButton.tsx',
  'src/components/search/animation/ErrorDisplay.tsx',
  'src/components/search/animation/AISearchAnimation.tsx',
  'src/components/search/SearchWithAnimation.tsx',
];

let totalSize = 0;
let totalLines = 0;

console.log('📊 AI Search Animation Bundle Analysis\n');
console.log('=' .repeat(60));

animationFiles.forEach((file) => {
  const filePath = path.join(__dirname, file);
  try {
    const stats = fs.statSync(filePath);
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n').length;

    totalSize += stats.size;
    totalLines += lines;

    console.log(`${file.padEnd(55)} ${(stats.size / 1024).toFixed(2).padStart(8)} KB`);
  } catch (err) {
    console.log(`${file.padEnd(55)} [NOT FOUND]`);
  }
});

console.log('=' .repeat(60));
console.log(`Total uncompressed size: ${(totalSize / 1024).toFixed(2)} KB`);
console.log(`Total lines of code: ${totalLines}`);

// Estimate gzipped size (typically 70-80% compression for code)
const estimatedGzipped = totalSize * 0.25; // Conservative 75% compression
console.log(`Estimated gzipped size: ${(estimatedGzipped / 1024).toFixed(2)} KB`);

// Dependencies estimate
console.log('\n📦 External Dependencies:');
console.log('  - framer-motion: ~15 KB (gzipped, tree-shaken)');
console.log('  - zustand: ~1 KB (gzipped)');
console.log('  - uuid: ~2 KB (gzipped)');
console.log('  - lucide-react icons: ~3 KB (gzipped, lazy-loaded)');

const totalWithDeps = estimatedGzipped + (15 + 1 + 2 + 3) * 1024;
console.log(`\nTotal with dependencies: ${(totalWithDeps / 1024).toFixed(2)} KB (gzipped)`);

// Target check
const target = 15 * 1024; // 15 KB
const isUnderTarget = totalWithDeps < target;

console.log('\n🎯 Performance Target:');
console.log(`  Target: 15 KB (gzipped)`);
console.log(`  Current: ${(totalWithDeps / 1024).toFixed(2)} KB`);
console.log(`  Status: ${isUnderTarget ? '✅ PASS' : '⚠️  OVER TARGET'}`);

if (!isUnderTarget) {
  console.log('\n💡 Optimization Suggestions:');
  console.log('  1. Lazy load ErrorDisplay component');
  console.log('  2. Code split analytics to separate chunk');
  console.log('  3. Use dynamic imports for icons');
  console.log('  4. Minimize error message strings');
}

console.log('\n✅ Analysis complete');
